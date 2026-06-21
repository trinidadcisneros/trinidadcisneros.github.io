# Data Analyst Interview Prep

A reusable interview-drill framework: one shared engine pattern (catalog → generate → diagnose → grade) behind several focused notebooks. Formerly `sql_practice_generator`.

## Notebooks

| Notebook | What it drills | Engine |
|---|---|---|
| `notebooks/nb01_sql_practice.ipynb` | SQL (Postgres/MySQL sandbox): analytical SELECTs, DO blocks, functions, recursive CTEs, DML, window edge cases | `sql_practice_utils.py` + `sandbox.py` |
| `notebooks/nb02_analyst_interview_drills.ipynb` | Data Transformation Modeling, Critical Reasoning SQL, Product Metrics & KPIs, Version Control | `nb02_drill_utils.py` |
| `notebooks/nb03_statistical_methods_drills.ipynb` | A/B testing, power & sample size, hypothesis tests, regression, claims metrics (PDC/PMPM) | `stats_drill_utils.py` |

`interview_practice_tool/` — a Claude-powered mock case-study coaching tool (5-phase product-analytics lifecycle, voice-to-text, rubric scoring). Self-contained, parked for evaluation.

## One-time setup

1. **(nb01 only) Docker Desktop** for the SQL sandbox: `docker compose up -d` (Postgres :5432, MySQL :3306).
2. **Python deps:** `pip install -r requirements.txt` (notebooks use numpy, scipy, pandas, ipywidgets; nb01 adds the DB drivers).
3. **API key (optional but recommended):** copy `.env.example` → `.env` and set `ANTHROPIC_API_KEY`. This enables Claude grading in nb02 and the Claude rubric + diagnosis feedback in nb03. Everything else (problem generation, the nb03 auto-run numeric check) works without it.
4. **Open a notebook**, e.g. `jupyter notebook notebooks/nb03_statistical_methods_drills.ipynb`.

## Daily use

Open the notebook for the skill you want to drill (nb01 SQL, nb02 analyst, nb03 statistics), run the top **Setup** cell once, then use the dropdowns and **Generate** buttons. Code cells collapse (▼ Show code / ▲ Hide code) so you can focus on the prompt.

**nb03 flow:** Section 1 pick a problem (Topic / Scenario / Difficulty / Source) → Section 2 click **Load current problem**, then Walkthrough (guided) or Solve (write it) → Section 3 click **Load current problem**, write Python, **Test** / **Submit** / **Reveal reference**.

## File layout

```
data_analyst_interview_prep/
├── README.md  context.md  HANDOFF.md  cowork_handoff.md
├── docker-compose.yml      # nb01 SQL sandbox (Postgres + MySQL)
├── requirements.txt  .env.example
├── notebooks/
│   ├── nb01_sql_practice.ipynb          sql_practice_utils.py  sandbox.py
│   ├── nb02_analyst_interview_drills.ipynb   nb02_drill_utils.py
│   └── nb03_statistical_methods_drills.ipynb  stats_drill_utils.py
├── interview_practice_tool/   # parked mock-interview coaching tool
└── data/outputs/              # generated problems, solved snapshots, stats_problems/
```

## Extending (the framework pattern)

Each engine module exposes: a catalog of topics/subtopics, a `generate_problem(...)`, a `reference(...)`, and graders. To add a topic, edit the engine module; the notebook stays thin. `nb03` / `stats_drill_utils.py` is the current template — copy its 3-step structure (Pick → Diagnose → Implement) when splitting nb02's categories into their own notebooks.
