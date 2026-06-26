# Data Analyst Interview Prep

A reusable interview-drill framework: one shared engine pattern (catalog → generate → diagnose → grade) behind several focused notebooks. Formerly `sql_practice_generator`.

## Notebooks

Renumbered 2026-06-25 to free `nb02` for a Python practice notebook.

| Notebook | What it drills | Engine |
|---|---|---|
| `notebooks/nb01_sql_practice.ipynb` | SQL (Postgres/MySQL sandbox): analytical SELECTs, DO blocks, functions, recursive CTEs, DML, window edge cases | `sql_practice_utils.py` + `sandbox.py` |
| `notebooks/nb02_python_practice.ipynb` | Python: pandas, numpy, Python basics (array and string operations) | (built separately) |
| `notebooks/nb03_data_cleaning_modeling_drills.ipynb` | Clean messy raw data and build the target model (CREATE TABLE AS SELECT) | `nb03_modeling_drill_utils.py` |
| `notebooks/nb04_analyst_interview_drills.ipynb` | Data Transformation Modeling, Critical Reasoning SQL, Product Metrics & KPIs, Version Control | `nb04_drill_utils.py` |
| `notebooks/nb05_statistical_methods_drills.ipynb` | A/B testing, power & sample size, hypothesis tests, regression, claims metrics (PDC/PMPM) | `stats_drill_utils.py` |
| `notebooks/nb06_sql_error_review.ipynb` | Reviews every failed Submit logged from nb01, ranked by error type | `sql_practice_utils.py` |

`interview_practice_tool/` — a Claude-powered mock case-study coaching tool (5-phase product-analytics lifecycle, voice-to-text, rubric scoring). Self-contained, parked for evaluation.

## One-time setup

1. **(nb01 only) Docker Desktop** for the SQL sandbox: `docker compose up -d` (Postgres :5432, MySQL :3306).
2. **Python deps:** `pip install -r requirements.txt` (notebooks use numpy, scipy, pandas, ipywidgets; nb01 adds the DB drivers).
3. **API key (optional but recommended):** copy `.env.example` → `.env` and set `ANTHROPIC_API_KEY`. This enables Claude grading in the analyst notebook (nb04) and the Claude rubric + diagnosis feedback in the statistical methods notebook (nb05). Everything else (problem generation, the nb05 auto-run numeric check) works without it.
4. **Open a notebook**, e.g. `jupyter notebook notebooks/nb05_statistical_methods_drills.ipynb`.

## Daily use

Open the notebook for the skill you want to drill (nb01 SQL, nb02 Python, nb03 data cleaning and modeling, nb04 analyst, nb05 statistics, nb06 SQL error review), run the top **Setup** cell once, then use the dropdowns and **Generate** buttons. Code cells collapse (▼ Show code / ▲ Hide code) so you can focus on the prompt.

**nb05 flow:** Section 1 pick a problem (Topic / Scenario / Difficulty / Source) → Section 2 click **Load current problem**, then Walkthrough (guided) or Solve (write it) → Section 3 click **Load current problem**, write Python, **Test** / **Submit** / **Reveal reference**.

## File layout

```
data_analyst_interview_prep/
├── README.md  context.md  HANDOFF.md  cowork_handoff.md
├── docker-compose.yml      # nb01 SQL sandbox (Postgres + MySQL)
├── requirements.txt  .env.example
├── notebooks/
│   ├── nb01_sql_practice.ipynb          sql_practice_utils.py  sandbox.py
│   ├── nb02_python_practice.ipynb       (pandas, numpy, Python basics)
│   ├── nb03_data_cleaning_modeling_drills.ipynb   nb03_modeling_drill_utils.py
│   ├── nb04_analyst_interview_drills.ipynb        nb04_drill_utils.py
│   ├── nb05_statistical_methods_drills.ipynb      stats_drill_utils.py
│   └── nb06_sql_error_review.ipynb      (uses sql_practice_utils.py)
├── interview_practice_tool/   # parked mock-interview coaching tool
└── data/outputs/              # generated problems, solved snapshots, stats_problems/
```

## Extending (the framework pattern)

Each engine module exposes: a catalog of topics/subtopics, a `generate_problem(...)`, a `reference(...)`, and graders. To add a topic, edit the engine module; the notebook stays thin. `nb05` / `stats_drill_utils.py` is the current template — copy its 3-step structure (Pick → Diagnose → Implement) when splitting the analyst notebook's categories into their own notebooks.
