# NEXT_SESSION_PROMPT.md — The Documentation Gap

**Last Updated:** 2026-04-01

---

## Before You Start

Read these files first:
1. `PROJECT_CONTEXT.md` (this project folder) — full pipeline plan, data sources, technical details, domain background
2. The Octave project for structural reference: `octave_behavioral_health_expansion/PROJECT_CONTEXT.md`

---

## Current State

**The project has been scoped but NO notebooks have been written yet.** The folder structure is created, context files are written, and data sources have been identified. Trinidad will run all notebooks herself to learn the domain.

### What Exists
- `PROJECT_CONTEXT.md` — complete project plan with 9 notebooks, data sources, key calculations, blog structure
- `PROJECT_ABSTRACT.md` — methodology overview
- Folder structure: `notebooks/{1_data_collection, 2_hospital_analysis, 3_gap_modeling, 4_visualizations}` and `data/{raw, inputs, outputs}`
- No notebooks, no data files, no blog HTML yet

### What Needs To Be Built (In Order)

**Phase 1: Data Collection (NB01-NB03)**
1. NB01 — Download CMS Provider of Services file, extract hospital characteristics (beds, teaching, ownership, urban/rural, state)
2. NB02 — Download CMS IPPS Impact File + Case Mix Index File, extract hospital-level CMI, DRG weights, severity tier distributions
3. NB03 — Download CMS Inpatient PUF, extract hospital-level charges and payments by DRG

**Phase 2: Hospital Analysis (NB04-NB06)**
4. NB04 — Claim denial analysis using KFF data + CMS MA metrics
5. NB05 — Quality score analysis using CMS Care Compare data
6. NB06 — CDI market landscape (competitor research, market sizing)

**Phase 3: Gap Modeling (NB07-NB08)**
7. NB07 — Peer-group CMI benchmarking and documentation gap scoring
8. NB08 — Revenue impact modeling (severity shift analysis)

**Phase 4: Visualizations (NB09)**
9. NB09 — All blog charts (interactive Plotly, same approach as Octave)

**Phase 5: Blog Post**
10. Create `ds_documentation_gap.html` in `folders/ds_blogs/` (NOT in project folder)
11. Register on homepage (`static/data/posts.json`) and category page (`ds_blog_landing_new.html`)

---

## Critical Design Decisions

1. **Blog file location:** `folders/ds_blogs/ds_documentation_gap.html` — this is the ds_blogs ROOT, not inside the project folder. Charts reference `projects/smarterdx_documentation_gap/data/outputs/blog_charts/` via relative path.

2. **Trinidad runs the notebooks:** She wants to run each notebook herself to understand the domain. Build notebooks with clear markdown explanations between code cells so she can follow the logic.

3. **Same blog template as Octave:** Tabbed HTML with interactive Plotly charts embedded as iframes. Use the same CSS classes (`.section-heading`, `.subsection-heading`, `.section-text`, `.chart-container`, `.chart-frame`, `.chart-caption`, `.assumptions-box`, `.takeaway-box`).

4. **No API keys required:** All CMS data is freely downloadable. KFF data is published as tables/downloads.

5. **Independent analysis framing:** Like the Octave blog, this is framed as an independent analytical exercise, not a SmarterDx marketing piece. The analysis examines the problem space, not the company's product.

---

## Key Domain Concepts Trinidad Should Learn

- **MS-DRG:** Medicare Severity Diagnosis Related Group — the payment category
- **CMI:** Case Mix Index — hospital's average DRG weight (higher = sicker patients = more revenue)
- **CC/MCC:** Complication/Comorbidity and Major CC — severity modifiers that shift DRG payment tiers
- **CDI:** Clinical Documentation Improvement — the practice of ensuring documentation matches care delivered
- **ICD-10:** International Classification of Diseases, 10th revision — the diagnosis code system
- **IPPS:** Inpatient Prospective Payment System — how Medicare pays hospitals for inpatient stays
- **Base rate:** ~$6,300-6,500 (FY 2025) — the starting point before DRG weight and adjustments
- **Severity shift:** Moving a case from "without CC" to "with CC" or "with MCC" — the revenue impact CDI captures

---

## Key Files (When Complete)

| File | Description |
|------|-------------|
| `folders/ds_blogs/ds_documentation_gap.html` | Published blog post (4-5 tabs, interactive charts) |
| `projects/smarterdx_documentation_gap/data/outputs/blog_charts/` | Interactive chart HTML files |
| `projects/smarterdx_documentation_gap/data/outputs/nb07_*/` | Master scoring data |
| `projects/smarterdx_documentation_gap/notebooks/` | 9 Jupyter notebooks organized by pipeline phase |

---

## Context: Why This Project Exists

Trinidad has a second-round hiring manager interview at SmarterDx on **April 2, 2026** for the **Senior Product Analyst** role with **Daniel Kreitzberg**. This project is designed to:
1. Teach her the CDI/RCM domain by working with real CMS data
2. Create a portfolio piece that demonstrates healthcare data fluency
3. Provide concrete talking points for the interview about DRGs, CMI, documentation accuracy, and revenue impact
4. Mirror the successful approach used for the Octave Behavioral Health Expansion project

The interview prep (STAR stories, questions for interviewer) is in a separate Cowork chat. The study guides are in:
`job_posting_resume_optimizer/data/outputs/nb19_resumes/interview_prep/`
