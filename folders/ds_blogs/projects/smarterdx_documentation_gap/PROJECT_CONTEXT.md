# PROJECT_CONTEXT.md — The Documentation Gap: Hospital Revenue & Clinical AI

**Last Updated:** 2026-04-01
**Project Path:** `bitterscientist.com/folders/ds_blogs/projects/smarterdx_documentation_gap/`
**Blog Output Path:** `bitterscientist.com/folders/ds_blogs/ds_documentation_gap.html`
**Purpose:** Portfolio blog post + interview discussion piece for SmarterDx Senior Product Analyst interview (April 2, 2026, with Daniel Kreitzberg)

---

## What This Project Is

A data analysis pipeline that uses publicly available CMS data to quantify how much revenue U.S. hospitals may be losing due to clinical documentation gaps — the exact problem that SmarterDx's AI platform is built to solve. The analysis examines hospital-level Case Mix Index (CMI) variation, DRG severity tier distributions, claim denial patterns, and quality score relationships to estimate the scope of the documentation accuracy problem across ~3,400 Medicare-participating hospitals.

This project mirrors the structure of the Octave Behavioral Health Expansion blog (`octave_behavioral_health_expansion/`): a multi-notebook pipeline producing a tabbed HTML blog post with interactive charts.

**Key difference from Octave project:** The blog HTML file should be placed in the ds_blogs ROOT folder as `ds_documentation_gap.html`, NOT inside the project folder. This follows the `ds_` naming convention used by all other blog posts on bitterscientist.com. The project folder holds notebooks, data, and context only.

---

## SmarterDx — Key Facts

- **What they do:** Clinical AI platform that reviews 100% of hospital patient charts to identify missed and incorrect diagnoses, improving both revenue capture and quality scores
- **Core product:** Retrospective chart review — AI scans completed charts, flags missing diagnoses (especially CC/MCC codes that shift DRG severity tiers and increase payment)
- **New product (Sept 2025):** SmarterNotes — concurrent/real-time documentation AI (acquired Pieces Technologies), helps doctors document correctly during the patient stay
- **Performance:** 99.4% micro-AUROC on ICD-10 coding (25% fewer errors than prior best), understands 10,000+ diagnoses/procedures
- **Revenue impact:** ~$2M net new revenue per 10,000 patient discharges for customers
- **Scale:** 50+ health systems, 200+ hospitals, 12M+ cases analyzed
- **Parent company:** Smarter Technologies (May 2025) — umbrella with Access Healthcare + Thoughtful.ai, $800M+ combined revenue, 500K+ providers, backed by New Mountain Capital
- **Funding:** $50M Series B (Nov 2023), $130M+ total
- **Team:** ~150 people, growing 250% YoY
- **Tech stack (from job posting):** SQL, dbt, Python, Hex, Omni/Evidence for visualization, Snowflake, Airflow

## Competitors

| Competitor | Focus | Model | Notable |
|---|---|---|---|
| AKASA | RCM automation (prior auth, coding, claims) | Generative AI agents | Broader RCM, less CDI-specific |
| Fathom | Medical coding automation | NLP/deep learning | 90%+ coding automation, coding focus not CDI |
| AGS Health | Full RCM services + AI | 11,000+ employees, outsourced + AI | Services-heavy, 100+ clients |
| CognitiveHealth | AI-driven RCM | Clinical AI | Smaller, competes with R1 RCM, Xifin |
| Iodine Software | Mid-revenue cycle CDI | NLP for concurrent CDI | Direct CDI competitor, acquired by Waystar |
| 3M/Solventum | Coding + CDI + grouper software | Legacy + AI add-ons | Incumbent, owns the MS-DRG grouper |

**SmarterDx differentiators:** Reviews 100% of charts (not sampling), AI-native (not rules-based), retrospective + concurrent (SmarterNotes), outcome data creates payer contracting leverage.

---

## The Domain: Clinical Documentation Improvement (CDI)

### How Hospital Revenue Works (DRG System)
1. Patient is admitted, receives care, clinicians document in the EHR
2. After discharge, medical coders translate documentation into ICD-10 diagnosis/procedure codes
3. ICD-10 codes are grouped into a **MS-DRG** (Medicare Severity Diagnosis Related Group) — one of ~750 categories
4. Each MS-DRG has a **relative weight** reflecting resource intensity
5. Medicare pays: `base_rate × DRG_weight × hospital_adjustments`
6. A hospital's **Case Mix Index (CMI)** = average DRG weight across all discharges — higher CMI = sicker patients = more revenue per discharge

### Why Documentation Accuracy Matters
- Many DRGs have 3 severity tiers: **without CC**, **with CC** (complication/comorbidity), **with MCC** (major CC)
- Moving from "without CC" to "with MCC" can increase payment by $5,000-$15,000+ per case
- If a clinician treats a condition but doesn't document it explicitly, the code is missed, and the hospital gets paid less
- This is NOT fraud — it's capturing care that was actually delivered but poorly documented
- **This is exactly what SmarterDx fixes:** their AI reads the full chart, finds clinical evidence of conditions the coder missed, and flags them

### Claim Denials
- Initial claim denial rates hit 11.8% in 2024 (up from ~10.2%)
- Medicare Advantage denies 17% of initial claims
- Many denials stem from insufficient clinical documentation to support the billed DRG
- SmarterDx reduces denials by ensuring documentation supports the assigned codes before the claim is submitted

### Quality Scores
- CMS Star Ratings, Patient Safety Indicators (PSIs), and risk-adjusted outcomes all depend on accurate ICD-10 coding
- Under-documentation makes a hospital look healthier than its patients actually are, which hurts risk-adjusted quality scores
- Better documentation → more accurate severity → better risk-adjusted outcomes → higher quality scores

---

## Pipeline Architecture

### Stage 1 — Data Collection (NB01-NB03)

| Notebook | What It Does | Data Source | Output |
|---|---|---|---|
| NB01 | Hospital characteristics: bed size, teaching status, ownership (for-profit/nonprofit/government), urban/rural, state, region | CMS Provider of Services file + AHA data via CMS | `hospital_characteristics.csv` |
| NB02 | Hospital-level DRG data: Case Mix Index, discharge counts, DRG weights, severity tier distribution (% without CC, with CC, with MCC) | CMS IPPS Impact File + Case Mix Index File (FY 2025) | `hospital_drg_data.csv` |
| NB03 | Hospital-level charges and payments by DRG: what hospitals charge vs. what Medicare pays, charge-to-payment ratios | CMS Medicare Provider Utilization & Payment Data (Inpatient PUF) | `hospital_payment_data.csv` |

### Stage 2 — Hospital Analysis (NB04-NB06)

| Notebook | What It Does | Data Source | Output |
|---|---|---|---|
| NB04 | Claim denial analysis: denial rates by payer type, denial reasons, appeal overturn rates | KFF Marketplace Denial Data + CMS MA Star Ratings (denial metrics) + OIG audit reports | `denial_analysis.csv` |
| NB05 | Quality score analysis: CMS Star Ratings, Patient Safety Indicators, relationship between CMI accuracy and quality outcomes | CMS Care Compare / Hospital Compare | `quality_scores.csv` |
| NB06 | CDI market landscape: competitor profiles, market size estimates, hospital CDI adoption rates | Public sources (press releases, SEC filings, industry reports) | `cdi_market.csv` |

### Stage 3 — Gap Modeling (NB07-NB08)

| Notebook | What It Does | Output |
|---|---|---|
| NB07 | Documentation gap scoring: peer-group CMI benchmarking (compare each hospital's CMI to similar hospitals by bed size + teaching + ownership), identify outliers, estimate under-documentation severity | `hospital_documentation_scores.csv` |
| NB08 | Revenue impact modeling: estimate revenue at stake per hospital using DRG severity shift analysis (what if X% of "without CC" cases should be "with CC"?), aggregate to national/state/hospital-type level | `revenue_gap_estimates.csv` |

### Stage 4 — Visualizations (NB09)

| Notebook | What It Does | Output |
|---|---|---|
| NB09 | All blog charts: CMI distribution maps, DRG severity breakdowns, denial trend charts, quality correlation plots, revenue gap estimates, peer comparison dashboards | `data/outputs/blog_charts/*.html` |

---

## Key Technical Details

### Data Sources & Access

| Source | URL | Format | Auth Required | Notes |
|---|---|---|---|---|
| CMS IPPS Impact File | [CMS Acute Inpatient Files](https://www.cms.gov/medicare/payment/prospective-payment-systems/acute-inpatient-pps/acute-inpatient-files-download) | CSV/Excel | No | Hospital-level CMI, DRG weights, wage index |
| CMS Case Mix Index File | Same page as above | CSV | No | Non-transfer-adjusted CMI by hospital CCN |
| CMS Inpatient PUF | [Data.CMS.gov](https://data.cms.gov/provider-summary-by-type-of-service) | CSV | No | Charges and payments by hospital × DRG |
| CMS Provider of Services | [Data.CMS.gov](https://data.cms.gov) | CSV | No | Hospital characteristics (beds, teaching, ownership) |
| CMS Care Compare | [Medicare.gov Care Compare](https://www.medicare.gov/care-compare/) | CSV downloads | No | Star ratings, PSIs, readmission rates |
| KFF Denial Data | [KFF Claims Denials](https://www.kff.org/private-insurance/issue-brief/claims-denials-and-appeals-in-aca-marketplace-plans-in-2023/) | Tables/CSV | No | Marketplace denial rates by insurer |
| MS-DRG Definitions | [CMS MS-DRG Classifications](https://www.cms.gov/medicare/payment/prospective-payment-systems/acute-inpatient-pps/ms-drg-classifications-and-software) | Excel | No | DRG weights, CC/MCC lists, severity tiers |

### Key Calculations

**Case Mix Index:**
```
CMI = sum(DRG_weight_i × discharges_i) / total_discharges
```

**Peer-Group CMI Benchmark:**
```
expected_CMI = median CMI of hospitals with same (bed_size_bucket × teaching_status × ownership_type)
CMI_gap = actual_CMI - expected_CMI
# Negative gap = potential under-documentation
```

**Revenue Impact Estimate (per hospital):**
```
severity_shift_rate = estimated % of "without CC" cases that should be "with CC" or "with MCC"
avg_payment_uplift = avg difference in DRG weight between severity tiers × base_rate
revenue_gap = discharges × severity_shift_rate × avg_payment_uplift
```
SmarterDx benchmark: ~$2M per 10,000 discharges → implies ~3-5% severity shift rate

**DRG Severity Distribution:**
```
pct_without_cc = discharges in base DRG / total discharges in DRG family
pct_with_cc = discharges in CC tier / total
pct_with_mcc = discharges in MCC tier / total
# Compare distribution across peer groups — hospitals with unusually high % "without CC" may be under-documenting
```

### Python Libraries Needed
- `pandas`, `numpy` — data manipulation
- `plotly` — interactive charts (same as Octave project)
- `scipy.stats` — statistical tests for peer comparisons
- `requests` — CMS data downloads
- `openpyxl` — reading CMS Excel files

---

## Blog Structure (Target: 4-5 Tabs)

### Tab 0: Executive Summary
- Driving question, key findings, revenue gap estimate, industry context
- 2-3 headline charts

### Tab 1: Background
- How the DRG system works (with visual)
- What CDI is and why it matters
- The clinical AI landscape (SmarterDx, competitors)
- The claim denial problem

### Tab 2: Methods
- Data sources table
- Scoring methodology (peer-group benchmarking)
- Normalization approach
- Limitations and caveats

### Tab 3: Results
- CMI distribution across hospitals
- DRG severity tier analysis
- Peer-group outlier identification
- Revenue gap estimates (national, by state, by hospital type)
- Quality score correlations

### Tab 4: Implications
- What this means for CDI platforms
- Which hospital segments are most affected
- Connection to SmarterDx's value proposition (without being a sales pitch)

---

## Naming Convention

- **Project folder:** `smarterdx_documentation_gap/`
- **Blog HTML (in ds_blogs root):** `ds_documentation_gap.html`
- **Chart files:** `data/outputs/blog_charts/chart_*.html`
- **Notebook outputs:** `data/outputs/nb0X_*/`

---

## Interview Context

- **Interview date:** April 2, 2026
- **Interviewer:** Daniel Kreitzberg (hiring manager)
- **Role:** Senior Product Analyst at SmarterDx
- **Round:** Second round (hiring manager)
- **First round was with:** Savannah Sprenzel (phone screen)
- **What to demonstrate:** Domain knowledge of DRGs/CMI/CDI, product analytics thinking, data pipeline skills, experiment design capability
- **Related prep materials:** `job_posting_resume_optimizer/data/outputs/nb19_resumes/interview_prep/` (STAR cheat sheet, study guides)
