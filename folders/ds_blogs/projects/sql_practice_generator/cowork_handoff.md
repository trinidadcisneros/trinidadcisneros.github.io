# SQL Practice Generator — Cowork Handoff

## What this is

A Jupyter notebook that uses the Claude API to generate SQL practice problems and run user solutions against a local PostgreSQL or MySQL sandbox. Built for Trinidad to practice problem types not covered by mainstream analytical SQL platforms: DO blocks, RETURNS TABLE / scalar functions, recursive CTEs, DML, and window function edge cases.

## Folder layout

```
sql_practice_generator/
├── docker-compose.yml          # Postgres :5432 + MySQL :3306
├── requirements.txt
├── README.md
├── .env.example                # template; copy to .env
├── notebooks/
│   ├── nb01_sql_practice.ipynb
│   ├── sql_practice_utils.py   # Claude generator + grader + persistence
│   └── sandbox.py              # DB connection, reset, run-query, compare-results
└── data/outputs/
    ├── generated_problems/      # all generated problem JSON
    ├── solved/                  # solved snapshots with user's solution
    └── sessions/                # session logs (reserved)
```

## Notebook flow

1. Setup cell — initializes Claude client, checks Postgres + MySQL reachability, sets paths.
2. Problem Picker — dialect, question type, source (New / Solved), Generate button.
3. Diagnostic Form — paraphrase, input classification, output shape, recipe, composite moves; Get Feedback button calls Claude grader.
4. Hint button — progressive hints (3 levels seeded by Claude when generating).
5. Code editor with Test / Run / Submit buttons.
6. Next Question — clears all state.

## Architecture notes

- `sql_practice_utils.py` mirrors the pattern from `interview_practice_tool/notebooks/interview_practice_utils.py` (init_claude, _call_claude, JSON-shaped problem schema).
- Default model is `claude-sonnet-4-5`; pass a different model name to `init_claude(model=...)` if needed.
- Claude generates problems as JSON with: title, prompt, schema_ddl, example_input_data, example_output_columns/rows, test_data, test_expected_columns/rows, classification, hints, answer_key.
- The Postgres script splitter in `sandbox.py` is dollar-quote aware so DO blocks and PL/pgSQL function bodies execute correctly.
- The MySQL script splitter is naive (splits on `;`); avoid generating MySQL stored procedures with embedded semicolons until that's improved.
- `compare_results` is order-insensitive by default.

## Runtime requirements

- Docker Desktop running (for the sandbox containers).
- Python 3.10+, packages from `requirements.txt`.
- `ANTHROPIC_API_KEY` in environment (or in `.env` next to the notebook).

## Things to know before extending

- Question types live in `sql_practice_utils.QUESTION_TYPES`; add new types by adding a key with `label`, `description`, `dialects`, then handle it in `_topic_specific_guidance`.
- The recipe vocabulary `RECIPE_VOCAB` mirrors the playbook's 14 recipes (12 SELECT + 2 procedural). Keep these in sync with `sql_problem_patterns.html`.
- The diagnostic grader is intentionally lenient about wording variants ("row filter" matches "row-filter").
- For procedural problems, the test harness compares the result of the trailing SELECT against `test_expected_rows`.

## Known limitations

- MySQL DO block support: MySQL doesn't have `DO $$` syntax; for stored procedures use `CREATE PROCEDURE` with `DELIMITER`. Currently `do_block` is gated to PostgreSQL only.
- The MySQL splitter doesn't handle `DELIMITER //` blocks. If you add MySQL stored procedures, replace it with a proper parser.
- Generation can occasionally produce schema/test_data mismatches. The Test/Run buttons surface SQL errors; regenerate if the answer_key itself errors.
- No syntax highlighting in the code editor (it's a textarea). For richer editing, swap `widgets.Textarea` for an `IntegratedEditor` from `jupyterlab-code-editor` or similar.

## How to test the project end-to-end

1. `docker compose up -d` from the project root.
2. `pip install -r requirements.txt`.
3. Set `ANTHROPIC_API_KEY` (or copy `.env.example` → `.env`).
4. Open `notebooks/nb01_sql_practice.ipynb` and run all setup cells.
5. Pick PostgreSQL + Select Analytical → Generate → fill diagnostic → click Run. Should pass on a fresh problem.
6. Switch to DO Block → Generate → write a trivial wrong solution → Submit. Should report FAIL with diff.
