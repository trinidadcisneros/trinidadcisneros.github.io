# Blog Post Architecture: The Tradeoff Matrix
## Loan Default Prediction — 15 Classifiers Compared

---

## 1. Concept

**Central thesis:** Every classifier lives on a spectrum from "catch every defaulter but annoy good borrowers" to "only flag sure things but miss risky loans." The business context — cost of a missed default vs cost of a false rejection — determines which model wins. This is a transferable framework, not just a model shootout.

**Format:** Single self-contained HTML file with tabbed navigation. Each tab is a deep dive into one model family. Interactive plotly charts embedded via iframes from per-model notebook exports.

**Audience:** Data science practitioners and students who want to understand *why* models behave differently, not just which one "wins."

---

## 2. Tab Structure (19 tabs total)

### Navigation Groups

The tabs are organized into logical groups with visual separators:

| Group | Tab | Content |
|-------|-----|---------|
| **Framework** | Overview | Purpose, dataset, methodology, the tradeoff spectrum concept |
| **Framework** | Decision Guide | Interactive decision tree — click a leaf → jump to that model's tab |
| **Linear Models** | Logistic Regression | Full derivation + HMEQ results |
| **Linear Models** | LDA | Full derivation + HMEQ results |
| **Linear Models** | QDA | Full derivation + HMEQ results |
| **Distance/Probability** | KNN | Full derivation + HMEQ results |
| **Distance/Probability** | Naive Bayes | Full derivation + HMEQ results |
| **Tree Based** | Decision Tree | Full derivation + HMEQ results |
| **Ensemble: Bagging** | Random Forest | Full derivation + HMEQ results |
| **Ensemble: Bagging** | Bagging Classifier | Full derivation + HMEQ results |
| **Ensemble: Boosting** | AdaBoost | Full derivation + HMEQ results |
| **Ensemble: Boosting** | Gradient Boosting | Full derivation + HMEQ results |
| **Ensemble: Boosting** | XGBoost | Full derivation + HMEQ results |
| **Ensemble: Boosting** | LightGBM | Full derivation + HMEQ results |
| **Ensemble: Boosting** | CatBoost | Full derivation + HMEQ results |
| **Black Box** | SVM (RBF) | Full derivation + HMEQ results |
| **Black Box** | MLP Neural Network | Full derivation + HMEQ results |
| **Synthesis** | Model Comparison | Head to head metrics, charts, rankings across all frameworks |
| **Synthesis** | Key Takeaways | Business recommendations, the two-stage framework |

---

## 3. Model Tab Template (sections within each model tab)

Every model tab follows this exact structure:

### Section A: Introduction & Intuition
- One paragraph positioning this model on the tradeoff spectrum
- Visual metaphor or analogy for how the model "thinks"
- Where it sits: conservative (high precision) vs aggressive (high recall)

### Section B: The Math
- **Core equation** — the fundamental formula with variable definitions
- **Step by step derivation** — how we get from inputs to predictions
- **Worked example** — using actual HMEQ data points:
  - Pick 2-3 real rows from the dataset
  - Walk through the math numerically
  - Show the predicted probability and classification
- **Training objective** — what the model is optimizing (loss function)
- All math rendered with MathJax (LaTeX notation)

### Section C: Assumptions & Requirements
- **Statistical assumptions** (e.g., linearity, independence, normality)
- **Data transformation requirements** (scaling, encoding, imputation)
- **When to use** — scenarios where this model excels
- **When NOT to use** — red flags and contraindications
- Formatted as colored callout cards (green for use, red for avoid)

### Section D: Diagnostic Plots
- Model-specific visualizations embedded as plotly HTML iframes
- Each chart has a "What to look for" interpretation guide below it
- See Section 6 below for the full chart inventory per model

### Section E: HMEQ Results
- Confusion matrix (styled HTML table, not image)
- Key metrics: recall, precision, F1, AUC, PR-AUC
- How this model performed relative to the tradeoff spectrum thesis
- Best hyperparameters found

### Section F: Interpretation & Limitations
- What the results tell us about this model's fit for the problem
- Known limitations and failure modes
- How it compares to adjacent models in its family

---

## 4. Special Tabs

### Overview Tab
- Blog purpose and reading guide
- Dataset summary (HMEQ: 5,960 loans, 13 features, 20% default rate)
- The Tradeoff Spectrum visual (horizontal spectrum from "catch all defaults" to "only flag sure things")
- Methodology: same train/test split, same preprocessing, same CV strategy across all models
- How to read the model tabs
- Color legend for the model families

### Decision Guide Tab
- Interactive HTML/CSS/JS decision tree
- Questions like: "Is interpretability required?" → "Do you have >10k samples?" → "Are features linearly separable?"
- Each leaf node is a model recommendation with a clickable link to that model's tab
- Responsive: vertical layout on mobile, horizontal on desktop
- Built with pure HTML/CSS (flexbox + CSS transitions), no external library

### Model Comparison Tab
- Grouped bar chart: recall across all 15 models
- Grouped bar chart: precision across all 15 models
- Scatter plot: recall vs precision (the tradeoff spectrum visualized)
- Radar chart: top 5 models across all metrics
- Ranking table: models sorted by recall, precision, F1, AUC (separate columns)
- The "no free lunch" analysis: which models trade what for what
- All charts are plotly HTML embeds from the comparison notebook

### Key Takeaways Tab
- The tradeoff spectrum conclusion
- Which model families land where on the spectrum
- The business context argument: your cost ratio determines your model
- The two-stage recommendation (train for recall, threshold for profit)
- Links to the Business Loss Function blog (the companion post)

---

## 5. File Structure

```
loanDefaultPrediction/
├── loan_default_tradeoff_matrix.html          ← THE BLOG POST
├── BLOG_ARCHITECTURE.md                       ← THIS FILE
│
├── notebooks/
│   ├── Cisneros_Loan_Default_Prediction.ipynb ← Capstone (existing)
│   ├── Cisneros_Business_Loss_Analysis.ipynb  ← Business loss (existing)
│   └── models/                                ← NEW: per-model notebooks
│       ├── 01_logistic_regression.ipynb
│       ├── 02_lda.ipynb
│       ├── 03_qda.ipynb
│       ├── 04_knn.ipynb
│       ├── 05_naive_bayes.ipynb
│       ├── 06_decision_tree.ipynb
│       ├── 07_random_forest.ipynb
│       ├── 08_bagging.ipynb
│       ├── 09_adaboost.ipynb
│       ├── 10_gradient_boosting.ipynb
│       ├── 11_xgboost.ipynb
│       ├── 12_lightgbm.ipynb
│       ├── 13_catboost.ipynb
│       ├── 14_svm.ipynb
│       ├── 15_mlp.ipynb
│       └── 00_comparison.ipynb               ← Cross-model comparison charts
│
├── data/
│   ├── inputs/
│   │   └── hmeq.csv                          ← Dataset (existing)
│   └── outputs/                               ← NEW: plotly HTML chart exports
│       ├── comparison/
│       │   ├── recall_all_models.html
│       │   ├── precision_all_models.html
│       │   ├── recall_vs_precision_scatter.html
│       │   ├── radar_top5.html
│       │   └── ranking_table.html
│       ├── logistic_regression/
│       │   ├── coefficients.html
│       │   ├── roc_curve.html
│       │   ├── precision_recall_curve.html
│       │   ├── confusion_matrix.html
│       │   ├── calibration_curve.html
│       │   └── decision_boundary_2d.html
│       ├── lda/
│       │   ├── discriminant_projection.html
│       │   ├── class_separation.html
│       │   ├── roc_curve.html
│       │   └── ...
│       ├── [one folder per model...]
│       └── mlp/
│           ├── training_loss_curve.html
│           ├── layer_activations.html
│           ├── roc_curve.html
│           └── ...
│
└── static/                                    ← Existing project assets
    └── images/
```

---

## 6. Chart Inventory Per Model

Each model notebook generates plotly HTML files. Here is what each model needs:

### Universal Charts (every model gets these)
1. **ROC Curve** — with AUC annotation
2. **Precision-Recall Curve** — with AP annotation
3. **Confusion Matrix Heatmap** — counts + percentages
4. **Classification Report Table** — styled HTML
5. **Threshold Sweep** — recall, precision, F1 vs threshold

### Model-Specific Charts

| Model | Specific Charts |
|-------|----------------|
| Logistic Regression | Coefficient bar chart, odds ratios, calibration curve, regularization path (C vs metrics) |
| LDA | Discriminant function projection (1D or 2D), class separation histogram, within/between scatter |
| QDA | Per-class decision boundaries (2D PCA projection), covariance ellipses |
| KNN | K vs metrics curve, distance distribution, 2D decision boundary (PCA space) |
| Naive Bayes | Feature likelihood distributions (per class), posterior probability distribution |
| Decision Tree | Tree structure visualization (top 4-5 levels), feature importance bar chart, max_depth vs metrics |
| Random Forest | Feature importance (MDI + permutation), OOB error curve, tree count vs metrics |
| Bagging | OOB error by n_estimators, feature importance, individual tree variance |
| AdaBoost | Estimator weight curve, staged predictions, feature importance |
| Gradient Boosting | Staged recall/F1 by n_estimators, learning rate comparison, feature importance (gain), partial dependence (top 3 features) |
| XGBoost | Feature importance (gain + cover + weight), staged predictions, learning curves, SHAP summary (if shap installed) |
| LightGBM | Feature importance (gain + split), leaf count distribution, learning curves, split info |
| CatBoost | Feature importance (native), staged predictions, learning curves, SHAP interactions (if available) |
| SVM | Support vector counts, margin visualization (2D PCA), C parameter sensitivity, kernel comparison |
| MLP | Training loss curve, layer-by-layer weight distribution, activation patterns, architecture diagram |

---

## 7. Notebook Template (what each model notebook contains)

Each of the 15 model notebooks follows this structure:

```
Cell 1: Markdown — Title and model overview
Cell 2: Code — Imports and data loading (shared across all, loads hmeq.csv)
Cell 3: Code — Preprocessing (same pipeline as capstone)
Cell 4: Code — Train/test split (same seed, same split)
Cell 5: Markdown — Model math and theory (rendered with markdown LaTeX)
Cell 6: Code — Worked example: manually compute prediction for 2-3 data points
Cell 7: Code — Train the model (same hyperparameter grid as capstone)
Cell 8: Code — Evaluate: confusion matrix, metrics, classification report
Cell 9-15: Code — Generate each diagnostic chart, save as HTML
Cell 16: Code — Export all charts to ../data/outputs/{model_name}/
Cell 17: Markdown — Results commentary
```

Each notebook is self-contained (can run independently) and exports its charts to the `data/outputs/` folder where the blog HTML picks them up.

---

## 8. Shared Code Module

To avoid duplicating 500 lines of setup code across 16 notebooks, create a shared utility module:

```
notebooks/models/shared_utils.py
```

Contains:
- `load_and_prep_data()` — loads hmeq.csv, creates missing flags, splits train/test
- `get_pipelines()` — returns prep_linear and prep_tree ColumnTransformers
- `evaluate_model()` — computes all metrics, returns dict
- `save_plotly_chart(fig, model_name, chart_name)` — saves to data/outputs/{model_name}/
- `plot_roc_curve(model, X_test, y_test)` — standard ROC chart
- `plot_pr_curve(model, X_test, y_test)` — standard PR chart
- `plot_confusion_matrix(y_test, y_pred)` — heatmap
- `plot_threshold_sweep(model, X_test, y_test)` — threshold analysis
- Constants: RANDOM_STATE, TARGET, color palette

---

## 9. HTML/CSS Architecture

### Framework
- Bootstrap 4.3.1 (matches existing bitterscientist.com pages)
- Custom CSS (not Tailwind, not the product analytics case study CSS)
- MathJax 3 for LaTeX rendering
- plotly.js not needed (charts are iframed HTML files)

### Color Palette
Aligned with the Midnight Executive theme from the presentation:
- **Navy**: `#1E2761` (primary headers, dark backgrounds)
- **Ice Blue**: `#CADCFC` (light backgrounds, callout boxes)
- **Accent Blue**: `#4A90D9` (links, active tabs, highlights)
- **Success Green**: `#2CA58D` (positive callouts, "when to use")
- **Warning Red**: `#E15554` (negative callouts, "when not to use")
- **Orange**: `#F18F01` (attention callouts, key insights)
- **Light BG**: `#f8f9fa` (alternating row backgrounds)
- **White**: `#ffffff` (card backgrounds)

### Tab Navigation Design
- Horizontal tab bar, centered, with group labels above
- Tab groups visually separated by thin vertical dividers
- Active tab: bottom border in Accent Blue + bold text
- Mobile: tabs become a dropdown selector (hamburger-style)
- Group labels: small gray uppercase text above tab groups

### Content Components (reusable CSS classes)
1. **Math Block** — `<div class="math-block">` with gray background, monospace font, MathJax rendered
2. **Worked Example** — `<div class="worked-example">` cream background, step-by-step with orange left border
3. **Assumption Card** — `<div class="assumption-card">` with icon (check or warning) and text
4. **Use/Avoid Cards** — `.use-card` (green left border) and `.avoid-card` (red left border)
5. **Chart Embed** — `<div class="chart-container"><iframe src="..."></iframe></div>` responsive 16:9 ratio
6. **Metric Badge** — `<span class="metric-badge">Recall: 0.8500</span>` inline colored badges
7. **Model Header** — model name, family badge, tradeoff position indicator
8. **Spectrum Bar** — horizontal bar showing where model sits on recall-precision spectrum
9. **Comparison Table** — sortable styled table with hover highlighting

### Responsive Breakpoints
- Desktop (>1024px): full tab bar, 2-column chart grid, side-by-side use/avoid cards
- Tablet (768-1024px): scrollable tab bar, single column charts
- Mobile (<768px): dropdown tab selector, stacked layout, full-width charts

---

## 10. Build Order

### Phase 1: Foundation
1. Create `notebooks/models/shared_utils.py`
2. Create the HTML shell with tab navigation (empty tabs)
3. Build the Overview tab content
4. Build the Decision Guide tab (interactive decision tree)

### Phase 2: Model Notebooks (one at a time)
For each model, create the notebook and generate charts. Suggested order (increasing complexity):
1. Logistic Regression (simplest math, most charts)
2. Decision Tree (visual, easy to explain)
3. KNN (intuitive distance concept)
4. Naive Bayes (probability foundation)
5. LDA / QDA (linear algebra)
6. Random Forest (builds on Decision Tree)
7. Bagging (simpler ensemble)
8. AdaBoost (boosting intro)
9. Gradient Boosting (builds on AdaBoost)
10. XGBoost (builds on Gradient Boosting)
11. LightGBM (builds on XGBoost)
12. CatBoost (builds on gradient boosting)
13. SVM (kernel math)
14. MLP (neural network math)

### Phase 3: Synthesis
15. Create `00_comparison.ipynb` — cross-model charts
16. Build the Model Comparison tab
17. Build the Key Takeaways tab
18. Write model tab HTML content for each of the 15 models

### Phase 4: Polish
19. Mobile responsiveness testing
20. MathJax rendering verification
21. Chart embed sizing and loading
22. Cross-browser testing
23. Deploy to bitterscientist.com

---

## 11. Estimated Scope

| Component | Count | Est. effort each | Total |
|-----------|-------|-------------------|-------|
| Shared utils module | 1 | Medium | 1 |
| Model notebooks | 15 | Large (math + charts) | 15 |
| Comparison notebook | 1 | Medium | 1 |
| HTML shell + CSS | 1 | Large | 1 |
| Overview tab content | 1 | Medium | 1 |
| Decision guide tab | 1 | Large (interactive) | 1 |
| Model tab content (HTML) | 15 | Medium (math writing) | 15 |
| Comparison tab content | 1 | Medium | 1 |
| Takeaways tab content | 1 | Small | 1 |
| **Total** | | | **37 deliverables** |

This is a multi-session project. Each session can realistically complete 2-3 model notebooks + their corresponding HTML tab content.
