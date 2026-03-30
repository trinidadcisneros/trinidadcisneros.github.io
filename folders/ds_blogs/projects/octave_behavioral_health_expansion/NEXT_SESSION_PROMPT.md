# NEXT_SESSION_PROMPT.md — Octave Behavioral Health Expansion

**Last Updated:** 2026-03-30

---

## Before You Start

Read these files first:
1. `PROJECT_CONTEXT.md` (this project folder) — full pipeline status, technical details, known issues
2. `README.rst` (this project folder) — business questions, data sources, notebook descriptions

---

## Current State

All 9 notebooks (NB01-NB09) have been built and contain complete code. The user (Trinidad) is running them sequentially in Jupyter and reporting any runtime errors.

### What's Been Run Successfully
- **NB01:** Runs clean after Puerto Rico NaN fix. Produces `state_population_base.csv` (51 rows).
- **NB02:** Updated with 7th provider type (NPs/PMHNPs). NPI Registry pagination fix applied. User is currently testing the updated NPI query cell.

### What Hasn't Been Run Yet (by the user)
- NB03 through NB09 — code is written but not yet executed by the user

### Known Issues to Watch For
- NB02's NPI Registry query takes 1-2 minutes due to pagination (200 records/page, 0.3s rate limit)
- If the NPI API is down or rate-limited, the merge cell handles it gracefully (falls back to BLS 5% estimate)
- NB06 regulatory data uses curated fallback tables — if any API sources are added later, ensure state name matching is consistent

---

## Likely Next Tasks

1. **User runs NB02 with NPI fix** — may report new issues from the paginated query
2. **User runs NB03-NB06** — watch for API failures, data shape mismatches
3. **User runs NB07-NB09** — expansion scoring and visualizations; may want to adjust weights or add dimensions
4. **Blog post conversion** — once all notebooks run clean, convert the pipeline to a publishable blog post on bitterscientist.com (follows the site's nbconvert workflow documented in the root PROJECT_CONTEXT.md)
5. **Interview prep refinement** — the user may want to refine the analysis to highlight specific talking points for the April 1 Octave interview

---

## Context: Why This Project Exists

Trinidad has a second-round hiring manager interview at Octave Health Group on **April 1, 2026** for the **Sr. Data Analyst, Providers** role. This project was built as both a portfolio piece and an interview discussion topic. The analysis should demonstrate provider analytics skills, healthcare data fluency, and strategic thinking about expansion — all directly relevant to the role.

There is a separate Cowork chat and context for STAR-based behavioral interview preparation (12 themes). The study guides for Octave are in:
`job_posting_resume_optimizer/data/outputs/nb19_resumes/interview_prep/study_guides/octave/`
