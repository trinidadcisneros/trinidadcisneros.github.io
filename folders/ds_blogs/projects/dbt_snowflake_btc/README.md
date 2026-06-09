# dbt + Snowflake Hands On (Udemy course companion)

## Goal

- Complete Daniel Weigel's Udemy course "The Complete Snowflake & dbt Hands On Course."
- Prep for the dbt Analytics Engineer certification exam.
- Ship two blog posts to bitterscientist.com from the course work.

## Blog post plan

- **Post 1** — Bike trips and weather correlation (built in Section 3 with dbt Cloud).
- **Post 2** — Bitcoin pipeline and Whale Alert audit framework (built in Sections 6 and 7 with dbt Core).

## Data story confirmation

- **Yes, the course has real analysis content.** Bike trips + daily weather gives a clear correlation story. The Bitcoin pipeline includes Whale Alert (large transaction tracking) and price enrichment, which is a time series story.
- The course is project based, so each section produces working models and tables that can be queried for the blog narrative.

## Cost guardrails

- Snowflake warehouse: XSMALL only, AUTO_SUSPEND = 60 seconds, AUTO_RESUME = TRUE.
- Drop test databases and schemas at the end of every session.
- Use the `course_tracking.md` log in `cost_tracking/` to record daily credit usage.
- dbt Cloud: stay on the Developer (free) tier; only one seat needed.
- dbt Core (Section 6+): runs locally in VS Code, zero cost beyond your laptop.
- AWS S3: lectures use Daniel's public buckets for reads, so no AWS spend unless you opt into Section 5 bonus.
- No Power BI on Mac: substitute Looker Studio (free) or Streamlit / Metabase for any dashboard step.

## Folder layout

- `course_materials/` — raw Udemy course inputs (transcripts, instructor PDFs, written resources); **gitignored** because it is paid content.
  - `roadmap/` — course wide roadmap PDF and transcript.
  - `section_01_snowflake/` — Section 1 transcripts and resources (more section folders added as you progress).
- `notes/` — **your own** section by section progress notes (safe to publish).
- `snowflake_sql/` — SQL scripts for Snowflake setup, warehouse config, cleanup.
- `dbt_project/` — the actual dbt project (created by `dbt init` during Section 6).
- `blog/` — blog post drafts (`.ipynb` or `.html`), with images in `blog/images/`.
- `cost_tracking/` — running log of Snowflake credit usage and any AWS spend.

## Git note

- The Udemy course has no public repo, so you build your own starting in Section 6.
- This folder lives inside the `bitterscientist.com` repo, which is already git tracked.
- The dbt project itself (under `dbt_project/`) can be a sub directory of this repo, or pushed to its own GitHub repo if you want the GitHub Actions CI lectures (Section 6) to feel realistic.

## Tools

- Visual Studio Code (VS Code) for editing and running dbt commands.
- Snowflake (paid account, used carefully).
- dbt Cloud free tier for Sections 3 to 5, dbt Core for Sections 6+.
- Python 3 (already set up locally for the bootcamp project).
