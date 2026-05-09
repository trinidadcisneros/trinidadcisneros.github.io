"""
SQL Practice Utilities — Claude-powered problem generator and grader
for analytical and procedural SQL practice.

Mirrors the pattern from interview_practice_utils.py: an init function,
a thin Claude wrapper, and topic-specific generators.
"""

import os
import json
import time
import uuid
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import pandas as pd

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False


# ============================================================
# LLM Setup
# ============================================================

_CLIENT = None
_MODEL = "claude-sonnet-4-5"


def init_claude(model: str = None):
    """Initialize the Claude client. Returns True if successful."""
    global _CLIENT, _MODEL
    if model:
        _MODEL = model
    if not CLAUDE_AVAILABLE:
        print("anthropic package not installed. Run: pip install anthropic")
        return False
    try:
        _CLIENT = anthropic.Anthropic()
        # Quick test
        _CLIENT.messages.create(
            model=_MODEL,
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}],
        )
        print(f"Claude ready ({_MODEL})")
        return True
    except Exception as e:
        print(f"Claude init failed: {e}")
        _CLIENT = None
        return False


def _call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 4000):
    if not _CLIENT:
        return None
    try:
        msg = _CLIENT.messages.create(
            model=_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return msg.content[0].text
    except Exception as e:
        print(f"Claude error: {e}")
        return None


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Pull a JSON object out of a Claude response, even if wrapped in markdown."""
    if not text:
        return None
    # Try fenced code block first
    if "```json" in text:
        try:
            chunk = text.split("```json", 1)[1].split("```", 1)[0]
            return json.loads(chunk.strip())
        except Exception:
            pass
    if "```" in text:
        try:
            chunk = text.split("```", 1)[1].split("```", 1)[0]
            return json.loads(chunk.strip())
        except Exception:
            pass
    # Fall back: find first { ... last }
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return None


# ============================================================
# Topic catalog
# ============================================================

QUESTION_TYPES = {
    "select_analytical": {
        "label": "Select Analytical",
        "description": "Standard analytical SELECT problems (filter, aggregate, join, window).",
        "dialects": ["postgresql", "mysql"],
    },
    "do_block": {
        "label": "DO Block (sequential UPDATE)",
        "description": "Apply a list of operations row by row inside DO $$ ... $$;",
        "dialects": ["postgresql"],
    },
    "do_block_queue": {
        "label": "DO Block (queue + state, per-row loop)",
        "description": "Two tables: a state table and a request/event log. FOR-loop the log in ID order, read current state, branch on request type, conditionally mutate state.",
        "dialects": ["postgresql"],
    },
    "returns_table": {
        "label": "RETURNS TABLE function",
        "description": "Function that wraps an inner SELECT and returns a TABLE.",
        "dialects": ["postgresql"],
    },
    "returns_scalar": {
        "label": "RETURNS scalar function",
        "description": "Function that returns a single value (INT, NUMERIC, etc.).",
        "dialects": ["postgresql"],
    },
    "recursive_cte": {
        "label": "Recursive CTE",
        "description": "Hierarchy traversal, path enumeration, or running calculations.",
        "dialects": ["postgresql", "mysql"],
    },
    "dml": {
        "label": "DML (UPDATE / DELETE / INSERT)",
        "description": "Mutation problems with explicit conditions; final SELECT confirms result.",
        "dialects": ["postgresql", "mysql"],
    },
    "window_edge": {
        "label": "Window Function Edge Cases",
        "description": "ROWS vs RANGE, frame edges, RANK vs DENSE_RANK vs ROW_NUMBER nuance.",
        "dialects": ["postgresql", "mysql"],
    },
    "union_islands": {
        "label": "Gaps-and-Islands (UNION dates + integer ids)",
        "description": "Collapse consecutive rows into [start, end] ranges using the row-number trick. Randomly picks one of four flavors per generation: (1) date with no missing days (date - rn form), (2) date with possible missing days (rn_overall - rn_per_state form), (3) integer ids in a single table (id - rn form, no UNION), (4) per-entity status periods (two source tables UNION'd by status, both windows partitioned by entity).",
        "dialects": ["postgresql", "mysql"],
    },
    "percentile_metrics": {
        "label": "Percentile & Distribution Metrics",
        "description": "Calculate percentiles, medians, quartile/decile bucketing, or top N% rankings. Randomly picks one flavor per generation: PERCENTILE_CONT/DISC for percentile aggregates (Postgres only), NTILE for quartile/decile buckets (both dialects), or PERCENT_RANK for top N% selection (both dialects).",
        "dialects": ["postgresql", "mysql"],
    },
    "pivot": {
        "label": "Pivot (long to wide)",
        "description": "Reshape long-format rows into wide-format columns using SUM/MAX/COUNT(CASE WHEN category = 'A' THEN value END) per target column. PostgreSQL CASE-based.",
        "dialects": ["postgresql"],
    },
    "unpivot": {
        "label": "Unpivot (wide to long)",
        "description": "Reshape wide-format columns into long-format rows using UNION ALL of SELECTs that pull each column with a literal label. PostgreSQL.",
        "dialects": ["postgresql"],
    },
    "cross_join": {
        "label": "Cross Join (motivated CROSS JOIN usage)",
        "description": "Practice using CROSS JOIN where it is the natural choice: calendar/category skeletons LEFT JOINed to actuals so missing combinations show as 0, fixed-bucket fan-out (one row per (entity, bucket) pair), or all-pairs self-cross-join for pairwise comparisons with a dedupe filter. PostgreSQL.",
        "dialects": ["postgresql"],
    },
    "date_operations": {
        "label": "Date Operations & Manipulations",
        "description": "Practice common date and timestamp methods: DATE_TRUNC for cohort buckets (month, week, quarter), EXTRACT for component access (year, dow, hour), date arithmetic with DATE ± INT and INTERVAL, 'X days ago' filtering, inclusive vs exclusive day counts, EXTRACT(EPOCH FROM interval) for durations, generate_series for filling missing days. PostgreSQL.",
        "dialects": ["postgresql"],
    },
}


RECIPE_VOCAB = [
    "row-filter", "group-aggregate", "scalar-extract", "rank-partition",
    "row-transform", "row-compare", "time-window", "normalize-bidirectional",
    "delete-duplicates", "enrich-join", "enrich-aggregate", "reshape",
    "function-wrapped", "do-block-sequential", "gaps-and-islands",
]


# ============================================================
# Generic code-reference templates per question type
# ============================================================
#
# Used by the notebook's "Code Reference" button. Returns a multi-line SQL
# skeleton with placeholders so the user sees the canonical structure for the
# current question type WITHOUT seeing the actual answer to their problem.
# Variables in <angle_brackets> are placeholders the user fills in based on
# their schema and prompt.

CODE_REFERENCE = {
    "select_analytical": """\
-- Generic SELECT analytical template
SELECT
    grouping_col_1,
    grouping_col_2,
    AGGREGATE_FN(metric_col) AS aggregated_metric
FROM main_table m
[INNER/LEFT JOIN lookup_table l ON m.fk = l.pk]
WHERE filter_condition
GROUP BY grouping_col_1, grouping_col_2
[HAVING aggregate_filter]
ORDER BY ordering_col [ASC|DESC];
""",
    "do_block": """\
-- Generic strict set-based DO block (NO LOOP, NO row-by-row state)
DO $$
BEGIN
    -- Rule 1: bulk UPDATE based on a fixed condition
    UPDATE target_table
    SET col_a = CASE
                  WHEN condition_1 THEN value_1
                  WHEN condition_2 THEN value_2
                  ELSE col_a
                END;

    -- Rule 2: another bulk UPDATE; do NOT re-read prior rows
    UPDATE target_table
    SET col_b = col_b + constant_or_lookup
    WHERE filter_condition;
END $$;

-- Trailing SELECT to confirm result
SELECT * FROM target_table ORDER BY pk;
""",
    "do_block_queue": """\
-- Generic DO block: FOR-loop the event log in order, branch on event type,
-- conditionally mutate state. Use when each event must read prior state.
DO $$
DECLARE
    v_event RECORD;
    v_state state_table%ROWTYPE;
BEGIN
    FOR v_event IN
        SELECT * FROM event_log ORDER BY event_id
    LOOP
        -- Read current state for this entity
        SELECT * INTO v_state FROM state_table WHERE entity_id = v_event.entity_id;

        -- Branch on event type
        IF v_event.event_type = 'TYPE_A' THEN
            UPDATE state_table
            SET status = 'new_status'
            WHERE entity_id = v_event.entity_id
              AND <condition based on v_state>;
        ELSIF v_event.event_type = 'TYPE_B' THEN
            UPDATE state_table
            SET <another mutation>
            WHERE entity_id = v_event.entity_id;
        END IF;
    END LOOP;
END $$;

SELECT * FROM state_table ORDER BY entity_id;
""",
    "returns_table": """\
-- Generic RETURNS TABLE function
CREATE OR REPLACE FUNCTION fn_name(p_arg1 INT, p_arg2 DATE)
RETURNS TABLE(col_a INT, col_b VARCHAR(100), col_c NUMERIC) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.col_a,
        s.col_b,
        s.col_c
    FROM source_table s
    WHERE s.filter_col = p_arg1
      AND s.date_col >= p_arg2
    ORDER BY s.col_a;
END $$;

-- Trailing call (CRITICAL: argument values must match expected output)
SELECT * FROM fn_name(<arg_1_value>, '<arg_2_value>'::DATE) ORDER BY col_a;

-- Watch out:
--   * Alias the source table and qualify EVERY column to avoid shadowing
--     the function's RETURNS TABLE output column names.
--   * VARCHAR(N) length must match the schema; bare VARCHAR mismatches.
--   * COUNT returns BIGINT; cast to INT if the RETURNS TABLE column is INT.
""",
    "returns_scalar": """\
-- Generic RETURNS scalar function
CREATE OR REPLACE FUNCTION fn_name(p_arg1 INT, p_arg2 DATE)
RETURNS NUMERIC LANGUAGE plpgsql AS $$
BEGIN
    RETURN (
        SELECT calculation
        FROM source_table
        WHERE col = p_arg1
          AND date_col >= p_arg2
    );
END $$;

-- Trailing call (CRITICAL: argument values must match expected output)
SELECT fn_name(<arg_1_value>, '<arg_2_value>'::DATE) AS result;

-- Watch out:
--   * Use RETURN ( ... ); NOT RETURN QUERY (that's for RETURNS TABLE).
--   * Scalar aggregate over an empty set returns NULL — COALESCE if 0/0 is
--     valid input.
""",
    "recursive_cte": """\
-- Generic recursive CTE: hierarchy traversal / path enumeration
WITH RECURSIVE traversal AS (
    -- Anchor: starting point(s)
    SELECT id, parent_id, 1 AS depth, ARRAY[id] AS path
    FROM source_table
    WHERE parent_id IS NULL  -- or some root condition

    UNION ALL

    -- Recursive step: extend by one level
    SELECT s.id, s.parent_id, t.depth + 1, t.path || s.id
    FROM source_table s
    JOIN traversal t ON s.parent_id = t.id
)
SELECT id, depth, path
FROM traversal
ORDER BY depth, id;
""",
    "dml": """\
-- UPDATE
UPDATE target_table
SET col_a = new_value
WHERE filter_col = some_value;

SELECT * FROM target_table ORDER BY pk;  -- confirm result

-- DELETE
DELETE FROM target_table
WHERE filter_col = some_value;

SELECT * FROM target_table ORDER BY pk;  -- confirm result

-- INSERT (often INSERT INTO ... SELECT)
INSERT INTO target_table (col_a, col_b)
SELECT col_a, col_b
FROM source_table
WHERE filter_condition;

SELECT * FROM target_table ORDER BY pk;  -- confirm result

-- Watch out:
--   * DELETE dedup: WHERE pk NOT IN (SELECT MIN(pk) FROM t GROUP BY group_cols)
--   * NOT IN with NULLs evaluates to UNKNOWN for every row; use NOT EXISTS
--     if the subquery can return NULL.
--   * Express WHERE for the rows you want to ACT on, not the inverse.
""",
    "window_edge": """\
-- ROW_NUMBER vs RANK vs DENSE_RANK
SELECT id, score,
    ROW_NUMBER() OVER (PARTITION BY group_col ORDER BY score DESC) AS rn,    -- 1, 2, 3, 4
    RANK()       OVER (PARTITION BY group_col ORDER BY score DESC) AS rk,    -- 1, 2, 2, 4 (gap)
    DENSE_RANK() OVER (PARTITION BY group_col ORDER BY score DESC) AS drk    -- 1, 2, 2, 3 (no gap)
FROM source_table;

-- ROWS vs RANGE for running totals
-- ROWS = fixed N preceding rows (positional)
-- RANGE = all rows whose ORDER BY value is within N of current (value-based)
SELECT id, value,
    SUM(value) OVER (ORDER BY id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3_rows,
    SUM(value) OVER (ORDER BY id RANGE BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_value_window
FROM source_table;

-- "Latest per group": DISTINCT ON in Postgres
SELECT DISTINCT ON (group_col) group_col, ts, val
FROM source_table
ORDER BY group_col, ts DESC;
""",
    "union_islands.date_calendar": """\
-- Gaps-and-islands: dates with NO missing days (calendar consecutive)
-- Form: date - rn_per_state
WITH base AS (
    SELECT 'state_a' AS state, date_col AS d
    FROM source_a WHERE d BETWEEN '<start>' AND '<end>'
    UNION ALL
    SELECT 'state_b', date_col
    FROM source_b WHERE d BETWEEN '<start>' AND '<end>'
),
grouping AS (
    SELECT *,
        d - (ROW_NUMBER() OVER (PARTITION BY state ORDER BY d))::INT AS grp
    FROM base
)
SELECT state, MIN(d) AS start_date, MAX(d) AS end_date
FROM grouping
GROUP BY state, grp
ORDER BY start_date;
""",
    "union_islands.date_sequence": """\
-- Gaps-and-islands: dates with POSSIBLE missing days (data-sequence consecutive)
-- Form: rn_overall - rn_per_state
WITH base AS (
    SELECT 'state_a' AS state, date_col AS d
    FROM source_a WHERE d BETWEEN '<start>' AND '<end>'
    UNION ALL
    SELECT 'state_b', date_col
    FROM source_b WHERE d BETWEEN '<start>' AND '<end>'
),
grouping AS (
    SELECT *,
        ROW_NUMBER() OVER (ORDER BY d)
      - ROW_NUMBER() OVER (PARTITION BY state ORDER BY d) AS grp
    FROM base
)
SELECT state, MIN(d) AS start_date, MAX(d) AS end_date
FROM grouping
GROUP BY state, grp
ORDER BY start_date;
""",
    "union_islands.integer_seq": """\
-- Gaps-and-islands: consecutive integer ids in a SINGLE table (no UNION)
-- Form: id - rn
WITH grouping AS (
    SELECT id_col,
        id_col - ROW_NUMBER() OVER (ORDER BY id_col) AS grp
    FROM source_table
)
SELECT MIN(id_col) AS start_id, MAX(id_col) AS end_id
FROM grouping
GROUP BY grp
ORDER BY start_id;
""",
    "union_islands.partitioned_status_periods": """\
-- Gaps-and-islands: per-entity timelines, BOTH windows partitioned by entity
WITH base AS (
    SELECT 'status_a' AS status, entity_id, status_date FROM source_a
    UNION ALL
    SELECT 'status_b', entity_id, status_date FROM source_b
),
grouping AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY status_date)
      - ROW_NUMBER() OVER (PARTITION BY entity_id, status ORDER BY status_date) AS grp
    FROM base
)
SELECT entity_id, status,
       MIN(status_date) AS start_date,
       MAX(status_date) AS end_date
FROM grouping
GROUP BY entity_id, status, grp
ORDER BY MIN(status_date), entity_id;
""",
    "percentile_metrics.percentile_aggregate": """\
-- PERCENTILE_CONT (interpolated) vs PERCENTILE_DISC (actual data value), Postgres only
SELECT
    group_col,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY metric_col) AS median_metric,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY metric_col) AS p90_metric,
    PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY metric_col) AS median_actual_value
FROM source_table
GROUP BY group_col
ORDER BY group_col;
""",
    "percentile_metrics.ntile_buckets": """\
-- NTILE(n) bucketing for quartiles, deciles, etc.
-- DESC ordering puts highest values in bucket 1
SELECT
    id_col,
    metric_col,
    NTILE(4) OVER (ORDER BY metric_col DESC) AS quartile
FROM source_table
ORDER BY quartile, metric_col DESC;

-- Optional: PARTITION BY for "quartile within each region/group"
-- NTILE(4) OVER (PARTITION BY region ORDER BY metric_col DESC) AS quartile
""",
    "percentile_metrics.top_n_percent": """\
-- PERCENT_RANK form for "top X%" with ties handled correctly
-- ORDER BY ASC means fastest/smallest sits at pr=0; filter pr <= 0.10 for top 10%
WITH ranked AS (
    SELECT
        id_col,
        metric_col,
        PERCENT_RANK() OVER (ORDER BY metric_col ASC) AS pr
    FROM source_table
)
SELECT id_col, metric_col
FROM ranked
WHERE pr <= 0.10
ORDER BY metric_col ASC, id_col ASC;

-- Watch out:
--   * Sort direction matters: ties always inherit the SMALLER rank, so flipping
--     ASC to DESC shifts ties asymmetrically. Use the direction that puts the
--     "best" rows at pr=0.
""",
    "pivot": """\
-- Pivot: long format to wide format (PostgreSQL CASE-based)
-- Slot 1: row key  -> GROUP BY
-- Slot 2: column key -> CASE WHEN inside the aggregate
-- Slot 3: cell value -> THEN clause inside CASE, wrapped in SUM/MAX/COUNT
SELECT
    entity_id,
    SUM(CASE WHEN category_col = 'A' THEN value_col END) AS a_total,
    SUM(CASE WHEN category_col = 'B' THEN value_col END) AS b_total,
    SUM(CASE WHEN category_col = 'C' THEN value_col END) AS c_total
FROM source_table
GROUP BY entity_id
ORDER BY entity_id;

-- COALESCE 0 default for missing categories (wrap each SUM):
--   COALESCE(SUM(CASE WHEN ... THEN value END), 0) AS col
-- Equivalent shorthand: ELSE 0 inside the CASE returns 0 (not NULL) on no match
--   SUM(CASE WHEN ... THEN value ELSE 0 END) AS col

-- LEFT JOIN to a lookup table to carry an enrichment column (e.g., entity_name):
--   FROM main_table m LEFT JOIN lookup l USING (entity_id)
--   GROUP BY m.entity_id, l.entity_name
""",
    "unpivot": """\
-- Unpivot: wide format to long format (UNION ALL of one SELECT per source column)
-- Drop "WHERE col IS NOT NULL" from each branch if the prompt says to keep NULLs
SELECT entity_id, 'col_a' AS label, col_a AS value FROM source_table WHERE col_a IS NOT NULL
UNION ALL
SELECT entity_id, 'col_b',         col_b         FROM source_table WHERE col_b IS NOT NULL
UNION ALL
SELECT entity_id, 'col_c',         col_c         FROM source_table WHERE col_c IS NOT NULL
ORDER BY entity_id, label;

-- Postgres alternative: CROSS JOIN LATERAL VALUES (one table scan instead of N)
SELECT m.entity_id, v.label, v.value
FROM source_table m
CROSS JOIN LATERAL (
    VALUES
        ('col_a', m.col_a),
        ('col_b', m.col_b),
        ('col_c', m.col_c)
) AS v(label, value)
ORDER BY m.entity_id, v.label;
""",
    "cross_join": """\
-- SHAPE A: Calendar/date skeleton + LEFT JOIN actuals (preserve missing days as 0)
WITH date_skeleton AS (
    SELECT generate_series('<start>'::date, '<end>'::date, INTERVAL '1 day')::date AS d
),
all_combos AS (
    SELECT e.entity_id, ds.d
    FROM entity_table e
    CROSS JOIN date_skeleton ds
)
SELECT ac.entity_id, ac.d, COALESCE(SUM(a.metric), 0) AS metric_total
FROM all_combos ac
LEFT JOIN actuals_table a
  ON a.entity_id = ac.entity_id AND a.event_date = ac.d
GROUP BY ac.entity_id, ac.d
ORDER BY ac.entity_id, ac.d;

-- SHAPE B: Categorical skeleton (fixed bucket fan-out, like #1907 salary bands)
SELECT c.category,
       COUNT(CASE WHEN c.category = 'Low'    AND e.metric < 20000             THEN 1 END
           + CASE WHEN c.category = 'Medium' AND e.metric BETWEEN 20000 AND 50000 THEN 1 END
           + CASE WHEN c.category = 'High'   AND e.metric > 50000             THEN 1 END) AS cnt
FROM (VALUES ('Low'), ('Medium'), ('High')) AS c(category)
CROSS JOIN entity_table e
GROUP BY c.category;

-- SHAPE C: All-pairs self cross-join with dedupe
SELECT a.id_col AS id_1, b.id_col AS id_2, <pair_metric>
FROM source_table a
CROSS JOIN source_table b
WHERE a.id_col < b.id_col   -- dedupe (a,b)/(b,a) AND exclude self-pairs
  AND <pair condition>
ORDER BY a.id_col, b.id_col;
""",
    "date_operations": """\
-- Date arithmetic: 'X days ago' filtering ('ago' = older = smaller date = <)
SELECT * FROM events_table WHERE event_date < CURRENT_DATE - 30;

-- Inclusive day count gotcha (Jan 10 - Jan 1 = 9, but the trial spans 10 days)
SELECT (end_date - start_date) + 1 AS duration_days FROM trials;

-- DATE_TRUNC for monthly/weekly cohort buckets
SELECT DATE_TRUNC('month', event_date)::date AS month_start, COUNT(*) AS events
FROM events_table
GROUP BY DATE_TRUNC('month', event_date)
ORDER BY month_start;

-- Cohort match (DATE_TRUNC includes year, so 2024-01 != 2025-01)
SELECT *
FROM events e
JOIN signups s
  ON DATE_TRUNC('month', e.event_date) = DATE_TRUNC('month', s.signup_date);

-- EXTRACT for component access
SELECT id,
       EXTRACT(YEAR  FROM event_date) AS yr,
       EXTRACT(DOW   FROM event_date) AS day_of_week,  -- 0 = Sunday in Postgres
       EXTRACT(HOUR  FROM event_ts)   AS hour_of_day
FROM events_table;

-- EXTRACT(EPOCH FROM interval) for durations in seconds; /60 for min, /3600 for hr
SELECT id, EXTRACT(EPOCH FROM (end_ts - start_ts)) / 3600 AS hours_elapsed
FROM events_table;

-- generate_series for filling missing days
SELECT d
FROM generate_series('2024-01-01'::date, '2024-12-31'::date, INTERVAL '1 day') AS d;

-- INTERVAL pitfall: column-driven interval (no string interpolation)
-- Use: CURRENT_DATE - col_days_int  OR  (col_days_int || ' days')::INTERVAL
-- AVOID: INTERVAL 'col_days days'  (treats 'col_days' as a literal, errors out)
""",
}


def get_code_reference(qtype: str, islands_flavor: str = None, percentile_flavor: str = None) -> str:
    """Return a generic code framework for the given question type.

    Looks up a flavor-qualified key first (e.g. 'union_islands.date_sequence'),
    falls back to the bare qtype, then to a generic fallback message.
    """
    if qtype == "union_islands" and islands_flavor:
        key = f"union_islands.{islands_flavor}"
        if key in CODE_REFERENCE:
            return CODE_REFERENCE[key]
    if qtype == "percentile_metrics" and percentile_flavor:
        key = f"percentile_metrics.{percentile_flavor}"
        if key in CODE_REFERENCE:
            return CODE_REFERENCE[key]
    if qtype in CODE_REFERENCE:
        return CODE_REFERENCE[qtype]
    return f"-- No code reference template available for question type: {qtype}\n"


# ============================================================
# Scenario themes — used to diversify generated problems
# ============================================================

SCENARIO_THEMES = [
    # E-commerce & retail
    "an e-commerce platform tracking customer orders, returns, and refunds",
    "a subscription-box retailer managing monthly box assembly and customer churn",
    "a marketplace platform tracking seller inventory and listing fees",
    "a loyalty program tracking points earned, redeemed, and tier upgrades",
    # B2B SaaS & ops
    "a B2B SaaS company tracking trial signups and conversion to paid plans",
    "an enterprise software vendor monitoring seat utilization across customers",
    "a customer support tool tracking ticket SLA breaches and reassignments",
    "a workflow automation tool tracking job runs, retries, and failures",
    # Healthcare
    "a hospital system tracking patient admissions, discharges, and readmissions",
    "a clinical documentation tool tracking diagnosis code reviews and denials",
    "a telehealth platform tracking appointment scheduling and no-shows",
    "an electronic health record system tracking medication orders and refills",
    "a clinical research platform tracking trial enrollment and adverse events",
    "a population health team tracking chronic-condition patient cohorts",
    "a hospital revenue cycle team tracking claim submissions and denial reasons",
    # Health-tech / digital health
    "a fitness app tracking workout completion streaks and member retention",
    "a wellness platform tracking sleep and activity goal achievement",
    "a mental health app tracking therapy session attendance and engagement",
    # Finance
    "a fintech app tracking transaction approvals and fraud flags",
    "a lending platform tracking loan application stages and approval times",
    # Logistics / operations
    "a logistics company tracking shipment milestones and on-time delivery",
    "a ride-share platform tracking driver shifts and trip completion rates",
    # Media & content
    "a streaming platform tracking content views, completion rates, and ratings",
    "a publishing platform tracking article views, comments, and editor approvals",
]


def _pick_scenario(qtype: str) -> str:
    """Pick a random scenario theme appropriate for the question type."""
    return random.choice(SCENARIO_THEMES)


# ============================================================
# Problem generation
# ============================================================

GENERATOR_SYSTEM = """\
You generate SQL practice problems for a learner preparing for technical assessments.
Output MUST be a single JSON object inside a ```json fenced block. No prose outside the block.

The JSON schema is:
{
  "title": "short title, 4-8 words",
  "prompt": "problem statement, 3-6 sentences, includes any constraints",
  "schema_ddl": "CREATE TABLE statements separated by semicolons",
  "example_input_data": "INSERT statements that match the prompt's example input table",
  "example_output_columns": ["col1", "col2"],
  "example_output_rows": [["v1", "v2"], ...],
  "test_data": "INSERT statements with DIFFERENT rows than the example, larger and edge-case-y",
  "test_expected_columns": ["col1", "col2"],
  "test_expected_rows": [["v1", "v2"], ...],
  "classification": {
    "input_arrival": "single_table | join | union | procedural",
    "output_shape": "fewer_rows | same_rows | single_value | state_mutation | scalar_return | table_return",
    "recipe": "one of: row-filter, group-aggregate, scalar-extract, rank-partition, row-transform, row-compare, time-window, normalize-bidirectional, delete-duplicates, enrich-join, enrich-aggregate, reshape, function-wrapped, do-block-sequential",
    "composite_moves": ["ordered list of recipe IDs and prep steps"]
  },
  "hints": ["hint 1 (vague)", "hint 2 (more specific)", "hint 3 (almost the answer)"],
  "answer_key": "a clean working solution in the requested dialect"
}

Hard rules:
- Schema DDL must be valid for the requested dialect (PostgreSQL or MySQL).
- For DO block / RETURNS TABLE / RETURNS scalar / recursive CTE / DML problems, the prompt MUST specify exactly what shape the answer takes (e.g., "write a DO block that ... then a trailing SELECT ...").
- For procedural problems, the test_expected_rows is what a SELECT * FROM target ORDER BY ... should return after the mutation runs.
- Example data should be small (4-8 rows) and easy to trace by hand.
- Test data should be larger (15-30 rows) and exercise edge cases (NULLs, ties, empty groups, dates at boundaries).
- The answer_key must compile AND, when executed against example_input_data, produce example_output_rows EXACTLY (column order, value formatting, row count, row order if order matters).
- The answer_key must ALSO produce test_expected_rows EXACTLY when executed against test_data.
- Before returning, mentally trace your answer_key against example_input_data row-by-row to confirm it produces example_output_rows. Do the same against test_data.
- Be careful with operator interpretation: "where final_price > 100" means AFTER the prior step's update, not the original column. Trace each rule using the value the row has at THAT moment.
- Be careful with PostgreSQL DECIMAL rounding: column types like DECIMAL(10,2) round intermediate UPDATE results, which can change which rows pass a strict ">" comparison. If the prompt depends on a strict comparison, design the data so it isn't sensitive to that rounding.
- Do NOT mention any commercial brand names (no platform names).
- TRAILING-CALL EXPLICITNESS (CRITICAL for parameterized problems): If the answer involves a function with parameters (RETURNS scalar, RETURNS TABLE) or any solution where a trailing SELECT call's argument values affect which rows appear in the output, the prompt text MUST include a sentence like "Test your function by calling: `SELECT * FROM fn_name(arg1, arg2);`" naming the EXACT parameter values whose result equals example_output_rows. The answer_key MUST end with that same trailing call verbatim. The validator runs the user's full submission (function definition + trailing call) and compares to example_output_rows; if the user's trailing call uses different arguments than the answer_key, they get different rows and the comparison fails even though the function logic is correct. Never leave the test invocation implicit; never let the user guess which arguments produce the example output.
- EXPLICIT FORMULA / COLUMN REFERENCES (CRITICAL for any rule that computes a value): Whenever a rule sets a column to a derived value (percentage of another column, multiplier, sum, weighted score, etc.), the prompt text MUST name the source column(s), the target column, AND the exact formula. Forbidden phrasings: "apply a 15% cancellation fee" (15% of WHAT?), "increase the price by 10%" (10% of base_price? of current price?), "calculate the bonus" (using which columns?). Required phrasing: "Set `cancellation_fee` to `base_fee * 0.15`," "Update `current_price` to `current_price * 1.10`," "Set `bonus = total_sales * commission_rate`." Always show the formula in `code` formatting using the actual schema column names. If the rule involves a percentage, the prompt must explicitly say "X% of `<column_name>`" where the column name appears in code formatting. Without this, learners hit ambiguous prompts where multiple readings (flat $15 vs 15% of base_fee vs 15% of current cancellation_fee) are all reasonable, and they fail the test by picking the wrong one.
- COLUMN-LABEL CONFUSION (CRITICAL for status/category fields): When a rule sets a status column to one value (e.g., 'high_risk') and a later rule references "patients/rows that are high_risk," the prompt MUST clarify whether "high_risk" means the literal status value or the underlying CRITERION (e.g., "patients with 3 or more no-shows"). If the schema uses a single status column with mutually exclusive values, status changes by an earlier rule make the label inaccessible to later rules with conflicting status filters. Prefer one of: (a) restate the criterion explicitly in later rules ("for any 'cancelled' appointment where `previous_no_shows >= 3`"), or (b) introduce a separate boolean/flag column so the label persists across status changes. Never reuse a status label in two rules whose status filters can't both be true at once.
"""


def _topic_specific_guidance(qtype: str, dialect: str, scenario: str = None, dml_op: str = None, islands_flavor: str = None, percentile_flavor: str = None) -> str:
    base = f"Question type: {QUESTION_TYPES[qtype]['label']} ({QUESTION_TYPES[qtype]['description']}).\n"
    base += f"Dialect: {dialect}.\n"
    if scenario:
        base += (
            f"Scenario theme: {scenario}. "
            "Use realistic table and column names that fit this domain. "
            "Do NOT use generic 'products / orders / users' tables unless the scenario "
            "asks for them; the schema and prompt should clearly reflect the domain.\n"
        )
    if qtype == "do_block":
        base += (
            "Generate a STRICTLY SET-BASED sequential UPDATE problem. The DO block "
            "is a thin wrapper around 2-4 `UPDATE` statements that fire in order. "
            "It is NOT a row-by-row loop. Hard requirements:\n"
            "1) The DO block contains 2-4 bare `UPDATE` statements applied in sequence. "
            "It MUST NOT contain `FOR ... LOOP`, `SELECT INTO`, `RECORD` variables, "
            "scalar state variables, or `IF/ELSIF` branching on row state. The only "
            "PL/pgSQL machinery used is `DO $$ BEGIN ... END $$;`. If the answer key "
            "needs ANY of those constructs, the problem is the wrong shape — it belongs "
            "in `do_block_queue`, not here.\n"
            "2) Each UPDATE rule's WHERE clause must reference ONLY columns on the row "
            "being updated, plus parameters, constants, or static joins to a lookup "
            "table. A rule MUST NOT depend on the post-update value of an earlier "
            "rule applied to the SAME row. Use `CASE WHEN ... THEN ... ELSE col END` "
            "for tiered or conditional value changes within a single UPDATE.\n"
            "3) Each UPDATE rule's SET expression must be either a constant, a function "
            "of the row's OTHER columns (not the column being updated), or a simple "
            "linear formula like `col = col + k` where k is a constant or row-derived "
            "value. NO COMPOUNDING formulas like `col = 2 * col + 1`, `col = col * 1.1` "
            "applied repeatedly, or anything where running the rule N times produces a "
            "different result than running it once. If the column being updated appears "
            "on the right-hand side of `SET`, the per-row contribution must be the same "
            "regardless of how many prior rows of the same entity were processed.\n"
            "4) Self-test before returning: 'Could I rewrite this DO block as a single "
            "`UPDATE` with `CASE WHEN`s?' If yes, it's a valid set-based problem. "
            "If no — if the answer requires reading a row, computing a new value, then "
            "writing it back, then re-reading the same row to apply another rule — it's "
            "row-by-row and DOES NOT BELONG in this question type.\n"
            "5) The schema is typically ONE table that gets mutated. A second table is "
            "OK ONLY as a static lookup (e.g., `tier_thresholds`) joined via subquery; "
            "it is NOT a queue or event log being iterated.\n"
            "6) The trailing statement MUST be `SELECT * FROM <target_table> ORDER BY <pk>;` "
            "so the test harness sees the post-mutation snapshot. answer_key must include "
            "both the DO block and the trailing SELECT.\n"
            "7) Forbidden prompt language (these signal row-by-row, not set-based):\n"
            "   - 'process the events/log in chronological order'\n"
            "   - 'iterate the requests/queue in order'\n"
            "   - 'after each update, the next rule should see ...'\n"
            "   - 'subsequent rows see the change'\n"
            "   - 'for each row in table X, update table Y'\n"
            "   - 'increment by the prior count'\n"
            "   - 'each occurrence adds (N+1)'\n"
            "   - 'the contribution depends on the current value'\n"
            "   - any phrasing where the per-iteration contribution depends on how many "
            "prior iterations already ran for the same entity\n"
            "Allowed prompt shapes (set-based):\n"
            "   - 'Apply these rules in order: rule 1 sets X to ..., rule 2 sets Y to ...'\n"
            "   - 'Update tier to gold where ...; then update bonus to ... where tier = gold'\n"
            "   - 'For rows meeting condition A, set status to X; for rows meeting B, set Y'\n"
            "   - Tiered discounts, status flips, percentage adjustments where the multiplier "
            "is the same for every row in that tier\n"
            "Reference shape (set-based, do not copy verbatim):\n"
            "   DO $$\n"
            "   BEGIN\n"
            "     UPDATE accounts SET tier = 'gold' WHERE total_spend >= 10000;\n"
            "     UPDATE accounts SET tier = 'silver' WHERE total_spend >= 5000 AND total_spend < 10000;\n"
            "     UPDATE accounts SET annual_bonus = total_spend * 0.05 WHERE tier = 'gold';\n"
            "   END $$;\n"
            "   SELECT * FROM accounts ORDER BY account_id;\n"
            "EXPLICIT FORMULA PER RULE: For every rule that computes a derived value "
            "(percentage, multiplier, sum, weighted score), the prompt text MUST name "
            "the source column AND the target column AND the formula in code formatting. "
            "Forbidden: 'apply a 15% cancellation fee' (15% of WHAT?). Required: 'set "
            "`cancellation_fee` to `base_fee * 0.15`.' If a percentage rule doesn't say "
            "'X% of `<column_name>`' with the column name in code formatting, the prompt "
            "is broken — rewrite it before returning.\n"
            "STATUS LABEL DISCIPLINE: If one rule sets a status column to a value (e.g., "
            "'high_risk') and a later rule references rows with that status, make sure "
            "the status filters in both rules can BOTH be true at the same time. If the "
            "first rule's filter excludes the second rule's filter (e.g., rule 1 sets "
            "status='high_risk' WHERE status='scheduled', then rule 3 looks for "
            "status='cancelled' AND patient='high_risk'), the second rule can never fire "
            "because the row's status is mutually exclusive. Either restate the criterion "
            "explicitly in the later rule (e.g., 'WHERE previous_no_shows >= 3') instead "
            "of reusing the label, or introduce a separate flag column. Never reuse a "
            "status label across rules whose status filters can't both be true at once.\n"
            "Set classification.recipe to `row-transform` or `row-filter` (NOT "
            "`do-block-sequential`, which is reserved for row-by-row loops). Set "
            "classification.input_arrival to `single_table` or `join` and "
            "classification.output_shape to `state_mutation`."
        )
    elif qtype == "do_block_queue":
        base += (
            "Build the airline-seats / queue-processor shape. Hard requirements:\n"
            "1) The schema MUST contain TWO tables:\n"
            "   - a STATE table (e.g., seats, accounts, inventory_lots, patient_beds, claim_lines) "
            "with a primary key and at least one mutable status/value column.\n"
            "   - a REQUEST LOG table (e.g., requests, events, transactions, claim_actions) with a "
            "monotonically increasing primary key (request_id / event_id), a TYPE column whose "
            "value selects which branch fires, a FOREIGN KEY pointing at the state row to act on, "
            "and any payload columns the rules need (person_id, amount, etc.).\n"
            "2) The DO block MUST:\n"
            "   - DECLARE a RECORD variable for the request row plus 1-3 scalar variables that hold "
            "the state row's current values.\n"
            "   - Use `FOR rec IN SELECT * FROM <request_log> ORDER BY <id> LOOP` to iterate the "
            "log in ID order. NO set-based UPDATE that bypasses the loop.\n"
            "   - Inside the loop, do `SELECT col1, col2 INTO var1, var2 FROM <state_table> WHERE "
            "<pk> = rec.<fk>;` to read CURRENT state freshly each iteration (the prior iteration's "
            "UPDATE must be visible).\n"
            "   - Branch with `IF ... ELSIF ... END IF;` on BOTH the request type AND the current "
            "state. Some requests must be no-ops because the current state does not satisfy any "
            "branch (this is the whole point of reading state per iteration).\n"
            "   - Conditionally `UPDATE <state_table> SET ... WHERE <pk> = rec.<fk>;` inside the "
            "matching branch. Do not update unconditionally.\n"
            "3) Design the test data so that:\n"
            "   - At least one request is a no-op because state already disqualifies it.\n"
            "   - At least one request CHANGES state in a way that affects whether a LATER request "
            "in the same run becomes valid or invalid (this is what makes the loop necessary).\n"
            "   - Borderline ordering matters: if you reordered two specific requests, the final "
            "state would differ.\n"
            "4) The trailing statement MUST be `SELECT * FROM <state_table> ORDER BY <pk>;` so the "
            "harness sees the post-mutation snapshot.\n"
            "5) DO NOT generate a problem solvable with two or three set-based UPDATEs. If your "
            "rules can collapse to `UPDATE ... WHERE <type predicate>;` chains, you have the wrong "
            "shape — add a state-dependent guard that requires reading the row's current value. "
            "If the answer can be rewritten as a single `UPDATE` with `CASE WHEN`s, that's `do_block` "
            "territory, NOT this question type.\n"
            "6) Required prompt language signals (use at least one explicitly):\n"
            "   - 'process the events/log in chronological order'\n"
            "   - 'iterate the queue in event_id order'\n"
            "   - 'each event must read the row's current state'\n"
            "   - 'subsequent events see the prior event's update'\n"
            "   - 'the contribution depends on the current value'\n"
            "   - any phrasing that makes it clear order-of-iteration matters and per-iteration "
            "state reads are required.\n"
            "7) PROMPT FORMATTING for event-type rules — NON-NEGOTIABLE. The most "
            "common failure mode is users not knowing what conditions to put in the "
            "IF/ELSIF branches because the rules were crammed into a paragraph. Fix "
            "this with strict bullet structure:\n"
            "   - Each event_type rule MUST be its OWN top-level bullet (one bullet "
            "per event type, never multiple types per bullet, never paragraph form).\n"
            "   - Each top-level bullet MUST begin with the literal phrase 'When "
            "event_type = N (label) applies:' using the schema's EXACT column name "
            "(`event_type`, NOT 'type' or 'kind' or 'action'). The label is the "
            "human-readable name of that event type (e.g., 'claim_review').\n"
            "   - Each top-level bullet MUST contain TWO sub-bullet sections:\n"
            "     * 'Preconditions:' with EACH precondition on its OWN sub-bullet. "
            "Name the EXACT column being checked (e.g., 'current `status` must be "
            "\\'pending\\'', 'the event\\'s `clinician_id` must equal the current "
            "`reviewer_id`'). Never combine two preconditions into one bullet with "
            "AND. If there are no preconditions other than 'always fires', say so "
            "explicitly.\n"
            "     * 'Actions:' with EACH state mutation on its OWN sub-bullet. Name "
            "the EXACT column being mutated AND the new value's source (e.g., 'set "
            "`status` to \\'under_review\\'', 'set `reviewer_id` to the event\\'s "
            "`clinician_id`'). Never combine two SET clauses into one bullet.\n"
            "   - When an event references a value FROM the event row, name the "
            "exact event column (e.g., 'the event\\'s `clinician_id`', 'the event\\'s "
            "`new_reviewer_id`'). Forbidden: 'their ID', 'the new value', 'the user' "
            "without naming the column.\n"
            "   - State explicitly that events failing their preconditions are "
            "no-ops (one final bullet outside the per-rule list).\n"
            "   - Forbidden phrasings: 'type 1 = name', 'type N (description, "
            "changing X and Y)' (paragraph form), 'their ID' (vague pronoun for a "
            "column).\n"
            "   - Required structure example (adapt names; do NOT copy these "
            "specific labels):\n"
            "     * When `event_type` = 1 ('claim_review') applies:\n"
            "       - Preconditions:\n"
            "         + current `status` must be 'pending'.\n"
            "       - Actions:\n"
            "         + set `status` to 'under_review'.\n"
            "         + set `reviewer_id` to the event's `clinician_id`.\n"
            "     * When `event_type` = 2 ('approve_code') applies:\n"
            "       - Preconditions:\n"
            "         + current `status` must be 'under_review'.\n"
            "         + the event's `clinician_id` must equal the current `reviewer_id`.\n"
            "       - Actions:\n"
            "         + set `status` to 'approved'.\n"
            "     * Events that fail their preconditions are no-ops (the state row is unchanged).\n"
            "Reference shape (do not copy verbatim, use as a structural template):\n"
            "   FOR r IN SELECT * FROM requests ORDER BY request_id LOOP\n"
            "     SELECT status, person_id INTO cur_status, cur_owner FROM seats WHERE seat_no = r.seat_no;\n"
            "     IF r.request = 1 AND cur_status = 0 THEN UPDATE seats SET ... ;\n"
            "     ELSIF r.request = 2 AND (cur_status = 0 OR (cur_status = 1 AND cur_owner = r.person_id)) THEN UPDATE seats SET ... ;\n"
            "     END IF;\n"
            "   END LOOP;\n"
            "Set classification.recipe to `do-block-sequential` and classification.input_arrival "
            "to `procedural`."
        )
    elif qtype == "returns_table":
        base += (
            "Function returns a row set via `RETURNS TABLE (...)`. "
            "schema_ddl MUST contain ONLY `CREATE TABLE` statements — do NOT put a "
            "function scaffold or placeholder body into schema_ddl, because Postgres "
            "validates plpgsql bodies at CREATE FUNCTION time and an empty "
            "`RETURN QUERY ( /* placeholder */ );` is a syntax error that fails "
            "schema loading. "
            "The prompt MUST specify the exact function signature the user should write: "
            "function name, parameter names and types, and the RETURNS TABLE column names "
            "and types (match source column lengths exactly, e.g. VARCHAR(100) not bare VARCHAR). "
            "The answer_key contains the full "
            "`CREATE OR REPLACE FUNCTION fn_name(...) RETURNS TABLE (...) AS $$ BEGIN "
            "RETURN QUERY ( ... ); END; $$ LANGUAGE plpgsql;` definition followed by a "
            "trailing `SELECT * FROM fn_name(arg1, arg2);` so the harness sees output. "
            "Alias the source table inside RETURN QUERY and qualify every column to avoid "
            "RETURNS TABLE column shadowing. "
            "EXPLICIT TEST CALL: the prompt text MUST include a sentence like 'Test your "
            "function by calling: `SELECT * FROM fn_name(arg1_value, arg2_value);`' naming "
            "the EXACT parameter values that produce example_output_rows. The same trailing "
            "call must appear verbatim at the end of answer_key. Different argument values "
            "produce different rows, so leaving the test call implicit forces the user to "
            "guess and produces row-count mismatches even when their function logic is right."
        )
    elif qtype == "returns_scalar":
        base += (
            "Function returns a scalar (e.g., INT, NUMERIC). Use `RETURN ( ... );` not `RETURN QUERY`. "
            "The answer_key calls the function via `SELECT fn_name(args) AS result;`. "
            "EXPLICIT TEST CALL: the prompt text MUST include a sentence like 'Test your "
            "function by calling: `SELECT fn_name(arg1_value, arg2_value) AS result;`' naming "
            "the EXACT parameter values that produce example_output_rows. The same trailing "
            "call must appear verbatim at the end of answer_key."
        )
    elif qtype == "recursive_cte":
        base += "The answer_key must use `WITH RECURSIVE`."
    elif qtype == "dml":
        # dml_op is chosen randomly in generate_problem so each generation lands on
        # a different operation. If somehow not provided, default to UPDATE.
        op = (dml_op or "UPDATE").upper()
        op_specific = {
            "UPDATE": (
                "Generate an UPDATE problem. The answer_key is a single bare `UPDATE` "
                "statement followed by a confirming SELECT. The prompt MUST say 'write "
                "a single UPDATE statement'. Use `SET col = CASE WHEN ... THEN ... ELSE "
                "col END` for tiered or conditional value changes; use `WHERE` ONLY when "
                "some rows should be left untouched entirely. Pick a real-world rule "
                "shape (tier upgrades, status flips, percentage adjustments, flag "
                "toggles) so the CASE branches do meaningful work. "
                "EXPLICIT FORMULA: If any branch computes a percentage, multiplier, or "
                "derived value, the prompt MUST name the source column AND the target "
                "column AND the formula in code formatting, e.g. 'set `final_price` to "
                "`base_price * 0.85`'. NEVER write 'apply a 15% discount' without naming "
                "which column the 15% multiplies."
            ),
            "DELETE": (
                "Generate a DELETE problem. The answer_key is a single bare `DELETE` "
                "statement followed by a confirming SELECT. The prompt MUST say 'write "
                "a single DELETE statement'. Pick a real-world removal rule: "
                "deduplicate keeping the smallest/largest id per group, drop rows that "
                "fail a quality check, prune rows older than a cutoff, remove orphaned "
                "rows (NOT IN / NOT EXISTS against another table). The WHERE clause "
                "should require a meaningful subquery or correlated condition, not "
                "just a trivial column comparison."
            ),
            "INSERT": (
                "Generate an INSERT problem. The answer_key is a single bare "
                "`INSERT INTO target (cols) SELECT ...` statement followed by a "
                "confirming SELECT. The prompt MUST say 'write a single INSERT "
                "statement' (using INSERT ... SELECT, NOT bulk INSERT VALUES). Pick a "
                "real-world seeding rule: copy qualifying rows from a source table to "
                "a target with transformation, archive matching rows, materialize a "
                "rolled-up summary into a target. The schema MUST include both a "
                "source table (pre-populated) and a target table (initially empty or "
                "partial) so the INSERT does meaningful work."
            ),
        }[op]
        base += (
            f"{op_specific}\n\n"
            "Hard requirements (apply to all DML operations):\n"
            "1) The answer_key MUST NOT contain `DO $$`, `BEGIN`, `END $$`, `DECLARE`, "
            "`FOR ... IN ... LOOP`, `IF ... THEN`, or any PL/pgSQL construct. If the "
            "rules cannot be expressed without procedural logic, generate a different "
            "problem &mdash; do not fall back to a DO block.\n"
            "2) The answer_key ends with a single confirming "
            "`SELECT * FROM target_table ORDER BY ...;` that the harness reads as the "
            "result.\n"
            "3) Each rule must be expressible inside the chosen DML statement (in the "
            "WHERE, the SET CASE, or the SELECT feeding the INSERT). No per-row state "
            "lookup, no cross-row dependency that would require a loop.\n"
            f"4) Pick a scenario-appropriate target table and rule. Operation requested: {op}.\n"
            "Set classification.input_arrival to `single_table` or `join` as "
            "appropriate. classification.output_shape is `state_mutation`."
        )
    elif qtype == "window_edge":
        base += (
            "Pick a problem where the choice between ROWS and RANGE, or between "
            "RANK and DENSE_RANK and ROW_NUMBER, materially changes the answer."
        )
    elif qtype == "union_islands":
        # Flavor decides which gaps-and-islands shape to generate. Three flavors at
        # 33/33/33 probability picked by the caller and passed in.
        flavor = islands_flavor or "date_sequence"
        base += (
            "Build a gaps-and-islands problem. The user collapses consecutive rows "
            "into [start, end] ranges using the row-number trick. The exact shape "
            f"is the '{flavor}' flavor (chosen by the harness this run).\n\n"
        )
        if flavor == "date_calendar":
            base += (
                "FLAVOR: date_calendar (dates with NO missing days expected, calendar-consecutive).\n"
                "Hard requirements:\n"
                "1) Schema MUST contain 2 source tables, each holding rows for ONE state "
                "only (state encoded by which table the row lives in). Examples: "
                "Failed(fail_date) + Succeeded(success_date), OnDuty(shift_date) + "
                "OffDuty(off_date), InStock(check_date) + OutOfStock(check_date).\n"
                "2) Test data MUST cover EVERY day in the prompt's date range. No gaps. "
                "Each calendar day in the range appears in exactly one of the two tables. "
                "This is what makes the date-minus-rownumber form work.\n"
                "3) The prompt MUST explicitly say 'every day in the range is covered' or "
                "'no missing days' so the user knows they can rely on calendar consecutiveness.\n"
                "4) The answer_key MUST use the date-minus-rownumber form: "
                "`d - (ROW_NUMBER() OVER (PARTITION BY state ORDER BY d))::INT AS grp` "
                "(Postgres) or equivalent. NO `rn_overall - rn_per_state` form.\n"
                "5) Example data MUST include at least 3 islands. Mix at least one "
                "single-day island (start = end) with multi-day islands.\n"
            )
        elif flavor == "date_sequence":
            base += (
                "FLAVOR: date_sequence (dates with POSSIBLE missing days, data-sequence consecutive).\n"
                "Hard requirements:\n"
                "1) Schema MUST contain 2 source tables, each holding rows for ONE state "
                "only (state encoded by which table the row lives in). Examples: "
                "completed_workouts(workout_date) + skipped_days(skip_date), "
                "Logins(login_date) + Logouts(logout_date), Active(check_date) + Idle(check_date).\n"
                "2) Test data MUST include AT LEAST ONE missing day in the date range "
                "where neither table has a row. The prompt should explicitly mention this "
                "is possible (e.g., 'some days may have no record at all').\n"
                "3) The prompt MUST define 'consecutive' to mean 'consecutive in the "
                "union of source tables, ignoring missing days' so the user picks the "
                "correct islands form.\n"
                "4) The answer_key MUST use the two-rownumber-difference form: "
                "`ROW_NUMBER() OVER (ORDER BY d) - ROW_NUMBER() OVER (PARTITION BY state ORDER BY d) AS grp`. "
                "NO `date - rn_per_state` form (it would break on the missing day).\n"
                "5) Example data MUST include at least 3 islands and at least one missing "
                "day between two same-state rows that should still be in the same island.\n"
            )
        elif flavor == "integer_seq":
            base += (
                "FLAVOR: integer_seq (consecutive integer ids in a SINGLE table, no UNION).\n"
                "Hard requirements:\n"
                "1) Schema MUST contain ONE source table with an integer id column "
                "and optionally a state/category column. Examples: Logs(log_id), "
                "TicketIds(ticket_id), OrderNumbers(order_no), SeatNumbers(seat_id, status).\n"
                "2) The prompt asks the user to find ranges of CONSECUTIVE integer ids "
                "(differ by 1). Output is [start_id, end_id] pairs.\n"
                "3) Optional state/category column: if included, group consecutive same-state "
                "ids into [start, end] ranges per state. Without a state column, just collapse "
                "consecutive ids into [start, end] ranges.\n"
                "4) The answer_key MUST use the id-minus-rownumber form: "
                "`id - ROW_NUMBER() OVER (ORDER BY id) AS grp` (no state) or "
                "`id - ROW_NUMBER() OVER (PARTITION BY state ORDER BY id) AS grp` (with state).\n"
                "5) Test data MUST include at least 3 ranges. Include at least one "
                "single-id range (start = end) and at least one gap (missing id).\n"
                "6) Do NOT use UNION in this flavor &mdash; it's single-table.\n"
            )
        elif flavor == "partitioned_status_periods":
            base += (
                "FLAVOR: partitioned_status_periods (per-entity timelines, two source tables UNION'd by status, BOTH windows partitioned by entity).\n"
                "Hard requirements:\n"
                "1) Schema MUST contain 2 source tables, each holding rows for ONE status "
                "only AND each tagged with an entity key column (the partition key). "
                "Examples: processing_orders(order_id, process_date) + shipped_orders(order_id, ship_date), "
                "active_subscriptions(user_id, active_date) + paused_subscriptions(user_id, pause_date), "
                "open_tickets(ticket_id, open_date) + closed_tickets(ticket_id, close_date).\n"
                "2) The prompt MUST ask for one row per consecutive status period PER ENTITY, "
                "with output columns including the entity key, the status label, the period "
                "start date, and the period end date. Multiple entities should appear in the "
                "expected output, each with their own timeline.\n"
                "3) The prompt MAY say 'status only flows forward' (once shipped, stays shipped) "
                "but does NOT have to. The query shape is the same either way.\n"
                "4) The prompt MUST define 'consecutive' to mean 'consecutive in the union of "
                "source tables for that entity, ignoring missing days' so the user picks the "
                "two-rownumber-difference form (not date - rn).\n"
                "5) The answer_key MUST partition BOTH windows by the entity key:\n"
                "   `ROW_NUMBER() OVER (PARTITION BY entity_key ORDER BY status_date)\n"
                "  - ROW_NUMBER() OVER (PARTITION BY entity_key, status ORDER BY status_date) AS grp`.\n"
                "   This restarts the global rn at 1 inside each entity's timeline so other "
                "entities' rows can't shift the math.\n"
                "6) The final GROUP BY MUST include all three keys: entity_key, status, grp. "
                "Dropping the entity_key would mash different entities into one row.\n"
                "7) Test data MUST include AT LEAST 3 entities and at least one entity with "
                "multiple status periods (e.g., processing run, then shipped run). Stagger the "
                "entity timelines so other entities' rows fall BETWEEN the runs of a target "
                "entity in the global date order &mdash; this is the failure mode the per-entity "
                "partition exists to prevent.\n"
                "8) The example_output_rows MUST contain at least 4 rows covering at least 2 "
                "distinct entities and at least 2 distinct statuses.\n"
                "9) Use UNION ALL, not UNION (no possible duplicates across the two source tables).\n"
            )
        # Common requirements applied to all flavors
        base += (
            "\nUniversal requirements (apply to whichever flavor was chosen):\n"
            "- The answer_key MUST end with the trailing SELECT shaping the output. "
            "GROUP BY state (if any) and grp, take MIN as start, MAX as end, ORDER BY start ASC.\n"
            "- The prompt MUST explicitly state the output column names (e.g., "
            "`state`, `start_date`, `end_date`, OR `start_id`, `end_id`).\n"
            "- The prompt MUST specify the required ORDER BY in the output.\n"
            "- For date flavors, apply the date-range filter in EACH UNION branch's "
            "WHERE (not the outer query).\n"
            "- Set classification.recipe to `gaps-and-islands`, "
            "classification.input_arrival to `union` (date flavors and partitioned_status_periods) "
            "or `single_table` (integer_seq), classification.output_shape to `fewer_rows`."
        )
    elif qtype == "percentile_metrics":
        flavor = percentile_flavor or "ntile_buckets"
        base += (
            "Build a percentile / distribution metrics problem. The user computes "
            "percentiles, medians, quartile/decile buckets, or top N% of rows. The "
            f"exact shape is the '{flavor}' flavor (chosen by the harness this run).\n\n"
        )
        if flavor == "percentile_aggregate":
            base += (
                "FLAVOR: percentile_aggregate (Postgres ONLY — uses PERCENTILE_CONT or PERCENTILE_DISC).\n"
                "Hard requirements:\n"
                "1) Schema MUST contain ONE main table holding numeric measurements "
                "(durations, latencies, scores, prices) plus optionally a grouping "
                "column (category, region, plan_tier, segment). Include 1 secondary "
                "lookup table only if needed for output naming.\n"
                "2) The prompt asks for a specific percentile or set of percentiles "
                "PER GROUP. Pick one shape:\n"
                "   - 'Find the median (50th percentile) <metric> for each <group>'\n"
                "   - 'Find the 90th percentile <metric> for each <group>'\n"
                "   - 'Return the median, P75, P90, and P95 of <metric> overall'\n"
                "3) The answer_key MUST use `PERCENTILE_CONT(p) WITHIN GROUP (ORDER BY metric)` "
                "for continuous percentiles (interpolated when between two values) OR "
                "`PERCENTILE_DISC(p) WITHIN GROUP (ORDER BY metric)` for discrete (returns "
                "an actual value from the data). The prompt MUST specify which one to use, "
                "OR explicitly leave it open and accept either.\n"
                "4) The prompt MUST explicitly name the percentile values (e.g., 0.5 for "
                "median, 0.9 for P90), the metric column, and the GROUP BY column(s) (if any).\n"
                "5) Test data should include groups with EVEN row counts (PERCENTILE_CONT "
                "interpolates between two values for even counts) and groups with ODD "
                "counts (single middle value), so the user sees how CONT and DISC differ.\n"
                "6) The prompt MUST explicitly state the output column names and ORDER BY.\n"
            )
        elif flavor == "ntile_buckets":
            base += (
                "FLAVOR: ntile_buckets (NTILE bucketing for quartiles, deciles, etc. — both dialects).\n"
                "Hard requirements:\n"
                "1) Schema MUST contain ONE main table holding rows to be bucketed by "
                "a numeric column (revenue, score, activity, spend). Include a row "
                "identifier (id, name) for output.\n"
                "2) The prompt asks the user to bucket rows into N equal-sized groups "
                "ordered by the metric. Pick one shape:\n"
                "   - 'Split <entities> into 4 quartiles by <metric>'\n"
                "   - 'Bucket <entities> into 10 deciles by <metric>'\n"
                "   - 'Assign each <entity> a quartile label (1-4) by <metric>; return "
                "<id>, <metric>, quartile, ordered by quartile then metric DESC'\n"
                "3) The answer_key MUST use `NTILE(4) OVER (ORDER BY metric DESC)` "
                "or similar. NTILE divides the rows as evenly as possible, leftover rows "
                "going to lower-numbered buckets.\n"
                "4) The prompt MUST explicitly name the bucket count (4 for quartiles, "
                "10 for deciles, etc.), the metric, and the sort direction (DESC for "
                "highest values in bucket 1, ASC for lowest first).\n"
                "5) Test data should include a row count that is NOT evenly divisible "
                "by the bucket count (e.g., 11 rows split into 4 quartiles produces buckets "
                "of size 3, 3, 3, 2) so the user sees how NTILE handles uneven splits.\n"
                "6) Optional: include a PARTITION BY column so each partition gets its "
                "own buckets independently (e.g., quartile within each region).\n"
                "7) The prompt MUST explicitly state the output column names and ORDER BY.\n"
            )
        elif flavor == "top_n_percent":
            base += (
                "FLAVOR: top_n_percent (find the top X% of rows using PERCENT_RANK or ROW_NUMBER/COUNT — both dialects).\n"
                "Hard requirements:\n"
                "1) Schema MUST contain ONE main table holding rows to be ranked by "
                "a numeric metric (revenue, score, count). Include a row identifier "
                "for output.\n"
                "2) The prompt asks the user to find the TOP X% of rows by the metric. "
                "Pick one shape:\n"
                "   - 'Find the top 10% of <entities> by <metric>'\n"
                "   - 'Return <entities> in the top quartile (top 25%) by <metric>'\n"
                "   - 'Find <entities> whose <metric> is in the top 5%'\n"
                "3) The answer_key MUST use ONE of these forms:\n"
                "   (a) `PERCENT_RANK() OVER (ORDER BY metric DESC) <= 0.10` for top 10%. "
                "Note: PERCENT_RANK ranges from 0 (highest) to 1 (lowest) when ordered DESC.\n"
                "   (b) `ROW_NUMBER() OVER (ORDER BY metric DESC) <= COUNT(*) OVER () * 0.10` "
                "(approximate, gives top N rows where N = ceil(total * 0.10)).\n"
                "   (c) For Postgres only: `PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY metric)` "
                "as a threshold value, then filter rows with `metric >= threshold`.\n"
                "4) The prompt MUST explicitly name the percentage cutoff and the metric "
                "column. The prompt MUST clarify whether ties are included or excluded "
                "at the boundary.\n"
                "5) Test data should include ties at the cutoff boundary so the user "
                "thinks about whether to include or exclude tied rows.\n"
                "6) Optional: include a PARTITION BY column for 'top X% per group' "
                "(e.g., top 10% spenders per region).\n"
                "7) The prompt MUST explicitly state the output column names and ORDER BY.\n"
            )
        # Common requirements applied to all flavors
        base += (
            "\nUniversal requirements (apply to whichever flavor was chosen):\n"
            "- The answer_key MUST end with the trailing SELECT producing the final "
            "output. CTE staircase is encouraged for readability (one CTE for raw "
            "calculations, one for filtering or grouping, final SELECT for output).\n"
            "- The prompt MUST explicitly state the output column names and required "
            "ORDER BY clause.\n"
            "- For ntile_buckets and top_n_percent, prefer DESC ordering by the metric "
            "so 'top' or 'highest' values appear in bucket 1 / pass the cutoff.\n"
            "- Set classification.recipe to `rank-partition` (most percentile shapes "
            "are rank-based), classification.input_arrival to `single_table`, "
            "classification.output_shape to `fewer_rows` for top-N% or `same_rows` "
            "for bucketing."
        )
    elif qtype == "pivot":
        base += (
            "Build a PIVOT problem (long format to wide format) using PostgreSQL "
            "CASE expressions. PostgreSQL has no native PIVOT keyword; the canonical "
            "approach is `aggfn(CASE WHEN category = 'X' THEN value END) AS x_col` "
            "in a GROUP BY query.\n\n"
            "Hard requirements:\n"
            "1) Schema MUST contain ONE main long-format source table with shape "
            "(entity_key, category_column, value_column). Examples: "
            "monthly_sales(region, month_name, sales_amount), "
            "exam_scores(student_id, subject, score), "
            "ticket_counts(team_id, severity, ticket_count). Optionally include 1 "
            "lookup table for naming the entity (e.g., region_lookup, student_lookup).\n"
            "2) The prompt MUST explicitly list the FIXED set of category values that "
            "become target columns (e.g., 'pivot the months Jan, Feb, Mar into "
            "columns jan_sales, feb_sales, mar_sales'). The category set is closed; "
            "the user is NOT expected to write dynamic SQL.\n"
            "3) The prompt MUST name each target column AND the aggregation function "
            "(SUM, MAX, MIN, COUNT, AVG). Forbidden: 'pivot the data' without naming "
            "columns; 'aggregate by month' without naming the function.\n"
            "4) The answer_key MUST use the form:\n"
            "   `aggfn(CASE WHEN category_column = 'val_a' THEN value_column END) AS col_a,`\n"
            "   `aggfn(CASE WHEN category_column = 'val_b' THEN value_column END) AS col_b,`\n"
            "   ... grouped by the entity key. The CASE returns NULL on non-matching "
            "rows, which most aggregations skip naturally.\n"
            "5) For SUM and COUNT pivots, wrap with `COALESCE(..., 0)` ONLY if the "
            "prompt asks for 0 instead of NULL when an entity has no rows in that "
            "category. The prompt MUST be explicit about NULL vs 0 expected output.\n"
            "6) Test data MUST include AT LEAST one entity that is missing rows for "
            "AT LEAST one category, so the user sees how the CASE+aggregation handles "
            "the empty bucket (NULL by default, 0 if COALESCE'd).\n"
            "7) Test data MUST include AT LEAST one entity with MULTIPLE rows in the "
            "SAME category, so the aggregation actually does work (SUM combines them, "
            "MAX picks one, etc.).\n"
            "8) The prompt MUST explicitly state the full ordered output column list "
            "AND the ORDER BY clause for the final result.\n"
            "9) Set classification.recipe to `reshape`, classification.input_arrival "
            "to `single_table` or `join`, classification.output_shape to `fewer_rows` "
            "(one row per entity in the wide output)."
        )
    elif qtype == "unpivot":
        base += (
            "Build an UNPIVOT problem (wide format to long format) using PostgreSQL. "
            "PostgreSQL has no native UNPIVOT; the canonical approach is `UNION ALL` "
            "of one SELECT per source column, each with a literal label.\n\n"
            "Hard requirements:\n"
            "1) Schema MUST contain ONE main wide-format source table with shape "
            "(entity_key, value_for_cat_a, value_for_cat_b, value_for_cat_c, ...). "
            "Examples: quarterly_revenue(company_id, q1_rev, q2_rev, q3_rev, q4_rev), "
            "patient_vitals(patient_id, heart_rate, blood_pressure, oxygen_sat, temperature), "
            "monthly_signups(team_id, jan_signups, feb_signups, mar_signups). The wide "
            "table MUST have AT LEAST 3 value columns to unpivot.\n"
            "2) The prompt MUST explicitly name the output schema: the entity key column, "
            "the new label column (e.g., quarter, metric_name), and the new value column "
            "(e.g., revenue, measurement). The prompt MUST also specify the EXACT label "
            "string for each source column (e.g., q1_rev becomes label 'Q1', not 'q1' "
            "or 'first_quarter').\n"
            "3) The answer_key MUST use the form:\n"
            "   `SELECT entity_key, 'label_a' AS new_label, col_a AS new_value FROM t`\n"
            "   `UNION ALL`\n"
            "   `SELECT entity_key, 'label_b' AS new_label, col_b AS new_value FROM t`\n"
            "   ... one branch per source column. Use UNION ALL (not UNION) to keep "
            "duplicate value rows.\n"
            "4) The prompt MUST be explicit about NULL handling: either 'include rows "
            "where the source column is NULL' (no filter) or 'exclude rows where the "
            "value is NULL' (add `WHERE col_a IS NOT NULL` to each branch, or wrap with "
            "an outer `WHERE new_value IS NOT NULL`).\n"
            "5) Test data MUST include AT LEAST one row with a NULL in one of the wide "
            "columns so the NULL handling rule is exercised.\n"
            "6) Test data MUST include AT LEAST 3 entities so the unpivoted output has "
            "(3 entities) x (number of columns unpivoted) rows minus any NULL exclusions.\n"
            "7) The prompt MUST explicitly state the output column names AND the ORDER BY "
            "clause for the final result (typically entity_key ASC, then label ASC).\n"
            "8) Postgres alternative form: `SELECT entity_key, v.label, v.value FROM t "
            "CROSS JOIN LATERAL (VALUES ('label_a', col_a), ('label_b', col_b), "
            "('label_c', col_c)) AS v(label, value)`. Either form is acceptable; the "
            "UNION ALL form is more portable and easier to read.\n"
            "9) Set classification.recipe to `reshape`, classification.input_arrival "
            "to `single_table`, classification.output_shape to `same_rows` is wrong &mdash; "
            "use a clarifying note in composite_moves; the row count GROWS by a factor "
            "of (number of unpivoted columns)."
        )
    elif qtype == "cross_join":
        base += (
            "Build a CROSS JOIN problem where the CROSS JOIN is the NATURAL choice, "
            "not a gratuitous Cartesian product. The user must understand WHY the cross "
            "join is needed. Pick ONE of these three shapes per generation (rotate "
            "across runs to expose the user to all of them):\n\n"
            "SHAPE A: Calendar / Date Skeleton + LEFT JOIN Actuals\n"
            "  - Use case: 'Report daily/weekly counts; days with no rows must show 0, not be missing.'\n"
            "  - Schema: ONE main event/transaction table with a date column + one entity table.\n"
            "  - Skeleton built via `generate_series(start, end, INTERVAL '1 day')::date` "
            "or a fixed VALUES list. Skeleton CROSS JOINed with the entity table to "
            "produce all (entity, date) combinations, then LEFT JOINed to the actuals "
            "with COALESCE(metric, 0).\n"
            "  - Test data MUST include AT LEAST one entity-day combination with NO "
            "actuals so the user sees the LEFT JOIN keeping the row and COALESCE "
            "filling the 0.\n\n"
            "SHAPE B: Categorical Skeleton (Fixed Bucket Fan-Out)\n"
            "  - Use case: 'Count entities in each of N fixed categories; categories "
            "with no entities must still appear in the output.'\n"
            "  - Schema: ONE main entity table + a small VALUES/UNION ALL list of "
            "category labels (e.g., 'Low Salary', 'Average Salary', 'High Salary' from "
            "the salary band shape).\n"
            "  - The category list CROSS JOINed with the entity table, then "
            "`COUNT(CASE WHEN c.category = 'Low' AND entity.metric < 20000 THEN 1 END)` "
            "matches each entity to ONE bucket per category check.\n"
            "  - Test data MUST include AT LEAST one category that has ZERO matching "
            "entities so the user sees the cross join preserving the empty bucket.\n\n"
            "SHAPE C: All-Pairs Self Cross-Join\n"
            "  - Use case: 'Find every pair of (X, Y) where ...' or 'Compare every "
            "row to every other row in the same table.'\n"
            "  - Schema: ONE main table (employees, products, players, customers) "
            "where pairs need to be compared.\n"
            "  - The query uses `FROM t a CROSS JOIN t b` (or comma-join) with "
            "`WHERE a.id < b.id` to dedupe pairs and exclude self-pairs.\n"
            "  - The prompt MUST explicitly define what constitutes a valid pair "
            "(e.g., 'pairs that share a department', 'pairs whose price difference "
            "is at most $10').\n"
            "  - Test data MUST include rows that are similar enough to test the "
            "pair filter (so the result isn't trivially empty).\n\n"
            "Universal hard requirements (apply to whichever shape was chosen):\n"
            "1) The prompt MUST explicitly motivate WHY a cross join is needed. "
            "Forbidden phrasings: 'cross join the tables' (gratuitous). Required: "
            "'every category must appear even if no rows match', 'report every day in "
            "the range even when no events happened', 'find every pair of products that...'\n"
            "2) The prompt MUST explicitly state the output column names AND the "
            "ORDER BY clause for the final result.\n"
            "3) For SHAPE A and SHAPE B, the answer_key MUST use COALESCE on the "
            "aggregated metric so missing combinations show 0 (not NULL) when the prompt "
            "asks for that. The prompt MUST be explicit about NULL vs 0.\n"
            "4) For SHAPE C, the answer_key MUST include the dedupe filter "
            "(`a.id < b.id` or `a.id <> b.id` depending on whether order matters). "
            "Forbidden: returning (A, B) and (B, A) as separate rows when the prompt "
            "asks for unordered pairs.\n"
            "5) Schema DDL must be valid PostgreSQL. Use `generate_series(...)::date` "
            "for date skeletons, NOT MySQL-specific syntax.\n"
            "6) Test data must be larger than the example data and include the edge "
            "cases relevant to the chosen shape (missing days, empty buckets, "
            "near-tie pairs).\n"
            "7) Set classification.recipe to `reshape` (for SHAPE A and SHAPE B "
            "skeleton fan-outs) or `enrich-join` (for SHAPE C all-pairs), "
            "classification.input_arrival to `join`, classification.output_shape to "
            "`same_rows` for skeletons or `fewer_rows` if the query also filters."
        )
    elif qtype == "date_operations":
        base += (
            "Build a DATE OPERATIONS problem where date or timestamp manipulation is "
            "the CENTERPIECE of the solution, not incidental. The problem must require "
            "the user to use AT LEAST ONE of these PostgreSQL date methods (rotate "
            "across runs to expose the user to all of them):\n\n"
            "TECHNIQUES (the chosen problem must exercise at least one):\n"
            "  - DATE_TRUNC for cohort bucketing (e.g., `DATE_TRUNC('month', signup_ts)::date` "
            "for monthly cohort match; `DATE_TRUNC('week', order_date)` for weekly rollup).\n"
            "  - EXTRACT for component access (e.g., `EXTRACT(YEAR FROM order_date)`, "
            "`EXTRACT(DOW FROM order_date)` for day-of-week, `EXTRACT(HOUR FROM event_ts)`).\n"
            "  - Date arithmetic: `DATE - INT` returns a date (e.g., `CURRENT_DATE - 30` "
            "is 30 days ago), `date2 - date1` returns an integer day count, "
            "`date + INTERVAL '7 days'` returns a date or timestamp.\n"
            "  - 'X days ago' filtering: `WHERE event_date < CURRENT_DATE - 90` for "
            "events older than 90 days. 'Ago' means smaller (older), so use `<`.\n"
            "  - Inclusive day count gotcha: `Jan 10 - Jan 1 = 9` but the trial spans "
            "10 days; the answer needs `(end - start) + 1`.\n"
            "  - EXTRACT(EPOCH FROM interval) for durations in seconds; divide by 60 "
            "for minutes, 3600 for hours (e.g., '`EXTRACT(EPOCH FROM (end_ts - start_ts)) / 3600`).\n"
            "  - Cohort match via DATE_TRUNC: `DATE_TRUNC('month', signup_date) = "
            "DATE_TRUNC('month', purchase_date)` (includes year, so 2024-01 is not "
            "the same as 2025-01).\n"
            "  - generate_series for filling a date skeleton: "
            "`generate_series(start, end, INTERVAL '1 day')::date` to ensure every "
            "day in the range appears even when the source has gaps.\n\n"
            "Common problem shapes the LLM should rotate through:\n"
            "  - 'For each user, find the time-to-X in days/hours' (date subtraction + "
            "EXTRACT EPOCH).\n"
            "  - 'Group orders by month and report monthly revenue' (DATE_TRUNC).\n"
            "  - 'Find users whose last activity was more than N days ago' (CURRENT_DATE - N).\n"
            "  - 'Find the day-of-week with highest activity per user' (EXTRACT DOW + "
            "GROUP BY + ranking).\n"
            "  - 'Calculate average days between consecutive events per user' (LAG date "
            "+ subtraction).\n"
            "  - 'Find trial duration in days inclusive' (end - start + 1).\n"
            "  - 'Report daily counts for every day in the range, including zero days' "
            "(generate_series + LEFT JOIN + COALESCE 0).\n\n"
            "Universal hard requirements:\n"
            "1) The schema MUST contain AT LEAST ONE date or timestamp column with "
            "realistic values (orders dates, signup timestamps, event times). The "
            "centerpiece of the solution must be a date method, not a side effect.\n"
            "2) The prompt MUST explicitly name the date method or operation needed, "
            "OR phrase the requirement so a single date method is the obvious answer "
            "(e.g., 'group by month' implies DATE_TRUNC; 'older than 90 days' implies "
            "CURRENT_DATE - 90; 'duration in hours' implies EXTRACT EPOCH).\n"
            "3) The prompt MUST explicitly state whether day counts are inclusive or "
            "exclusive when relevant ('the trial lasted X days inclusive of both "
            "endpoints' vs 'X days passed between the two events').\n"
            "4) For 'X days ago' style filters, the prompt MUST clarify what 'today' "
            "means: use `CURRENT_DATE` for date-only comparisons, `CURRENT_TIMESTAMP` "
            "or `NOW()` for timestamps. The answer_key must match.\n"
            "5) For interval parameter pitfall: if the answer uses an interval driven "
            "by a column or parameter (not a literal), use `(col_value || ' days')::INTERVAL` "
            "or `CURRENT_DATE - col_value` (DATE - INT works). NEVER write "
            "`INTERVAL 'col_value days'` (string interpolation does not happen).\n"
            "6) Test data MUST include boundary cases relevant to the chosen technique: "
            "month-end, year-end, leap year (Feb 29 if the date range includes 2020 or "
            "2024), or the exact 'X days ago' cutoff so the user sees how `<` vs `<=` "
            "matters.\n"
            "7) The prompt MUST explicitly state the output column names AND the "
            "ORDER BY clause for the final result.\n"
            "8) Schema DDL must be valid PostgreSQL (use TIMESTAMP or DATE types, "
            "not MySQL DATETIME). Use `CURRENT_DATE` and `CURRENT_TIMESTAMP`, not "
            "`NOW()` (NOW() works but CURRENT_TIMESTAMP is more standard).\n"
            "9) Set classification.recipe to `time-window` (most date problems are "
            "time-window shaped), classification.input_arrival to `single_table` or "
            "`join`, classification.output_shape to whatever the problem produces "
            "(usually `fewer_rows` for aggregations, `same_rows` for row-level "
            "transformations)."
        )
    return base


def _validate_problem(problem: Dict[str, Any]) -> tuple:
    """
    Validate by RUNNING the answer_key and using its actual output as the
    source of truth. Replaces example_output_columns/rows and
    test_expected_columns/rows with what the answer_key actually produces.
    This guarantees the user's grading is self-consistent with the answer.

    Failure modes that still trigger a retry:
      - schema_ddl, example_input_data, or test_data fail to load
      - answer_key throws a SQL error
      - answer_key returns no result set (no trailing SELECT)

    Returns (is_valid: bool, error_msg: str). Mutates `problem` on success.
    """
    import sandbox as sbx  # deferred to avoid circular import
    dialect = problem.get("_meta", {}).get("dialect")
    schema = problem.get("schema_ddl", "") or ""
    answer = problem.get("answer_key", "") or ""
    if not dialect:
        return False, "Missing dialect in metadata."
    if not schema.strip():
        return False, "Missing schema_ddl."
    if not answer.strip():
        return False, "Missing answer_key."

    # --- Run answer_key against example data, capture truth ---
    try:
        sbx.reset(dialect)
        sbx.execute_script(dialect, schema)
        sbx.execute_script(dialect, problem.get("example_input_data", "") or "")
    except Exception as e:
        return False, f"Loading schema/example_input_data failed: {e}"
    df_ex, err = sbx.run_query(dialect, answer)
    if err:
        return False, f"Answer key errored on example data: {err}"
    if df_ex is None or df_ex.empty and not list(df_ex.columns):
        return False, "Answer key produced no result set on example data (missing trailing SELECT?)."
    # Replace the problem's example output with the actual result
    problem["example_output_columns"] = list(df_ex.columns)
    problem["example_output_rows"] = df_ex.astype(object).where(
        df_ex.notna(), None
    ).values.tolist()

    # --- Run answer_key against hidden test data, capture truth ---
    try:
        sbx.reset(dialect)
        sbx.execute_script(dialect, schema)
        sbx.execute_script(dialect, problem.get("test_data", "") or "")
    except Exception as e:
        return False, f"Loading schema/test_data failed: {e}"
    df_te, err = sbx.run_query(dialect, answer)
    if err:
        return False, f"Answer key errored on test data: {err}"
    if df_te is None or df_te.empty and not list(df_te.columns):
        return False, "Answer key produced no result set on test data (missing trailing SELECT?)."
    problem["test_expected_columns"] = list(df_te.columns)
    problem["test_expected_rows"] = df_te.astype(object).where(
        df_te.notna(), None
    ).values.tolist()

    # Sanity: column shape must match between example and test
    if list(df_ex.columns) != list(df_te.columns):
        return False, (
            f"Answer key returned different columns on example vs test data: "
            f"{list(df_ex.columns)} vs {list(df_te.columns)}."
        )

    return True, "Valid."


def generate_problem(
    qtype: str,
    dialect: str,
    max_retries: int = 4,
    on_attempt=None,
) -> Optional[Dict[str, Any]]:
    """
    Generate a fresh problem and validate it before returning. Retries with
    error context if the answer_key doesn't actually produce the claimed
    expected outputs.

    `on_attempt` is an optional callback `fn(attempt_num, total, last_error)`
    so the notebook can surface progress.
    """
    if qtype not in QUESTION_TYPES:
        print(f"Unknown question type: {qtype}")
        return None
    if dialect not in QUESTION_TYPES[qtype]["dialects"]:
        print(f"Question type '{qtype}' is not supported in dialect '{dialect}'.")
        return None

    last_error = None
    scenario = _pick_scenario(qtype)  # pick once so retries refine the same scenario
    # For dml, pick which operation (UPDATE / DELETE / INSERT) once so retries stay
    # consistent. Each option has equal probability.
    dml_op = random.choice(["UPDATE", "DELETE", "INSERT"]) if qtype == "dml" else None
    # For union_islands, pick which flavor of gaps-and-islands at 25/25/25/25 once so
    # retries stay consistent. Flavors:
    #   date_calendar              - dates with no missing days expected; uses date - rn_per_state
    #   date_sequence              - dates with possible missing days; uses rn_overall - rn_per_state
    #   integer_seq                - integer ids in a single table; uses id - rn (no UNION)
    #   partitioned_status_periods - per-entity timelines, two source tables UNION'd by status,
    #                                BOTH windows partitioned by entity key
    islands_flavor = random.choice([
        "date_calendar", "date_sequence", "integer_seq", "partitioned_status_periods"
    ]) if qtype == "union_islands" else None
    # For percentile_metrics, pick a flavor based on dialect (PERCENTILE_CONT is
    # Postgres-only; NTILE and PERCENT_RANK work in both):
    #   percentile_aggregate - PERCENTILE_CONT/DISC for median, P75, P90, P95, P99 (Postgres only)
    #   ntile_buckets        - NTILE(n) for quartile/decile bucketing (both dialects)
    #   top_n_percent        - PERCENT_RANK or ROW_NUMBER/COUNT for top X% selection (both dialects)
    percentile_flavor = None
    if qtype == "percentile_metrics":
        if dialect == "postgresql":
            percentile_flavor = random.choice(["percentile_aggregate", "ntile_buckets", "top_n_percent"])
        else:
            percentile_flavor = random.choice(["ntile_buckets", "top_n_percent"])
    for attempt in range(1, max_retries + 1):
        if on_attempt:
            try:
                on_attempt(attempt, max_retries, last_error)
            except Exception:
                pass

        user_prompt = _topic_specific_guidance(qtype, dialect, scenario=scenario, dml_op=dml_op, islands_flavor=islands_flavor, percentile_flavor=percentile_flavor)
        if last_error:
            user_prompt += (
                "\n\nPREVIOUS ATTEMPT FAILED VALIDATION. The answer_key did not "
                "actually produce the expected outputs. Error from the validator:\n"
                f"{last_error}\n\n"
                "Re-think the problem so the prompt, example_input_data, "
                "example_output_rows, test_data, test_expected_rows, AND answer_key "
                "are all internally consistent. Trace the answer_key row by row "
                "before returning."
            )
        user_prompt += "\n\nReturn the JSON object now."

        text = _call_claude(GENERATOR_SYSTEM, user_prompt, max_tokens=4000)
        parsed = _extract_json(text)
        if not parsed:
            last_error = "Could not parse JSON from response."
            continue
        parsed["_meta"] = {
            "question_type": qtype,
            "dialect": dialect,
            "generated_at": datetime.now().isoformat(),
            "problem_id": uuid.uuid4().hex[:12],
            "validation_attempts": attempt,
            "scenario": scenario,
            "dml_op": dml_op,  # None for non-dml types; UPDATE/DELETE/INSERT for dml
            "islands_flavor": islands_flavor,  # None for non-union_islands; date_calendar/date_sequence/integer_seq/partitioned_status_periods otherwise
            "percentile_flavor": percentile_flavor,  # None for non-percentile_metrics; percentile_aggregate/ntile_buckets/top_n_percent otherwise
        }
        ok, err = _validate_problem(parsed)
        if ok:
            return parsed
        last_error = err

    print(
        f"Generation failed validation after {max_retries} attempts. "
        f"Last error: {last_error}"
    )
    return None


# ============================================================
# Diagnostic feedback
# ============================================================

DIAGNOSTIC_SYSTEM = """\
You are a SQL coach grading a student's problem analysis. The student fills out a
diagnostic form before writing SQL. Give terse, encouraging feedback.

Output MUST be a single JSON object inside a ```json fenced block:
{
  "paraphrase_feedback": "1-2 sentences on whether their paraphrase captures the goal",
  "input_classification_correct": true | false,
  "input_classification_feedback": "1 sentence",
  "output_shape_correct": true | false,
  "output_shape_feedback": "1 sentence",
  "recipe_correct": true | false,
  "recipe_feedback": "1 sentence",
  "composite_moves_feedback": "1-2 sentences on whether their move sequence is reasonable",
  "overall": "one short sentence summary"
}

Hard rules:
- Be terse, lay language, no metaphors.
- Treat near-correct answers as correct (e.g., "row filter" matches "row-filter").
- Do NOT show the answer or write SQL for them.
"""


def grade_diagnostic(problem: Dict[str, Any], answers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    user_prompt = f"""Problem prompt:
{problem.get('prompt', '')}

Answer key classification (do not reveal to student):
{json.dumps(problem.get('classification', {}), indent=2)}

Student answers:
- Paraphrase: {answers.get('paraphrase', '')}
- Input classification: {answers.get('input_arrival', '')}
- Output shape: {answers.get('output_shape', '')}
- Recipe: {answers.get('recipe', '')}
- Composite moves: {answers.get('composite_moves', '')}

Grade the student.
"""
    text = _call_claude(DIAGNOSTIC_SYSTEM, user_prompt, max_tokens=1000)
    return _extract_json(text)


# ============================================================
# Hint progression
# ============================================================

def get_hint(problem: Dict[str, Any], hint_index: int) -> str:
    hints = problem.get("hints", [])
    if not hints:
        return "(No hints available for this problem.)"
    idx = min(hint_index, len(hints) - 1)
    return hints[idx]


# ============================================================
# Persistence
# ============================================================

def save_problem(problem: Dict[str, Any], outputs_dir: str) -> str:
    """Save problem JSON to disk. Returns the file path."""
    os.makedirs(outputs_dir, exist_ok=True)
    pid = problem.get("_meta", {}).get("problem_id", uuid.uuid4().hex[:12])
    qtype = problem.get("_meta", {}).get("question_type", "unknown")
    dialect = problem.get("_meta", {}).get("dialect", "unknown")
    fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{dialect}_{qtype}_{pid}.json"
    path = os.path.join(outputs_dir, fname)
    with open(path, "w") as f:
        json.dump(problem, f, indent=2, default=str)
    return path


def load_problem(path: str) -> Dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def list_problems(outputs_dir: str, dialect: Optional[str] = None, qtype: Optional[str] = None) -> List[Dict[str, str]]:
    """List saved problems, optionally filtered. Returns list of {path, title, dialect, qtype, generated_at}."""
    if not os.path.isdir(outputs_dir):
        return []
    out = []
    for fname in sorted(os.listdir(outputs_dir), reverse=True):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(outputs_dir, fname)
        try:
            p = load_problem(path)
            meta = p.get("_meta", {})
            if dialect and meta.get("dialect") != dialect:
                continue
            if qtype and meta.get("question_type") != qtype:
                continue
            out.append({
                "path": path,
                "title": p.get("title", fname),
                "dialect": meta.get("dialect", ""),
                "qtype": meta.get("question_type", ""),
                "generated_at": meta.get("generated_at", ""),
            })
        except Exception:
            continue
    return out


def save_solved(problem: Dict[str, Any], user_solution: str, outputs_dir: str) -> str:
    """Record a successful solve."""
    os.makedirs(outputs_dir, exist_ok=True)
    pid = problem.get("_meta", {}).get("problem_id", uuid.uuid4().hex[:12])
    record = {
        "problem": problem,
        "user_solution": user_solution,
        "solved_at": datetime.now().isoformat(),
    }
    path = os.path.join(outputs_dir, f"{pid}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2, default=str)
    return path


# ============================================================
# Helpers used by the notebook
# ============================================================

def expected_to_dataframe(problem: Dict[str, Any], which: str = "example") -> pd.DataFrame:
    """which: 'example' or 'test'."""
    if which == "example":
        cols = problem.get("example_output_columns", [])
        rows = problem.get("example_output_rows", [])
    else:
        cols = problem.get("test_expected_columns", [])
        rows = problem.get("test_expected_rows", [])
    return pd.DataFrame(rows, columns=cols)


# ============================================================
# Rendering helpers for the notebook UI
# Parse CREATE TABLE / INSERT INTO / prompt strings and emit HTML
# tables and bullet lists so the notebook never shows blobs of SQL.
# ============================================================

import re as _re


def _split_top_level(s: str):
    """Split a string on commas at paren-depth 0, respecting single quotes."""
    parts, depth, cur, in_str = [], 0, '', False
    for ch in s:
        if in_str:
            cur += ch
            if ch == "'":
                in_str = False
        elif ch == "'":
            in_str = True
            cur += ch
        elif ch == '(':
            depth += 1
            cur += ch
        elif ch == ')':
            depth -= 1
            cur += ch
        elif ch == ',' and depth == 0:
            parts.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def parse_create_tables(ddl: str):
    """Return [(table_name, [(col_name, type), ...]), ...]. Handles nested parens like VARCHAR(20), DECIMAL(10,2)."""
    out = []
    if not ddl:
        return out
    # Find each CREATE TABLE header, then walk the body with paren balancing
    header = _re.compile(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w_]+)\s*\(', _re.IGNORECASE)
    pos = 0
    while True:
        m = header.search(ddl, pos)
        if not m:
            break
        name = m.group(1)
        i = m.end()  # right after the opening (
        depth = 1
        body_start = i
        while i < len(ddl) and depth > 0:
            ch = ddl[i]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            i += 1
        body = ddl[body_start:i - 1]  # exclude the closing )
        pos = i
        cols = _split_top_level(body)
        parsed = []
        for col in cols:
            up = col.strip().upper()
            if up.startswith(('PRIMARY KEY', 'FOREIGN KEY', 'CONSTRAINT', 'UNIQUE', 'CHECK')):
                continue
            parts = col.strip().split(None, 1)
            if len(parts) == 2:
                parsed.append((parts[0], parts[1].rstrip(',')))
            elif len(parts) == 1:
                parsed.append((parts[0], ''))
        out.append((name, parsed))
    return out


def parse_inserts(sql: str):
    """Return {table_name: (col_names, [row_values, ...])}."""
    out = {}
    pattern = r"INSERT\s+INTO\s+([\w_]+)\s*\(([^)]+)\)\s*VALUES\s*(.+?);"
    for m in _re.finditer(pattern, sql or '', _re.IGNORECASE | _re.DOTALL):
        name = m.group(1)
        cols = [c.strip() for c in m.group(2).split(',')]
        rows = _parse_value_rows(m.group(3))
        if name in out:
            out[name][1].extend(rows)
        else:
            out[name] = (cols, rows)
    return out


def _parse_value_rows(s: str):
    rows, depth, cur_row, cur_val, in_str = [], 0, [], '', False
    for ch in s:
        if in_str:
            cur_val += ch
            if ch == "'":
                in_str = False
        elif ch == "'":
            in_str = True
            cur_val += ch
        elif ch == '(' and depth == 0:
            depth, cur_row, cur_val = 1, [], ''
        elif ch == ')' and depth == 1:
            cur_row.append(cur_val.strip())
            rows.append(cur_row)
            depth, cur_val = 0, ''
        elif ch == ',' and depth == 1:
            cur_row.append(cur_val.strip())
            cur_val = ''
        elif depth == 1:
            cur_val += ch
    return rows


def schema_to_html(ddl: str) -> str:
    """Render every CREATE TABLE statement as a Column / Type HTML table."""
    tables = parse_create_tables(ddl)
    if not tables:
        return f'<pre style="background:#0d1117; color:#e6edf3; padding:8px; border-radius:4px; font-size:12px; white-space:pre-wrap;">{ddl}</pre>'
    parts = []
    for name, cols in tables:
        df = pd.DataFrame(cols, columns=['Column', 'Type'])
        parts.append(
            f'<div style="margin-bottom:12px;">'
            f'<div style="font-weight:600; margin:6px 0; font-size:13px;">Table: <code>{name}</code></div>'
            + df.to_html(index=False, classes='nb-schema-table')
            + '</div>'
        )
    return ''.join(parts)


def _clean_sql_value(v: str) -> str:
    """Strip wrapping single quotes from string literals; pass numerics and NULL through."""
    s = v.strip()
    if len(s) >= 2 and s.startswith("'") and s.endswith("'"):
        # Unescape doubled single quotes inside ('It''s' -> "It's")
        return s[1:-1].replace("''", "'")
    return s


def insert_data_to_html(sql: str) -> str:
    """Render every INSERT INTO statement as an HTML table of the rows it inserts."""
    tables = parse_inserts(sql)
    if not tables:
        return f'<pre style="background:#0d1117; color:#e6edf3; padding:8px; border-radius:4px; font-size:12px; white-space:pre-wrap;">{sql}</pre>'
    parts = []
    for name, (cols, rows) in tables.items():
        cleaned = [[_clean_sql_value(v) for v in row] for row in rows]
        df = pd.DataFrame(cleaned, columns=cols)
        parts.append(
            f'<div style="margin-bottom:12px;">'
            f'<div style="font-weight:600; margin:6px 0; font-size:13px;">Data: <code>{name}</code></div>'
            + df.to_html(index=False, classes='nb-data-table')
            + '</div>'
        )
    return ''.join(parts)


def prompt_to_bullets(prompt: str) -> str:
    """Split a prompt into sentences and render as a bulleted list."""
    if not prompt:
        return ''
    raw = _re.split(r'(?<=[.!?])\s+', prompt.strip())
    sentences = [s.strip() for s in raw if s.strip()]
    items = ''.join(f'<li style="margin-bottom:4px;">{s}</li>' for s in sentences)
    return f'<ul style="line-height:1.6; margin:0 0 8px 18px; padding-left:0;">{items}</ul>'
