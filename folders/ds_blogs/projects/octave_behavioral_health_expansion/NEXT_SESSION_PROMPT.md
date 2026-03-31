# NEXT_SESSION_PROMPT.md — Octave Behavioral Health Expansion

**Last Updated:** 2026-03-31

---

## Before You Start

Read these files first:
1. `PROJECT_CONTEXT.md` (this project folder) — full pipeline status, session log, technical details
2. `PROJECT_ABSTRACT.md` (this project folder) — methodology, findings, recommendations
3. `CHARTS_README.md` (this project folder) — catalog of all 22 blog charts

---

## Current State

**The blog post is published and live on bitterscientist.com.** All 9 notebooks ran successfully, the blog (`blog_expansion_analysis.html`) has been built with 5 tabs and 22 interactive charts, and it is registered on both the homepage (`static/data/posts.json`) and the Data Science category page (`folders/ds_blogs/ds_blog_landing_new.html`).

### Interview Context
- **Interview date:** April 1, 2026 (hiring manager round with Alex Newbegin)
- **Role:** Sr. Data Analyst, Providers at Octave Health Group
- **Blog purpose:** Portfolio piece and interview discussion topic
- **Walkthrough target:** Executive Summary tab is optimized for a 3-5 minute guided walkthrough

### Blog Structure (5 tabs)
1. **Executive Summary** — Driving question, methods flow diagram, 3 key findings, 3-group benchmark chart, provider summary table, revenue model, entry recommendations, analytics infrastructure challenge
2. **Background** — Octave profile, market context, competitors, independent analysis disclaimer
3. **Methods** — Data sources, scoring model, normalization, weighting rationale
4. **Results** — 16+ interactive charts covering footprint, demand, providers, competition, scoring, projections
5. **Recommendations** — 4 strategic priorities with 4 exhaustive state archetypes (all 28 states covered)

---

## Likely Next Tasks

1. **Interview walkthrough rehearsal** — Practice walking through the Executive Summary tab in 3-5 minutes, then fielding questions by directing to specific tabs
2. **Post-interview updates** — If the interviewer raises questions or angles not covered, add analysis or charts
3. **Sensitivity analysis** — Vary scoring weights to test robustness of Tier 1 selections (mentioned in Recommendations as future work)
4. **Additional blog posts** — The pipeline and data are reusable for follow-up analyses (e.g., deep dive on a single state, provider recruitment funnel modeling)
5. **Code cleanup** — Notebooks could be refactored for cleaner public sharing if desired

---

## Key Files

| File | Description |
|------|-------------|
| `blog_expansion_analysis.html` | Published blog post (5 tabs, 22 charts) |
| `data/outputs/blog_charts/` | 22 interactive chart HTML files |
| `data/outputs/nb07_expansion_scoring/state_expansion_scores.csv` | Master scoring data (51 states × 33 columns) |
| `notebooks/` | 9 Jupyter notebooks organized by pipeline phase |
| `static/data/posts.json` | Website homepage post registry |

---

## Context: Why This Project Exists

Trinidad has a second-round hiring manager interview at Octave Health Group on **April 1, 2026** for the **Sr. Data Analyst, Providers** role. This project was built as both a portfolio piece and an interview discussion topic. The analysis demonstrates provider analytics skills, healthcare data fluency, and strategic thinking about expansion — all directly relevant to the role.

There is a separate Cowork chat and context for STAR-based behavioral interview preparation (12 themes). The study guides for Octave are in:
`job_posting_resume_optimizer/data/outputs/nb19_resumes/interview_prep/study_guides/octave/`
