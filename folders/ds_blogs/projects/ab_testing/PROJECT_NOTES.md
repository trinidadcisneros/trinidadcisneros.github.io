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
