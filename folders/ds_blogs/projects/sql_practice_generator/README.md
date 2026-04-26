# SQL Practice Generator

Claude-powered SQL practice notebook with a local Postgres and MySQL sandbox. Generates problems modeled on analytical SQL platforms plus procedural shapes (DO blocks, RETURNS TABLE, recursive CTEs, DML) that those platforms skip.

## One-time setup

1. **Install Docker Desktop** (free for personal use): https://www.docker.com/products/docker-desktop/
2. **Start the sandbox containers:**
   ```bash
   cd folders/ds_blogs/projects/sql_practice_generator
   docker compose up -d
   ```
   This starts Postgres on `localhost:5432` and MySQL on `localhost:3306`.

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your API key** — copy `.env.example` to `.env` and fill in `ANTHROPIC_API_KEY`.

5. **Open the notebook:**
   ```bash
   jupyter notebook notebooks/nb01_sql_practice.ipynb
   ```

## Daily use

- Run the setup cell (initializes Claude client and sandbox connections).
- Pick dialect (PostgreSQL or MySQL), question type, and source (New or Solved).
- Click Generate Problem.
- Fill out the diagnostic form, click Get Feedback for grading.
- Click Hint for progressive hints.
- Write your SQL and use Test, Run, Submit.
- Click Next Question to clear and start over.

## Question types

- **Select Analytical** — standard analytical SELECT problems (filtering, aggregation, joins, windows).
- **DO Block** — sequential UPDATE problems using PL/pgSQL `DO $$ ... $$;` blocks (Postgres only).
- **RETURNS TABLE function** — function-wrapped queries.
- **RETURNS scalar function** — scalar-returning functions.
- **Recursive CTE** — hierarchy traversal, path enumeration.
- **DML** — UPDATE, DELETE, INSERT problems.
- **Window Function Edge Cases** — ROWS vs RANGE, frame edge cases, RANK vs DENSE_RANK vs ROW_NUMBER.

## Resetting the sandbox

```bash
docker compose down -v   # destroy data volumes
docker compose up -d     # fresh start
```

## File layout

```
sql_practice_generator/
├── docker-compose.yml          # Postgres + MySQL sandbox
├── requirements.txt
├── .env.example
├── notebooks/
│   ├── nb01_sql_practice.ipynb
│   ├── sql_practice_utils.py   # Claude generator + grader
│   └── sandbox.py              # DB connection + execution helpers
└── data/
    └── outputs/
        ├── generated_problems/  # generated problem JSON files
        ├── solved/              # solved problem solutions
        └── sessions/            # session logs
```
