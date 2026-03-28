# Potential Customers Prediction - Project Context

**Last Updated:** 2026-03-27
**Status:** In Progress - Notebook Built, Needs Execution & Review

---

## 1. Project Overview

**Project Name:** potential_customers_prediction
**Location:** `ds_blogs/projects/potential_customers_prediction/`
**Program:** Data Science Elective - Supervised Learning (Classification)
**Submission Type:** Full-code (Jupyter Notebook submitted as .html)

### Objective
ExtraaLearn (EdTech startup) wants to predict which leads are likely to convert to paid customers. As a data scientist, the goals are:
1. Analyze and build an ML model to identify leads likely to convert
2. Find the factors driving the lead conversion process
3. Create a profile of leads likely to convert

### Dual Purpose
- **Program Submission:** Complete the learner notebook per rubric criteria, submit as .html
- **Blog Post / Data Story:** Expand analysis for trinidadcisneros.com (static HTML/Bootstrap site hosted via GitHub Pages) with richer visualizations and narrative

---

## 2. Folder Structure

```
potential_customers_prediction/
  data/
    inputs/           # Raw data and reference docs
      ExtraaLearn.csv
      Report Template - Potential Customers Prediction.docx
    outputs/          # Processed data, model outputs, exported visuals
  notebooks/
    Learner Notebook - Full Code Version - Potential Customers Prediction.ipynb
  context.md          # This file - project tracking
```

---

## 3. Dataset Summary

**File:** `ExtraaLearn.csv`
**Rows:** 4612 (based on learner notebook reference)
**Target Variable:** `status` (1 = converted/paid, 0 = not converted)

### Features
| Feature | Type | Description |
|---------|------|-------------|
| ID | Identifier | Lead ID (EXT###) |
| age | Numeric | Age of lead |
| current_occupation | Categorical | Professional, Unemployed, Student |
| first_interaction | Categorical | Website, Mobile App |
| profile_completed | Ordinal | Low (0-50%), Medium (50-75%), High (75-100%) |
| website_visits | Numeric | Number of website visits |
| time_spent_on_website | Numeric | Total seconds on website |
| page_views_per_visit | Numeric | Avg pages viewed per visit |
| last_activity | Categorical | Email Activity, Phone Activity, Website Activity |
| print_media_type1 | Binary | Saw ad in Newspaper (Yes/No) |
| print_media_type2 | Binary | Saw ad in Magazine (Yes/No) |
| digital_media | Binary | Saw ad on digital platforms (Yes/No) |
| educational_channels | Binary | Heard via education channels (Yes/No) |
| referral | Binary | Heard through referral (Yes/No) |
| status | Binary (Target) | 1 = paid customer, 0 = not paid |

---

## 4. Program Rubric Criteria (60 points total)

### EDA (12 points)
- [ ] Problem definition
- [ ] Univariate analysis
- [ ] Bivariate analysis
- [ ] Comments on visualizations (range, outliers, distribution)
- [ ] Appropriate visualizations for patterns/insights
- [ ] Key observations on individual variables and relationships

### Data Pre-processing (4 points)
- [ ] Drop insignificant variables with comments
- [ ] Missing value treatment (if needed) with comments
- [ ] Outlier detection/treatment (if needed) with comments
- [ ] Feature engineering (if possible) with comments
- [ ] Data split (train/test)

### Decision Tree Model (5 points)
- [ ] Build the model
- [ ] Comment on model performance

### Decision Tree - Evaluation & Improvement (10 points)
- [ ] Hyperparameter tuning with GridSearchCV
- [ ] Evaluate on appropriate metric
- [ ] Comment on model performance
- [ ] Feature importance analysis with comments

### Random Forest Model (5 points)
- [ ] Build the model
- [ ] Comment on model performance

### Random Forest - Evaluation & Improvement (10 points)
- [ ] Hyperparameter tuning with GridSearchCV
- [ ] Evaluate on appropriate metric
- [ ] Comment on model performance
- [ ] Feature importance analysis with comments

### Actionable Insights & Recommendations (6 points)
- [ ] Key takeaways from important features
- [ ] Business-actionable recommendations

### Notebook Quality (8 points)
- [ ] Structure and flow
- [ ] Well-commented code
- [ ] Inline comments explaining functionality
- [ ] Markdown cells with observations/insights
- [ ] No warnings or errors
- [ ] Sequential execution from start to finish

---

## 5. EDA Questions to Address (from notebook template)

1. How does current occupation affect lead status?
2. Do the first channels of interaction impact lead status?
3. Which interaction mode works best?
4. Which marketing channels have the highest lead conversion rate?
5. Does profile completion increase chances of conversion?

---

## 6. Blog Post / Data Story Expansion Plans

### Additional Analysis (beyond rubric)
- Deeper statistical tests (chi-square, ANOVA) for feature significance
- Correlation heatmap for numeric features
- Cross-validation analysis beyond GridSearchCV
- ROC/AUC curves comparison between models
- Precision-Recall tradeoff analysis
- SHAP or feature importance visualization
- Lead scoring model / probability calibration
- Confusion matrix deep-dive with business cost analysis

### Visualization & Presentation
- **Hex Integration (Research):** Hex supports embedding individual cells/charts via iframe into any website
  - Public embedding: no auth required, good for blog/portfolio
  - Signed embedding: single-use signed URLs for secure content
  - Can embed entire apps or individual cells
  - Works with iframe approach compatible with HTML/Bootstrap site
  - **Action needed:** Check Hex free tier availability for embedding; create Hex project mirroring analysis
  - **Reference:** https://hex.tech/product/embedded-analytics/

### Website Framework
- trinidadcisneros.com is a static HTML + Bootstrap 3.4 site (GitHub Pages)
- Hex embeds via iframe would work with this setup: `<iframe src="HEX_EMBED_URL" width="100%" height="600"></iframe>`
- Alternative: export static charts as images or interactive HTML (Plotly) for direct embedding

---

## 7. Key Decisions & Notes

### Notebook Current State (2026-03-27)
- Template downloaded: has section headers but ALL code cells are empty
- Needs full implementation from scratch
- Must use Decision Tree and Random Forest (as specified by rubric)
- GridSearchCV required for hyperparameter tuning
- Submit as .html (not .ipynb)

### Tech Stack
- Python (pandas, numpy, matplotlib, seaborn, scikit-learn)
- Jupyter Notebook
- Optional: Plotly for interactive charts (blog version)
- Optional: Hex for embedded analytics on website

---

## 8. Progress Log

| Date | Activity | Status |
|------|----------|--------|
| 2026-03-27 | Project setup: folder structure, file organization, context.md created | Done |
| 2026-03-27 | Requirements review: rubric criteria mapped, notebook template assessed | Done |
| 2026-03-27 | Hex embedding research completed | Done |
| 2026-03-27 | Full notebook built (82 cells: 33 markdown + 49 code) | Done |
| | Notebook files: Original template (read-only) + ExtraaLearn_Full_Analysis.ipynb (working copy) | Note |
| | Run notebook end-to-end, verify outputs, fix any errors | Not Started |
| | Review generated images and data outputs for quality | Not Started |
| | Blog post creation | Not Started |
| | Hex integration for website | Not Started |

---

## 9. Future Data Recommendations

If ExtraaLearn can expand their data collection, the following would strengthen the model:

1. **IP address / Zip code geolocation:** Capturing a lead's region would allow enrichment with Census tract median household income data. This provides a direct measure of purchasing power rather than relying on `current_occupation` as a rough proxy for ability to pay. The hypothesis is that Professionals convert at higher rates partly because they (or their employers) can fund the program — income data would let the model test that directly.

2. **Employer-sponsored education flag:** A simple yes/no field for whether the lead has employer tuition reimbursement or education stipends would isolate financial friction as a conversion driver.

3. **Lead source granularity:** The current marketing flags (print, digital, educational, referral) are binary. Capturing the specific platform (e.g., LinkedIn ad vs. Google search vs. YouTube) would enable finer-grained channel optimization.

4. **Session-level engagement data:** The current data aggregates website behavior into totals. Session-level data (time per visit, pages per session, recency of last visit) would capture engagement trends over time.

5. **Page-level visit data:** We know leads view ~3 pages on average, but not *which* pages. Tracking specific pages visited (pricing, curriculum, testimonials, checkout, FAQ, etc.) would reveal intent signals — a lead who views 3 pages including the pricing page is much higher intent than one browsing 3 blog posts. This would also explain the 10–18 page outliers: are they doing deep program research or stuck in a confusing navigation flow?

6. **Profile field-level completion data:** We know whether a lead's profile is Low/Medium/High but not how many total fields the profile has, which specific fields were filled vs. skipped, or how long the form takes to complete. If the profile has 20+ fields, the form itself may be a friction point discouraging completion. Knowing which fields get abandoned most often would inform UX improvements (shorter forms, progressive profiling, removing low-value fields).

7. **Profile field content:** Beyond which fields were filled, the actual content matters — a lead who enters a work email (company domain) vs. a personal Gmail signals different intent levels. Job title, company size, and education background fields would enrich the demographic picture beyond the three occupation buckets we currently have.

8. **Phone call outcome data:** Phone Activity has the lowest conversion rate (21.3%), but we don't know why. Tracking call duration, call disposition (interested/not interested/callback requested), and number of call attempts would help identify which leads actually benefit from a phone call vs. those who convert better through self-service website/email channels. A future project could build a model specifically to predict which leads should receive a call vs. be nurtured digitally — optimizing sales team time by routing leads to the channel where they're most likely to convert.

9. **Device/platform journey tracking:** Q2 showed Website first interaction converts at 4.3x the rate of Mobile App. Tracking the full device journey (e.g., first discovered on mobile app, later converted via website) would reveal whether mobile is a discovery channel that feeds website conversions, rather than a dead end.

11. **Profile completion as checkout requirement:** 8 out of 107 Low-profile leads still converted (7.5%), meaning it's possible to become a paid customer without completing the online profile — likely through phone sales or direct payment links. ExtraaLearn should investigate whether profile completion is required before checkout or just encouraged. If optional, making a streamlined version mandatory before payment could both improve data quality and act as a natural intent filter — ensuring the sales team only engages leads who have demonstrated enough commitment to fill out basic information.

12. **Educational channel content audit:** Educational channels showed a -2.3pp conversion lift — the only negative channel. A future study should identify which specific forums, discussion threads, and educational websites are driving this traffic, and what content or sentiment about ExtraaLearn exists on those platforms. Possible explanations include: leads are comparison-shopping across competitors, negative reviews or pricing complaints are discouraging conversion, or the audience on these channels has different expectations (e.g., expecting free content rather than paid programs). Understanding the root cause would inform whether to improve ExtraaLearn's presence on these channels or reallocate spend elsewhere.

---

## 10. Resumption Instructions

If opening a new Cowork session, provide this context:
1. Read this file: `ds_blogs/projects/potential_customers_prediction/context.md`
2. The notebook is in: `notebooks/Learner Notebook - Full Code Version - Potential Customers Prediction.ipynb`
3. The data is in: `data/inputs/ExtraaLearn.csv`
4. Check the Progress Log (Section 8) for current status
5. Check rubric checklists (Section 4) for what's been completed
