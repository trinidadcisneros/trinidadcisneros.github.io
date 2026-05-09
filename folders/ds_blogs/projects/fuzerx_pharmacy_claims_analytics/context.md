# FuzeRx Pharmacy Claims Analytics — Project Context

**Last Updated:** 2026-05-01
**Status:** Proposal drafted. Awaiting approval to scaffold NB01.

---

## 1. Project Overview

**Project Name:** fuzerx_pharmacy_claims_analytics
**Location:** `folders/ds_blogs/projects/fuzerx_pharmacy_claims_analytics/`
**Primary Purpose:** Interview preparation for the second round (pharmacy claims review team) of the **Staff Product Analyst, Care — FuzeRx** role at Fuze Health (req R200617, applied 2026-04-13 via LinkedIn / Workday).
**Secondary Purpose:** Public data story published to bitterscientist.com under `folders/ds_blogs/`, modeled on the same case study framework used in `product_analytics_interview_prep/product_analytics_case_study.html`.

### What the project does
Simulates a realistic pharmacy claim level dataset and walks through the full operational analytics workflow a Staff Product Analyst on the FuzeRx Care team would actually run: adjudication funnel, reject reason taxonomy, segment performance, A/B test of an automated recycling workflow, time to fill survival analysis, margin and revenue impact model, and an executive recommendation synthesis with supply chain implications.

### Why this project
- The JD's first listed responsibility is in depth analysis on prescription processing and patient care to drive operational decisions. A pharmacy claim adjudication and recycling project is the most direct demonstration possible of that work.
- The recruiter screen prep flagged pharmacy claims as the strongest natural fit lane (5 yrs at GoodRx on drug pricing, formulary coverage, vendor pipeline ETL across 18,000+ products and 10+ vendors). This project extends that lane from upstream pricing into downstream adjudication and fulfillment.
- Several JD assets currently flagged as portfolio only or adjacent (A/B testing, supply chain optimization, marketplace style data) are demonstrated end to end inside this project.

---

## 2. Alignment to the Job Posting

### Mapped responsibilities

| JD Responsibility | How this project demonstrates it |
|---|---|
| In depth analysis on prescription processing and patient care to drive operational decisions | NB01 to NB04 build the claim flow, isolate where rejections happen, and quantify operational and patient impact (delay to therapy, abandonment, manual touch volume). |
| Design and build data models that elevate data driven decisioning | NB01 builds a claim level fact table with dimensional keys (drug class, payer, channel, geography, prescriber). NB07 packages a margin and revenue impact model that finance and operations can use directly. |
| Design, implement, and launch dashboards using SQL to measure product success | The notebooks export a tidy set of result tables (`data/outputs/nbXX_*.csv`) sized and shaped to drop into a Looker explore or Power BI semantic model. NB08 includes a sketch of the dashboard view. |
| Critical thought partner across Finance, Product, Engineering, Growth, Operations | NB07 and NB08 frame findings for each function: revenue lift (Finance), prioritized product investments (Product), workflow automation candidates (Engineering / Operations), patient experience signals (Growth / Care). |
| Contribute to defining team and company data culture | Project follows the same documentation and notebook conventions as `product_analytics_interview_prep` and `potential_customers_prediction` — auditable, reproducible, and reusable. |

### Mapped qualifications

| JD Qualification | How the project demonstrates it |
|---|---|
| Advanced SQL, ETL design, large dataset extraction | NB01 generates a claim level fact table and a transactional event log (submitted, rejected, recycled, paid, reversed, dispensed, delivered). All downstream notebooks use SQL style joins and aggregations in pandas, with parallel SQL snippets in markdown for the blog post audience. |
| Looker, Tableau, or similar BI tool comfort | NB08 publishes a dashboard sketch with the metrics, segments, and filters a real Looker explore would expose. |
| Strong written and verbal communication for non technical audience | Each notebook closes with an executive summary written in plain language. NB08 includes the speaking outline for the interview. |
| Bias toward actionable insights | Every notebook ends with a recommendation block: what to do, who owns it, what it is worth. |
| Healthcare or pharmaceutical industry (preferred) | Entire domain is pharmacy claim adjudication. |
| Supply chain optimization, marketplaces, logistics (preferred) | NB07 extends the analysis into supply chain implications: substitution to covered alternatives, inventory and fill rate effects, NADAC vs paid spread. |
| Python (preferred) | All notebooks are Python (pandas, numpy, scipy, statsmodels, lifelines, matplotlib, seaborn). |

### Honest scope notes
- This project does **not** demonstrate live experimentation with real patients or production claim systems. It is a simulation grounded in publicly known reject code patterns and CMS Part D drug mix data.
- The dataset is synthetic by design. No PHI, no real claim data. Honest framing in the interview: *"I built this to give myself a credible sandbox to demonstrate the methods. I would expect the real first task at FuzeRx to be inheriting and validating Alto's claim and event tables, not building from scratch."*

---

## 3. Business Hypothesis

**Premise.** At a digital pharmacy like FuzeRx, every prescription submitted to a PBM goes through real time adjudication. A meaningful share of submitted claims reject on first pass for reasons that are recyclable: prior authorization needed, formulary substitution available, coordination of benefits stale, days supply or quantity edits, refill too soon, NDC not covered. Each rejection costs three things: pharmacy team manual touch time, patient delay (and risk of abandonment), and revenue (when claims never recycle to paid).

**Project hypothesis.** A modest 2 to 5 percentage point improvement in first pass acceptance rate, driven by automated recycling on the most common recoverable reject codes (and proactive formulary substitution suggestions), produces a quantifiable lift in revenue per script, reduction in time to fill, and reduction in script abandonment — without breaching guardrails on patient safety, prescriber relationships, or substitution appropriateness.

**Why a Staff Analyst should care.** First pass rate is one of the few pharmacy operational KPIs that ties Finance (revenue per script, write offs), Product (workflow automation), Operations (manual touch time per FTE), and Care (patient experience and adherence) into a single number. Owning that number is owning the cross functional thought partnership the JD describes.

---

## 4. Folder Structure

```
fuzerx_pharmacy_claims_analytics/
├── context.md                                    ← this file
├── data/
│   ├── raw/                                      ← generated synthetic datasets
│   │   ├── claims_dataset.csv                    ← claim level fact table
│   │   ├── claim_events_dataset.csv              ← event log (submit, reject, recycle, pay, reverse)
│   │   ├── drug_mix_reference.csv                ← drug class anchors (CMS Part D Spending grounding)
│   │   ├── reject_code_taxonomy.csv              ← realistic NCPDP style reject codes + recyclability flag
│   │   └── ab_test_dataset.csv                   ← simulated A/B test of automated recycling workflow
│   ├── inputs/                                   ← cleaned data (output of NB01)
│   └── outputs/
│       ├── nb01/                                 ← EDA outputs
│       ├── nb02/                                 ← Adjudication funnel outputs
│       ├── nb03/                                 ← Reject taxonomy and pareto outputs
│       ├── nb04/                                 ← Segment performance outputs
│       ├── nb05/                                 ← A/B test outputs
│       ├── nb06/                                 ← Survival / time to fill outputs
│       ├── nb07/                                 ← Margin and revenue model outputs
│       └── nb08/                                 ← Synthesis and dashboard sketch outputs
├── notebooks/
│   ├── nb01_data_generation_and_eda.ipynb
│   ├── nb02_adjudication_funnel.ipynb
│   ├── nb03_reject_reason_taxonomy.ipynb
│   ├── nb04_segment_performance.ipynb
│   ├── nb05_ab_test_recycling_workflow.ipynb
│   ├── nb06_time_to_fill_survival.ipynb
│   ├── nb07_margin_revenue_supply_chain_model.ipynb
│   └── nb08_synthesis_recommendations_speaking_outline.ipynb
└── static/
    └── images/                                   ← exported chart PNGs for the blog post
```

---

## 5. Notebook Pipeline

| Notebook | Purpose | Methods | Framework Phase | Outputs |
|---|---|---|---|---|
| NB01 | Data generation and EDA | Synthetic claim and event generation, drug mix anchored to CMS Part D Spending, EDA, data quality checks | Foundation | claim fact table, event log, reject taxonomy reference |
| NB02 | Adjudication funnel | Sequential funnel (submit → adjudicate → accept / reject → recycle → pay → reverse → dispense → deliver), step conversion, drop off attribution | Validation / Rollout | funnel CSVs, funnel charts |
| NB03 | Reject reason taxonomy | Pareto by reject code, recyclability classification, repeat reject pattern analysis | Validation | top reject reasons CSV, recyclability matrix |
| NB04 | Segment performance | Segmented funnel by drug class, payer, channel, geography, prescriber tenure | Validation / Rollout | per segment performance CSVs |
| NB05 | A/B test of automated recycling workflow | Z-test, chi square, sample size and power, sequential testing, guardrails | Rollout | test result CSV, decision write up |
| NB06 | Time to fill survival analysis | Kaplan Meier, log rank, hazard interpretation, abandonment as competing risk | Rollout / Scale | survival curves, abandonment hazard tables |
| NB07 | Margin, revenue, and supply chain model | Per script revenue impact model, NADAC vs paid spread, formulary substitution impact, inventory and fill rate implications | Scale | financial impact CSV, supply chain implications memo |
| NB08 | Synthesis, recommendations, and interview speaking outline | Executive summary, dashboard sketch, prioritization matrix, speaking outline for the second round interview | All | synthesis deck, dashboard mock, speaking outline |

### Sequencing rule
Per Trinidad's request, **one notebook at a time**. Each notebook gets discussed before scaffolding the next. This mirrors the cadence used in `product_analytics_interview_prep`.

---

## 6. Key Metrics

### Operational
- **First pass acceptance rate** = paid on first submit / total submitted
- **Recycling success rate** = paid after recycle / rejected and recyclable
- **Manual touch volume per 1,000 scripts** = manual interventions / scripts × 1,000
- **Median time to fill** = dispense timestamp − submit timestamp
- **Script abandonment rate** = scripts never dispensed within N days / total submitted

### Financial
- **Revenue per dispensed script** = paid amount per script
- **Margin per dispensed script** = paid − ingredient cost − dispensing cost
- **Write off rate** = scripts permanently rejected / total submitted
- **Lift from first pass improvement** = (Δ first pass rate) × scripts × revenue per script

### Patient experience
- **Median delay to therapy after rejection** = (dispense − submit) for rejected then recycled scripts
- **Refill rate at 30 days** = 30 day refill scripts / first fill scripts (proxy for adherence funnel)

### Guardrail
- **Substitution appropriateness rate** = clinically appropriate substitutions / all suggested substitutions
- **Prescriber callback rate** = scripts requiring a prescriber phone call / total recycled
- **Patient complaint rate** = complaints / 1,000 dispensed scripts

---

## 7. Methods Covered (Mapped to Interview Talking Points)

- **Funnel analysis** (NB02) — directly relevant to *prescription processing* responsibility.
- **Pareto analysis and reason code segmentation** (NB03) — operational analytics 101 for any claims team.
- **Cohort and segment performance analysis** (NB04) — supports product strategy by drug class and payer mix.
- **A/B testing end to end** (NB05) — moves A/B testing from *portfolio only* to *demonstrated*. Includes sample size, sequential testing, guardrails, and decision framework.
- **Survival analysis** (NB06) — Kaplan Meier on time to fill given rejection, log rank to compare workflows. Pulls from your lifelines experience.
- **Financial impact modeling** (NB07) — translates analytics findings into dollars and supply chain implications.
- **Synthesis and storytelling** (NB08) — the cross functional thought partnership the JD calls out.

---

## 8. Data Sources and Generation Approach

### Public anchors
- **CMS Medicare Part D Spending Dashboard** — used to anchor the drug mix (top 100 drug classes by claim volume, generic vs brand split, average payment per claim).
- **NADAC (National Average Drug Acquisition Cost)** — used to anchor ingredient cost assumptions for margin modeling.
- **NCPDP reject code patterns** — publicly documented categories (e.g., 70 NDC not covered, 75 prior authorization required, 76 plan limitations exceeded, 79 refill too soon, 88 DUR reject). The project models a realistic but custom taxonomy mapped to recyclability.

### Synthetic generation
- 250,000 claims across 12 weeks of activity, ~20,000 to 25,000 unique patients, ~30 drug classes
- Realistic reject rate distribution (target ~12 to 18% first pass rejection, in line with industry reporting)
- Embedded patterns: certain payers reject more on PA, certain drug classes reject more on formulary, refill too soon clusters in early cycle weeks, and a treatment cohort sees automated recycling improve outcomes by an embedded effect size

### No PHI
The dataset is synthetic by design. All patient and prescriber IDs are randomly generated. The project explicitly notes this in the blog post.

---

## 9. Deliverables

1. **Eight Jupyter notebooks** under `notebooks/` (built one at a time per Trinidad).
2. **Tidy result CSVs** under `data/outputs/nbXX/` ready to drop into a BI tool.
3. **Static chart PNGs** under `static/images/` for the blog post.
4. **One blog post HTML** under `folders/ds_blogs/` titled along the lines of `ds_pharmacy_claims_recycling_analytics.html`, modeled on `product_analytics_case_study.html`. Will follow the Discovery → Validation → Build → Rollout → Scale phase tabs from the playbook framework.
5. **Speaking outline** inside NB08 (markdown cells) using the 🎙 / 💪 / 🧠 framework from `playbook_product_analytics_framework.html`, ready for the second round interview.

---

## 10. Risks and Mitigation

| Risk | Mitigation |
|---|---|
| Synthetic data feels too clean and the interview team sees through it | Embed realistic noise, mixed data quality, late arriving events, partial reversals, and ambiguous reject codes. Be transparent in the blog post and in the interview that the data is simulated and explain the choices. |
| NCPDP reject code modeling is technically incorrect | Use the public categories (PA, formulary, days supply, refill too soon, DUR, COB) without claiming exact NCPDP standard fidelity. Frame as *realistic taxonomy*, not literal NCPDP. |
| Project feels too academic for an operational team | Each notebook ends with a recommendation block written for the team that owns the workflow. NB07 and NB08 explicitly translate findings to dollars, FTE hours, and patient outcomes. |
| Scope creep across 8 notebooks | One notebook at a time, with explicit success criteria checked off in this context.md before moving on. |

---

## 11. Progress Log

| Date | Activity | Status |
|---|---|---|
| 2026-05-01 | Project proposal drafted, folder scaffolded, context.md written | Done |
| | NB01 data generation and EDA — to scaffold next | Pending Trinidad approval |

---

## 12. Resumption Instructions

If opening a new Cowork session:
1. Read this file: `folders/ds_blogs/projects/fuzerx_pharmacy_claims_analytics/context.md`
2. Cross reference the JD: `folders/ds_blogs/projects/job_posting_resume_optimizer/data/inputs/job_postings/analyst_txt/fuze_health_staff_product_analyst_care.txt`
3. Cross reference the recruiter prep: `folders/ds_blogs/projects/job_posting_resume_optimizer/data/outputs/nb19_resumes/interview_prep/fuze_health_recruiter_questions.html`
4. Mirror the structural conventions of `folders/ds_blogs/projects/product_analytics_interview_prep/`
5. Check the Progress Log (Section 11) for current status
