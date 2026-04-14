"""
Shared utilities for the Loan Default Prediction model notebooks.

Usage:
    from shared_utils import *
    X_train, X_test, y_train, y_test, df, prep_linear, prep_tree, cv = load_and_prep()
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from pathlib import Path

# Visualization
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.templates.default = "plotly_white"

# Sklearn
from sklearn.model_selection import (
    train_test_split, GridSearchCV, StratifiedKFold, cross_val_score
)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    roc_curve, precision_recall_curve, classification_report,
    make_scorer
)

# ================================================================
# CONSTANTS
# ================================================================
RANDOM_STATE = 42
TARGET = "BAD"
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = _PROJECT_ROOT / "data" / "inputs" / "hmeq.csv"
OUTPUT_BASE = _PROJECT_ROOT / "data" / "outputs"

# Color palette (Midnight Executive)
COLORS = {
    "navy":    "#1E2761",
    "ice":     "#CADCFC",
    "accent":  "#4A90D9",
    "green":   "#2CA58D",
    "red":     "#E15554",
    "orange":  "#F18F01",
    "light":   "#f8f9fa",
    "white":   "#ffffff",
    "gray":    "#6c757d",
}

# Plotly color sequences
COLOR_SEQ = [COLORS["navy"], COLORS["accent"], COLORS["ice"],
             COLORS["green"], COLORS["orange"], COLORS["red"]]
COLOR_BINARY = [COLORS["accent"], COLORS["red"]]


# ================================================================
# DATA LOADING
# ================================================================
def load_and_prep():
    """
    Load HMEQ data, create missing flags, split train/test, build pipelines.

    Returns
    -------
    X_train, X_test, y_train, y_test : arrays
    df : original DataFrame
    df_proc : processed DataFrame (with missing flags)
    prep_linear : ColumnTransformer for linear/distance models
    prep_tree : ColumnTransformer for tree models
    cv : StratifiedKFold cross-validator
    numeric_features : list of numeric column names
    categorical_features : list of categorical column names
    """
    df = pd.read_csv(DATA_PATH)

    # Missing flags
    flag_cols = [c for c in df.columns
                 if c != TARGET and df[c].isna().sum() > 0 and df[c].dtype != "object"]
    flag_cols = sorted(flag_cols, key=lambda c: df[c].isna().sum(), reverse=True)[:5]

    df_proc = df.copy()
    for c in flag_cols:
        df_proc[f"{c}_missing"] = df_proc[c].isna().astype(int)

    categorical_features = ["REASON", "JOB"]
    numeric_features = [c for c in df_proc.columns
                        if c not in categorical_features + [TARGET]
                        and df_proc[c].dtype != "object"]

    X = df_proc.drop(columns=[TARGET])
    y = df_proc[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE
    )

    prep_linear = ColumnTransformer([
        ("num", Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("scale",  StandardScaler()),
        ]), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ])

    prep_tree = ColumnTransformer([
        ("num", SimpleImputer(strategy="median"), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Default rate: {y.mean():.2%}")
    print(f"Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")
    print(f"Numeric features: {len(numeric_features)} | Categorical: {len(categorical_features)}")
    print(f"Positive class weight: {pos_weight:.2f}")

    return (X_train, X_test, y_train, y_test, df, df_proc,
            prep_linear, prep_tree, cv,
            numeric_features, categorical_features, pos_weight)


# ================================================================
# EVALUATION
# ================================================================
def evaluate_model(name, model, X_test, y_test, cv_score=None):
    """
    Score a fitted model on test set. Returns a dict of metrics.
    """
    y_pred = model.predict(X_test)

    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X_test)[:, 1]
    elif hasattr(model, "decision_function"):
        y_score = model.decision_function(X_test)
    else:
        y_score = y_pred.astype(float)

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        "model": name,
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision_1": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall_1": round(recall_score(y_test, y_pred), 4),
        "f1_1": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_score), 4),
        "pr_auc": round(average_precision_score(y_test, y_score), 4),
        "cv_score": round(cv_score, 4) if cv_score is not None else None,
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }

    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    print(f"  Recall: {metrics['recall_1']:.4f}  |  Precision: {metrics['precision_1']:.4f}  |  F1: {metrics['f1_1']:.4f}")
    print(f"  AUC: {metrics['roc_auc']:.4f}  |  PR-AUC: {metrics['pr_auc']:.4f}")
    print(f"  Confusion: TP={tp} FP={fp} FN={fn} TN={tn}")

    return metrics, y_pred, y_score


# ================================================================
# UNIVERSAL CHART FUNCTIONS
# ================================================================
def plot_roc_curve(y_test, y_score, model_name):
    """ROC curve with AUC annotation."""
    fpr, tpr, _ = roc_curve(y_test, y_score)
    auc_val = roc_auc_score(y_test, y_score)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr, mode="lines",
        name=f"{model_name} (AUC={auc_val:.4f})",
        line=dict(color=COLORS["navy"], width=2),
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines",
        name="Random (AUC=0.50)",
        line=dict(color=COLORS["gray"], width=1, dash="dash"),
    ))
    fig.update_layout(
        title=f"ROC Curve: {model_name}",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=450, width=600,
        legend=dict(x=0.4, y=0.1),
    )
    return fig


def plot_pr_curve(y_test, y_score, model_name):
    """Precision-Recall curve with AP annotation."""
    prec_arr, rec_arr, _ = precision_recall_curve(y_test, y_score)
    ap = average_precision_score(y_test, y_score)
    baseline = y_test.mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rec_arr, y=prec_arr, mode="lines",
        name=f"{model_name} (AP={ap:.4f})",
        line=dict(color=COLORS["accent"], width=2),
    ))
    fig.add_hline(y=baseline, line_dash="dash", line_color=COLORS["gray"],
                  annotation_text=f"Baseline ({baseline:.2%})")
    fig.update_layout(
        title=f"Precision-Recall Curve: {model_name}",
        xaxis_title="Recall",
        yaxis_title="Precision",
        height=450, width=600,
    )
    return fig


def plot_confusion_matrix(y_test, y_pred, model_name):
    """Confusion matrix heatmap."""
    cm = confusion_matrix(y_test, y_pred)
    total = cm.sum()

    labels = np.array([
        [f"TN={cm[0,0]}<br>({cm[0,0]/total:.1%})", f"FP={cm[0,1]}<br>({cm[0,1]/total:.1%})"],
        [f"FN={cm[1,0]}<br>({cm[1,0]/total:.1%})", f"TP={cm[1,1]}<br>({cm[1,1]/total:.1%})"],
    ])

    fig = go.Figure(data=go.Heatmap(
        z=cm, x=["Predicted Good", "Predicted Default"],
        y=["Actually Good", "Actually Default"],
        text=labels, texttemplate="%{text}",
        colorscale=[[0, COLORS["ice"]], [1, COLORS["navy"]]],
        showscale=False,
    ))
    fig.update_layout(
        title=f"Confusion Matrix: {model_name}",
        height=400, width=500,
        yaxis=dict(autorange="reversed"),
    )
    return fig


def plot_threshold_sweep(y_test, y_score, model_name):
    """Recall, Precision, F1 vs classification threshold."""
    thresholds = np.arange(0.01, 1.00, 0.01)
    rows = []
    for t in thresholds:
        y_pred_t = (y_score >= t).astype(int)
        if len(np.unique(y_pred_t)) < 2:
            continue
        rows.append({
            "threshold": t,
            "recall": recall_score(y_test, y_pred_t),
            "precision": precision_score(y_test, y_pred_t, zero_division=0),
            "f1": f1_score(y_test, y_pred_t),
        })
    df_t = pd.DataFrame(rows)

    fig = go.Figure()
    for metric, color in [("recall", COLORS["navy"]),
                          ("precision", COLORS["accent"]),
                          ("f1", COLORS["orange"])]:
        fig.add_trace(go.Scatter(
            x=df_t["threshold"], y=df_t[metric],
            name=metric.capitalize(),
            line=dict(color=color, width=2),
        ))
    fig.add_vline(x=0.5, line_dash="dash", line_color=COLORS["gray"],
                  annotation_text="Default (0.5)")
    fig.update_layout(
        title=f"Threshold Sweep: {model_name}",
        xaxis_title="Classification Threshold",
        yaxis_title="Score",
        height=450, width=650,
        legend=dict(orientation="h", y=1.1),
    )
    return fig


def plot_feature_importance(importances, feature_names, model_name, importance_type=""):
    """Horizontal bar chart of feature importances."""
    df_imp = pd.DataFrame({
        "feature": feature_names,
        "importance": importances,
    }).sort_values("importance", ascending=True).tail(15)

    title = f"Feature Importance: {model_name}"
    if importance_type:
        title += f" ({importance_type})"

    fig = px.bar(
        df_imp, x="importance", y="feature", orientation="h",
        title=title,
        color_discrete_sequence=[COLORS["navy"]],
        height=max(350, len(df_imp) * 28),
    )
    fig.update_layout(yaxis_title="", xaxis_title="Importance")
    return fig


# ================================================================
# CHART EXPORT
# ================================================================
def save_chart(fig, model_slug, chart_name):
    """
    Save a plotly figure as an interactive HTML file.

    Parameters
    ----------
    fig : plotly Figure
    model_slug : str — folder name (e.g., 'logistic_regression')
    chart_name : str — file stem (e.g., 'roc_curve')
    """
    out_dir = OUTPUT_BASE / model_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{chart_name}.html"
    fig.write_html(
        str(path),
        include_plotlyjs="cdn",
        full_html=True,
        config={"displayModeBar": True, "responsive": True},
    )
    print(f"  Saved: {path.relative_to(OUTPUT_BASE.parent)}")
    return path


def save_all_universal_charts(y_test, y_pred, y_score, model_name, model_slug):
    """Generate and save all 4 universal charts."""
    charts = {}
    charts["roc"] = plot_roc_curve(y_test, y_score, model_name)
    charts["pr"] = plot_pr_curve(y_test, y_score, model_name)
    charts["cm"] = plot_confusion_matrix(y_test, y_pred, model_name)
    charts["threshold"] = plot_threshold_sweep(y_test, y_score, model_name)

    print(f"\nSaving universal charts for {model_name}:")
    save_chart(charts["roc"], model_slug, "roc_curve")
    save_chart(charts["pr"], model_slug, "precision_recall_curve")
    save_chart(charts["cm"], model_slug, "confusion_matrix")
    save_chart(charts["threshold"], model_slug, "threshold_sweep")

    return charts


# ================================================================
# WORKED EXAMPLE HELPERS
# ================================================================
def get_example_rows(df, n=3):
    """
    Pick example rows from the dataset for worked examples.
    Returns n rows: at least 1 default and 1 non-default.
    """
    defaults = df[df[TARGET] == 1].sample(max(1, n // 2), random_state=RANDOM_STATE)
    non_defaults = df[df[TARGET] == 0].sample(n - len(defaults), random_state=RANDOM_STATE)
    examples = pd.concat([non_defaults, defaults]).reset_index(drop=True)
    return examples


def print_example_row(row, idx):
    """Pretty print a data row for worked examples."""
    print(f"\n--- Example Borrower {idx + 1} (Actual: {'DEFAULT' if row[TARGET] == 1 else 'GOOD'}) ---")
    for col, val in row.items():
        if col != TARGET:
            print(f"  {col:15s}: {val}")
