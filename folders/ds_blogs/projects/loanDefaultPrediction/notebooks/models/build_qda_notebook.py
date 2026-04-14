"""
Builder script to generate 03_qda.ipynb for the loan default prediction blog.
Constructs a complete Jupyter notebook with QDA analysis following the pattern
established by existing models (Decision Tree, Naive Bayes, etc).
"""

import ast
import json
from pathlib import Path

def build_notebook():
    """Build QDA notebook cells."""

    cells = []

    # Cell 0: Title markdown
    cells.append({
        "cell_type": "markdown",
        "id": "cell-0",
        "metadata": {},
        "source": [
            "# Quadratic Discriminant Analysis (QDA): Deep Dive\n",
            "## Loan Default Prediction (HMEQ Dataset)\n",
            "\n",
            "*Part of the [ML Model Comparison](../loan_default_tradeoff_matrix.html) series on bitterscientist.com*\n",
            "\n",
            "This notebook covers:\n",
            "1. The math behind QDA (class-conditional Gaussians, separate covariance matrices, quadratic decision boundary)\n",
            "2. Comparison with LDA (shared vs. separate covariance)\n",
            "3. Worked examples using actual HMEQ data\n",
            "4. Model training with hyperparameter tuning\n",
            "5. Diagnostic visualizations (exported as interactive plotly HTML)\n",
            "6. Results interpretation"
        ]
    })

    # Cell 1: Section divider
    cells.append({
        "cell_type": "markdown",
        "id": "cell-1",
        "metadata": {},
        "source": ["---\n", "## 1. Setup"]
    })

    # Cell 2: Imports and setup
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-2",
        "metadata": {},
        "outputs": [],
        "source": [
            "import sys\n",
            "sys.path.insert(0, \".\")\n",
            "from shared_utils import *\n",
            "\n",
            "# Additional imports\n",
            "from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis, LinearDiscriminantAnalysis\n",
            "from sklearn.decomposition import PCA\n",
            "\n",
            "MODEL_NAME = \"Quadratic Discriminant Analysis\"\n",
            "MODEL_SLUG = \"qda\"\n",
            "\n",
            "# Load data\n",
            "(X_train, X_test, y_train, y_test, df, df_proc,\n",
            " prep_linear, prep_tree, cv,\n",
            " numeric_features, categorical_features, pos_weight) = load_and_prep()"
        ]
    })

    # Cell 3: Math section intro
    cells.append({
        "cell_type": "markdown",
        "id": "cell-3",
        "metadata": {},
        "source": [
            "---\n",
            "## 2. The Math Behind QDA\n",
            "\n",
            "### 2.1 From Bayes' Theorem to QDA\n",
            "\n",
            "QDA, like Linear Discriminant Analysis (LDA), is grounded in Bayes' theorem:\n",
            "\n",
            "$$P(Y=c \\mid \\mathbf{x}) = \\frac{P(\\mathbf{x} \\mid Y=c) \\cdot P(Y=c)}{P(\\mathbf{x})}$$\n",
            "\n",
            "For classification, we compare classes via:\n",
            "\n",
            "$$\\hat{y} = \\arg\\max_c \\ P(\\mathbf{x} \\mid Y=c) \\cdot P(Y=c)$$\n",
            "\n",
            "The key difference between LDA and QDA is in the covariance structure:\n",
            "\n",
            "| Method | Covariance | Decision Boundary | Flexibility |\n",
            "|--------|-----------|-------------------|-------------|\n",
            "| **LDA** | Same (\\(\\boldsymbol{\\Sigma}\\)) across all classes | Linear | Lower (fewer parameters) |\n",
            "| **QDA** | Separate (\\(\\boldsymbol{\\Sigma}_c\\)) per class | Quadratic | Higher (more parameters) |\n",
            "\n",
            "### 2.2 The Multivariate Gaussian Assumption\n",
            "\n",
            "Both methods assume each class follows a multivariate Gaussian distribution:\n",
            "\n",
            "$$P(\\mathbf{x} \\mid Y=c) = \\frac{1}{(2\\pi)^{p/2} |\\boldsymbol{\\Sigma}_c|^{1/2}} \\exp\\left(-\\frac{1}{2}(\\mathbf{x} - \\boldsymbol{\\mu}_c)^T \\boldsymbol{\\Sigma}_c^{-1} (\\mathbf{x} - \\boldsymbol{\\mu}_c)\\right)$$\n",
            "\n",
            "where:\n",
            "- \\(\\boldsymbol{\\mu}_c\\) is the mean vector for class \\(c\\)\n",
            "- \\(\\boldsymbol{\\Sigma}_c\\) is the covariance matrix for class \\(c\\)\n",
            "- \\(|\\boldsymbol{\\Sigma}_c|\\) is the determinant of \\(\\boldsymbol{\\Sigma}_c\\)\n",
            "\n",
            "### 2.3 QDA: Separate Covariance Matrices\n",
            "\n",
            "The quadratic discriminant function is derived by taking the log of the Gaussian likelihood. For a new sample \\(\\mathbf{x}\\), define:\n",
            "\n",
            "$$\\delta_c^{\\text{QDA}}(\\mathbf{x}) = -\\frac{1}{2}\\ln|\\boldsymbol{\\Sigma}_c| - \\frac{1}{2}(\\mathbf{x} - \\boldsymbol{\\mu}_c)^T \\boldsymbol{\\Sigma}_c^{-1} (\\mathbf{x} - \\boldsymbol{\\mu}_c) + \\ln P(Y=c)$$\n",
            "\n",
            "The first term \\(-\\frac{1}{2}\\ln|\\boldsymbol{\\Sigma}_c|\\) varies with class, making the decision boundary nonlinear. When expanded in matrix form, this is a quadratic function of \\(\\mathbf{x}\\).\n",
            "\n",
            "Classification rule:\n",
            "$$\\hat{y} = \\arg\\max_c \\ \\delta_c^{\\text{QDA}}(\\mathbf{x})$$\n",
            "\n",
            "### 2.4 LDA: Shared Covariance Matrix (for comparison)\n",
            "\n",
            "LDA assumes all classes share the same covariance matrix \\(\\boldsymbol{\\Sigma}\\). The discriminant function becomes:\n",
            "\n",
            "$$\\delta_c^{\\text{LDA}}(\\mathbf{x}) = -\\frac{1}{2}(\\mathbf{x} - \\boldsymbol{\\mu}_c)^T \\boldsymbol{\\Sigma}^{-1} (\\mathbf{x} - \\boldsymbol{\\mu}_c) + \\ln P(Y=c)$$\n",
            "\n",
            "The covariance determinant term cancels out (same for all classes), and when expanded, the quadratic term is the same for all classes—leaving only a linear function in \\(\\mathbf{x}\\). This creates a linear decision boundary.\n",
            "\n",
            "### 2.5 Parameter Estimation\n",
            "\n",
            "**Mean vectors** (fitted from training data):\n",
            "$$\\boldsymbol{\\mu}_c = \\frac{1}{n_c} \\sum_{i: y_i = c} \\mathbf{x}_i$$\n",
            "\n",
            "**QDA Covariance** (separate per class):\n",
            "$$\\boldsymbol{\\Sigma}_c = \\frac{1}{n_c} \\sum_{i: y_i = c} (\\mathbf{x}_i - \\boldsymbol{\\mu}_c)(\\mathbf{x}_i - \\boldsymbol{\\mu}_c)^T$$\n",
            "\n",
            "**LDA Covariance** (pooled across classes):\n",
            "$$\\boldsymbol{\\Sigma} = \\sum_{c} \\frac{n_c}{n} \\boldsymbol{\\Sigma}_c$$\n",
            "\n",
            "**Class priors**:\n",
            "$$P(Y=c) = \\frac{n_c}{n}$$\n",
            "\n",
            "### 2.6 Regularization: The reg_param\n",
            "\n",
            "When the number of features is large relative to the number of samples per class, the sample covariance matrix becomes singular or ill-conditioned. Sklearn's `reg_param` applies regularization:\n",
            "\n",
            "$$\\boldsymbol{\\Sigma}_c^{\\text{reg}} = (1 - \\text{reg\\_param}) \\boldsymbol{\\Sigma}_c + \\text{reg\\_param} \\cdot \\text{diag}(\\boldsymbol{\\Sigma}_c)$$\n",
            "\n",
            "This shrinks the off-diagonal covariance elements toward zero, stabilizing the matrix inversion and reducing overfitting."
        ]
    })

    # Cell 4: Covariance visualization
    cells.append({
        "cell_type": "markdown",
        "id": "cell-4",
        "metadata": {},
        "source": [
            "---\n",
            "## 3. Visualizing Class-Conditional Covariance Matrices"
        ]
    })

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-5",
        "metadata": {},
        "outputs": [],
        "source": [
            "# Transform training data\n",
            "X_train_t = prep_linear.fit_transform(X_train)\n",
            "X_test_t = prep_linear.transform(X_test)\n",
            "\n",
            "cat_encoder = prep_linear.named_transformers_[\"cat\"]\n",
            "cat_names = list(cat_encoder.get_feature_names_out(categorical_features))\n",
            "all_feature_names = numeric_features + cat_names\n",
            "\n",
            "# Fit QDA and LDA to extract covariance structure\n",
            "qda = QuadraticDiscriminantAnalysis()\n",
            "qda.fit(X_train_t, y_train)\n",
            "\n",
            "lda = LinearDiscriminantAnalysis()\n",
            "lda.fit(X_train_t, y_train)\n",
            "\n",
            "# QDA has separate covariance matrices for each class\n",
            "pca = PCA(n_components=10, random_state=42)\n",
            "pca.fit(X_train_t)\n",
            "\n",
            "# Project covariance matrices to 2D for visualization\n",
            "# Show the first 5 PCA components\n",
            "n_comp_viz = min(5, X_train_t.shape[1])\n",
            "\n",
            "from plotly.subplots import make_subplots\n",
            "\n",
            "fig = make_subplots(\n",
            "    rows=1, cols=2,\n",
            "    subplot_titles=(\"QDA: Good Loans (Class 0)\", \"QDA: Defaults (Class 1)\"),\n",
            ")\n",
            "\n",
            "for class_idx, color, title_suffix in [(0, COLORS[\"accent\"], \"Good\"), (1, COLORS[\"red\"], \"Default\")]:\n",
            "    cov_matrix = qda.covariance_[class_idx][:n_comp_viz, :n_comp_viz]\n",
            "    \n",
            "    fig.add_trace(go.Heatmap(\n",
            "        z=cov_matrix,\n",
            "        colorscale=[[0, COLORS[\"ice\"]], [0.5, COLORS[\"white\"]], [1, color]],\n",
            "        colorbar=dict(title=\"Cov\", x=0.46 if class_idx == 0 else 1.02),\n",
            "        showscale=True,\n",
            "        text=np.round(cov_matrix, 3),\n",
            "        texttemplate=\"%{text:.2f}\",\n",
            "        textfont={\"size\": 8},\n",
            "    ), row=1, col=class_idx + 1)\n",
            "\n",
            "fig.update_layout(\n",
            "    title=\"QDA: Class-Specific Covariance Matrices (First 5 PCA Components)\",\n",
            "    height=500, width=900,\n",
            ")\n",
            "fig.show()\n",
            "save_chart(fig, MODEL_SLUG, \"covariance_matrices\")"
        ]
    })

    # Cell 6: Worked example
    cells.append({
        "cell_type": "markdown",
        "id": "cell-6",
        "metadata": {},
        "source": [
            "---\n",
            "## 4. Worked Example: Manual QDA Prediction"
        ]
    })

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-7",
        "metadata": {},
        "outputs": [],
        "source": [
            "print(\"=\"*70)\n",
            "print(\"WORKED EXAMPLE: Manual QDA Discriminant Calculation\")\n",
            "print(\"=\"*70)\n",
            "\n",
            "# Use first test sample\n",
            "test_idx = 0\n",
            "x_query = X_test_t[test_idx]\n",
            "actual = y_test.iloc[test_idx]\n",
            "\n",
            "print(f\"\\nQuery borrower (Actual: {'DEFAULT' if actual == 1 else 'GOOD'})\")\n",
            "print(f\"Feature vector (first 5 components): {x_query[:5]}\")\n",
            "\n",
            "# Class priors\n",
            "prior_0 = qda.priors_[0]\n",
            "prior_1 = qda.priors_[1]\n",
            "\n",
            "print(f\"\\nStep 1: Class Priors (from training data)\")\n",
            "print(f\"  P(Good)    = {prior_0:.4f}\")\n",
            "print(f\"  P(Default) = {prior_1:.4f}\")\n",
            "\n",
            "# Compute discriminant functions\n",
            "print(f\"\\nStep 2: Compute QDA Discriminant Functions\")\n",
            "print(f\"  QDA uses SEPARATE covariance matrices per class\")\n",
            "print(f\"  Σ_good shape:    {qda.covariance_[0].shape}\")\n",
            "print(f\"  Σ_default shape: {qda.covariance_[1].shape}\")\n",
            "\n",
            "# Manual discriminant computation for visualization\n",
            "for c in [0, 1]:\n",
            "    mu = qda.means_[c]\n",
            "    sigma = qda.covariance_[c]\n",
            "    \n",
            "    diff = x_query - mu\n",
            "    try:\n",
            "        sigma_inv = np.linalg.inv(sigma)\n",
            "        det_sigma = np.linalg.det(sigma)\n",
            "    except:\n",
            "        print(f\"  Warning: Singular covariance for class {c}\")\n",
            "        continue\n",
            "    \n",
            "    # Quadratic term (class-specific)\n",
            "    quad_term = -0.5 * diff @ sigma_inv @ diff\n",
            "    # Determinant term (class-specific - this is what makes it QUADRATIC)\n",
            "    det_term = -0.5 * np.log(det_sigma)\n",
            "    # Prior term\n",
            "    prior_term = np.log(qda.priors_[c])\n",
            "    \n",
            "    delta_c = quad_term + det_term + prior_term\n",
            "    \n",
            "    class_name = \"Good\" if c == 0 else \"Default\"\n",
            "    print(f\"\\n  Class {c} ({class_name}):\")\n",
            "    print(f\"    Quadratic term:    {quad_term:.4f}\")\n",
            "    print(f\"    Log|Σ| term:       {det_term:.4f}\")\n",
            "    print(f\"    Log Prior term:    {prior_term:.4f}\")\n",
            "    print(f\"    Total δ_c:         {delta_c:.4f}\")\n",
            "\n",
            "# Use sklearn's predict_proba\n",
            "prob_sklearn = qda.predict_proba(x_query.reshape(1, -1))[0]\n",
            "pred_sklearn = qda.predict(x_query.reshape(1, -1))[0]\n",
            "\n",
            "print(f\"\\nStep 3: Final Probabilities (via softmax)\")\n",
            "print(f\"  P(Good|x)    = {prob_sklearn[0]:.4f}\")\n",
            "print(f\"  P(Default|x) = {prob_sklearn[1]:.4f}\")\n",
            "\n",
            "pred_str = \"DEFAULT\" if prob_sklearn[1] >= 0.5 else \"GOOD\"\n",
            "actual_str = \"DEFAULT\" if actual == 1 else \"GOOD\"\n",
            "match = \"CORRECT\" if pred_str == actual_str else \"INCORRECT\"\n",
            "\n",
            "print(f\"\\nStep 4: Classification Decision\")\n",
            "print(f\"  Predicted: {pred_str}\")\n",
            "print(f\"  Actual:    {actual_str}\")\n",
            "print(f\"  Result:    {match}\")"
        ]
    })

    # Cell 8: Model training
    cells.append({
        "cell_type": "markdown",
        "id": "cell-8",
        "metadata": {},
        "source": [
            "---\n",
            "## 5. Model Training with Hyperparameter Tuning"
        ]
    })

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-9",
        "metadata": {},
        "outputs": [],
        "source": [
            "# QDA hyperparameter: reg_param for regularization\n",
            "param_grid = {\n",
            "    \"clf__reg_param\": np.linspace(0.0, 1.0, 11),\n",
            "}\n",
            "\n",
            "qda_pipe = Pipeline([\n",
            "    (\"prep\", prep_linear),\n",
            "    (\"clf\", QuadraticDiscriminantAnalysis()),\n",
            "])\n",
            "\n",
            "grid = GridSearchCV(\n",
            "    qda_pipe, param_grid, cv=cv,\n",
            "    scoring=\"recall\", n_jobs=-1, refit=True,\n",
            ")\n",
            "grid.fit(X_train, y_train)\n",
            "\n",
            "best_qda = grid.best_estimator_\n",
            "best_reg_param = grid.best_params_[\"clf__reg_param\"]\n",
            "print(f\"Best reg_param: {best_reg_param:.4f}\")\n",
            "print(f\"Best CV recall: {grid.best_score_:.4f}\")"
        ]
    })

    # Cell 10: Evaluation
    cells.append({
        "cell_type": "markdown",
        "id": "cell-10",
        "metadata": {},
        "source": [
            "---\n",
            "## 6. Model Evaluation"
        ]
    })

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-11",
        "metadata": {},
        "outputs": [],
        "source": [
            "cv_scores = cross_val_score(best_qda, X_train, y_train, cv=cv, scoring=\"recall\")\n",
            "cv_mean = cv_scores.mean()\n",
            "print(f\"CV Recall scores: {cv_scores}\")\n",
            "print(f\"CV Recall mean: {cv_mean:.4f} (+/- {cv_scores.std():.4f})\")\n",
            "\n",
            "# Test set evaluation\n",
            "metrics, y_pred, y_score = evaluate_model(MODEL_NAME, best_qda, X_test, y_test, cv_mean)\n",
            "\n",
            "print(f\"\\nClassification Report:\")\n",
            "print(classification_report(y_test, y_pred, target_names=[\"Good Loan\", \"Default\"]))"
        ]
    })

    # Cell 12: QDA vs LDA comparison
    cells.append({
        "cell_type": "markdown",
        "id": "cell-12",
        "metadata": {},
        "source": [
            "---\n",
            "## 7. QDA vs LDA: Comparison on the HMEQ Data"
        ]
    })

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-13",
        "metadata": {},
        "outputs": [],
        "source": [
            "# Train LDA for comparison\n",
            "lda_pipe = Pipeline([\n",
            "    (\"prep\", prep_linear),\n",
            "    (\"clf\", LinearDiscriminantAnalysis(shrinkage=\"auto\", solver=\"lsqr\")),\n",
            "])\n",
            "lda_pipe.fit(X_train, y_train)\n",
            "\n",
            "# Compare metrics\n",
            "models_to_compare = [\n",
            "    (\"QDA\", best_qda),\n",
            "    (\"LDA\", lda_pipe),\n",
            "]\n",
            "\n",
            "comparison_results = []\n",
            "for name, model in models_to_compare:\n",
            "    y_pred_temp = model.predict(X_test)\n",
            "    y_proba_temp = model.predict_proba(X_test)[:, 1]\n",
            "    \n",
            "    comparison_results.append({\n",
            "        \"Model\": name,\n",
            "        \"Accuracy\": accuracy_score(y_test, y_pred_temp),\n",
            "        \"Recall\": recall_score(y_test, y_pred_temp),\n",
            "        \"Precision\": precision_score(y_test, y_pred_temp, zero_division=0),\n",
            "        \"F1\": f1_score(y_test, y_pred_temp),\n",
            "        \"AUC\": roc_auc_score(y_test, y_proba_temp),\n",
            "    })\n",
            "\n",
            "df_comparison = pd.DataFrame(comparison_results)\n",
            "print(\"\\nQDA vs LDA Performance Comparison:\")\n",
            "print(df_comparison.to_string(index=False))\n",
            "\n",
            "# Visualize\n",
            "fig_comp = go.Figure(data=[\n",
            "    go.Bar(name=\"QDA\", x=df_comparison.columns[1:], y=df_comparison.iloc[0, 1:].values,\n",
            "           marker_color=COLORS[\"navy\"]),\n",
            "    go.Bar(name=\"LDA\", x=df_comparison.columns[1:], y=df_comparison.iloc[1, 1:].values,\n",
            "           marker_color=COLORS[\"accent\"]),\n",
            "])\n",
            "fig_comp.update_layout(\n",
            "    title=\"QDA vs LDA: Performance Comparison\",\n",
            "    yaxis_title=\"Score\",\n",
            "    height=450, width=700,\n",
            "    barmode=\"group\",\n",
            ")\n",
            "fig_comp.show()\n",
            "save_chart(fig_comp, MODEL_SLUG, \"qda_vs_lda_comparison\")"
        ]
    })

    # Cell 14: Decision boundary
    cells.append({
        "cell_type": "markdown",
        "id": "cell-14",
        "metadata": {},
        "source": [
            "---\n",
            "## 8. Decision Boundary Visualization (QDA vs LDA)"
        ]
    })

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-15",
        "metadata": {},
        "outputs": [],
        "source": [
            "pca_2d = PCA(n_components=2, random_state=42)\n",
            "X_train_2d = pca_2d.fit_transform(X_train_t)\n",
            "X_test_2d = pca_2d.transform(X_test_t)\n",
            "\n",
            "# Train QDA and LDA on 2D data\n",
            "qda_2d = QuadraticDiscriminantAnalysis(reg_param=best_reg_param)\n",
            "qda_2d.fit(X_train_2d, y_train)\n",
            "\n",
            "lda_2d = LinearDiscriminantAnalysis(shrinkage=\"auto\", solver=\"lsqr\")\n",
            "lda_2d.fit(X_train_2d, y_train)\n",
            "\n",
            "# Create mesh\n",
            "h = 0.1\n",
            "x_min, x_max = X_test_2d[:, 0].min() - 1, X_test_2d[:, 0].max() + 1\n",
            "y_min, y_max = X_test_2d[:, 1].min() - 1, X_test_2d[:, 1].max() + 1\n",
            "xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))\n",
            "\n",
            "Z_qda = qda_2d.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1].reshape(xx.shape)\n",
            "Z_lda = lda_2d.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1].reshape(xx.shape)\n",
            "\n",
            "from plotly.subplots import make_subplots\n",
            "\n",
            "fig_db = make_subplots(\n",
            "    rows=1, cols=2,\n",
            "    subplot_titles=(\"QDA Decision Boundary (Quadratic)\", \"LDA Decision Boundary (Linear)\"),\n",
            ")\n",
            "\n",
            "for col, Z, title in [(1, Z_qda, \"qda\"), (2, Z_lda, \"lda\")]:\n",
            "    fig_db.add_trace(go.Contour(\n",
            "        x=np.arange(x_min, x_max, h), y=np.arange(y_min, y_max, h), z=Z,\n",
            "        colorscale=[[0, COLORS[\"ice\"]], [0.5, COLORS[\"white\"]], [1, \"#ffcccc\"]],\n",
            "        contours=dict(start=0, end=1, size=0.1),\n",
            "        showscale=(col == 2), colorbar=dict(title=\"P(Default)\"),\n",
            "        opacity=0.7,\n",
            "    ), row=1, col=col)\n",
            "\n",
            "# Add points\n",
            "for label, color, name in [(0, COLORS[\"accent\"], \"Good Loan\"), (1, COLORS[\"red\"], \"Default\")]:\n",
            "    mask = y_test == label\n",
            "    fig_db.add_trace(go.Scatter(\n",
            "        x=X_test_2d[mask, 0], y=X_test_2d[mask, 1],\n",
            "        mode=\"markers\", name=name,\n",
            "        marker=dict(color=color, size=4, opacity=0.6),\n",
            "        showlegend=(col == 1),\n",
            "    ), row=1, col=1 if label == 0 else 2)\n",
            "    fig_db.add_trace(go.Scatter(\n",
            "        x=X_test_2d[mask, 0], y=X_test_2d[mask, 1],\n",
            "        mode=\"markers\", name=name,\n",
            "        marker=dict(color=color, size=4, opacity=0.6),\n",
            "        showlegend=False,\n",
            "    ), row=1, col=2)\n",
            "\n",
            "fig_db.update_layout(\n",
            "    title=\"QDA vs LDA: Decision Boundary Comparison (2D PCA Projection)\",\n",
            "    height=550, width=1000,\n",
            ")\n",
            "fig_db.show()\n",
            "save_chart(fig_db, MODEL_SLUG, \"decision_boundary_qda_vs_lda\")"
        ]
    })

    # Cell 16: Covariance ellipses
    cells.append({
        "cell_type": "markdown",
        "id": "cell-16",
        "metadata": {},
        "source": [
            "---\n",
            "## 9. Covariance Ellipses (Class-Specific Shapes)"
        ]
    })

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-17",
        "metadata": {},
        "outputs": [],
        "source": [
            "from matplotlib.patches import Ellipse\n",
            "import matplotlib.patches as mpatches\n",
            "\n",
            "def plot_covariance_ellipse(fig, mu, cov, color, name, n_std=2.0):\n",
            "    \"\"\"Add a covariance ellipse to a plotly figure.\"\"\"\n",
            "    eigenvalues, eigenvectors = np.linalg.eig(cov)\n",
            "    order = eigenvalues.argsort()[::-1]\n",
            "    eigenvalues = eigenvalues[order]\n",
            "    eigenvectors = eigenvectors[:, order]\n",
            "    \n",
            "    angle = np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0]))\n",
            "    width, height = 2 * n_std * np.sqrt(eigenvalues)\n",
            "    \n",
            "    # Create ellipse path\n",
            "    theta = np.linspace(0, 2*np.pi, 100)\n",
            "    ellipse_x = width/2 * np.cos(theta)\n",
            "    ellipse_y = height/2 * np.sin(theta)\n",
            "    \n",
            "    # Rotate\n",
            "    angle_rad = np.radians(angle)\n",
            "    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)\n",
            "    x_rot = cos_a * ellipse_x - sin_a * ellipse_y + mu[0]\n",
            "    y_rot = sin_a * ellipse_x + cos_a * ellipse_y + mu[1]\n",
            "    \n",
            "    fig.add_trace(go.Scatter(\n",
            "        x=x_rot, y=y_rot, mode=\"lines\", name=name,\n",
            "        line=dict(color=color, width=2),\n",
            "        fill=\"toself\", fillcolor=color, opacity=0.2,\n",
            "    ))\n",
            "\n",
            "fig_ellipse = go.Figure()\n",
            "\n",
            "# Plot training data\n",
            "for label, color, name in [(0, COLORS[\"accent\"], \"Good Loan\"), (1, COLORS[\"red\"], \"Default\")]:\n",
            "    mask = y_train == label\n",
            "    fig_ellipse.add_trace(go.Scatter(\n",
            "        x=X_train_2d[mask, 0], y=X_train_2d[mask, 1],\n",
            "        mode=\"markers\", name=name,\n",
            "        marker=dict(color=color, size=3, opacity=0.5),\n",
            "    ))\n",
            "\n",
            "# Get QDA means and covariances in 2D space\n",
            "qda_2d_fitted = QuadraticDiscriminantAnalysis(reg_param=best_reg_param)\n",
            "qda_2d_fitted.fit(X_train_2d, y_train)\n",
            "\n",
            "for c, color, name in [(0, COLORS[\"accent\"], \"Good (Σ₀)\"), (1, COLORS[\"red\"], \"Default (Σ₁)\")]:\n",
            "    mu = qda_2d_fitted.means_[c]\n",
            "    cov = qda_2d_fitted.covariance_[c]\n",
            "    plot_covariance_ellipse(fig_ellipse, mu, cov, color, f\"{name} (2σ ellipse)\", n_std=2)\n",
            "\n",
            "fig_ellipse.update_layout(\n",
            "    title=\"QDA: Class-Specific Covariance Ellipses (2D PCA Space, 2σ contours)\",\n",
            "    xaxis_title=f\"PC1 ({pca_2d.explained_variance_ratio_[0]:.1%})\",\n",
            "    yaxis_title=f\"PC2 ({pca_2d.explained_variance_ratio_[1]:.1%})\",\n",
            "    height=600, width=750,\n",
            ")\n",
            "fig_ellipse.show()\n",
            "save_chart(fig_ellipse, MODEL_SLUG, \"covariance_ellipses_2d\")"
        ]
    })

    # Cell 18: Diagnostic charts
    cells.append({
        "cell_type": "markdown",
        "id": "cell-18",
        "metadata": {},
        "source": [
            "---\n",
            "## 10. Diagnostic Charts"
        ]
    })

    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-19",
        "metadata": {},
        "outputs": [],
        "source": [
            "charts = save_all_universal_charts(y_test, y_pred, y_score, MODEL_NAME, MODEL_SLUG)\n",
            "for name, fig in charts.items():\n",
            "    fig.show()"
        ]
    })

    # Cell 20: Summary
    cells.append({
        "cell_type": "markdown",
        "id": "cell-20",
        "metadata": {},
        "source": [
            "---\n",
            "## 11. Summary\n",
            "\n",
            "### Where QDA Sits on the Tradeoff Spectrum\n",
            "\n",
            "QDA is the **flexible discriminant** that relaxes LDA's homogeneity of variance assumption. By allowing each class to have its own covariance matrix, QDA can capture scenarios where defaulters and non-defaulters have fundamentally different feature relationships (e.g., defaults show higher variance in debt-to-income ratio).\n",
            "\n",
            "On the recall-precision spectrum, QDA typically performs between LDA and fully nonlinear models. It often achieves higher recall than LDA (catching more defaults) because the class-specific boundaries can better isolate high-risk segments.\n",
            "\n",
            "### Strengths for This Problem\n",
            "- Captures class-specific covariance structures (more flexible than LDA)\n",
            "- Creates nonlinear decision boundaries (quadratic rather than linear)\n",
            "- Still probabilistically grounded in Bayes' theorem\n",
            "- Relatively few hyperparameters (just regularization)\n",
            "- Produces well-calibrated probabilities when Gaussian assumption holds\n",
            "\n",
            "### Limitations for This Problem\n",
            "- Assumes multivariate Gaussian distribution (often violated for count/zero-inflated features)\n",
            "- Requires more parameters per class (potentially unstable with small n_c)\n",
            "- Can overfit when sample size is small relative to number of features\n",
            "- Less interpretable than LDA (no single discriminant rule per feature)\n",
            "- May be outperformed by flexible nonparametric methods in high dimensions\n",
            "\n",
            "### Key Comparison: QDA vs LDA\n",
            "\n",
            "| Aspect | LDA | QDA |\n",
            "|--------|-----|-----|\n",
            "| **Covariance** | Shared across classes | Separate per class |\n",
            "| **Decision Boundary** | Linear | Quadratic |\n",
            "| **Flexibility** | Lower | Higher |\n",
            "| **Parameters** | O(p²) total | O(p² × K) (K = num classes) |\n",
            "| **Bias** | Higher | Lower |\n",
            "| **Variance** | Lower | Higher |\n",
            "| **Sample Requirements** | Fewer | More |\n",
            "\n",
            "### Key Takeaway\n",
            "QDA is the **middle ground between LDA and fully nonlinear models**. It provides a principled extension of LDA that can capture heteroscedastic data (different variances per class) while remaining interpretable and efficient. If LDA underfits and tree-based models seem like overkill, QDA is worth exploring."
        ]
    })

    # Cell 21: Footer
    cells.append({
        "cell_type": "markdown",
        "id": "cell-21",
        "metadata": {},
        "source": [
            "---\n",
            "*Notebook by Trinidad Cisneros — MIT Applied Data Science Program, April 2026*"
        ]
    })

    return cells


def main():
    """Build and save the notebook."""
    notebook_path = Path("/sessions/friendly-focused-carson/mnt/bitterscientist.com/folders/ds_blogs/projects/loanDefaultPrediction/notebooks/models/03_qda.ipynb")

    cells = build_notebook()

    # Validate all code cells
    for cell in cells:
        if cell["cell_type"] == "code":
            source_str = "".join(cell["source"])
            try:
                ast.parse(source_str)
            except SyntaxError as e:
                print(f"SYNTAX ERROR in cell {cell.get('id', 'unknown')}: {e}")
                return False

    # Create notebook structure
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    # Write notebook
    notebook_path.parent.mkdir(parents=True, exist_ok=True)
    with open(notebook_path, "w") as f:
        json.dump(notebook, f, indent=1)

    print(f"✓ Built notebook: {notebook_path}")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
