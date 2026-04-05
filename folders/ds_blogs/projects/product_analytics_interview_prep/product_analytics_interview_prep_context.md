# Product Analytics Interview Prep — Project Context

## Purpose
Educational project to build hands-on product analytics experience in preparation for a case study interview at **SmarterDx** (Senior Product Analyst role). The interview is a 60-minute product case study with Barry Leybovich (Staff PM, New Markets) and Teigen Judd (Senior Data Analyst), where they will present a product idea and discuss what analytics you would provide to support development and rollout.

## Interview Date
April 9, 2026, 11:00am–12:00pm PDT

## Framework
This project applies the **Discovery → Validation → Build → Rollout → Scale** product analytics lifecycle from `playbook_product_analytics_framework.html`. The datasets map to three phases: Validation (NB02 metrics definition), Rollout (NB02 funnels, NB03 A/B testing, NB03b quasi-experimental methods), and Scale (NB04 cohorts, NB05 retention). NB07 adds the Model Performance and Outcome/Impact metric layers that are critical for AI products like SmarterDx.

## Project Structure

```
product_analytics_interview_prep/
├── product_analytics_interview_prep_context.md   ← this file
├── data/
│   ├── raw/                    ← original generated datasets
│   │   ├── user_funnels_dataset.csv
│   │   ├── ab_testing_dataset.csv
│   │   └── user_activity_dataset.csv
│   ├── inputs/                 ← cleaned data (output of NB01)
│   │   ├── funnel_clean.csv
│   │   ├── ab_clean.csv
│   │   ├── activity_clean.csv
│   │   └── model_performance_clean.csv
│   └── outputs/
│       ├── nb01/               ← EDA outputs
│       ├── nb02/               ← Funnel analysis outputs
│       ├── nb03/               ← A/B testing outputs
│       ├── nb03b/              ← Quasi-experimental outputs
│       ├── nb04/               ← Cohort analysis outputs
│       ├── nb05/               ← Retention analysis outputs
│       ├── nb06/               ← Synthesis outputs
│       └── nb07/               ← Model performance outputs
└── notebooks/
    ├── nb01_data_loading_cleaning_eda.ipynb
    ├── nb02_adoption_funnel_analysis.ipynb
    ├── nb03_ab_testing_methods.ipynb
    ├── nb03b_quasi_experimental_methods.ipynb
    ├── nb04_cohort_analysis.ipynb
    ├── nb05_retention_analysis.ipynb
    ├── nb06_synthesis_product_recommendations.ipynb
    └── nb07_model_performance_outcome_impact.ipynb
```

## Notebook Pipeline

| Notebook | Purpose | Methods Covered | Framework Phase |
|----------|---------|-----------------|-----------------|
| NB01 | Data loading, cleaning, EDA | Data quality checks, distributions | Foundation |
| NB02 | Adoption funnel analysis | Classic funnel, segmented funnel, time-to-convert, weighted scoring | Rollout |
| NB03 | A/B testing | Z-test, chi-square, Bayesian, bootstrap, sequential testing | Rollout |
| NB04 | Cohort analysis | Time-based, behavioral, segment-based, LTV | Scale |
| NB05 | Retention analysis | N-week retention, rolling retention, Kaplan-Meier survival, curve fitting, churn scoring | Scale |
| NB06 | Synthesis & recommendations | Executive dashboard, impact-effort matrix, North Star metrics tree, SmarterDx mapping | All |
| NB03b | Quasi-experimental methods | Difference-in-differences, regression discontinuity, sample size/power analysis | Rollout |
| NB07 | Model performance & outcome impact | Precision, recall, calibration, AI suggestion funnel, acceptance rates, outcome value, 2x2 outcome matrix | Rollout, Scale |

## Datasets

All datasets are synthetic, generated to mimic realistic product analytics patterns. The first three are independent; the fourth links to the activity dataset users.

1. **user_funnels_dataset.csv** (5,000 users) — e-commerce funnel: landing_page → signup → product_view → add_to_cart → purchase. Includes device and channel segmentation.
2. **ab_testing_dataset.csv** (4,000 users) — controlled experiment with ~3% treatment lift in conversion. Includes pages viewed, time on site, and revenue.
3. **user_activity_dataset.csv** (3,000 users) — 12 weekly signup cohorts with natural retention decay. Includes event types, session duration, and plan type.
4. **ai_model_performance_dataset.csv** (10,150 interactions, same 3,000 users) — AI model suggestions with confidence scores, user acceptance decisions, ground truth correctness, outcome values, and suggestion categories. Model quality improves across cohorts (W01-W12).

## Metric Category Coverage

| Metric Category | Covered? | Where |
|---|---|---|
| Acquisition | Yes | NB02 (funnel stages, channel attribution) |
| Activation | Yes | NB02 (time-to-convert, signup rates) |
| Engagement | Yes | NB04 (session frequency, behavioral cohorts), NB07 (AI feature engagement) |
| Retention | Yes | NB04, NB05 (5 methods including survival analysis) |
| Revenue | Partial | NB03 (revenue per user in A/B test), NB04 (LTV proxy) |
| Outcome / Impact | Yes | NB07 (outcome value analysis, net impact, 2x2 outcome matrix) |
| Model Performance | Yes | NB07 (precision, recall, calibration, performance over time) |
| Guardrails | Conceptual | Markdown callouts in NB02, NB03, NB03b, NB05, NB06; measurable guardrail checks in NB07 |

## Output Naming Convention
All output files follow: `nbXX_<descriptive_name>.<ext>` (e.g., `nb02_classic_funnel.csv`, `nb03_bayesian_posteriors.png`)

## Dependencies
pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, lifelines, statsmodels

## SmarterDx Connection
- Funnel analysis → hospital onboarding pipeline (demo → pilot → go-live → expansion)
- A/B testing → comparing AI model versions or CDI workflow changes
- Quasi-experimental (DiD) → staggered hospital rollouts where randomization isn't possible
- Cohort analysis → hospitals grouped by go-live date
- Retention → continued chart review adoption, license renewals
- Model performance → AI suggestion precision, recall, confidence calibration
- Outcome impact → net diagnoses captured, false positive costs
- North Star → net correct suggestions accepted per user per month
