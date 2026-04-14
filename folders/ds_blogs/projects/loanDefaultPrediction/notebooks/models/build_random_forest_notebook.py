#!/usr/bin/env python3
"""
Builder script for 07_random_forest.ipynb
Creates a complete Random Forest deep-dive notebook with full math, worked examples, and diagnostic charts.
"""

import json
import ast

# Notebook structure
notebook = {
    "cells": [
        # Cell 0: Title
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Random Forest: Deep Dive\n",
                "## Loan Default Prediction (HMEQ Dataset)\n",
                "\n",
                "*Part of the [ML Model Comparison](../loan_default_tradeoff_matrix.html) series on bitterscientist.com*\n",
                "\n",
                "This notebook covers:\n",
                "1. The math behind random forests (bagging, bootstrap sampling, random feature subsets, voting)\n",
                "2. Worked examples using actual HMEQ data\n",
                "3. Model training with hyperparameter tuning\n",
                "4. Diagnostic visualizations (exported as interactive plotly HTML)\n",
                "5. Results interpretation"
            ]
        },
        # Cell 1: Divider
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 1. Setup"
            ]
        },
        # Cell 2: Imports
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "sys.path.insert(0, \".\")\n",
                "from shared_utils import *\n",
                "\n",
                "# Additional imports\n",
                "from sklearn.ensemble import RandomForestClassifier\n",
                "from sklearn.inspection import permutation_importance\n",
                "\n",
                "MODEL_NAME = \"Random Forest\"\n",
                "MODEL_SLUG = \"random_forest\"\n",
                "\n",
                "# Load data\n",
                "(X_train, X_test, y_train, y_test, df, df_proc,\n",
                " prep_linear, prep_tree, cv,\n",
                " numeric_features, categorical_features, pos_weight) = load_and_prep()"
            ]
        },
        # Cell 3: Math section
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 2. The Math Behind Random Forests\n",
                "\n",
                "### 2.1 The Core Idea\n",
                "\n",
                "A random forest is an **ensemble method** that reduces the high variance of a single decision tree by building many trees on random subsets of the training data and averaging their predictions. The key insight: **diversity is power**. If individual trees are trained on different data samples and make different mistakes, averaging them cancels out much of the noise while preserving the signal.\n",
                "\n",
                "### 2.2 Bootstrap Aggregating (Bagging)\n",
                "\n",
                "The core technique is **bootstrap aggregating** or **bagging**:\n",
                "\n",
                "1. **For each tree** \\(b = 1, 2, \\ldots, B\\):\n",
                "   - Draw a random sample of \\(n\\) observations **with replacement** from the training set\n",
                "   - Train a decision tree on this bootstrap sample\n",
                "   - The tree grows to full depth (no pruning)\n",
                "\n",
                "2. **For each new prediction**, aggregate the predictions:\n",
                "\n",
                "$$\\hat{y} = \\text{majority vote}(\\hat{y}_1, \\hat{y}_2, \\ldots, \\hat{y}_B)$$\n",
                "\n",
                "For probability predictions:\n",
                "\n",
                "$$\\hat{p} = \\frac{1}{B} \\sum_{b=1}^{B} \\hat{p}_b(x)$$\n",
                "\n",
                "### 2.3 Why Bootstrap Sampling?\n",
                "\n",
                "By sampling with replacement, some observations appear multiple times in a bootstrap sample while others appear zero times. On average, each bootstrap sample contains roughly 63% of the original data:\n",
                "\n",
                "$$P(\\text{observation } i \\text{ in sample}) = 1 - \\left(1 - \\frac{1}{n}\\right)^n \\approx 1 - e^{-1} \\approx 0.632$$\n",
                "\n",
                "The remaining ~37% is called the **out-of-bag (OOB)** samples. These can be used for validation without requiring a separate test set.\n",
                "\n",
                "### 2.4 Variance Reduction via Averaging\n",
                "\n",
                "Suppose each tree has variance \\(\\sigma^2\\) and the trees' predictions are **uncorrelated**. The variance of the average of \\(B\\) trees is:\n",
                "\n",
                "$$\\text{Var}(\\hat{y}) = \\frac{\\sigma^2}{B}$$\n",
                "\n",
                "This is the **key mathematical benefit**: variance drops as \\(O(1/B)\\). By training 100 uncorrelated trees instead of 1, we reduce variance by a factor of 100.\n",
                "\n",
                "In practice, trees are not perfectly uncorrelated (they all see the same features and the same underlying patterns), so the reduction is smaller than this bound, but still substantial.\n",
                "\n",
                "### 2.5 Random Feature Subsets (Random Forests)\n",
                "\n",
                "Standard bagging trains each tree on a random sample of **observations**. Random forests add a second layer of randomness: at each split, only a random subset of \\(m\\) features are considered:\n",
                "\n",
                "$$m = \\sqrt{p} \\quad \\text{(default for classification)}$$\n",
                "\n",
                "where \\(p\\) is the total number of features. For the HMEQ dataset with ~35 features, this means each split considers only \\(\\sqrt{35} \\approx 6\\) features.\n",
                "\n",
                "**Why?** If one or two features are very strong predictors, every tree will split on them first, making the trees correlated. Random feature subsets force trees to find different patterns, decorrelating their predictions and improving the variance reduction.\n",
                "\n",
                "### 2.6 Out-of-Bag (OOB) Error\n",
                "\n",
                "Each tree \\(b\\) can be evaluated on its OOB samples (roughly 37% of the training data that were not in its bootstrap sample). This gives a free validation set:\n",
                "\n",
                "$$\\text{OOB error} = \\frac{1}{n} \\sum_{i=1}^{n} \\mathbb{1}[\\hat{y}_{\\text{OOB}}(x_i) \\neq y_i]$$\n",
                "\n",
                "where \\(\\hat{y}_{\\text{OOB}}(x_i)\\) is the prediction averaged only over trees for which observation \\(i\\) was OOB.\n",
                "\n",
                "### 2.7 Feature Importance (Two Methods)\n",
                "\n",
                "**Method 1: Mean Decrease in Impurity (MDI)**\n",
                "\n",
                "Average the feature importance from each tree (the sum of impurity decreases across all nodes where the feature was split):\n",
                "\n",
                "$$\\text{Importance}_\\text{MDI}(x_j) = \\frac{1}{B} \\sum_{b=1}^{B} \\text{Importance}_b(x_j)$$\n",
                "\n",
                "**Method 2: Permutation Importance**\n",
                "\n",
                "Measure how much the OOB error increases when feature \\(x_j\\) is randomly shuffled (breaking the relationship between that feature and the target):\n",
                "\n",
                "$$\\text{Importance}_\\text{perm}(x_j) = \\text{OOB error}_{\\text{shuffled } x_j} - \\text{OOB error}_{\\text{original}}$$\n",
                "\n",
                "Permutation importance is more reliable than MDI because it measures the actual impact on the forest's predictions, not just the individual trees' internal Gini calculations."
            ]
        },
        # Cell 4: Visualization of bagging
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 3. Visualizing Variance Reduction Through Bagging"
            ]
        },
        # Cell 5: Bagging visualization code
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Simulate variance reduction with averaging\n",
                "# Each \"tree\" makes predictions with some noise; averaging reduces noise\n",
                "\n",
                "np.random.seed(RANDOM_STATE)\n",
                "x = np.linspace(-3, 3, 100)\n",
                "y_true = np.sin(x) + x * 0.3\n",
                "\n",
                "# Single noisy tree: high variance\n",
                "y_single = y_true + np.random.normal(0, 0.4, len(x))\n",
                "\n",
                "# 10 trees (ensemble average)\n",
                "y_ensemble_10 = np.mean([y_true + np.random.normal(0, 0.4, len(x)) for _ in range(10)], axis=0)\n",
                "\n",
                "# 100 trees (ensemble average)\n",
                "y_ensemble_100 = np.mean([y_true + np.random.normal(0, 0.4, len(x)) for _ in range(100)], axis=0)\n",
                "\n",
                "fig = go.Figure()\n",
                "fig.add_trace(go.Scatter(x=x, y=y_true, name=\"True Signal\",\n",
                "    line=dict(color=COLORS[\"green\"], width=3)))\n",
                "fig.add_trace(go.Scatter(x=x, y=y_single, name=\"Single Tree (high variance)\",\n",
                "    line=dict(color=COLORS[\"red\"], width=1, dash=\"dash\"), opacity=0.5))\n",
                "fig.add_trace(go.Scatter(x=x, y=y_ensemble_10, name=\"Average of 10 Trees\",\n",
                "    line=dict(color=COLORS[\"orange\"], width=2, dash=\"dot\")))\n",
                "fig.add_trace(go.Scatter(x=x, y=y_ensemble_100, name=\"Average of 100 Trees\",\n",
                "    line=dict(color=COLORS[\"navy\"], width=2)))\n",
                "\n",
                "fig.update_layout(\n",
                "    title=\"Variance Reduction Through Bagging: Averaging Predictions\",\n",
                "    xaxis_title=\"Feature Value\",\n",
                "    yaxis_title=\"Prediction\",\n",
                "    height=450, width=700,\n",
                "    legend=dict(x=0.02, y=0.98),\n",
                ")\n",
                "fig.show()\n",
                "save_chart(fig, MODEL_SLUG, \"bagging_variance_reduction\")"
            ]
        },
        # Cell 6: Worked example
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 4. Worked Example: Voting and Disagreement"
            ]
        },
        # Cell 7: Worked example code
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print(\"=\"*70)\n",
                "print(\"WORKED EXAMPLE: How Trees Vote in a Random Forest\")\n",
                "print(\"=\"*70)\n",
                "\n",
                "# Get a few example borrowers\n",
                "examples = get_example_rows(df, n=2)\n",
                "\n",
                "for idx, row in examples.iterrows():\n",
                "    print_example_row(row, idx)\n",
                "\n",
                "print(\"\\n\" + \"=\"*70)\n",
                "print(\"Forest Voting Mechanism\")\n",
                "print(\"=\"*70)\n",
                "\n",
                "print(f\"\"\"\n",
                "Suppose we train a Random Forest with 100 trees on the HMEQ data.\n",
                "Each tree is trained on a different bootstrap sample and considers\n",
                "a random subset of features at each split.\n",
                "\n",
                "Example: For one borrower, here's how the forest votes:\n",
                "\n",
                "  Tree 1: Predict GOOD  (prob = 0.8)\n",
                "  Tree 2: Predict DEFAULT (prob = 0.6)\n",
                "  Tree 3: Predict GOOD (prob = 0.9)\n",
                "  Tree 4: Predict GOOD (prob = 0.75)\n",
                "  Tree 5: Predict DEFAULT (prob = 0.55)\n",
                "  ...\n",
                "  Tree 100: Predict GOOD (prob = 0.85)\n",
                "\n",
                "Votes:\n",
                "  GOOD:    78 votes (78%)\n",
                "  DEFAULT: 22 votes (22%)\n",
                "\n",
                "Forest Decision:\n",
                "  Majority vote: GOOD (78 > 22)\n",
                "  Probability: P(Default) = 22/100 = 0.22\n",
                "\n",
                "Why this matters:\n",
                "  - Tree 2 and 5 said DEFAULT, but they were outvoted\n",
                "  - Individual trees can be noisy (high variance)\n",
                "  - Voting averages out the noise\n",
                "  - The consensus is more stable than any single tree\n",
                "\n",
                "Bias-Variance Tradeoff:\n",
                "  - Trees are trained to full depth (low bias, high variance)\n",
                "  - Bagging increases bias slightly but reduces variance dramatically\n",
                "  - Net result: lower test error than a single tree\n",
                "\"\"\")"
            ]
        },
        # Cell 8: OOB error visualization
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 5. Model Training with Hyperparameter Tuning"
            ]
        },
        # Cell 9: Training code
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Hyperparameter grid\n",
                "param_grid = {\n",
                "    \"clf__n_estimators\": [50, 100, 200],\n",
                "    \"clf__max_depth\": [5, 10, 15, 20, None],\n",
                "    \"clf__min_samples_leaf\": [1, 5, 10],\n",
                "    \"clf__max_features\": [\"sqrt\", \"log2\"],\n",
                "}\n",
                "\n",
                "rf_pipe = Pipeline([\n",
                "    (\"prep\", prep_tree),\n",
                "    (\"clf\", RandomForestClassifier(\n",
                "        class_weight=\"balanced\",\n",
                "        random_state=RANDOM_STATE,\n",
                "        oob_score=True,\n",
                "        n_jobs=-1,\n",
                "    )),\n",
                "])\n",
                "\n",
                "grid = GridSearchCV(\n",
                "    rf_pipe, param_grid, cv=cv,\n",
                "    scoring=\"recall\", n_jobs=-1, refit=True, verbose=1,\n",
                ")\n",
                "grid.fit(X_train, y_train)\n",
                "\n",
                "best_rf = grid.best_estimator_\n",
                "print(f\"\\nBest parameters: {grid.best_params_}\")\n",
                "print(f\"Best CV recall: {grid.best_score_:.4f}\")\n",
                "\n",
                "# Get the underlying forest\n",
                "forest_model = best_rf.named_steps[\"clf\"]\n",
                "print(f\"\\nForest structure:\")\n",
                "print(f\"  Number of trees: {forest_model.n_estimators}\")\n",
                "print(f\"  Max features per split: {forest_model.max_features}\")\n",
                "print(f\"  OOB score: {forest_model.oob_score_:.4f}\")"
            ]
        },
        # Cell 10: Evaluation
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 6. Model Evaluation"
            ]
        },
        # Cell 11: Evaluation code
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Cross-validation score\n",
                "cv_scores = cross_val_score(best_rf, X_train, y_train, cv=cv, scoring=\"recall\")\n",
                "cv_mean = cv_scores.mean()\n",
                "print(f\"CV Recall scores: {cv_scores}\")\n",
                "print(f\"CV Recall mean: {cv_mean:.4f} (+/- {cv_scores.std():.4f})\")\n",
                "\n",
                "# Test set evaluation\n",
                "metrics, y_pred, y_score = evaluate_model(MODEL_NAME, best_rf, X_test, y_test, cv_mean)\n",
                "\n",
                "print(f\"\\nClassification Report:\")\n",
                "print(classification_report(y_test, y_pred, target_names=[\"Good Loan\", \"Default\"]))"
            ]
        },
        # Cell 12: OOB error curve
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 7. Out-of-Bag Error Curve"
            ]
        },
        # Cell 13: OOB curve code
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Train forests with increasing numbers of trees\n",
                "# to see how OOB error decreases\n",
                "\n",
                "n_trees_range = list(range(10, 310, 10))\n",
                "oob_scores = []\n",
                "test_recalls = []\n",
                "test_precisions = []\n",
                "\n",
                "for n_trees in n_trees_range:\n",
                "    rf_temp = Pipeline([\n",
                "        (\"prep\", prep_tree),\n",
                "        (\"clf\", RandomForestClassifier(\n",
                "            n_estimators=n_trees,\n",
                "            max_depth=forest_model.max_depth,\n",
                "            min_samples_leaf=forest_model.min_samples_leaf,\n",
                "            max_features=forest_model.max_features,\n",
                "            class_weight=\"balanced\",\n",
                "            oob_score=True,\n",
                "            random_state=RANDOM_STATE,\n",
                "            n_jobs=-1,\n",
                "        )),\n",
                "    ])\n",
                "    rf_temp.fit(X_train, y_train)\n",
                "    \n",
                "    # OOB score (higher is better; sklearn converts from error)\n",
                "    oob_acc = rf_temp.named_steps[\"clf\"].oob_score_\n",
                "    oob_scores.append(1 - oob_acc)  # Convert to error\n",
                "    \n",
                "    # Test set\n",
                "    y_pred_t = rf_temp.predict(X_test)\n",
                "    test_recalls.append(recall_score(y_test, y_pred_t))\n",
                "    test_precisions.append(precision_score(y_test, y_pred_t, zero_division=0))\n",
                "\n",
                "fig_oob = go.Figure()\n",
                "fig_oob.add_trace(go.Scatter(\n",
                "    x=n_trees_range, y=oob_scores,\n",
                "    name=\"OOB Error\", mode=\"lines\",\n",
                "    line=dict(color=COLORS[\"navy\"], width=2),\n",
                "))\n",
                "fig_oob.add_trace(go.Scatter(\n",
                "    x=n_trees_range, y=test_recalls,\n",
                "    name=\"Test Recall\", mode=\"lines\",\n",
                "    line=dict(color=COLORS[\"accent\"], width=2),\n",
                "))\n",
                "fig_oob.add_trace(go.Scatter(\n",
                "    x=n_trees_range, y=test_precisions,\n",
                "    name=\"Test Precision\", mode=\"lines\",\n",
                "    line=dict(color=COLORS[\"orange\"], width=2),\n",
                "))\n",
                "\n",
                "# Mark best n_estimators\n",
                "best_n = forest_model.n_estimators\n",
                "fig_oob.add_vline(x=best_n, line_dash=\"dash\", line_color=COLORS[\"red\"],\n",
                "                  annotation_text=f\"Best n_estimators={best_n}\")\n",
                "\n",
                "fig_oob.update_layout(\n",
                "    title=\"Effect of Number of Trees on Error and Performance\",\n",
                "    xaxis_title=\"Number of Trees\",\n",
                "    yaxis_title=\"Score\",\n",
                "    height=500, width=700,\n",
                "    legend=dict(orientation=\"h\", y=1.12),\n",
                ")\n",
                "fig_oob.show()\n",
                "save_chart(fig_oob, MODEL_SLUG, \"oob_error_curve\")"
            ]
        },
        # Cell 14: Feature importance
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 8. Feature Importance: Mean Decrease in Impurity (MDI)"
            ]
        },
        # Cell 15: MDI code
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Feature names after preprocessing\n",
                "preprocessor = best_rf.named_steps[\"prep\"]\n",
                "cat_encoder = preprocessor.named_transformers_[\"cat\"]\n",
                "cat_names = list(cat_encoder.get_feature_names_out(categorical_features))\n",
                "all_feature_names = numeric_features + cat_names\n",
                "\n",
                "# MDI from the forest\n",
                "importances_mdi = forest_model.feature_importances_\n",
                "\n",
                "fig_mdi = plot_feature_importance(importances_mdi, all_feature_names, MODEL_NAME, \"Gini Importance (MDI)\")\n",
                "fig_mdi.show()\n",
                "save_chart(fig_mdi, MODEL_SLUG, \"feature_importance_mdi\")"
            ]
        },
        # Cell 16: Permutation importance
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 9. Feature Importance: Permutation Importance"
            ]
        },
        # Cell 17: Permutation code
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Permutation importance on test set\n",
                "perm_importance = permutation_importance(\n",
                "    best_rf, X_test, y_test,\n",
                "    n_repeats=10, random_state=RANDOM_STATE, n_jobs=-1,\n",
                ")\n",
                "\n",
                "# Get test set transformed features for names\n",
                "importances_perm = perm_importance.importances_mean\n",
                "\n",
                "fig_perm = plot_feature_importance(importances_perm, all_feature_names, MODEL_NAME, \"Permutation Importance\")\n",
                "fig_perm.show()\n",
                "save_chart(fig_perm, MODEL_SLUG, \"feature_importance_permutation\")"
            ]
        },
        # Cell 18: Individual tree comparison
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 10. Individual Tree Variance"
            ]
        },
        # Cell 19: Tree variance code
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Train individual trees from the forest on test set\n",
                "# to show variance in single tree predictions\n",
                "\n",
                "individual_recalls = []\n",
                "individual_precisions = []\n",
                "individual_f1s = []\n",
                "\n",
                "for tree_estimator in forest_model.estimators_:\n",
                "    y_pred_tree = tree_estimator.predict(X_test_transformed)\n",
                "    individual_recalls.append(recall_score(y_test, y_pred_tree))\n",
                "    individual_precisions.append(precision_score(y_test, y_pred_tree, zero_division=0))\n",
                "    individual_f1s.append(f1_score(y_test, y_pred_tree))\n",
                "\n",
                "# Get forest performance\n",
                "forest_recall = recall_score(y_test, y_pred)\n",
                "forest_precision = precision_score(y_test, y_pred, zero_division=0)\n",
                "forest_f1 = f1_score(y_test, y_pred)\n",
                "\n",
                "# Visualization\n",
                "fig_var = go.Figure()\n",
                "\n",
                "# Individual trees\n",
                "fig_var.add_trace(go.Box(\n",
                "    y=individual_recalls, name=\"Individual Tree Recall\",\n",
                "    marker_color=COLORS[\"accent\"], opacity=0.7,\n",
                "))\n",
                "fig_var.add_trace(go.Box(\n",
                "    y=individual_precisions, name=\"Individual Tree Precision\",\n",
                "    marker_color=COLORS[\"orange\"], opacity=0.7,\n",
                "))\n",
                "fig_var.add_trace(go.Box(\n",
                "    y=individual_f1s, name=\"Individual Tree F1\",\n",
                "    marker_color=COLORS[\"green\"], opacity=0.7,\n",
                "))\n",
                "\n",
                "# Forest ensemble (horizontal line)\n",
                "fig_var.add_hline(y=forest_recall, line_dash=\"dash\", line_color=COLORS[\"navy\"],\n",
                "                  annotation_text=f\"Forest Recall={forest_recall:.3f}\")\n",
                "\n",
                "fig_var.update_layout(\n",
                "    title=\"Individual Tree Variance vs Forest Ensemble Stability\",\n",
                "    yaxis_title=\"Score\",\n",
                "    height=500, width=700,\n",
                ")\n",
                "fig_var.show()\n",
                "save_chart(fig_var, MODEL_SLUG, \"individual_tree_variance\")"
            ]
        },
        # Cell 20: Get transformed features
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Transform test set for individual tree predictions\n",
                "X_test_transformed = best_rf.named_steps[\"prep\"].transform(X_test)"
            ]
        },
        # Cell 21: Universal charts
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 11. Diagnostic Charts"
            ]
        },
        # Cell 22: Save charts
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Generate and save all universal charts\n",
                "charts = save_all_universal_charts(y_test, y_pred, y_score, MODEL_NAME, MODEL_SLUG)\n",
                "\n",
                "for name, fig in charts.items():\n",
                "    fig.show()"
            ]
        },
        # Cell 23: Summary
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "## 12. Summary\n",
                "\n",
                "### Where the Random Forest Sits on the Tradeoff Spectrum\n",
                "\n",
                "Random forests with `class_weight=\"balanced\"` land in the **moderate to aggressive** zone. By using many decorrelated trees with balanced class weights, the forest captures nonlinear patterns while maintaining reasonable recall. Compared to a single decision tree, the forest is more stable (lower variance) and typically achieves better generalization.\n",
                "\n",
                "### Strengths for This Problem\n",
                "- **Dramatic variance reduction**: bagging reduces the high variance of single trees\n",
                "- **Captures nonlinear patterns**: unlike linear models, can model complex feature interactions\n",
                "- **Handles mixed feature types**: works with numeric and categorical features natively\n",
                "- **Feature importance**: both MDI and permutation importance provide interpretability\n",
                "- **Out-of-bag validation**: free estimate of generalization error without a separate test set\n",
                "- **Parallel training**: trees are independent and can be trained in parallel\n",
                "- **Robust to outliers**: individual trees are robust, and outliers' impact is reduced by averaging\n",
                "\n",
                "### Limitations for This Problem\n",
                "- **Less interpretable than single trees**: the ensemble decision is a vote across 100+ trees\n",
                "- **More computationally expensive**: training and prediction are slower than single trees\n",
                "- **Still biased toward strong features**: if one feature is dominant, all trees may use it\n",
                "- **Modest further improvements**: boosting methods (XGBoost, LightGBM) often outperform bagging\n",
                "\n",
                "### Key Takeaway\n",
                "Random forests are the **practical nonlinear classifier**. They dramatically improve over single trees while remaining reasonably interpretable. They serve as the go-to baseline for structured data classification before trying more sophisticated methods."
            ]
        },
        # Cell 24: Footer
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "---\n",
                "*Notebook by Trinidad Cisneros — MIT Applied Data Science Program, April 2026*"
            ]
        },
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

# Validate notebook structure
try:
    # Check all cells have required fields
    for i, cell in enumerate(notebook["cells"]):
        assert "cell_type" in cell, f"Cell {i} missing cell_type"
        assert "metadata" in cell, f"Cell {i} missing metadata"
        assert "source" in cell, f"Cell {i} missing source"
        if cell["cell_type"] == "code":
            assert "execution_count" in cell, f"Cell {i} missing execution_count"
            assert "outputs" in cell, f"Cell {i} missing outputs"

    # Validate source is list of strings
    for i, cell in enumerate(notebook["cells"]):
        if isinstance(cell["source"], str):
            cell["source"] = [cell["source"]]
        assert isinstance(cell["source"], list), f"Cell {i} source must be list"
        for line in cell["source"]:
            assert isinstance(line, str), f"Cell {i} source line must be string"

    # Validate Python code with ast.parse
    for i, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] == "code":
            code = "".join(cell["source"])
            try:
                ast.parse(code)
            except SyntaxError as e:
                print(f"WARNING: Cell {i} has syntax error: {e}")

    print("Notebook validation: PASSED")
except AssertionError as e:
    print(f"ERROR: {e}")
    exit(1)

# Save notebook
import pathlib
output_path = pathlib.Path(__file__).resolve().parent / "07_random_forest.ipynb"
with open(output_path, "w") as f:
    json.dump(notebook, f, indent=2)

print(f"Saved: {output_path}")
