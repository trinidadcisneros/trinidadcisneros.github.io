# A/B Testing Portfolio Project — Tracking Notes

**Dataset:** Hillstrom MineThatData Email Marketing (2008)
**Last Updated:** 2026-03-23

---

## Open Questions & Comments

### Data Design Questions
- [x] **How were customers assigned to treatment groups?** The near-perfect 33.3% split (21,307 / 21,306 / 21,387) strongly suggests **simple (pure) random assignment** without stratification. The covariate balance check confirms this — all covariates are nearly identical across groups, which at n=64,000 is expected from randomization alone. No evidence of stratified or blocked randomization.
  - **Industry context:** In practice, most companies use **stratified randomization** (also called blocked randomization) rather than pure random assignment. They define stratification variables — typically recency, spending tier, geographic region, new vs. returning, acquisition channel, and demographics when available — then randomly assign within each stratum to guarantee balance on key variables. Some use adaptive/covariate-adaptive designs that dynamically rebalance as users enter the experiment. The Hillstrom dataset's simple randomization works fine here because n=64,000 is large enough that random chance alone produces good balance.
- [x] **Were Men's emails only sent to men? (ANSWERED: No — there is crossover.)** The `mens` and `womens` columns indicate **past purchase department history**, NOT customer gender. The dataset contains no gender field. Row 0 example: customer with `mens=1, womens=0` (historically bought men's products) was assigned to "Womens E-Mail" group. This confirms **email type assignment was random and NOT based on purchase history or gender**. The business question becomes: does sending a men's merchandise email to someone who historically buys women's merchandise (or vice versa) matter? This is a subgroup analysis opportunity for uplift modeling (nb08) — does purchase-history-to-email-type match/mismatch predict differential response?
- [ ] **Should zip_code be used in downstream analysis?** The `zip_code` field has 3 levels: Suburban (44.9%), Urban (40.1%), Rural (14.9%). This should be explored as a stratification variable — do email campaigns perform differently in Suburban vs Urban vs Rural areas? Relevant for: subgroup analysis in classical tests, a covariate in CUPED (nb07), and a feature in uplift modeling (nb08). Could also check if zip_code interacts with email type.

### Dataset Limitations
- [ ] **No email content details available.** The dataset does not include subject lines, body text, images, send times, or open/click tracking. We only know *which type* of email was sent (Men's vs Women's merchandise) and the behavioral outcomes. This means we can conclude whether email campaigns lift outcomes, but we cannot attribute *why* at the creative level — the Men's email may have outperformed simply due to a better subject line, not because men's products are inherently more engaging. **For write-up:** Frame this as a limitation and recommend a follow-up experiment that holds product category constant while varying creative elements (subject line, CTA, imagery, send time) to isolate what drives the lift.
- [ ] **No customer demographics.** No gender, age, income, or household data. The `mens`/`womens` flags are purchase history, not identity. This limits our ability to do true demographic segmentation, though `zip_code` serves as a rough geographic/socioeconomic proxy. **Important:** The email-match analysis classifies Match/Mismatch/Mixed based on *purchase department history*, NOT gender. A `mens=1` customer could be any gender. **Recommendation for write-up:** In a real business setting, collecting actual customer demographic data would enable true demographic targeting analysis and should be proposed as a follow-up data collection initiative.
- [ ] **No temporal data.** No timestamps on when emails were sent or when visits/conversions occurred. This prevents time-to-event analysis (survival models), seasonality checks, and novelty effect assessment. We treat all outcomes as a single post-treatment snapshot.

### Data Quality Notes
- [ ] **6,562 duplicate rows (10.3%):** These are NOT data errors. With mostly categorical/binned features (binary mens/womens, 3 zip codes, 3 channels, 7 history segments), many customers naturally share identical feature combinations. Each row represents a unique customer. No rows should be dropped.
- [ ] **Conversion is very sparse:** Only 0.9% overall conversion rate. This extreme class imbalance will affect power for conversion-based tests and should be discussed in the diagnostics notebook (nb10).
- [ ] **Spend is heavily zero-inflated:** Median spend is $0.00, mean is $1.05, max is $499. The distribution is highly right-skewed. This violates normality assumptions for t-tests and should be addressed with non-parametric alternatives and noted in assumption diagnostics.

### Analysis Direction Notes
- [x] **Email-purchase history match analysis (ADDED to nb01):** Created `email_match` and `email_match_simple` columns classifying each customer as Match, Mismatch, Mixed, or Control. EDA charts compare visit/conversion/spend by match status. Columns are saved in the clean CSV so all downstream notebooks can use them.
- [ ] **Downstream: Formal match/mismatch testing needed in:**
  - **nb02 (Z-Test/T-Test):** Add stratified tests — Match vs Control and Mismatch vs Control — to formally determine if aligned emails outperform misaligned ones
  - **nb08 (Uplift Modeling):** Use `email_match_simple` as a feature to see if match status drives heterogeneous treatment effects. Already uses `mens`/`womens` as raw features which partially captures this, but the explicit match variable will be more interpretable
- [ ] The 3-arm design (Mens Email vs Womens Email vs No Email) allows both "any email vs none" and "men's vs women's email" comparisons — make sure both are covered
- [ ] **Zip code stratification — downstream coverage:**
  - **nb08 (Uplift Modeling):** Already uses `zip_code` as a feature — this will capture whether treatment effects vary by geography through the model's feature importance and uplift predictions by subgroup
  - **nb10 (Diagnostics):** Should add stratified results by zip_code to the sensitivity analysis section
  - **NOT currently in nb02/nb03:** Could add stratified frequentist tests within each zip_code level, but this may be better handled by nb08's uplift approach (avoids multiple testing issues from running 3×3 pairwise tests)

---

## Notebook Execution Log

| Notebook | Status | Date | Notes |
|----------|--------|------|-------|
| nb01 - Data Acquisition & EDA | Running | 2026-03-23 | Fixed NaN in balance table, added duplicate clarification |
| nb02 - Z-Test & T-Test | Pending | — | — |
| nb03 - Chi-Square | Pending | — | — |
| nb04 - CI & Bootstrap | Pending | — | — |
| nb05 - Sequential Testing | Pending | — | — |
| nb06 - Bayesian A/B | Pending | — | — |
| nb07 - CUPED | Pending | — | — |
| nb08 - Uplift Modeling | Pending | — | — |
| nb09 - Multi-Armed Bandits | Pending | — | — |
| nb10 - Comparison & Diagnostics | Pending | — | — |

---

## Data Story Framing Ideas
- Lead with the business question: "Should this e-commerce company invest in email marketing, and if so, which type of email campaign?"
- Emphasize the randomized experiment design — this is causal inference, not just correlation
- The 3-arm design is a strength: it lets you compare email vs no email AND men's vs women's email
- End with actionable recommendations: which campaign, for which customer segments, and how confident are we?

---

## Blog Post Framework Requirement

**The A/B testing blog post MUST follow the same framework as `ds_loan_default_tradeoff_matrix.html`** (located at `/folders/ds_blogs/ds_loan_default_tradeoff_matrix.html`). Specifically:

### Structure to Replicate
- **Two-tier tab navigation:**
  - *Tier 1 — Category pills* (`class="category-btn"`) group related methods together (e.g., "Framework", "Frequentist", "Bayesian/Bootstrap", "Sequential/Bandits", "ML Methods", "Synthesis")
  - *Tier 2 — Method tabs* (`class="nav-tab"`) appear under the active category, one row at a time via `switchCategory()` / `switchTab()` JS
- **Tab content containers:** `<div id="{tabId}" class="tab-content">` with a single `active` tab shown at a time
- **Section controls per tab:** "Expand All" / "Collapse All" buttons calling `expandAllSections(tabId)` / `collapseAllSections(tabId)`
- **Collapsible sections:** each content block is a `<details class="model-section"><summary>Section Title</summary><div class="model-section-body">…</div></details>` — first section uses `open` attribute
- **Consistent per-method layout:** Every method tab should have the same set of sections (e.g., Purpose, Math/Intuition, Assumptions, Results, Diagnostic Plots, Business Interpretation, Lay-Language Summary)
- **Framework tabs up front:** Overview + Decision Guide tabs (mirroring the loan post) explain the A/B testing framework and how to choose between methods before diving into per-method tabs
- **Synthesis tabs at the end:** Cross-method comparison + Key Takeaways tabs

### Styling and Includes
- Use `<div w3-include-html="/folders/navbar_footer/navbar_pages.html">` and `/folders/navbar_footer/footer.html` for navbar/footer
- Match the existing CSS patterns (page-container, content-wrap, blog-container, main-container, page-header)
- Reuse the same JS helpers: `switchCategory`, `switchTab`, `expandAllSections`, `collapseAllSections`

### Interactivity Where Applicable
- Plotly charts embedded inline for: distribution plots, bootstrap distributions, Bayesian posteriors, sequential boundaries, Qini curves, bandit regret curves
- Interactive tables with sortable/filterable results where useful
- Equations rendered via MathJax (match how the loan post handles math notation)

### Proposed Tab Structure for A/B Testing Post
- **Framework category:** Overview, Decision Guide (which test when)
- **Frequentist category:** Z-Test/T-Test (nb02), Chi-Square (nb03)
- **Estimation category:** Confidence Intervals & Bootstrap (nb04)
- **Sequential/Adaptive category:** Sequential Testing (nb05), Multi-Armed Bandits (nb09)
- **Bayesian category:** Bayesian A/B (nb06)
- **Variance Reduction & ML category:** CUPED (nb07), Uplift Modeling (nb08)
- **Synthesis category:** Method Comparison & Diagnostics (nb10), Key Takeaways

**How to apply:** When building the final blog HTML, copy the head/style/script block and navigation scaffolding from `ds_loan_default_tradeoff_matrix.html` and populate the tabs from each notebook's outputs (charts saved to `data/outputs/nb##/`). Keep section titles consistent across method tabs so readers can compare methods the same way they compare models in the loan post.

---

## Notebook Completion Status (as of 2026-04-14)

All 10 notebooks exist in `projects/ab_testing/notebooks/`:

| # | File | Built | Executed |
|---|------|-------|----------|
| 1 | nb01_data_acquisition_eda.ipynb | Yes | Yes (by user) |
| 2 | nb02_frequentist_ztest_ttest.ipynb | Yes (Primary/Secondary/Exploratory restructure) | In progress |
| 3 | nb03_chi_square_test.ipynb | Yes | Not yet |
| 4 | nb04_confidence_intervals_bootstrap.ipynb | Yes | Not yet |
| 5 | nb05_sequential_testing.ipynb | Yes | Not yet |
| 6 | nb06_bayesian_ab_testing.ipynb | Yes | Not yet |
| 7 | nb07_cuped_variance_reduction.ipynb | Yes | Not yet |
| 8 | nb08_uplift_modeling.ipynb | Yes | Not yet |
| 9 | nb09_multi_armed_bandits.ipynb | Yes | Not yet |
| 10 | nb10_comparison_diagnostics.ipynb | Yes (reads from nb07/nb08/nb09 outputs) | Not yet |

Plan: user runs notebooks one at a time, starting from nb02 onward.

---

## Blog Section Template (per method tab)

Every method tab in the final blog (mirroring `ds_loan_default_tradeoff_matrix.html`) should contain these five collapsible `<details class="model-section">` blocks, in this order:

1. **Math behind the test** — formulas, symbols, intuition, and a worked mini-example
2. **Assumptions and requirements** — when the method applies, what breaks it, preconditions on data
3. **Diagnostic charts/plots** — visualizations that verify assumptions OR show the method in action
4. **Results and interpretation** — numerical outputs plus lay-language reading
5. **Limitations** — what this method cannot tell you, common failure modes, when to prefer another approach

Every notebook should produce enough content and charts to fill these five sections cleanly.

---

## Per-Notebook Gap Analysis & Planned Additions

### nb02 — Z-Test / T-Test
- **Present:** Math, Assumptions (normality / variance / independence), Q-Q plots, histograms, results, limitations (partial)
- **Add:**
  - Dedicated "Z-Test vs T-Test — when to use which" markdown block
  - **Power curve chart** — detectable effect size vs sample size (critical for blog)
  - **Forest plot** — effect sizes + 95% CIs across all tested metrics/arms side-by-side
  - Levene's-test visualization for equal-variance assumption
  - Explicit Limitations section ("assumes independent observations", "sensitive to outliers in spend", "doesn't handle zero-inflation directly")

### nb03 — Chi-Square Test
- **Present:** Math, Assumptions (expected cell count), contingency heatmap, results with Cramér's V
- **Add:**
  - **Observed vs Expected frequency side-by-side heatmap**
  - **Standardized residuals heatmap** — shows which cells drive significance
  - Cell-count adequacy indicator (visual marker for E_ij ≥ 5)
  - Explicit Limitations section (sparse tables, low-count bias, directionless)

### nb04 — Confidence Intervals & Bootstrap
- **Present:** Math, bootstrap logic, replicate histograms, multi-method CIs
- **Add:**
  - **Bootstrap distribution histogram with CI markers overlaid** (percentile, BCa, Wald)
  - **Side-by-side analytical vs bootstrap CI comparison plot** (forest style)
  - Percentile vs BCa correction comparison
  - Explicit Limitations section (bootstrap fails on extreme skew, dependent obs, heavy ties)

### nb05 — Sequential Testing
- **Present:** Math of spending functions, boundaries, z-stat evolution
- **Add:**
  - **Z-statistic trajectory over time with O'Brien-Fleming + Pocock boundaries overlaid** (signature sequential chart)
  - **Spending function comparison** (O'Brien-Fleming vs Pocock vs fixed-sample)
  - **Sample-size savings chart** — sequential vs fixed-sample at same power
  - Explicit Limitations section (requires pre-registered look schedule, inflation if peeking outside plan)

### nb06 — Bayesian A/B Testing
- **Present:** Beta-Binomial math, prior/posterior intro, some posterior plots
- **Add:**
  - **Prior vs posterior density overlay per arm** (cornerstone Bayesian chart)
  - **Posterior distribution of the difference (A − B or treatment − control)** with credible interval
  - **Probability A > B cumulative curve over time** (evidence evolution)
  - **Prior sensitivity panel** — posterior under weak/moderate/strong priors
  - Explicit Limitations section (prior choice matters when n is small, decision thresholds are subjective)

### nb07 — CUPED
- **Present:** CUPED formula, variance reduction quantification, adjusted-vs-unadjusted hist
- **Add:**
  - **Pre vs post covariate scatter** — illustrates the stability assumption CUPED relies on
  - **Variance comparison bar chart** — σ² unadjusted vs σ² CUPED with % reduction label
  - **Power curve comparison** — standard t-test vs CUPED t-test across sample sizes
  - Discussion of when CUPED *hurts* (weak pre-period correlation, selection bias)
  - Explicit Limitations section

### nb08 — Uplift Modeling  ✅ UPDATED 2026-04-14
- **Added:** Mixed-group confound framing, `cross_shopper` feature, stratified uplift by `buyer_type` chart + CSV, interpretation block
- **Still to add for blog:**
  - Formal HTE math block ($\tau(x) = E[Y|X,W=1] - E[Y|X,W=0]$) with T-Learner, S-Learner, X-Learner formulations side-by-side
  - **Feature-importance plot** for differential response (already partially present — verify works with new `cross_shopper` feature)
  - **Cumulative-gain / Qini curve** polish for embedding
  - Explicit Limitations section (no ground-truth uplift, model extrapolation risk, decile instability at low conversion rates)

### nb09 — Multi-Armed Bandits
- **Present:** Arm-selection plots, cumulative regret, some comparison
- **Add:**
  - Formal math block (regret definition, Thompson Sampling posterior update, UCB1 confidence bound)
  - **Cumulative regret with theoretical log-t bound overlay**
  - **Arm-pull-frequency evolution over time** (stacked area or line-per-arm)
  - **Posterior evolution** for top 2 arms (Beta densities at multiple time snapshots)
  - **Direct comparison**: ε-greedy vs Thompson vs UCB1 on same axes
  - Explicit Limitations section (non-stationary arms, many-arm cold-start, delayed feedback)

### nb10 — Comparison & Diagnostics
- **Present:** Method-agreement heatmap, Q-Q plots, power analysis, sensitivity analyses
- **Add:**
  - **P-value comparison scatter** (method A vs method B with y=x line)
  - **Effect-size forest plot across ALL methods**
  - **Power-curve overlay across methods**
  - Practical vs statistical significance callout
  - Explicit Limitations section on the comparison framework itself

---

## Plotly Refactor Plan

Every chart destined for the blog must also exist as responsive Plotly HTML saved to `data/outputs/nb##/nb##_<name>_interactive.html`. Pattern already established in `notebooks/nb01_plotly_charts.py` — replicate for each notebook:

- Standalone `nb##_plotly_charts.py` per notebook that reads that notebook's output CSVs / re-computes what it needs and writes all charts as HTML
- Every figure uses: `include_plotlyjs='cdn'`, `config={'responsive': True}`, `automargin=True` on all axes, tick rotation on long labels, explicit y-axis headroom for outside-positioned data labels, legends pushed outside plot area

**Priority order for Plotly conversion** (highest blog value first):
1. nb05 — sequential boundary trajectory (most visually compelling)
2. nb06 — prior→posterior animation/overlay
3. nb02 — power curve
4. nb08 — Qini curve + new stratified-by-buyer-type chart
5. nb09 — regret curves with bounds
6. nb10 — method-agreement heatmap + cross-method forest plot
7. nb03 — residuals heatmap
8. nb04 — bootstrap distribution with CI markers
9. nb07 — variance reduction + pre/post scatter

---

## Execution Order Recommendation

1. User runs nb02 through nb07 (current plan) — I monitor outputs and refine
2. User runs nb08 with the new stratified analysis
3. User runs nb09, nb10
4. I add missing sections/charts per this gap analysis, one notebook at a time so each can be re-run and verified
5. I write per-notebook `nb##_plotly_charts.py` files
6. Finally: assemble the blog HTML using the `ds_loan_default_tradeoff_matrix.html` framework, pulling from each notebook's `data/outputs/nb##/` folder
