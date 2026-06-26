# Data Analyst Interview Prep — Cowork Handoff

## What this is

A reusable interview-drill framework (formerly `sql_practice_generator`). One shared engine pattern — catalog → generate → diagnose → grade — behind several focused Jupyter notebooks, each scoped to one skill area. Claude API powers grading where a key is present; all problem generation works offline.

## Folder layout

```
data_analyst_interview_prep/
├── docker-compose.yml          # nb01 SQL sandbox: Postgres :5432 + MySQL :3306
├── requirements.txt  .env.example  README.md  context.md  HANDOFF.md
├── notebooks/
│   ├── nb01_sql_practice.ipynb           # SQL drills
│   ├── sql_practice_utils.py             # nb01 generator + grader + persistence (also feeds nb06)
│   ├── sandbox.py                        # DB connection / reset / run / compare
│   ├── nb02_python_practice.ipynb        # NEW: pandas, numpy, Python basics (array + string ops), built separately
│   ├── nb03_data_cleaning_modeling_drills.ipynb  # clean messy raw data, build the target model
│   ├── nb03_modeling_drill_utils.py      # nb03 engine
│   ├── nb04_analyst_interview_drills.ipynb   # modeling, critical-reasoning SQL, product KPIs, version control
│   ├── nb04_drill_utils.py               # nb04 catalog, prompts, validators, graders
│   ├── nb05_statistical_methods_drills.ipynb # A/B, power, hypothesis tests, regression, claims metrics
│   ├── stats_drill_utils.py              # nb05 engine (scenarios, difficulty, diagnose specs, references)
│   └── nb06_sql_error_review.ipynb       # reviews failed Submits logged from nb01 (uses sql_practice_utils.py)
├── interview_practice_tool/              # parked mock case-study coaching tool (voice-to-text, rubric scoring)
└── data/outputs/                         # generated_problems/, solved/, stats_problems/, ...
```

## nb05 statistical methods flow (the current framework template)

1. **Setup cell** — imports, loads `stats_drill_utils`, loads `.env` (for `ANTHROPIC_API_KEY`).
2. **Section 1 — Pick a problem:** dropdowns for Topic, Scenario (same industry list as nb01 and the analyst notebook), Difficulty (Easy/Moderate/Hard), Source (New / Solved-replay). Generate renders a scenario-grounded problem card. Problems are saved to `data/outputs/stats_problems/`.
3. **Section 2 — Diagnose before coding:** Load current problem, then **Walkthrough** (guided dropdowns lead to the right test and assemble the strategy, with per-step "why") or **Solve** (write a diagnosis, get Claude feedback / reference approach). A worked-example card is collapsible inline.
4. **Section 3 — Implement:** the scenario card is shown above a Python editor (`data` holds inputs; `np`, `stats`, `math` available). **Test** runs and shows output; **Submit** auto-checks the `answers` dict against the reference and adds a Claude rubric; **Reveal reference** shows approach + model code.

## SQL playbook (separate file, heavily reworked 2026-06-16)

The nb01 SQL recipe playbook is `folders/sql/sql_problem_patterns.html` (NOT `pharmacy_problem_patterns.html`, which is a different blog). Its canonical changelog is `folders/sql/HANDOFF.md` — read the 2026-06-16 entry first. As of that session: the Single-Table tab is grouped into technique/method leaves (Filter, Aggregate, Scalar, Dedup) each with a decision tree, a mirrored reference table, and a Template card; Window/Pair/Rank templates live inside their leaves; the Sessionization section is organized by output shape (pick a template by reading the expected output columns) with all jargon removed. The nb01 engine `notebooks/sql_practice_utils.py` is now 32 qtypes (new `window_benchmark_compare`, rotated `left_join_on_filter` and `window_running_total`).

## Architecture notes

- Engines are thin-notebook-friendly: catalog of subtopics, `generate_problem(...)`, `reference(...)`, graders/renderers. `stats_drill_utils.py` is the cleanest reference implementation.
- nb05 numeric checks are deterministic (no API). Claude rubric/diagnosis grading activates only when `ANTHROPIC_API_KEY` is set; default model `claude-sonnet-4-6` (override with `DRILL_MODEL`).
- The notebooks reuse the same collapsible code-cell toggle (▼ Show code / ▲ Hide code) so the UI stays clean.
- nb01 needs Docker (the SQL sandbox); nb02 (Python), nb04 (analyst), and nb05 (statistics) do not. nb03 (data cleaning and modeling) runs SQL in the Postgres sandbox, so it needs Docker too; nb06 just reads nb01's logged errors.

## Before extending

- Add topics/subtopics in the relevant engine module, not the notebook.
- To add a new domain notebook, copy nb05's 3-step structure and write a sibling engine module.
- For structural changes, build in an isolated copy and validate headless (nbclient) before adopting into the live files.

## Validate end-to-end

1. `pip install -r requirements.txt`.
2. Open `notebooks/nb05_statistical_methods_drills.ipynb`, run Setup.
3. Section 1: pick A/B testing + Hard + a scenario → Generate. Section 2: Load → Walkthrough → Check approach. Section 3: Load → Reveal reference → paste it into the editor → Submit (all checks should pass).
