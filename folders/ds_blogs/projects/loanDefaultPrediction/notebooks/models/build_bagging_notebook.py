#!/usr/bin/env python3
"""
Build the Bagging Classifier notebook for HMEQ loan default prediction.
Generates 08_bagging.ipynb with full math, worked examples, diagnostic charts.
"""

import json

# Notebook cells as dicts
cells = [
    # Cell 0: Title
    {
        "cell_type": "markdown",
        "id": "cell-0",
        "metadata": {},
        "source": [
            "# Bagging Classifier: Deep Dive\n",
            "## Loan Default Prediction (HMEQ Dataset)\n",
            "\n",
            "*Part of the [ML Model Comparison](../loan_default_tradeoff_matrix.html) series on bitterscientist.com*\n",
            "\n",
            "This notebook covers:\n",
            "1. Bootstrap aggregating: the intuition and the math\n",
            "2. Variance reduction via averaging and bias-variance decomposition\n",
            "3. Out-of-bag (OOB) error estimation\n",
            "4. Comparison with Random Forest (all features vs random subset per split)\n",
            "5. Worked examples using actual HMEQ data\n",
            "6. Model training with hyperparameter tuning\n",
            "7. Diagnostic visualizations (OOB error, feature importance, individual tree variance)\n",
            "8. Results interpretation"
        ]
    },

    # Cell 1: Separator
    {
        "cell_type": "markdown",
        "id": "cell-1",
        "metadata": {},
        "source": ["---\n", "## 1. Setup"]
    },

    # Cell 2: Setup code
    {
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
            "from sklearn.ensemble import BaggingClassifier\n",
            "from sklearn.tree import DecisionTreeClassifier\n",
            "\n",
            "MODEL_NAME = \"Bagging Classifier\"\n",
            "MODEL_SLUG = \"bagging\"\n",
            "\n",
            "# Load data\n",
            "(X_train, X_test, y_train, y_test, df, df_proc,\n",
            " prep_linear, prep_tree, cv,\n",
            " numeric_features, categorical_features, pos_weight) = load_and_prep()"
        ]
    },

    # Cell 3: Math section header
    {
        "cell_type": "markdown",
        "id": "cell-3",
        "metadata": {},
        "source": [
            "---\n",
            "## 2. The Math Behind Bagging (Bootstrap Aggregating)\n",
            "\n",
            "### 2.1 The Core Idea\n",
            "\n",
            "**Bagging** (Bootstrap Aggregating) is an ensemble method that reduces variance by training multiple estimators on random samples of the training data and averaging their predictions.\n",
            "\n",
            "The key insight: if we had access to multiple independent samples from the population, we could train a separate model on each and average their predictions. This averaging would reduce variance without increasing bias, provided the samples are truly independent. In practice, we only have one dataset, so bagging approximates this by drawing multiple samples **with replacement** (bootstrap samples) from the original training data.\n",
            "\n",
            "### 2.2 The Bootstrap Sampling Process\n",
            "\n",
            "Given training data $\\{(x_1, y_1), \\ldots, (x_n, y_n)\\}$, bootstrap sampling works as follows:\n",
            "\n",
            "1. For the $m$-th bootstrap replicate (where $m = 1, 2, \\ldots, M$):\n",
            "   - **Draw $n$ samples with replacement** from the original training set\n",
            "   - This creates a dataset $D^{(m)}$ of size $n$ (same as original, but with duplicates and omissions)\n",
            "   - **Train an estimator** $\\hat{f}^{(m)}$ on $D^{(m)}$\n",
            "\n",
            "2. **Aggregate predictions**:\n",
            "   - For regression: $\\hat{f}_{\\text{bagging}}(x) = \\frac{1}{M} \\sum_{m=1}^{M} \\hat{f}^{(m)}(x)$\n",
            "   - For classification: $\\hat{f}_{\\text{bagging}}(x) = \\text{argmax}_k \\frac{1}{M} \\sum_{m=1}^{M} \\mathbb{1}[\\hat{f}^{(m)}(x) = k]$ (majority vote)\n",
            "   - For probability: $\\hat{p}_k(x) = \\frac{1}{M} \\sum_{m=1}^{M} P(\\hat{f}^{(m)}(x) = k)$ (average probabilities)\n",
            "\n",
            "### 2.3 Why Averaging Reduces Variance\n",
            "\n",
            "Suppose we have $M$ independent estimators with variance $\\sigma^2$. If the estimators are independent, the variance of their average is:\n",
            "\n",
            "$$\\text{Var}\\left[\\frac{1}{M} \\sum_{m=1}^{M} \\hat{f}^{(m)}\\right] = \\frac{1}{M^2} \\sum_{m=1}^{M} \\text{Var}[\\hat{f}^{(m)}] = \\frac{1}{M^2} \\cdot M \\sigma^2 = \\frac{\\sigma^2}{M}$$\n",
            "\n",
            "The variance is **reduced by a factor of $M$** (the number of estimators). This is the fundamental appeal of bagging.\n",
            "\n",
            "In practice, bootstrap samples are not independent (they all come from the same data), so the variance reduction is less than the theoretical maximum. A rule of thumb: bagging reduces variance by a factor of approximately $\\sqrt{M}$ to $M$, depending on the base estimator and data.\n",
            "\n",
            "### 2.4 Bias-Variance Decomposition for Ensembles\n",
            "\n",
            "The mean squared error can be decomposed as:\n",
            "\n",
            "$$\\text{MSE}[\\hat{f}] = \\text{Bias}[\\hat{f}]^2 + \\text{Var}[\\hat{f}] + \\sigma_\\epsilon^2$$\n",
            "\n",
            "where $\\sigma_\\epsilon^2$ is the irreducible error.\n",
            "\n",
            "For bagging:\n",
            "- **Bias:** Approximately unchanged (or slightly decreased). If each $\\hat{f}^{(m)}$ is unbiased, then $\\mathbb{E}[\\hat{f}_{\\text{bagging}}] \\approx \\mathbb{E}[\\hat{f}^{(m)}]$.\n",
            "- **Variance:** Reduced significantly by averaging (as shown above).\n",
            "\n",
            "This makes bagging particularly powerful for **high-variance, low-bias models** like decision trees. It is less effective for models that are already biased (e.g., linear models with insufficient feature engineering).\n",
            "\n",
            "### 2.5 Out-of-Bag (OOB) Error Estimation\n",
            "\n",
            "A clever property of bagging with bootstrap samples: each training sample is left out of approximately $\\left(1 - \\frac{1}{n}\\right)^n \\approx e^{-1} \\approx 0.368$ (36.8%) of the bootstrap samples.\n",
            "\n",
            "We can use these **out-of-bag samples** to estimate test error without a separate validation set:\n",
            "\n",
            "1. For each training sample $i$, identify all bootstrap samples that **did not include** sample $i$\n",
            "2. Average predictions from those estimators (they have never seen sample $i$ during training)\n",
            "3. Compare to the true label $y_i$\n",
            "4. Compute error across all out-of-bag predictions\n",
            "\n",
            "OOB error estimates test error surprisingly well and is **nearly unbiased** (similar to leave-one-out cross-validation but much cheaper computationally).\n",
            "\n",
            "### 2.6 Bagging vs Random Forest\n",
            "\n",
            "| Aspect | Bagging | Random Forest |\n",
            "|--------|---------|---------------|\n",
            "| Base estimator | Any model (usually trees) | Decision trees |\n",
            "| Sampling strategy | Bootstrap all features | Bootstrap samples AND random feature subset per split |\n",
            "| Feature diversity | Low (same features at each node of each tree) | High (each split considers only ~√p features) |\n",
            "| Variance reduction | Moderate (~√M to M) | High (additional randomness in features) |\n",
            "| Bias | Unchanged | Slightly increased |\n",
            "| Interpretability | Per-tree interpretability still exists | Even harder to interpret due to feature randomization |\n",
            "| Use case | Baseline ensemble; works with any base estimator | More powerful; usually preferred for trees |\n",
            "\n",
            "When you use `BaggingClassifier` with `DecisionTreeClassifier` as the base estimator, you get **Bagging**. When you use Random Forest, you get the additional feature randomization that makes it more powerful."
        ]
    },

    # Cell 4: Visualization setup
    {
        "cell_type": "markdown",
        "id": "cell-4",
        "metadata": {},
        "source": ["---\n", "## 3. Visualizing Bootstrap Samples"]
    },

    # Cell 5: Bootstrap visualization
    {
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-5",
        "metadata": {},
        "outputs": [],
        "source": [
            "# Demonstrate bootstrap sampling\n",
            "np.random.seed(RANDOM_STATE)\n",
            "n_samples = len(y_train)\n",
            "n_bootstraps = 100\n",
            "\n",
            "# Track how many times each sample appears in each bootstrap\n",
            "appearance_counts = np.zeros((n_samples, n_bootstraps))\n",
            "oob_counts = np.zeros(n_samples)\n",
            "\n",
            "for b in range(n_bootstraps):\n",
            "    # Draw bootstrap sample\n",
            "    boot_indices = np.random.choice(n_samples, size=n_samples, replace=True)\n",
            "    appearance_counts[boot_indices, b] += 1\n",
            "    \n",
            "    # Count samples NOT in this bootstrap (out-of-bag)\n",
            "    in_bag = np.zeros(n_samples, dtype=bool)\n",
            "    in_bag[boot_indices] = True\n",
            "    oob_counts[~in_bag] += 1\n",
            "\n",
            "# Plot: how many times each sample appears across all bootstraps\n",
            "avg_appearances = appearance_counts.mean(axis=1)\n",
            "avg_oob = oob_counts / n_bootstraps\n",
            "\n",
            "fig = go.Figure()\n",
            "fig.add_trace(go.Histogram(\n",
            "    x=avg_appearances, nbinsx=20,\n",
            "    name=\"Avg appearances per bootstrap\",\n",
            "    marker_color=COLORS[\"navy\"],\n",
            "))\n",
            "fig.add_vline(x=1.0, line_dash=\"dash\", line_color=COLORS[\"red\"],\n",
            "              annotation_text=\"Expected (1.0)\")\n",
            "fig.update_layout(\n",
            "    title=f\"Bootstrap Sample Appearances ({n_bootstraps} replicates)\",\n",
            "    xaxis_title=\"Average appearances per training sample\",\n",
            "    yaxis_title=\"Number of training samples\",\n",
            "    height=450, width=700,\n",
            ")\n",
            "fig.show()\n",
            "save_chart(fig, MODEL_SLUG, \"bootstrap_distribution\")\n",
            "\n",
            "print(f\"Average sample appearances per bootstrap: {avg_appearances.mean():.4f}\")\n",
            "print(f\"Average OOB rate per sample: {avg_oob.mean():.4f} (expected ~0.368)\")"
        ]
    },

    # Cell 6: Worked example
    {
        "cell_type": "markdown",
        "id": "cell-6",
        "metadata": {},
        "source": ["---\n", "## 4. Worked Example: Variance Reduction"]
    },

    # Cell 7: Worked example code
    {
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-7",
        "metadata": {},
        "outputs": [],
        "source": [
            "# Train a single decision tree and a bagging ensemble on HMEQ\n",
            "# Compare their variance across bootstrap samples\n",
            "\n",
            "print(\"=\"*70)\n",
            "print(\"WORKED EXAMPLE: Variance Reduction via Bagging\")\n",
            "print(\"=\"*70)\n",
            "\n",
            "# Single decision tree\n",
            "single_tree = Pipeline([\n",
            "    (\"prep\", prep_tree),\n",
            "    (\"clf\", DecisionTreeClassifier(\n",
            "        max_depth=7, class_weight=\"balanced\",\n",
            "        random_state=RANDOM_STATE,\n",
            "    )),\n",
            "])\n",
            "single_tree.fit(X_train, y_train)\n",
            "y_pred_single = single_tree.predict_proba(X_test)[:, 1]\n",
            "single_recall = recall_score(y_test, (y_pred_single >= 0.5).astype(int))\n",
            "\n",
            "print(f\"\\nSingle Decision Tree (depth=7):\")\n",
            "print(f\"  Test recall: {single_recall:.4f}\")\n",
            "print(f\"  This tree captures a single view of the data.\")\n",
            "print(f\"  Different random samples might produce very different trees.\")\n",
            "\n",
            "# Bagging ensemble\n",
            "bagging = Pipeline([\n",
            "    (\"prep\", prep_tree),\n",
            "    (\"clf\", BaggingClassifier(\n",
            "        estimator=DecisionTreeClassifier(\n",
            "            max_depth=7, class_weight=\"balanced\",\n",
            "        ),\n",
            "        n_estimators=50,\n",
            "        random_state=RANDOM_STATE,\n",
            "    )),\n",
            "])\n",
            "bagging.fit(X_train, y_train)\n",
            "y_pred_bag = bagging.predict_proba(X_test)[:, 1]\n",
            "bag_recall = recall_score(y_test, (y_pred_bag >= 0.5).astype(int))\n",
            "\n",
            "print(f\"\\nBagging Ensemble (50 trees, depth=7):\")\n",
            "print(f\"  Test recall: {bag_recall:.4f}\")\n",
            "print(f\"  By averaging 50 trees trained on different bootstrap samples,\")\n",
            "print(f\"  we reduce variance without sacrificing bias.\")\n",
            "\n",
            "# Variance analysis\n",
            "# For each test sample, look at the range of predictions across the individual trees\n",
            "base_clf = bagging.named_steps[\"clf\"]\n",
            "prep_obj = bagging.named_steps[\"prep\"]\n",
            "X_test_prep = prep_obj.transform(X_test)\n",
            "\n",
            "individual_probs = np.array([\n",
            "    est.predict_proba(X_test_prep)[:, 1] for est in base_clf.estimators_\n",
            "])\n",
            "pred_variance = individual_probs.var(axis=0)\n",
            "pred_mean = individual_probs.mean(axis=0)\n",
            "\n",
            "print(f\"\\nVariance Analysis:\")\n",
            "print(f\"  Average prediction variance across test samples: {pred_variance.mean():.6f}\")\n",
            "print(f\"  Min variance: {pred_variance.min():.6f}\")\n",
            "print(f\"  Max variance: {pred_variance.max():.6f}\")\n",
            "print(f\"\\n  High variance samples are those where individual trees disagree.\")\n",
            "print(f\"  Averaging smooths out these disagreements.\")"
        ]
    },

    # Cell 8: Training header
    {
        "cell_type": "markdown",
        "id": "cell-8",
        "metadata": {},
        "source": ["---\n", "## 5. Model Training with Hyperparameter Tuning"]
    },

    # Cell 9: Training code
    {
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-9",
        "metadata": {},
        "outputs": [],
        "source": [
            "# Hyperparameter grid for bagging\n",
            "param_grid = {\n",
            "    \"clf__n_estimators\": [10, 25, 50, 100, 200],\n",
            "    \"clf__max_samples\": [0.5, 0.75, 1.0],\n",
            "    \"clf__max_features\": [0.5, 0.75, 1.0],\n",
            "    \"clf__estimator__max_depth\": [5, 7, 10],\n",
            "}\n",
            "\n",
            "bagging_pipe = Pipeline([\n",
            "    (\"prep\", prep_tree),\n",
            "    (\"clf\", BaggingClassifier(\n",
            "        estimator=DecisionTreeClassifier(\n",
            "            class_weight=\"balanced\",\n",
            "            random_state=RANDOM_STATE,\n",
            "        ),\n",
            "        random_state=RANDOM_STATE,\n",
            "    )),\n",
            "])\n",
            "\n",
            "grid = GridSearchCV(\n",
            "    bagging_pipe, param_grid, cv=cv,\n",
            "    scoring=\"recall\", n_jobs=-1, refit=True,\n",
            ")\n",
            "grid.fit(X_train, y_train)\n",
            "\n",
            "best_bagging = grid.best_estimator_\n",
            "print(f\"Best parameters: {grid.best_params_}\")\n",
            "print(f\"Best CV recall: {grid.best_score_:.4f}\")\n",
            "\n",
            "# Get ensemble details\n",
            "ensemble = best_bagging.named_steps[\"clf\"]\n",
            "print(f\"\\nEnsemble structure:\")\n",
            "print(f\"  n_estimators: {ensemble.n_estimators}\")\n",
            "print(f\"  max_samples: {ensemble.max_samples}\")\n",
            "print(f\"  max_features: {ensemble.max_features}\")"
        ]
    },

    # Cell 10: Evaluation header
    {
        "cell_type": "markdown",
        "id": "cell-10",
        "metadata": {},
        "source": ["---\n", "## 6. Model Evaluation"]
    },

    # Cell 11: Evaluation code
    {
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-11",
        "metadata": {},
        "outputs": [],
        "source": [
            "# Cross-validation score\n",
            "cv_scores = cross_val_score(best_bagging, X_train, y_train, cv=cv, scoring=\"recall\")\n",
            "cv_mean = cv_scores.mean()\n",
            "print(f\"CV Recall scores: {cv_scores}\")\n",
            "print(f\"CV Recall mean: {cv_mean:.4f} (+/- {cv_scores.std():.4f})\")\n",
            "\n",
            "# Test set evaluation\n",
            "metrics, y_pred, y_score = evaluate_model(MODEL_NAME, best_bagging, X_test, y_test, cv_mean)\n",
            "\n",
            "print(f\"\\nClassification Report:\")\n",
            "print(classification_report(y_test, y_pred, target_names=[\"Good Loan\", \"Default\"]))"
        ]
    },

    # Cell 12: Feature importance header
    {
        "cell_type": "markdown",
        "id": "cell-12",
        "metadata": {},
        "source": ["---\n", "## 7. Feature Importance from Bagging"]
    },

    # Cell 13: Feature importance code
    {
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-13",
        "metadata": {},
        "outputs": [],
        "source": [
            "# Get feature names after preprocessing\n",
            "preprocessor = best_bagging.named_steps[\"prep\"]\n",
            "cat_encoder = preprocessor.named_transformers_[\"cat\"]\n",
            "cat_names = list(cat_encoder.get_feature_names_out(categorical_features))\n",
            "all_feature_names = numeric_features + cat_names\n",
            "\n",
            "# Average feature importance across all trees in the ensemble\n",
            "ensemble = best_bagging.named_steps[\"clf\"]\n",
            "importances = np.zeros(len(all_feature_names))\n",
            "for estimator in ensemble.estimators_:\n",
            "    importances += estimator.feature_importances_\n",
            "importances /= len(ensemble.estimators_)\n",
            "\n",
            "fig_imp = plot_feature_importance(importances, all_feature_names, MODEL_NAME, \"Mean across Ensemble\")\n",
            "fig_imp.show()\n",
            "save_chart(fig_imp, MODEL_SLUG, \"feature_importance\")"
        ]
    },

    # Cell 14: OOB error analysis header
    {
        "cell_type": "markdown",
        "id": "cell-14",
        "metadata": {},
        "source": ["---\n", "## 8. Out-of-Bag (OOB) Error Analysis"]
    },

    # Cell 15: OOB code
    {
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-15",
        "metadata": {},
        "outputs": [],
        "source": [
            "# Create bagging ensemble with OOB_score enabled\n",
            "bag_oob = Pipeline([\n",
            "    (\"prep\", prep_tree),\n",
            "    (\"clf\", BaggingClassifier(\n",
            "        estimator=DecisionTreeClassifier(\n",
            "            max_depth=ensemble.estimators_[0].max_depth,\n",
            "            class_weight=\"balanced\",\n",
            "            random_state=RANDOM_STATE,\n",
            "        ),\n",
            "        n_estimators=ensemble.n_estimators,\n",
            "        max_samples=ensemble.max_samples,\n",
            "        max_features=ensemble.max_features,\n",
            "        oob_score=True,\n",
            "        random_state=RANDOM_STATE,\n",
            "    )),\n",
            "])\n",
            "bag_oob.fit(X_train, y_train)\n",
            "\n",
            "oob_score = bag_oob.named_steps[\"clf\"].oob_score_\n",
            "print(f\"OOB Score (accuracy): {oob_score:.4f}\")\n",
            "print(f\"\\nOOB error is an unbiased estimate of test error.\")\n",
            "print(f\"It uses predictions from estimators that never saw each training sample.\")\n",
            "print(f\"This avoids the need for a separate validation set.\")"
        ]
    },

    # Cell 16: Ensemble diversity header
    {
        "cell_type": "markdown",
        "id": "cell-16",
        "metadata": {},
        "source": ["---\n", "## 9. Ensemble Diversity and Prediction Variance"]
    },

    # Cell 17: Ensemble diversity code
    {
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-17",
        "metadata": {},
        "outputs": [],
        "source": [
            "# Analyze individual tree predictions and their agreement\n",
            "prep_obj = best_bagging.named_steps[\"prep\"]\n",
            "X_test_prep = prep_obj.transform(X_test)\n",
            "ensemble = best_bagging.named_steps[\"clf\"]\n",
            "\n",
            "# Get predictions from each tree\n",
            "individual_probs = np.array([\n",
            "    est.predict_proba(X_test_prep)[:, 1] for est in ensemble.estimators_\n",
            "])\n",
            "\n",
            "# Ensemble prediction is the average\n",
            "ensemble_prob = individual_probs.mean(axis=0)\n",
            "\n",
            "# Variance of predictions\n",
            "pred_variance = individual_probs.var(axis=0)\n",
            "pred_std = individual_probs.std(axis=0)\n",
            "\n",
            "# Plot: relationship between ensemble variance and prediction\n",
            "fig = go.Figure()\n",
            "for label, color, name in [(0, COLORS[\"accent\"], \"Good Loan\"), (1, COLORS[\"red\"], \"Default\")]:\n",
            "    mask = y_test == label\n",
            "    fig.add_trace(go.Scatter(\n",
            "        x=ensemble_prob[mask], y=pred_std[mask],\n",
            "        mode=\"markers\", name=name,\n",
            "        marker=dict(color=color, size=5, opacity=0.6),\n",
            "    ))\n",
            "\n",
            "fig.update_layout(\n",
            "    title=\"Individual Tree Disagreement vs Ensemble Prediction\",\n",
            "    xaxis_title=\"Ensemble probability (average of trees)\",\n",
            "    yaxis_title=\"Standard deviation of individual tree predictions\",\n",
            "    height=450, width=700,\n",
            ")\n",
            "fig.show()\n",
            "save_chart(fig, MODEL_SLUG, \"tree_disagreement\")\n",
            "\n",
            "print(f\"Prediction variance statistics:\")\n",
            "print(f\"  Mean: {pred_variance.mean():.6f}\")\n",
            "print(f\"  Std: {pred_variance.std():.6f}\")\n",
            "print(f\"  Max: {pred_variance.max():.6f}\")\n",
            "print(f\"\\n  High variance = individual trees disagree (more uncertainty)\")\n",
            "print(f\"  Low variance = individual trees agree (more confidence)\")"
        ]
    },

    # Cell 18: n_estimators analysis header
    {
        "cell_type": "markdown",
        "id": "cell-18",
        "metadata": {},
        "source": ["---\n", "## 10. OOB Error by n_estimators"]
    },

    # Cell 19: n_estimators analysis
    {
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-19",
        "metadata": {},
        "outputs": [],
        "source": [
            "# Sweep n_estimators to show variance reduction over ensemble size\n",
            "n_est_values = [5, 10, 20, 50, 75, 100, 150, 200]\n",
            "oob_results = []\n",
            "\n",
            "for n_est in n_est_values:\n",
            "    bag_temp = Pipeline([\n",
            "        (\"prep\", prep_tree),\n",
            "        (\"clf\", BaggingClassifier(\n",
            "            estimator=DecisionTreeClassifier(\n",
            "                max_depth=ensemble.estimators_[0].max_depth,\n",
            "                class_weight=\"balanced\",\n",
            "                random_state=RANDOM_STATE,\n",
            "            ),\n",
            "            n_estimators=n_est,\n",
            "            max_samples=ensemble.max_samples,\n",
            "            max_features=ensemble.max_features,\n",
            "            oob_score=True,\n",
            "            random_state=RANDOM_STATE,\n",
            "        )),\n",
            "    ])\n",
            "    bag_temp.fit(X_train, y_train)\n",
            "    oob_score = bag_temp.named_steps[\"clf\"].oob_score_\n",
            "    \n",
            "    # Test score for comparison\n",
            "    y_pred_temp = bag_temp.predict(X_test)\n",
            "    test_score = accuracy_score(y_test, y_pred_temp)\n",
            "    \n",
            "    oob_results.append({\n",
            "        \"n_estimators\": n_est,\n",
            "        \"oob_accuracy\": oob_score,\n",
            "        \"test_accuracy\": test_score,\n",
            "    })\n",
            "\n",
            "df_oob = pd.DataFrame(oob_results)\n",
            "\n",
            "fig = go.Figure()\n",
            "fig.add_trace(go.Scatter(\n",
            "    x=df_oob[\"n_estimators\"], y=df_oob[\"oob_accuracy\"],\n",
            "    name=\"OOB Accuracy\", mode=\"lines+markers\",\n",
            "    line=dict(color=COLORS[\"navy\"], width=2),\n",
            "    marker=dict(size=8),\n",
            "))\n",
            "fig.add_trace(go.Scatter(\n",
            "    x=df_oob[\"n_estimators\"], y=df_oob[\"test_accuracy\"],\n",
            "    name=\"Test Accuracy\", mode=\"lines+markers\",\n",
            "    line=dict(color=COLORS[\"accent\"], width=2, dash=\"dash\"),\n",
            "    marker=dict(size=8),\n",
            "))\n",
            "\n",
            "fig.update_layout(\n",
            "    title=\"OOB Error vs Number of Estimators\",\n",
            "    xaxis_title=\"Number of Base Learners\",\n",
            "    yaxis_title=\"Accuracy\",\n",
            "    height=450, width=700,\n",
            ")\n",
            "fig.show()\n",
            "save_chart(fig, MODEL_SLUG, \"oob_vs_estimators\")"
        ]
    },

    # Cell 20: Universal charts header
    {
        "cell_type": "markdown",
        "id": "cell-20",
        "metadata": {},
        "source": ["---\n", "## 11. Diagnostic Charts"]
    },

    # Cell 21: Universal charts
    {
        "cell_type": "code",
        "execution_count": None,
        "id": "cell-21",
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

    # Cell 22: Summary header
    {
        "cell_type": "markdown",
        "id": "cell-22",
        "metadata": {},
        "source": ["---\n", "## 12. Summary"]
    },

    # Cell 23: Summary text
    {
        "cell_type": "markdown",
        "id": "cell-23",
        "metadata": {},
        "source": [
            "### Where Bagging Sits on the Tradeoff Spectrum\n",
            "\n",
            "Bagging tends toward the **moderate/balanced** end of the spectrum. While the individual decision trees in the ensemble use `class_weight=\"balanced\"` (pushing toward higher recall), the averaging process smooths out extreme predictions, resulting in more conservative overall estimates. The ensemble is less aggressive than a single balanced tree but more aggressive than a linear model.\n",
            "\n",
            "### Strengths for This Problem\n",
            "- **Variance reduction:** Dramatically reduces the variance of high-variance base learners like decision trees\n",
            "- **No increase in bias:** Averaging preserves the expected prediction, so bias does not increase\n",
            "- **OOB error estimation:** Provides an unbiased estimate of test error without a separate validation set\n",
            "- **Feature importance:** Still interpretable, as we can average feature importances across trees\n",
            "- **Parallelizable:** Each bootstrap sample is independent, enabling easy parallelization\n",
            "- **Works with any base estimator:** Can use decision trees, neural networks, or any other model\n",
            "- **Robust to outliers:** The ensemble is more stable than individual trees\n",
            "\n",
            "### Limitations for This Problem\n",
            "- **Less powerful than Random Forest:** Does not introduce feature randomization, so variance reduction is less dramatic\n",
            "- **Still limited by base estimator:** If the base learner is fundamentally poor, bagging cannot fix it\n",
            "- **Does not reduce bias:** If the base learner is biased, that bias persists in the bagged ensemble\n",
            "- **Correlated base learners:** Bootstrap samples are not independent, so trees are still correlated\n",
            "- **Slower inference:** Must average predictions from M estimators instead of making a single prediction\n",
            "\n",
            "### Key Takeaway\n",
            "Bagging is the **bridge between single learners and advanced ensembles**. It reduces variance without the complexity of boosting or the feature randomization of Random Forest. For decision trees, Random Forest (which adds feature randomization) almost always outperforms Bagging, but Bagging is a useful baseline and works well with other base learners like neural networks or support vector machines."
        ]
    },

    # Cell 24: Footer
    {
        "cell_type": "markdown",
        "id": "cell-24",
        "metadata": {},
        "source": [
            "---\n",
            "*Notebook by Trinidad Cisneros — MIT Applied Data Science Program, April 2026*"
        ]
    },
]

# Build notebook structure
notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": 3
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.9.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

# Write notebook file
output_path = "/sessions/friendly-focused-carson/mnt/bitterscientist.com/folders/ds_blogs/projects/loanDefaultPrediction/notebooks/models/08_bagging.ipynb"
with open(output_path, "w") as f:
    json.dump(notebook, f, indent=1)

print(f"Notebook created: {output_path}")
