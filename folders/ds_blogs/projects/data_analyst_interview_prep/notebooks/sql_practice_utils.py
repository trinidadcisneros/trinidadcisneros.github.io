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
from typing import Optional, Dict, Any, List, Tuple

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
    # Lazy reinit: if the Claude client never initialized (e.g., the first
    # init_claude() call hit an API overload), try once more here so a stuck
    # session can self-heal once the API is healthy again. Without this every
    # subsequent call returns None silently and the generator retry loop just
    # reports "Could not parse JSON from response." over and over.
    global _CLIENT
    if not _CLIENT:
        print("Claude client not initialized — attempting reinit ...")
        if not init_claude(_MODEL):
            print(
                "Claude client still not available. Re-run the setup cell once "
                "the API is healthy, or call spu.init_claude() manually."
            )
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
        # Surface the underlying error so the generator's retry loop can show
        # something more useful than the generic "Could not parse JSON" message
        # that follows when _call_claude returns None.
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
        "label": "DML — any (random UPDATE / DELETE / INSERT)",
        "description": "Mutation problems with explicit conditions; final SELECT confirms result.",
        "dialects": ["postgresql", "mysql"],
        "hidden_in_picker": True,  # superseded by the three split options below
    },
    "dml_update": {
        "label": "DML — UPDATE",
        "description": "UPDATE-focused mutation problem with explicit WHERE conditions; final SELECT confirms result.",
        "dialects": ["postgresql", "mysql"],
    },
    "dml_delete": {
        "label": "DML — DELETE",
        "description": "DELETE-focused mutation problem; final SELECT confirms remaining rows.",
        "dialects": ["postgresql", "mysql"],
    },
    "delete_duplicates": {
        "label": "Dedup (delete duplicate rows)",
        "description": "Single-table dedup: physically DELETE duplicate rows, keeping one survivor per key. Methods: keep the lowest id (NOT IN MIN), self-join delete the higher-id twin, or ROW_NUMBER then delete rn > 1. Answer is a DELETE + a trailing SELECT showing the survivors.",
        "dialects": ["postgresql", "mysql"],
    },
    "dml_insert": {
        "label": "DML — INSERT",
        "description": "INSERT-focused problem (often with SELECT-from-source or conflict handling); final SELECT confirms inserted rows.",
        "dialects": ["postgresql", "mysql"],
    },
    "filter_strategies": {
        "label": "Filter — strategies (WHERE / HAVING rotation)",
        "description": "A single filtering problem; rotates EQUALLY across comparison & boolean, NULL-aware, pattern (LIKE/regex), membership (IN/EXISTS), anti-join (NOT IN/NOT EXISTS), and group-threshold (GROUP BY + HAVING across distinct rows).",
        "dialects": ["postgresql", "mysql"],
    },
    "scalar_extract": {
        "label": "Scalar (one value: top-1 / Nth highest / aggregate / ratio)",
        "description": "A single table reduces to EXACTLY ONE row, one value: a whole-table aggregate, the top-1 row (ORDER BY ... LIMIT 1), the 2nd/Nth highest (LIMIT 1 OFFSET N-1 or a NULL-safe subquery-in-SELECT), or a single ratio. Centers the LIMIT/OFFSET shape and the WHERE-returns-0-rows-instead-of-NULL trap.",
        "dialects": ["postgresql", "mysql"],
    },
    "anti_join": {
        "label": "Anti-join (never / did not / no match)",
        "description": "Keep rows in one set with NO matching row in another (customers who never ordered, products never sold). NOT EXISTS (NULL-safe), LEFT JOIN ... WHERE right IS NULL, or NOT IN (only when the subquery column is non-NULL).",
        "dialects": ["postgresql", "mysql"],
    },
    "window_edge": {
        "label": "Window Function Edge Cases",
        "description": "ROWS vs RANGE, frame edges, RANK vs DENSE_RANK vs ROW_NUMBER nuance.",
        "dialects": ["postgresql", "mysql"],
    },
    "union_islands": {
        "label": "Gaps-and-Islands (UNION dates + integer ids)",
        "description": "Collapse consecutive rows into [start, end] ranges or measure streak length using the row-number trick. Randomly picks one of five flavors per generation: (1) date with no missing days (date - rn form), (2) date with possible missing days (rn_overall - rn_per_state form), (3) integer ids in a single table (id - rn form, no UNION), (4) per-entity status periods (two source tables UNION'd by status, both windows partitioned by entity), and (5) consecutive_day_streak_per_entity (medium / hard only): per entity streak detection with DUPLICATE same day source rows that must be deduped FIRST, then HAVING COUNT(*) >= N gate, then EXISTS / IN membership semantics in the final SELECT; LeetCode #1454 Active Users shape.",
        "dialects": ["postgresql", "mysql"],
    },
    "percentile_metrics": {
        "label": "Percentile & Distribution Metrics",
        "description": "Calculate percentiles, medians, quartile/decile bucketing, or top N% rankings. Randomly picks one flavor per generation: PERCENTILE_CONT/DISC for percentile aggregates (Postgres only), NTILE for quartile/decile buckets (both dialects), PERCENT_RANK for top N% selection (both dialects), `extreme_exclusion` (whole population DENSE_RANK ASC + DESC, exclude both ends; LeetCode #1149 Activities Without Extremes shape), or `extreme_exclusion_per_group` (per partition DENSE_RANK ASC + DESC + HAVING MIN(rn) > 1 across the entity's rows; LeetCode #1412 Quiet Students shape).",
        "dialects": ["postgresql", "mysql"],
    },
    "pivot": {
        "label": "Pivot (long to wide / signed aggregate / membership filter / threshold per category)",
        "description": "CASE inside aggregate. Randomly picks one flavor per generation: (1) `multi_column_pivot` reshapes long to wide with one CASE per target column (jan_sales, feb_sales, ...); (2) `signed_aggregate` collapses opposing categories (Buy / Sell, debit / credit, income / expense) into a single net total via SUM(CASE ... +price ... -price END); (3) `membership_filter` uses CASE in HAVING as a set membership gate (bought ALL of X, NONE of Y) via BOOL_OR per category or MAX(CASE ... THEN 1 ELSE 0 END); (4) `threshold_per_category` uses SUM(CASE) >= N in HAVING as a numeric threshold gate across multiple categories (spent >= $100 in June AND >= $100 in July). All four use PostgreSQL CASE inside an aggregate.",
        "dialects": ["postgresql"],
    },
    "unpivot": {
        "label": "Unpivot (wide to long)",
        "description": "Reshape wide-format columns into long-format rows using UNION ALL of SELECTs that pull each column with a literal label. PostgreSQL.",
        "dialects": ["postgresql"],
    },
    "matchup_unpivot": {
        "label": "Matchup Unpivot (two-sided rows -> per-team aggregate)",
        "description": "A single row holds both sides of a head-to-head event: two participant columns and their two scores (home_team/away_team, host_goals/guest_goals). UNION ALL splits it into one row per participant carrying its own score and the opponent's, a CASE turns each matchup into a result (win/draw/loss -> points), then GROUP BY participant aggregates, typically LEFT JOINed to a teams/players dimension so a participant with zero games still appears with 0.",
        "dialects": ["postgresql", "mysql"],
    },
    "gated_lookup": {
        "label": "Gated Lookup (cross-table threshold gates a per-group pick)",
        "description": "Two tables share an entity key: one carries a gating attribute (a rating, score, flag, status, or date), the other carries values to choose from (prices, bids, dates). Look up the gate, pick a per-group target row from the second table (cheapest, highest, earliest, latest), then a CASE/WHERE on the gate decides whether to keep that value or substitute a fallback (0, NULL, or drop the row). The gate reaching across tables is the defining move; it is not a sum/avg aggregate.",
        "dialects": ["postgresql", "mysql"],
    },
    "left_join_on_filter": {
        "label": "LEFT JOIN ON vs WHERE (right-side filter placement)",
        "description": "A LEFT JOIN must keep every left row, but a condition on the RIGHT table is involved (a date window, a status, a category, a numeric threshold). Putting that right-side filter in ON preserves unmatched left rows (they show NULL / 0); putting the same filter in WHERE silently drops them, turning the LEFT JOIN into an INNER JOIN. Rotates across six shapes: right-side date window, status/category, numeric threshold, a left-filter-in-WHERE plus right-filter-in-ON combo, SUM/AVG with COALESCE, and a boolean existence flag. The problem is built so at least one left entity has no qualifying right row, which exposes the difference between the correct ON placement and the WHERE trap.",
        "dialects": ["postgresql", "mysql"],
    },
    "enrich_join": {
        "label": "Look up columns from another table (enrich-join)",
        "description": "JOIN to pull a column/value onto each row (not aggregate-per-group). Methods: straight lookup/enrich, self-join (one table, two roles), cross join (all combinations), match a per-group value, or compound eligibility (roll up then multi-condition filter).",
        "dialects": ["postgresql", "mysql"],
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
    "series_generation": {
        "label": "Series Generation (generate_series)",
        "description": "Practice generate_series as the centerpiece: build a complete date or number spine over a fixed range, CROSS JOIN it to entities, then LEFT JOIN actuals with COALESCE so missing slots show 0; integer series for fixed buckets (1..N, hours 0..23); and per-row range expansion via CROSS JOIN LATERAL generate_series. Ranges are literal or derived from MIN/MAX of the data, never CURRENT_DATE. PostgreSQL.",
        "dialects": ["postgresql"],
    },
    # ---- Window function variants ---------------------------------------
    "window_running_total": {
        "label": "Window — Running total / cumulative aggregate",
        "description": "SUM/AVG/COUNT OVER (PARTITION BY ... ORDER BY ...) with UNBOUNDED PRECEDING for cumulative metrics that reset per group.",
        "dialects": ["postgresql", "mysql"],
    },
    "window_lag_lead": {
        "label": "Compare to previous / next row",
        "description": "Sequential neighbour comparison (row-compare): compare a row to its previous/next row's value, measure the gap/delta, detect a fixed-length run, or pair two rows by role. Uses LAG/LEAD or a self-join, NOT a foreign-key lookup.",
        "dialects": ["postgresql", "mysql"],
    },
    "window_top_n_per_group": {
        "label": "Window — Top N per group (ROW_NUMBER + filter)",
        "description": "ROW_NUMBER PARTITION BY in a CTE/subquery, then filter rn <= N. Top 3 products per category, most recent order per customer, etc.",
        "dialects": ["postgresql", "mysql"],
    },
    "point_in_time": {
        "label": "Point in Time (as-of lookup)",
        "description": "Single history table: the value in effect as of a cutoff date. Most recent row on/before the cutoff per entity (ROW_NUMBER rn=1 + date guard), a default when no history yet, or fill-forward over a date spine.",
        "dialects": ["postgresql", "mysql"],
    },
    "window_sliding": {
        "label": "Window — Sliding window aggregate (rolling N days)",
        "description": "Explicit frame clause ROWS BETWEEN n PRECEDING AND CURRENT ROW for moving averages, trailing N-day metrics.",
        "dialects": ["postgresql", "mysql"],
    },
    "window_first_last": {
        "label": "Window — FIRST_VALUE / LAST_VALUE",
        "description": "First and last value in a partition; LAST_VALUE requires explicit ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING.",
        "dialects": ["postgresql", "mysql"],
    },
    "window_sessionization": {
        "label": "Window — Sessionization (gap-based grouping)",
        "description": "LAG to find gap to previous event per user, conditional flag for new session, cumulative SUM of flag to assign session_id.",
        "dialects": ["postgresql", "mysql"],
    },
    "window_frames": {
        "label": "Window — Frame clauses (ROWS / RANGE BETWEEN)",
        "description": "Drills the explicit frame clause: UNBOUNDED PRECEDING / FOLLOWING, CURRENT ROW, N PRECEDING / FOLLOWING, ROWS vs RANGE distinction, and why default frames fail with LAST_VALUE.",
        "dialects": ["postgresql", "mysql"],
    },
    "window_benchmark_compare": {
        "label": "Window — Compare row to group average (AVG OVER, no ORDER BY)",
        "description": "AVG/MIN/MAX OVER (PARTITION BY group) with NO ORDER BY puts the whole-group benchmark on every row; the outer query then compares each row to it (above / below the average). Because a window function cannot live in WHERE, the benchmark is computed in a CTE/subquery and filtered in the outer query. Distinct from the cumulative running average (which has ORDER BY) and the rolling window (fixed N PRECEDING).",
        "dialects": ["postgresql", "mysql"],
    },
    "root_cause_analysis": {
        "label": "Root Cause Analysis (diagnostic SQL: find the bug, not just the metric)",
        "description": (
            "Diagnostic problems where the analyst is handed a symptom (metric drop / spike, "
            "duplicate inflation, missing rows, NULL propagation, date or timezone bug, stale "
            "snapshot, two-source mismatch) and must write SQL that PINPOINTS the root cause "
            "instead of just reporting the headline number. Each problem rotates one of 7 "
            "scenario archetypes, plants a planted bug in seed data the analyst's SQL must "
            "surface, and ships an answer_key that exercises Postgres diagnostic features "
            "(CTE chains, LAG/LEAD/SUM OVER for current-vs-prior, EXCEPT/INTERSECT for set "
            "comparisons, DISTINCT ON, COALESCE/NULLIF, generate_series for time-axis fill, "
            "date_trunc / AT TIME ZONE for boundary bugs). Postgres only."
        ),
        "dialects": ["postgresql"],
    },
    # ---- Meta qtypes: resolve to a concrete qtype at generation time ----
    "window_random": {
        "label": "Window — 🎲 random (any of the 8 variants)",
        "description": "Picks one of running_total, lag_lead, top_n_per_group, sliding, first_last, sessionization, frames, or benchmark_compare at random.",
        "dialects": ["postgresql", "mysql"],
    },
    "random_any": {
        "label": "🎲 Random (any qtype, no recursive CTE)",
        "description": "Picks any qtype at random from the full catalog excluding recursive_cte, legacy dml, and the meta-random types themselves.",
        "dialects": ["postgresql", "mysql"],
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
    "filter_strategies": """\
-- Comparison & boolean (row-level WHERE)
SELECT * FROM t
WHERE price >= 100 AND category IN ('A', 'B') AND id % 2 = 1;

-- NULL-aware
SELECT * FROM t WHERE quality_flag IS NULL OR duration < 180;

-- Pattern match
SELECT * FROM t WHERE name LIKE 'A%' AND email NOT LIKE '%@test.com';

-- Membership (keep rows that match another set)
SELECT * FROM t WHERE id IN (SELECT id FROM other WHERE active);
-- or: WHERE EXISTS (SELECT 1 FROM other o WHERE o.id = t.id)

-- Anti-join (no match in another set)
SELECT * FROM t WHERE NOT EXISTS (SELECT 1 FROM other o WHERE o.id = t.id);
-- NOT IN only if the subquery column is guaranteed NON-NULL

-- Group-threshold across distinct rows (GROUP BY + HAVING)
SELECT entity_id, entity_name
FROM t
GROUP BY entity_id, entity_name
HAVING SUM(CASE WHEN slice = 'A' THEN value ELSE 0 END) >= threshold_a
   AND SUM(CASE WHEN slice = 'B' THEN value ELSE 0 END) >= threshold_b;
-- broken instinct: GROUP BY entity, slice HAVING slice='A' AND slice='B' (impossible on one row)
""",
    "anti_join": """\
-- Anti-join: rows in A with NO match in B (customers who never ordered)

-- NOT EXISTS (preferred, NULL-safe)
SELECT a.*
FROM a
WHERE NOT EXISTS (SELECT 1 FROM b WHERE b.fk = a.id);

-- LEFT JOIN ... WHERE right IS NULL
SELECT a.*
FROM a
LEFT JOIN b ON b.fk = a.id
WHERE b.fk IS NULL;

-- NOT IN (ONLY if the subquery column is guaranteed non-NULL)
SELECT a.*
FROM a
WHERE a.id NOT IN (SELECT fk FROM b WHERE fk IS NOT NULL);
-- a single NULL in the NOT IN list returns ZERO rows for everyone.
""",
    "scalar_extract": """\
-- Single aggregate over the whole table (one row, one value)
SELECT MAX(salary) AS top_salary FROM employees;

-- Top-1 row (the single winner) -- ORDER BY + LIMIT 1, with a tiebreak
SELECT name FROM employees ORDER BY salary DESC, name LIMIT 1;

-- Nth highest distinct value (2nd highest -> OFFSET 1)
SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1;

-- Nth highest, NULL-safe (returns NULL, not zero rows, when there is no Nth)
SELECT (SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1) AS second_highest;

-- Single ratio over the whole table (guard the denominator)
SELECT ROUND(SUM(accepted)::numeric / NULLIF(SUM(sent), 0), 4) AS acceptance_rate FROM events;
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
    "window_benchmark_compare": """\
-- Compare each row to its GROUP benchmark (whole-group AVG, no ORDER BY).
-- Goal: keep rows whose value is above the average OF THEIR GROUP.

-- Step 1 (CTE): stamp the whole-group benchmark on every row.
--   No ORDER BY -> the window is the ENTIRE partition, so avg_in_group
--   is identical for every row in the same group.
WITH benchmarked AS (
    SELECT
        id,
        group_col,
        value,
        AVG(value) OVER (PARTITION BY group_col) AS avg_in_group   -- whole-group average
    FROM source_table
)
-- Step 2 (outer): compare in the OUTER query. A window function cannot
-- go in WHERE, which is exactly why Step 1 is a separate CTE.
SELECT id, group_col, value, avg_in_group
FROM benchmarked
WHERE value > avg_in_group          -- above the group average ( >= to include ties )
ORDER BY group_col, value DESC;

-- Whole-population variant: AVG(value) OVER () with an EMPTY partition
-- compares every row to the overall average across all rows.

-- Contrast (do NOT confuse):
--   AVG(value) OVER (PARTITION BY g)                 -> whole-group benchmark (this qtype)
--   AVG(value) OVER (PARTITION BY g ORDER BY d)      -> cumulative running average
--   AVG(value) OVER (ORDER BY d ROWS 6 PRECEDING ...) -> fixed rolling window
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
    "union_islands.consecutive_day_streak_per_entity": """\
-- Per entity streak detection with DUPLICATE same day source rows (LeetCode #1454 Active Users).
-- Three structural lessons: (1) dedupe first, (2) partition the ROW_NUMBER by entity,
-- (3) final SELECT uses MEMBERSHIP semantics (EXISTS / IN), NOT cosmetic DISTINCT.

WITH base AS (
    -- Step 1: dedupe same day events FIRST. Without DISTINCT, a duplicate
    -- (entity_id, event_date) row advances ROW_NUMBER by 1 without
    -- advancing event_date, breaking the date - rn streak math.
    SELECT DISTINCT entity_id, event_date
    FROM fact_table
),
date_groups AS (
    -- Step 2: gaps and islands per entity. PARTITION BY entity_id is
    -- mandatory; without it the rn sequence runs across all entities and
    -- unrelated entities collapse into the same grp.
    SELECT
        entity_id,
        event_date - ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY event_date)::int AS grp
    FROM base
),
streaks AS (
    -- Step 3: one row per qualifying (entity, streak) pair.
    SELECT entity_id
    FROM date_groups
    GROUP BY entity_id, grp
    HAVING COUNT(*) >= 5
)
-- Step 4: membership check, NOT GROUP BY + DISTINCT. The outer SELECT is
-- grained per dim row, so an entity with multiple qualifying streaks
-- collapses to one output row naturally.
SELECT a.id, a.name
FROM dim_table AS a
WHERE EXISTS (SELECT 1 FROM streaks s WHERE s.entity_id = a.id)
ORDER BY a.id;

-- Equivalent membership form using IN:
--   WHERE a.id IN (SELECT entity_id FROM streaks)

-- Equivalent per user 2 stage aggregate form:
-- WITH ... (base + date_groups as above)
-- streak_lengths AS (
--     SELECT entity_id, grp, COUNT(*) AS days
--     FROM date_groups
--     GROUP BY entity_id, grp
-- ),
-- per_user AS (
--     SELECT entity_id
--     FROM streak_lengths
--     GROUP BY entity_id
--     HAVING MAX(days) >= 5
-- )
-- SELECT a.id, a.name
-- FROM dim_table a
-- JOIN per_user p ON p.entity_id = a.id
-- ORDER BY a.id;

-- FORBIDDEN anti pattern (the symptomatic fix):
--   SELECT DISTINCT a.id, a.name
--   FROM dim_table a JOIN date_groups d ON d.entity_id = a.id
--   GROUP BY a.id, a.name, grp
--   HAVING COUNT(*) >= 5;
-- Works only because DISTINCT collapses extra rows. The grain of the final
-- SELECT is wrong for the question; forget DISTINCT once and duplicates
-- leak into production. Use membership semantics instead.
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
    "percentile_metrics.extreme_exclusion": """\
-- Extreme exclusion (LeetCode #1149-style): entities with NEITHER the max NOR
-- the min per-entity metric. Pair of DENSE_RANK windows, ASC and DESC, then
-- filter where neither rank = 1 so the whole min cluster AND the whole max
-- cluster drop together.
WITH fact_counts AS (
    -- Step 1: per-entity COUNT (or SUM) from the fact table.
    SELECT entity_key, COUNT(*) AS n
    FROM fact_table
    GROUP BY entity_key
),
ranked AS (
    -- Step 2: bring the count onto the dim, rank from BOTH ends.
    -- LEFT JOIN + COALESCE 0 so a zero-event entity still gets ranked
    -- (it lands at rn_asc = 1 and is correctly excluded as the min).
    SELECT
        d.entity_id,
        d.entity_name,
        COALESCE(f.n, 0)                                       AS n,
        DENSE_RANK() OVER (ORDER BY COALESCE(f.n, 0) ASC)      AS rn_asc,
        DENSE_RANK() OVER (ORDER BY COALESCE(f.n, 0) DESC)     AS rn_desc
    FROM dim_table AS d
    LEFT JOIN fact_counts AS f ON f.entity_key = d.entity_id
)
-- Step 3: keep rows that are neither the min cluster nor the max cluster.
SELECT entity_id, entity_name, n
FROM ranked
WHERE rn_asc  > 1
  AND rn_desc > 1;

-- Watch out:
--   * DENSE_RANK, not ROW_NUMBER. ROW_NUMBER breaks ties arbitrarily, so if two
--     entities tie at the min only one would get rn_asc = 1 and the other would
--     be incorrectly kept. DENSE_RANK gives every tied row the same rank, so the
--     filter drops the whole tie cluster on each end.
--   * Drive the FROM off the dim, LEFT JOIN to the count CTE. FROM the fact
--     would silently drop zero-event entities and they'd never appear in the rank.
--   * COALESCE inside the ORDER BY, not just the SELECT. Sorting NULL with DESC
--     would put NULL FIRST in Postgres and incorrectly classify the zero-event
--     entity as the max.
--   * Edge case: if every entity has the same count, every row gets both ranks
--     equal to 1 and the result is empty. That matches the prompt's spirit.
""",
    "percentile_metrics.extreme_exclusion_per_group": """\
-- Per partition extreme exclusion (LeetCode #1412 Quiet Students shape):
-- entities who, in EVERY group they participated in, were NEITHER the max NOR
-- the min on the metric. Per partition DENSE_RANK pair + per entity HAVING MIN.

WITH base AS (
    -- Step 1: per group, rank each entity by the metric in BOTH directions.
    -- PARTITION BY group_col is MANDATORY; without it the ranking is global
    -- and the answer collapses to "the globally lowest / highest entity."
    SELECT
        group_col,
        entity_id,
        DENSE_RANK() OVER (PARTITION BY group_col ORDER BY metric_col ASC)  AS rn_asc,
        DENSE_RANK() OVER (PARTITION BY group_col ORDER BY metric_col DESC) AS rn_desc
    FROM fact_table
)
-- Step 2: attach entity name (INNER JOIN drops dim entities with zero fact
-- rows, satisfying "participated in at least one group" automatically).
-- Step 3: GROUP BY entity, HAVING MIN(rn) > 1 in BOTH directions enforces
-- "FOR ALL the entity's rows, rn > 1" -- they were never extreme in any group.
SELECT d.entity_id, d.entity_name
FROM base AS b
JOIN dim_table AS d ON d.entity_id = b.entity_id
GROUP BY d.entity_id, d.entity_name
HAVING MIN(b.rn_asc)  > 1
   AND MIN(b.rn_desc) > 1
ORDER BY d.entity_id;

-- Alternate equally-correct HAVING forms (validator MUST accept any of these):
--   HAVING NOT BOOL_OR(b.rn_asc = 1) AND NOT BOOL_OR(b.rn_desc = 1)
--   HAVING MAX(CASE WHEN b.rn_asc = 1 OR b.rn_desc = 1 THEN 1 ELSE 0 END) = 0

-- FORBIDDEN anti pattern:
--   HAVING BOOL_OR(b.rn_asc > 1) AND BOOL_OR(b.rn_desc > 1)
-- That's an EXISTS check ("at least one row where they weren't the min"),
-- not a FOR ALL check. An entity who was extreme in some groups but not
-- others would pass this gate incorrectly. Use MIN(rn) > 1 (smallest rank
-- the entity ever held is still above 1) for the FOR ALL semantics.

-- Watch out:
--   * PARTITION BY group_col on BOTH window functions. Without it the
--     ranking is across all fact rows and "extreme in their group" loses
--     its per group meaning.
--   * DENSE_RANK, not ROW_NUMBER. ROW_NUMBER breaks ties arbitrarily; if
--     two entities tie for highest in a group, ROW_NUMBER gives only one
--     of them rank 1 and the other could pass the gate incorrectly.
--   * INNER JOIN, not LEFT JOIN. Driving from base (which only has rows
--     for entities that participated in at least one group) and INNER
--     JOIN to dim automatically excludes zero participation entities.
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
    "pivot.multi_column_pivot": """\
-- multi_column_pivot: classic long-to-wide with one CASE per target column

-- TYPE 1: stored category column
SELECT
    entity_id,
    SUM(CASE WHEN category_col = 'A' THEN value_col ELSE 0 END) AS a_total,
    SUM(CASE WHEN category_col = 'B' THEN value_col ELSE 0 END) AS b_total,
    SUM(CASE WHEN category_col = 'C' THEN value_col ELSE 0 END) AS c_total
FROM source_table
GROUP BY entity_id
ORDER BY entity_id;

-- TYPE 2: pivot column derived from a DATE via DOW (day name) or month name.
-- LEFT JOIN dim so entities with zero fact rows still appear.
-- *** USE TO_CHAR(date, 'FMDay') NOT 'Day' -- the non-FM form pads to 9 chars
-- *** and silently fails string equality against literals like 'Monday'.
SELECT
    d.entity_id AS Category,
    SUM(CASE WHEN TO_CHAR(f.date_col, 'FMDay') = 'Monday'    THEN f.value_col ELSE 0 END) AS Monday,
    SUM(CASE WHEN TO_CHAR(f.date_col, 'FMDay') = 'Tuesday'   THEN f.value_col ELSE 0 END) AS Tuesday,
    SUM(CASE WHEN TO_CHAR(f.date_col, 'FMDay') = 'Wednesday' THEN f.value_col ELSE 0 END) AS Wednesday,
    SUM(CASE WHEN TO_CHAR(f.date_col, 'FMDay') = 'Thursday'  THEN f.value_col ELSE 0 END) AS Thursday,
    SUM(CASE WHEN TO_CHAR(f.date_col, 'FMDay') = 'Friday'    THEN f.value_col ELSE 0 END) AS Friday,
    SUM(CASE WHEN TO_CHAR(f.date_col, 'FMDay') = 'Saturday'  THEN f.value_col ELSE 0 END) AS Saturday,
    SUM(CASE WHEN TO_CHAR(f.date_col, 'FMDay') = 'Sunday'    THEN f.value_col ELSE 0 END) AS Sunday
FROM dim_table d
LEFT JOIN fact_table f ON f.entity_id = d.entity_id
GROUP BY d.entity_id
ORDER BY d.entity_id;

-- Acceptable alternates for the DOW expression (all produce 'Monday', 'Tuesday', ...):
--   TRIM(TO_CHAR(f.date_col, 'Day'))            -- noisier but works
--   EXTRACT(ISODOW FROM f.date_col)             -- returns 1..7 (Mon..Sun); use INT in CASE
-- FORBIDDEN: TO_CHAR(f.date_col, 'Day') without FM -- silently 0 for all days except Wednesday.

-- ELSE 0 inside CASE removes the need for COALESCE around SUM (SUM over only zeros = 0).
""",
    "pivot.signed_aggregate": """\
-- signed_aggregate: opposing categories collapsed into ONE net total per entity.
-- LeetCode #1393 Capital Gain/Loss is the canonical shape.

-- Form A: two CASE expressions, subtracted (most readable)
SELECT
    entity_key,
    SUM(CASE WHEN signed_cat = 'positive_val' THEN value_col ELSE 0 END
      - CASE WHEN signed_cat = 'negative_val' THEN value_col ELSE 0 END) AS net_amount
FROM source_table
GROUP BY entity_key;

-- Form B: single CASE with both branches (one expression, fewer keystrokes)
SELECT
    entity_key,
    SUM(CASE WHEN signed_cat = 'positive_val' THEN  value_col
             WHEN signed_cat = 'negative_val' THEN -value_col
             ELSE 0 END) AS net_amount
FROM source_table
GROUP BY entity_key;

-- If an entity may have ZERO rows in either category and must still appear with 0,
-- LEFT JOIN a dim table and COALESCE the SUM:
SELECT
    d.entity_key,
    COALESCE(SUM(CASE WHEN s.signed_cat = 'positive_val' THEN s.value_col
                      WHEN s.signed_cat = 'negative_val' THEN -s.value_col
                      ELSE 0 END), 0) AS net_amount
FROM dim_table d
LEFT JOIN source_table s ON s.entity_key = d.entity_key
GROUP BY d.entity_key;

-- Forbidden: two subqueries (sum_pos and sum_neg) joined on entity_key.
-- The lesson is CASE inside ONE aggregate, not two scans subtracted.
""",
    "pivot.membership_filter": """\
-- membership_filter: CASE in HAVING as a set membership gate
-- "bought ALL of X, NONE of Y". LeetCode #1965 Customers Who Bought A and B but Not C.
-- BOTH forms below are accepted. Pick by dialect / readability preference.

-- Form A: BOOL_OR per category (Postgres native, reads as English)
SELECT e.entity_id, e.entity_name
FROM entity_table AS e
JOIN fact_table AS f ON f.entity_id = e.entity_id
GROUP BY e.entity_id, e.entity_name
HAVING BOOL_OR(f.category_col = 'A')
   AND BOOL_OR(f.category_col = 'B')
   AND NOT BOOL_OR(f.category_col = 'C')
ORDER BY e.entity_id;

-- Form B: MAX(CASE ... THEN 1 ELSE 0 END) per category (portable across dialects)
SELECT e.entity_id, e.entity_name
FROM entity_table AS e
JOIN fact_table AS f ON f.entity_id = e.entity_id
GROUP BY e.entity_id, e.entity_name
HAVING MAX(CASE WHEN f.category_col = 'A' THEN 1 ELSE 0 END) = 1
   AND MAX(CASE WHEN f.category_col = 'B' THEN 1 ELSE 0 END) = 1
   AND MAX(CASE WHEN f.category_col = 'C' THEN 1 ELSE 0 END) = 0
ORDER BY e.entity_id;

-- Alternative: set operations (same answer, different mental model)
WITH bought_a AS (SELECT DISTINCT entity_id FROM fact_table WHERE category_col = 'A'),
     bought_b AS (SELECT DISTINCT entity_id FROM fact_table WHERE category_col = 'B'),
     bought_c AS (SELECT DISTINCT entity_id FROM fact_table WHERE category_col = 'C'),
     qualifies AS (
         SELECT entity_id FROM bought_a
         INTERSECT
         SELECT entity_id FROM bought_b
         EXCEPT
         SELECT entity_id FROM bought_c
     )
SELECT e.entity_id, e.entity_name
FROM entity_table AS e
JOIN qualifies AS q ON q.entity_id = e.entity_id
ORDER BY e.entity_id;

-- FORBIDDEN: SUM(CASE A->+1, B->+1, C->-1) = 2 as the gate.
-- Counts purchases instead of presence. Breaks when an entity bought a required
-- category multiple times (SUM > 2, excluded incorrectly) or when extra required
-- purchases land at the threshold despite owning forbidden (SUM = 2, included
-- incorrectly). Use existence flags (BOOL_OR or MAX CASE), not arithmetic.
""",
    "pivot.threshold_per_category": """\
-- threshold_per_category: SUM(CASE) >= N per category in HAVING.
-- "Customers who spent at least $100 in EACH of June AND July 2020."
-- Same technique family as membership_filter but threshold (numeric) instead of presence.

WITH base AS (
    -- Pre compute the value to sum per row (e.g. quantity * price).
    -- Filter to the categories of interest so we don't scan irrelevant rows.
    SELECT
        o.customer_id,
        c.name,
        DATE_TRUNC('month', o.order_date)::date AS month_cohort,
        o.quantity * p.price                    AS spent
    FROM orders    AS o
    JOIN products  AS p USING (product_id)
    JOIN customers AS c USING (customer_id)
    WHERE o.order_date >= DATE '2020-06-01'
      AND o.order_date <  DATE '2020-08-01'
)
SELECT customer_id, name
FROM base
GROUP BY customer_id, name
HAVING SUM(CASE WHEN month_cohort = '2020-06-01' THEN spent ELSE 0 END) >= 100
   AND SUM(CASE WHEN month_cohort = '2020-07-01' THEN spent ELSE 0 END) >= 100
ORDER BY customer_id;

-- Key insight: GROUP BY entity ONLY (NOT entity + category). Each output row holds
-- ALL the entity's categories together, and the per category SUM(CASE) expressions
-- cherry pick each category's total as a separate number on the same row. HAVING
-- can then AND across those numbers because they coexist on one row.

-- FORBIDDEN anti pattern (the most common mistake):
--   GROUP BY customer_id, name, month_cohort
--   HAVING (month_cohort = '2020-06-01' AND SUM(spent) >= 100)
--      AND (month_cohort = '2020-07-01' AND SUM(spent) >= 100);
-- Impossible: one row can only have one month_cohort value, so the AND is never true.
-- Symptom: empty result on every input.

-- Variants:
--   thresholds can differ per category (June >= 100 AND July >= 50)
--   3 or 4 categories (Q1, Q2, Q3, Q4) -- just add more SUM(CASE) clauses to HAVING
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
-- Anchor "older than N days" to a LITERAL or data-derived cutoff
-- (never CURRENT_DATE: the data is static, so a clock-relative filter goes empty)
SELECT * FROM events_table WHERE event_date < DATE '2024-03-01' - 30;
-- data-derived cutoff: N days before the latest event in the table
SELECT * FROM events_table
WHERE event_date < (SELECT MAX(event_date) FROM events_table) - 30;

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
-- Use: some_date_col - col_days_int  OR  (col_days_int || ' days')::INTERVAL
-- AVOID: INTERVAL 'col_days days'  (treats 'col_days' as a literal, errors out)
-- AVOID CURRENT_DATE entirely: anchor to a literal date or a data-derived MAX(date).
""",
    "series_generation": """\
-- SHAPE A: date spine over a LITERAL range, CROSS JOIN entities, LEFT JOIN actuals
WITH date_spine AS (
    SELECT generate_series(DATE '2024-01-01', DATE '2024-01-31', INTERVAL '1 day')::date AS d
)
SELECT e.entity_id, s.d, COALESCE(SUM(a.metric), 0) AS metric_total
FROM (SELECT DISTINCT entity_id FROM entity_table) e
CROSS JOIN date_spine s
LEFT JOIN actuals_table a
  ON a.entity_id = e.entity_id AND a.event_date = s.d
GROUP BY e.entity_id, s.d
ORDER BY e.entity_id, s.d;

-- data-derived range (no CURRENT_DATE): bound the spine by what the data holds
WITH bounds AS (
    SELECT MIN(event_date) AS lo, MAX(event_date) AS hi FROM actuals_table
)
SELECT generate_series(lo, hi, INTERVAL '1 day')::date AS d FROM bounds;

-- SHAPE B: integer / number series for fixed buckets (1..N, hours 0..23)
SELECT g AS bucket FROM generate_series(1, 12) AS g;          -- months 1..12
SELECT h AS hour_of_day FROM generate_series(0, 23) AS h;     -- hours 0..23

-- SHAPE C: expand each row's [start, end] range into one row per day (LATERAL)
SELECT t.id, d::date AS day
FROM ranges_table t
CROSS JOIN LATERAL generate_series(t.start_date, t.end_date, INTERVAL '1 day') AS d
ORDER BY t.id, day;

-- SHAPE D (hard): histogram / distribution over an integer axis, bounds derived from a CTE.
-- Output is one row per possible integer count from min..max, with the bucket nobody hit
-- still appearing as 0. Use case: "transactions per visit," "items per order," "errors per session."
WITH base AS (
    -- Step 1: per-entity count. LEFT JOIN parent -> child + COUNT(child.col) so no-child
    -- entities land at 0 (COUNT ignores the NULL from the unmatched LEFT JOIN row).
    SELECT
        p.entity_id,
        p.bucket_key,                                            -- e.g. visit_date
        COUNT(c.value_col) AS per_entity_count
    FROM parent_table   AS p
    LEFT JOIN child_table AS c
           ON c.entity_id  = p.entity_id
          AND c.bucket_key = p.bucket_key
    GROUP BY p.entity_id, p.bucket_key
),
spine AS (
    -- Step 2: integer spine. Read the PROMPT for the lower bound — it is usually a
    -- LITERAL (0 for counts, 1 for months, 0 for hours). `(SELECT MIN(...) FROM base)`
    -- looks reasonable but silently skips the 0 / 1 buckets when no entity in the data
    -- happened to hit them. UPPER bound is data-driven so the spine right-sizes.
    SELECT generate_series(
        0,                                                       -- literal from the prompt
        (SELECT MAX(per_entity_count) FROM base)                 -- data-driven upper bound
    ) AS bucket
)
-- Step 3: spine LEFT JOIN base on the bucket; COUNT(base.col) lands at 0 for empty buckets.
SELECT
    s.bucket                       AS per_entity_count,
    COUNT(b.per_entity_count)      AS visits_count
FROM spine AS s
LEFT JOIN base AS b ON b.per_entity_count = s.bucket
GROUP BY s.bucket
ORDER BY s.bucket;
-- Notes: COUNT(b.col) NOT COUNT(*) — the LEFT JOIN's unmatched bucket row would otherwise
-- count as 1. No COALESCE needed: COUNT on a non-empty GROUP BY result is 0, never NULL.

-- SHAPE F (medium / hard): active-in-period overlap.
-- The fact table holds entities with a CREATED date and a NULLABLE ENDED date.
-- Question: how many entities were ACTIVE in each period over a fixed window.
-- Active = overlaps the period (created by period end AND open OR closed at/after start).
WITH period_spine AS (
    -- Period starts only — 6 months in this example.
    SELECT generate_series(
        DATE '2024-01-01', DATE '2024-06-01', INTERVAL '1 month'
    )::date AS period_start
)
SELECT
    e.entity_id,
    p.period_start,
    -- COUNT a column from the right side. NULL on unmatched rows → 0 active for that cell.
    COUNT(f.record_id) AS active_count
FROM period_spine AS p
CROSS JOIN dim_entity AS e
-- The OVERLAP predicate lives in the ON, NOT the WHERE. WHERE would drop zero-fill rows.
LEFT JOIN fact_table AS f
       ON f.entity_id = e.entity_id
      -- born by period end (half open form: created BEFORE next period starts)
      AND f.created_date <  p.period_start + INTERVAL '1 month'
      -- still open OR closed at/after period start
      AND (f.ended_date IS NULL OR f.ended_date >= p.period_start)
GROUP BY e.entity_id, p.period_start
ORDER BY e.entity_id, p.period_start;
-- Watch outs:
--   * Overlap predicate MUST sit in ON, not WHERE (LEFT JOIN's NULL row would be rejected).
--   * COUNT(f.record_id) not COUNT(*) (empty cells would count as 1).
--   * Half open form `< period_start + INTERVAL '1 month'` avoids inclusive BETWEEN traps.
--   * `IS NULL OR >= period_start` keeps still-open entities (the most important set).
""",
    "matchup_unpivot": """\
-- Matchup unpivot: one wide row holds BOTH sides; split AND score in one step, aggregate.
-- matches(match_id, host_team, guest_team, host_goals, guest_goals)

-- STEP 1+2 together: split the two sides with UNION ALL and score each branch
-- right where it is written. Each branch already sees both wide-row scores, so it
-- compares its OWN side against the opponent directly -- no goals-for/against swap
-- to track. Note the comparison flips between the two branches.
WITH per_side AS (
    SELECT host_team AS team,
           CASE WHEN host_goals > guest_goals THEN 3
                WHEN host_goals = guest_goals THEN 1
                ELSE 0 END AS points,
           CASE WHEN host_goals > guest_goals THEN 1 ELSE 0 END AS wins,
           CASE WHEN host_goals = guest_goals THEN 1 ELSE 0 END AS draws,
           CASE WHEN host_goals < guest_goals THEN 1 ELSE 0 END AS losses
    FROM matches
    UNION ALL
    SELECT guest_team AS team,
           CASE WHEN guest_goals > host_goals THEN 3
                WHEN guest_goals = host_goals THEN 1
                ELSE 0 END AS points,
           CASE WHEN guest_goals > host_goals THEN 1 ELSE 0 END AS wins,
           CASE WHEN guest_goals = host_goals THEN 1 ELSE 0 END AS draws,
           CASE WHEN guest_goals < host_goals THEN 1 ELSE 0 END AS losses
    FROM matches
)
-- STEP 3: aggregate per participant. LEFT JOIN the dimension so a team that
-- never played still appears with zero-filled metrics.
SELECT t.team_id, t.team_name,
       COALESCE(SUM(s.points), 0) AS points,
       COALESCE(SUM(s.wins),   0) AS wins,
       COALESCE(SUM(s.draws),  0) AS draws,
       COALESCE(SUM(s.losses), 0) AS losses
FROM teams t
LEFT JOIN per_side s ON s.team = t.team_id
GROUP BY t.team_id, t.team_name
ORDER BY points DESC, t.team_id ASC;
""",
    "gated_lookup": """\
-- Gated lookup: a condition on table A gates a per-entity pick from table B.
-- gate table:  products(product_id, rating)         -- rating 1..5 is the GATE
-- value table: pricing(product_id, price)            -- many prices per product

-- FALLBACK = 0 or NULL -> use a CASE, and every entity appears.
WITH cheapest AS (                          -- per-entity pick from table B (top-1 by price)
    SELECT product_id, MIN(price) AS min_price
    FROM pricing
    GROUP BY product_id
    -- equivalently: ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY price) = 1
)
SELECT p.product_id,
       p.rating,
       CASE WHEN p.rating >= 4 THEN c.min_price      -- gate on table A's attribute
            ELSE 0 END AS reported_price             -- fallback when the gate fails
FROM products AS p                          -- drive off the gate table so all entities show
LEFT JOIN cheapest AS c ON c.product_id = p.product_id
ORDER BY p.product_id;

-- FALLBACK = EXCLUDE non-qualifying rows -> use a WHERE instead of CASE.
SELECT p.product_id, MIN(pr.price) AS min_price
FROM products AS p
JOIN pricing AS pr ON pr.product_id = p.product_id
WHERE p.rating >= 4                          -- gate filters entities out entirely
GROUP BY p.product_id
ORDER BY p.product_id;
""",
    "left_join_on_filter": """\
-- LEFT JOIN ON vs WHERE: keep every left row, count only the qualifying right rows.
-- Goal: every customer appears, with their 2024 order count (0 if none).

-- CORRECT: the right-side filter lives in the ON, so unmatched customers survive.
SELECT c.customer_id,
       c.name,
       COUNT(o.order_id) AS orders_2024      -- COUNT a right column, not COUNT(*)
FROM customers AS c
LEFT JOIN orders AS o
       ON o.customer_id = c.customer_id
      AND o.order_date >= DATE '2024-01-01'   -- right-side filter in ON
      AND o.order_date <  DATE '2025-01-01'
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id;
-- A customer whose only orders are in 2023 (or who has none) still shows up with 0.

-- WRONG: same filter in WHERE -> the LEFT JOIN collapses to INNER, dropping those customers.
SELECT c.customer_id, c.name, COUNT(o.order_id) AS orders_2024
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.order_date >= DATE '2024-01-01'       -- filters the NULL row away -> row vanishes
  AND o.order_date <  DATE '2025-01-01'
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id;

-- Note: COUNT(o.order_id) ignores the NULL from a non-match (gives 0);
-- COUNT(*) would wrongly count the NULL-filled row as 1.

-- BOTH SIDES: a filter on the LEFT (driver) table goes in WHERE, not ON.
-- A left filter in ON is a silent no-op -- the LEFT JOIN keeps the row anyway.
-- A right filter in WHERE silently drops kept rows. They go to different clauses.
SELECT e.employee_id,
       e.employee_name,
       COUNT(s.session_id) AS q1_session_count   -- count a right column, 0 if none
FROM employees AS e
LEFT JOIN enrollment_sessions AS s
       ON s.employee_id = e.employee_id
      AND s.session_date >= DATE '2024-01-01'     -- RIGHT-table filter -> ON (keeps left rows)
      AND s.session_date <  DATE '2024-04-01'
WHERE e.hire_date >= DATE '2024-01-01'            -- LEFT-table filter -> WHERE (really removes)
  AND e.hire_date <  DATE '2025-01-01'
GROUP BY e.employee_id, e.employee_name
ORDER BY e.employee_id;
-- 2024 hires with no Q1 sessions show 0; pre-2024 hires are correctly absent.
""",
    "root_cause_analysis": """\
-- Root Cause Analysis: the answer surfaces the BUG ROWS, not the broken metric.
-- A CTE staircase walks symptom -> per-dimension breakdown -> the offender.
-- Pattern below: metric-drop archetype. Swap CTEs for the other archetypes.

WITH per_day AS (
    SELECT order_date,
           SUM(revenue) AS daily_revenue
    FROM orders
    GROUP BY order_date
),
daily_diff AS (                                   -- current-vs-prior, the symptom view
    SELECT order_date,
           daily_revenue,
           LAG(daily_revenue) OVER (ORDER BY order_date)         AS prev_revenue,
           daily_revenue
             - LAG(daily_revenue) OVER (ORDER BY order_date)     AS day_over_day_delta
    FROM per_day
),
per_day_by_cat AS (                               -- the breakdown the symptom hides
    SELECT order_date,
           product_category,
           SUM(revenue) AS cat_revenue
    FROM orders
    GROUP BY order_date, product_category
),
cat_diff AS (
    SELECT order_date,
           product_category,
           cat_revenue,
           cat_revenue
             - LAG(cat_revenue) OVER (PARTITION BY product_category ORDER BY order_date)
             AS cat_day_over_day
    FROM per_day_by_cat
)
SELECT order_date,
       product_category,
       cat_day_over_day                            -- the bug rows: the cause, not the metric
FROM cat_diff
WHERE order_date = DATE '<symptom day>'
  AND cat_day_over_day < 0
ORDER BY cat_day_over_day ASC;

-- Postgres features the archetypes pull from (swap in as needed):
--   * EXCEPT / NOT EXISTS         -> missing_rows_antijoin
--   * GROUP BY + HAVING COUNT > 1 -> duplicate_inflation
--   * LEFT JOIN dim WHERE dim.x IS NULL  -> null_propagation
--   * date_trunc('day', ts AT TIME ZONE 'UTC') vs AT TIME ZONE 'America/Los_Angeles'
--       -> date_timezone_bug; surface the 2-3 boundary rows where the two land on different days
--   * snapshot.updated_at < (SELECT MAX(refresh_started_at) FROM refresh_log) - INTERVAL '1 day'
--       -> stale_snapshot
--   * FULL JOIN a ... ON a.key = b.key WHERE a.metric IS DISTINCT FROM b.metric
--       -> two_source_mismatch
""",
}


def get_code_reference(qtype: str, islands_flavor: str = None, percentile_flavor: str = None, pivot_flavor: str = None) -> str:
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
    if qtype == "pivot" and pivot_flavor:
        key = f"pivot.{pivot_flavor}"
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


# Industry scenarios — mirror of nb02's dict so nb01 can offer the same
# Scenario dropdown. Used when the picker passes a non-None industry slug.
INDUSTRY_SCENARIOS = {
    "consumer_social": [
        "a dating app tracking mutual matches and messaging engagement",
        "a photo sharing app tracking story creation and view rates",
        "a short video platform tracking watch time and completion rates",
        "a community forum tracking thread participation and member retention",
        "a podcast app tracking listening sessions and episode completion",
    ],
    "marketplace": [
        "a ride share app tracking match rate from request to driver acceptance",
        "a food delivery service tracking order completion and delivery time",
        "a gig labor marketplace tracking job acceptance and completion rates",
        "a P2P resale marketplace tracking listing-to-sale conversion",
        "a real estate listing platform tracking saved searches and inquiry rates",
    ],
    "ecommerce": [
        "a D2C subscription box service tracking renewal and churn",
        "a fashion ecommerce site tracking add-to-cart and conversion",
        "an online grocery service tracking basket size and reorder rates",
        "a beauty retailer tracking loyalty program redemption rates",
    ],
    "fintech": [
        "a neobank tracking debit card swipes and deposit funnel",
        "a buy-now-pay-later service tracking installment payment compliance",
        "a robo advisor tracking portfolio rebalancing and AUM growth",
        "a crypto exchange tracking trading volume and on-ramp deposits",
        "an expense management app tracking receipt capture and policy compliance",
    ],
    "b2b_saas": [
        "a CRM tracking pipeline coverage and won opportunity rates",
        "a project management tool tracking sprint completion and task throughput",
        "an HR platform tracking onboarding completion and benefits enrollment",
        "an observability platform tracking alert acknowledge time and MTTR",
        "a developer tools company tracking trial-to-paid conversion and seat expansion",
    ],
    "productivity_media": [
        "a note-taking app tracking notebook creation and daily writing streaks",
        "a streaming video service tracking watch time and binge depth",
        "a music streaming service tracking saved tracks and playlist creation",
        "a news app tracking article completion and subscription conversion",
    ],
    "health_wellness": [
        "a telehealth platform tracking visit completion and follow-up scheduling",
        "a mental health app tracking session completion and journal entries",
        "a fitness app tracking workout completion and active days per week",
        "a sleep tracking app tracking sleep score and goal achievement",
    ],
    "gaming": [
        "a free-to-play mobile game tracking session length and ad impressions",
        "a console online service tracking multiplayer match acceptance",
        "a battle royale mobile game tracking match completion and squad invites",
    ],
    "education": [
        "an online course platform tracking course completion and certification",
        "a language learning app tracking daily streaks and lesson completion",
        "a tutoring marketplace tracking session booking and tutor ratings",
        "a K-12 homework app tracking assignment turn-in and grade improvement",
    ],
    "pharmacy_care": [
        "a digital pharmacy tracking prescription submissions through PBM adjudication",
        "a same day medication delivery service tracking on-time delivery performance",
        "a prescription refill adherence program tracking 30/60/90 day refill rates",
        "a prior authorization cycle time tracking system across payers",
        "a telehealth visit completion funnel from booking to provider sign-off",
        "an at-home diagnostic test kit platform tracking kit shipped and results released",
    ],
}


def _pick_scenario(qtype: str = None, industry: str = None) -> str:
    """Pick a scenario theme for the prompt.

    industry can be:
      - None or "random" — pick across all INDUSTRY_SCENARIOS
      - "booedup" — return the BooedUp dating app anchor (rich app context
        is injected separately by the form)
      - an INDUSTRY_SCENARIOS key — pick within that vertical only
    qtype is kept for legacy callers but is ignored when industry is set.
    Without an industry argument the legacy SCENARIO_THEMES list is used.
    """
    if industry == "booedup":
        return "the BooedUp dating app"
    if industry and industry in INDUSTRY_SCENARIOS:
        return random.choice(INDUSTRY_SCENARIOS[industry])
    if industry == "random" or industry is None:
        # Use the industry pool if asked for random; fall back to legacy themes
        # when the picker did not pass anything.
        if industry == "random":
            pool = []
            for v in INDUSTRY_SCENARIOS.values():
                pool.extend(v)
            return random.choice(pool) if pool else random.choice(SCENARIO_THEMES)
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
- NO CLOCK-RELATIVE DATES (CRITICAL): The prompt, schema_ddl, data, and answer_key MUST NOT use CURRENT_DATE, NOW(), CURRENT_TIMESTAMP, LOCALTIMESTAMP, or any "last N days/months/years relative to today" filter. The example_input_data is fixed, so a clock-relative filter (e.g., WHERE d >= CURRENT_DATE - INTERVAL '6 months') returns a different result every day and almost always yields an EMPTY result against the static data, which makes the problem ungradable and non-reproducible (the expected output is captured once at generation time and would not match when the learner runs it later). Instead: (a) anchor every date window to LITERAL dates that exist in the data (e.g., WHERE month >= DATE '2024-01-01'), or (b) derive the reference date FROM the data itself (e.g., (SELECT MAX(signup_date) FROM users), or (SELECT DATE_TRUNC('month', MAX(signup_date)) FROM users) - INTERVAL '5 months'). If the prompt needs a "recent" or "last 6 months" window, define those bounds with explicit literals or a data-derived MAX so the same rows always come back. The expected output rows MUST be non-empty.
"""


SUBTYPES = {
    "filter_strategies": [
        ("comparison", "Comparison & boolean logic"),
        ("null_aware", "NULL-aware filters"),
        ("pattern", "Pattern matching (LIKE / regex)"),
        ("membership", "Membership via subquery (IN / EXISTS)"),
        ("anti_join", "Anti-join (NOT IN / NOT EXISTS)"),
        ("group_threshold", "Qualify on thresholds across distinct rows (HAVING)"),
    ],
    "anti_join": [
        ("not_exists", "NOT EXISTS (NULL-safe, preferred)"),
        ("left_join_null", "LEFT JOIN ... WHERE right IS NULL"),
        ("not_in", "NOT IN (only when subquery column is non-NULL)"),
    ],
    "scalar_extract": [
        ("single_aggregate", "Single aggregate over the whole table"),
        ("top1", "Top-1 row (the single winner)"),
        ("nth", "Second / Nth highest value (LIMIT OFFSET / subquery)"),
        ("ratio", "Ratio / percentage / weighted average"),
    ],
    "series_generation": [
        ("full_date_spine", "Full date spine × all entities"),
        ("bounds_from_data", "Bounds derived from the data"),
        ("filtered_entities", "Spine × filtered entities"),
        ("categorical_label_spine", "Categorical label spine"),
        ("lateral_range_expansion", "Per-row range expansion (LATERAL)"),
        ("period_overlap", "Period overlap (active in period)"),
    ],
    "dml_delete": [
        ("conditional", "Conditional delete"),
        ("duplicate_rows", "Duplicate rows"),
        ("orphan_rows", "Orphan rows"),
        ("cross_table", "Cross table"),
        ("time_based", "Time-based pruning"),
        ("two_condition", "Two-condition (group + row)"),
        ("null_safe_positive", "NULL-safe positive WHERE"),
    ],
    "delete_duplicates": [
        ("keep_min_id", "Keep the lowest id (NOT IN MIN)"),
        ("self_join", "Self-join delete (remove the higher-id twin)"),
        ("row_number", "ROW_NUMBER then delete rn > 1"),
    ],
    "left_join_on_filter": [
        ("date_window", "Right-side date window (count in a date range)"),
        ("status_category", "Right-side status / category equality"),
        ("numeric_threshold", "Right-side numeric threshold"),
        ("both_sides", "Left filter in WHERE + right filter in ON"),
        ("sum_coalesce", "SUM / AVG with COALESCE (not COUNT)"),
        ("existence_flag", "Boolean / existence flag per entity"),
    ],
    "date_operations": [
        ("date_trunc_cohort", "DATE_TRUNC cohort buckets (month / week / quarter)"),
        ("extract_component", "EXTRACT a component (year, day-of-week, hour)"),
        ("date_arithmetic", "Date arithmetic (DATE +/- days / INTERVAL, cutoffs)"),
        ("duration_between", "Duration between two timestamps (EXTRACT EPOCH)"),
        ("day_count_boundaries", "Inclusive vs exclusive day counts"),
    ],
    "unpivot": [
        ("drop", "Columns to rows, drop the empties (WHERE IS NOT NULL)"),
        ("keep", "Columns to rows, keep the empties (NULLs stay as rows)"),
        ("aggregate", "Unpivot then aggregate (stack in a CTE, one GROUP BY)"),
    ],
    "enrich_join": [
        ("straight_lookup", "Straight lookup / enrich (pull a column via JOIN)"),
        ("self_join", "Self-join: one table, two roles"),
        ("cross_join", "Cross join: all combinations, then LEFT JOIN"),
        ("per_group", "Match each row to a per-group value"),
        ("compound", "Compound eligibility (roll up, then multi-condition filter)"),
    ],
    "union_islands": [
        ("date_calendar", "Consecutive calendar days (date - rn)"),
        ("date_sequence", "Consecutive in data sequence (rn - rn)"),
        ("integer_seq", "Consecutive integer ids (id - rn)"),
        ("partitioned_status_periods", "Per-entity status timelines"),
        ("consecutive_day_streak_per_entity", "Per-entity day streak (HAVING COUNT)"),
    ],
    "percentile_metrics": [
        ("percentile_aggregate", "Percentile (PERCENTILE_CONT / DISC)"),
        ("ntile_buckets", "NTILE buckets"),
        ("top_n_percent", "PERCENT_RANK top X%"),
        ("extreme_exclusion", "Exclude min and max (DENSE_RANK both ends)"),
        ("extreme_exclusion_per_group", "Exclude min and max per group"),
    ],
    "pivot": [
        ("multi_column_pivot", "Long to wide (multi-column pivot)"),
        ("signed_aggregate", "Signed aggregate (net total)"),
        ("membership_filter", "Bought ALL / NONE (HAVING membership)"),
        ("threshold_per_category", "Threshold per category (HAVING)"),
    ],
    "gated_lookup": [
        ("case_keep", "CASE around the aggregate (keep all, 0 / NULL)"),
        ("gate_on", "Gate in the JOIN ON (drop before aggregating)"),
        ("where_exclude", "WHERE filter (drop non-qualifiers)"),
        ("distinct_on", "DISTINCT ON (latest / earliest per entity)"),
        ("rownumber_pick", "ROW_NUMBER + rn = 1 (pick by order)"),
    ],
    "window_running_total": [
        ("SUM", "Running total (SUM)"),
        ("AVG", "Running average (AVG)"),
        ("COUNT", "Running count (COUNT)"),
    ],
    "window_benchmark_compare": [
        ("AVG", "Compare to group average (AVG)"),
        ("MIN", "Compare to group minimum (MIN)"),
        ("MAX", "Compare to group maximum (MAX)"),
    ],
    "window_lag_lead": [
        ("neighbour_value", "Compare to neighbour's value (LAG/LEAD then compare)"),
        ("gap_delta", "Gap / delta to the neighbour (LAG/LEAD then subtract)"),
        ("fixed_run", "Fixed-length run of N rows (LAG + LEAD)"),
        ("pair_by_role", "Pair two rows by role (self-join / MAX(CASE))"),
    ],
    "window_sessionization": [
        ("one_per_session", "One row per session (roll up per session)"),
        ("one_per_person", "One row per person (aggregate sessions per entity)"),
        ("one_per_event", "One row per event (label each row, no GROUP BY)"),
    ],
    "window_frames": [
        ("rows_between", "ROWS BETWEEN (row-count frame)"),
        ("range_between", "RANGE BETWEEN (value / interval frame)"),
    ],
    "window_top_n_per_group": [
        ("top1_by_value", "Top 1 per group by value (highest / max metric)"),
        ("top1_by_date", "Top 1 per group by date (most recent / earliest)"),
        ("topn", "Top N per group (N > 1)"),
        ("nth", "Nth specific position (exactly N, not top N)"),
        ("special", "Special rank patterns (median, threshold from rank, rank deltas)"),
    ],
    "point_in_time": [
        ("asof_single", "As of a single cutoff date (ROW_NUMBER rn=1 + date guard)"),
        ("default_no_history", "Default when no history (entity must still appear)"),
        ("fill_forward", "Fill forward over a date spine"),
    ],
    "root_cause_analysis": [
        ("metric_drop_dimension", "Metric drop by dimension"),
        ("duplicate_inflation", "Duplicate inflation"),
        ("missing_rows_antijoin", "Missing rows (anti-join)"),
        ("null_propagation", "NULL propagation"),
        ("date_timezone_bug", "Date / timezone boundary bug"),
        ("stale_snapshot", "Stale snapshot"),
        ("two_source_mismatch", "Two-source mismatch"),
    ],
}


def _topic_specific_guidance(qtype: str, dialect: str, scenario: str = None, dml_op: str = None, islands_flavor: str = None, percentile_flavor: str = None, difficulty: str = None, pivot_flavor: str = None, subtype: str = None) -> str:
    base = f"Question type: {QUESTION_TYPES[qtype]['label']} ({QUESTION_TYPES[qtype]['description']}).\n"
    base += f"Dialect: {dialect}.\n"
    if difficulty:
        diff_text = {
            "easy": (
                "Difficulty: EASY. Keep the schema to 1 or 2 tables, "
                "example data to 4 to 6 rows, and the answer key to a "
                "single SELECT or simple JOIN. Avoid window functions, "
                "CTEs, or subqueries. The learner is here to drill core "
                "syntax."
            ),
            "moderate": (
                "Difficulty: MODERATE. Use 2 to 3 tables, example data of "
                "6 to 10 rows, and an answer key that requires one of: a "
                "GROUP BY with HAVING, a window function (ROW_NUMBER, RANK, "
                "SUM OVER), a single CTE, or a subquery. Include one realistic "
                "edge case (NULL, tie, empty group) the answer must handle."
            ),
            "hard": (
                "Difficulty: HARD. Use 3 to 5 tables, example data of 10 to "
                "16 rows, and an answer key that requires MULTIPLE techniques "
                "(e.g., two CTEs with a window function, a self-join with a "
                "running aggregate, gaps-and-islands, or recursive CTE). "
                "Include 2 or 3 edge cases (NULLs in different columns, "
                "ties, rows at boundary dates, partial groups) the answer "
                "must handle correctly."
            ),
        }.get(difficulty.lower())
        if diff_text:
            base += diff_text + "\n"
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
            "   - BULLET MARKER CHARACTERS — use the LITERAL Unicode characters shown:\n"
            "     * Top-level event rules: use '•' (Unicode U+2022 BULLET).\n"
            "     * Sub-section labels ('Preconditions:' / 'Actions:'): use '-' (ASCII hyphen).\n"
            "     * Leaf items (individual conditions or state changes): use '+' (ASCII plus).\n"
            "     * Forbidden at the TOP LEVEL: '*', '-', '1.', '(1)' &mdash; the prompt "
            "renderer detects '•' specifically and other characters leak into the "
            "user-facing output as literal text.\n"
            "   - Required structure example. Use the EXACT bullet characters shown "
            "(the top-level marker is the Unicode BULLET '•', not '*'):\n"
            "     • When `event_type` = 1 ('claim_review') applies:\n"
            "       - Preconditions:\n"
            "         + current `status` must be 'pending'.\n"
            "       - Actions:\n"
            "         + set `status` to 'under_review'.\n"
            "         + set `reviewer_id` to the event's `clinician_id`.\n"
            "     • When `event_type` = 2 ('approve_code') applies:\n"
            "       - Preconditions:\n"
            "         + current `status` must be 'under_review'.\n"
            "         + the event's `clinician_id` must equal the current `reviewer_id`.\n"
            "       - Actions:\n"
            "         + set `status` to 'approved'.\n"
            "     • Events that fail their preconditions are no-ops (the state row is unchanged).\n"
            "   - SELF-CHECK before returning: count the top-level event rules in your "
            "prompt. Each one MUST begin with the '•' character (Unicode U+2022). "
            "If you used '*', '-', or any other marker at the top level, REWRITE using "
            "'•'. Sub-sections still use '-' and leaf items still use '+', but the "
            "top-level marker is non-negotiable.\n"
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
    elif qtype == "filter_strategies":
        # Rotate EQUALLY across the six common filtering strategies (mirrors the
        # playbook's single-table Filter leaves).
        _filter_cases = {
            "comparison":
                "COMPARISON & BOOLEAN - a plain WHERE decided from the row itself. Combine "
                "two or more conditions with AND / OR using =, !=, <, >, BETWEEN, an IN literal "
                "list, modulo, or a date range. No subquery; single table.",
            "null_aware":
                "NULL-AWARE - the keep/drop test hinges on a value being MISSING: IS NULL / IS "
                "NOT NULL (or a COALESCE default). Include a column that is genuinely NULL in "
                "some rows so the natural wrong answer (=, !=, or NOT IN against NULL) silently "
                "drops them.",
            "pattern":
                "PATTERN MATCH - filter text against a pattern with LIKE / NOT LIKE (% and _) "
                "or a regex (~, !~, SIMILAR TO). Single table; the rule is a string shape "
                "(prefix, suffix, contains, format).",
            "membership":
                "MEMBERSHIP - keep rows that DO appear in / match another set: IN (subquery) or "
                "EXISTS. Schema needs a second table (or self-reference) the subquery reads; "
                "data must include rows that match and rows that don't.",
            "anti_join":
                "ANTI-JOIN - keep rows with NO match in another set ('never', 'did not', 'no "
                "X'): NOT EXISTS (preferred) or NOT IN. If NOT IN, the subquery column MUST be "
                "guaranteed non-NULL or the whole result vanishes - say so. Data must include at "
                "least one row with no match.",
            "group_threshold":
                "GROUP-THRESHOLD across distinct rows - an entity qualifies only if it clears "
                "MULTIPLE thresholds that live in SEPARATE rows (spent >= X in June AND >= X in "
                "July; bought A AND bought B). Answer = GROUP BY entity, one `SUM(CASE WHEN "
                "<slice> THEN value ELSE 0 END)` per condition, AND the thresholds in HAVING. "
                "FORBID the broken `GROUP BY entity, slice HAVING slice='A' AND slice='B'` form "
                "(a single row is only one slice). Data must include an entity that clears every "
                "threshold and ones that clear only some.",
        }
        _fcase = subtype if subtype in _filter_cases else random.choice(list(_filter_cases))
        base += (
            "FILTER STRATEGIES - the answer keeps a SUBSET of rows (or groups), nothing more. "
            "USE THIS EXACT strategy (do not substitute another): " + _filter_cases[_fcase] +
            "\n- Name the output columns and the ORDER BY in the prompt.\n"
            "- The answer_key is a single SELECT (no mutation, no window function unless the "
            "strategy needs none).\n"
            "- classification.recipe = `row-filter`. classification.input_arrival is "
            "`single_table` or `join` as the strategy requires; classification.output_shape is "
            "`filtered_rows`."
        )
    elif qtype == "scalar_extract":
        _se = {
            "single_aggregate": "SINGLE AGGREGATE over the whole table - one MAX / MIN / SUM / COUNT (or two combined, e.g. max minus min). No GROUP BY; the answer is one row, one value.",
            "top1": "TOP-1 row (the single winner) - the one row that wins a ranking: ORDER BY metric DESC LIMIT 1, with a deterministic tiebreak column. Output the winning row's identifier / value.",
            "nth": "Nth HIGHEST distinct value - 2nd, 3rd, Nth: SELECT DISTINCT metric ORDER BY metric DESC LIMIT 1 OFFSET N-1. The prompt MUST state what to return when there is no Nth. If NULL is required, wrap the LIMIT/OFFSET query in an outer SELECT (subquery in SELECT) so an empty result yields one NULL row, not zero rows.",
            "ratio": "SINGLE RATIO / percentage / weighted average over the whole table - accepted / sent, percent immediate, count-weighted mean. One row, one number; NULLIF the denominator to avoid divide-by-zero.",
        }
        _k = subtype if subtype in _se else random.choice(list(_se))
        base += (
            "Build a SCALAR-EXTRACT problem: a single table reduces to EXACTLY ONE row with one (or a few) scalar values. "
            "USE THIS EXACT shape: " + _se[_k] + "\n"
            "- Single table only; no join needed. The prompt names the output column(s) and any tiebreak.\n"
            "- TRAP to design for (Nth / top-1): if the prompt wants NULL when nothing qualifies (no 2nd highest, empty "
            "table), a bare WHERE returns ZERO rows, not a NULL row - the answer must use a subquery in SELECT so it "
            "always returns exactly one row.\n"
            "- Example data must exercise the boundary (ties at the top, or a case with no Nth value when NULL is required).\n"
            "- classification.recipe = `scalar-extract`; classification.output_shape is `single_value`."
        )
    elif qtype == "anti_join":
        _aj_forms = {
            "not_exists": "USE THIS FORM: NOT EXISTS (the NULL-safe default) -- `WHERE NOT EXISTS (SELECT 1 FROM b WHERE b.fk = a.id)`.",
            "left_join_null": "USE THIS FORM: LEFT JOIN ... WHERE right IS NULL -- `FROM a LEFT JOIN b ON b.fk = a.id WHERE b.fk IS NULL`.",
            "not_in": "USE THIS FORM: NOT IN, and guarantee the subquery column is NON-NULL (else every row vanishes) -- `WHERE a.id NOT IN (SELECT fk FROM b WHERE fk IS NOT NULL)`.",
        }
        base += (
            "Build an ANTI-JOIN problem: keep the rows in one set that have NO matching "
            "row in another set (customers who never ordered, products never sold, users "
            "with no logins). The answer keeps the NON-matchers.\n"
            "Hard requirements:\n"
            "1) Two tables (or a self-reference) sharing a key. Test data MUST include at "
            "least one entity with NO match (so the anti-join returns rows) AND at least "
            "one entity WITH a match (so the answer is not trivially every row).\n"
            "2) The three correct forms are NOT EXISTS, LEFT JOIN ... WHERE right IS NULL, "
            "and NOT IN. The NULL trap is the teaching point: NOT IN against a subquery "
            "column that can be NULL evaluates to UNKNOWN for every row and returns ZERO "
            "rows, so the answer must guarantee the subquery column is non-NULL or use "
            "NOT EXISTS.\n"
            "3) Do NOT make the headline an aggregate -- this is a row filter, not a count. "
            "The prompt MUST name the output columns and the ORDER BY. classification.recipe "
            "= `row-filter`; classification.output_shape is `filtered_rows`."
        )
        if subtype in _aj_forms:
            base += "\n\n" + _aj_forms[subtype]
    elif qtype == "delete_duplicates":
        base += (
            "DEDUP (delete duplicate rows) — a single table holds duplicate rows; physically "
            "DELETE the extras so one survivor per duplicate key remains. This MUST modify the "
            "table, not just SELECT distinct rows.\n"
            "Hard requirements:\n"
            "1) The answer_key is a DELETE statement (or statements) FOLLOWED BY a trailing "
            "`SELECT * FROM t ORDER BY ...` that shows the surviving rows; example_output_rows "
            "and test_expected_rows are the rows that REMAIN after the delete.\n"
            "2) The prompt must say 'delete' / 'remove' (not 'find' / 'show'). Duplicate key = "
            "the column(s) that define a duplicate (e.g. email); the table also has a primary "
            "key id used to choose the survivor.\n"
            "3) Test data MUST include at least one key with 2+ rows AND at least one key with "
            "a single row (which must survive untouched).\n"
            "- classification.recipe = `delete-duplicates`; classification.output_shape is "
            "`state_mutation`."
        )
        _dd_opts = ("keep_min_id", "self_join", "row_number")
        _dd = subtype if subtype in _dd_opts else random.choice(list(_dd_opts))
        _DD = {
            "keep_min_id": (
                "\nSUBTYPE PIN — KEEP THE LOWEST id (NOT IN MIN). Find the survivor per key with "
                "MIN(id), delete the rest: `DELETE FROM t WHERE id NOT IN (SELECT MIN(id) FROM t "
                "GROUP BY dup_key);`. The keep column MUST be the primary key so NOT IN is "
                "NULL-safe. Simplest, most portable form."
            ),
            "self_join": (
                "\nSUBTYPE PIN — SELF-JOIN DELETE (remove the higher-id twin). Pair each row with "
                "its duplicates and delete the losing side of an inequality: Postgres `DELETE "
                "FROM t USING t t2 WHERE t.dup_key = t2.dup_key AND t.id > t2.id;` (MySQL: "
                "`DELETE t FROM t JOIN t t2 ON t.dup_key = t2.dup_key AND t.id > t2.id;`). The "
                "direction of > / < picks which twin survives."
            ),
            "row_number": (
                "\nSUBTYPE PIN — ROW_NUMBER THEN DELETE rn > 1. Number rows within each duplicate "
                "group and delete everything past the first: a CTE with `ROW_NUMBER() OVER "
                "(PARTITION BY dup_key ORDER BY <survivor_order>)`, then `DELETE FROM t WHERE id "
                "IN (SELECT id FROM cte WHERE rn > 1);`. Use this when the survivor is chosen by "
                "a NON-id column (e.g. keep the most recent), which MIN(id) cannot express."
            ),
        }
        base += _DD[_dd]
    elif qtype == "enrich_join":
        base += (
            "LOOK UP COLUMNS FROM ANOTHER TABLE (enrich-join) — JOIN to pull a column or value "
            "onto each row. This is NOT an aggregate-per-group (that's the Join-Then-Aggregate "
            "recipe); the output keeps the row grain (or close to it) and the join just enriches "
            "it.\n"
            "- Schema: 2 tables sharing a key (or one table used twice for a self-join).\n"
            "- Use LEFT JOIN when non-matching left rows must stay (they show NULL); INNER when "
            "only matches should appear. Design at least one row that exposes that choice.\n"
            "- classification.recipe = `enrich-join`."
        )
        _ej_opts = ("straight_lookup", "self_join", "cross_join", "per_group", "compound")
        _ej = subtype if subtype in _ej_opts else random.choice(list(_ej_opts))
        _EJ = {
            "straight_lookup": (
                "\nSUBTYPE PIN — STRAIGHT LOOKUP / ENRICH. INNER or LEFT JOIN a reference / dim "
                "table to pull a descriptive column (name, category) onto each fact row. Keep the "
                "fact grain; the join adds columns, it does not aggregate. Use LEFT JOIN if rows "
                "with no matching reference must still appear with NULL."
            ),
            "self_join": (
                "\nSUBTYPE PIN — SELF-JOIN, ONE TABLE TWO ROLES. Alias the SAME table twice so a "
                "row can relate to another row in that table (employee -> manager via reports_to; "
                "follower -> followee; pair two co-occurring rows). The ON clause relates the two "
                "aliases. For unordered pairs add a.id < b.id so each pair appears once and no row "
                "pairs with itself. Design data with a row that has no partner (e.g. the top "
                "manager) to test INNER vs LEFT."
            ),
            "cross_join": (
                "\nSUBTYPE PIN — CROSS JOIN, ALL COMBINATIONS. CROSS JOIN two small sets to force "
                "every combination (every (entity, category) pair, a skeleton grid), then LEFT "
                "JOIN the actuals so missing combinations show as 0 / NULL. Design data missing at "
                "least one combination so the zero-fill is visible."
            ),
            "per_group": (
                "\nSUBTYPE PIN — MATCH EACH ROW TO A PER-GROUP VALUE. Compute a per-group value in "
                "a subquery / CTE (the group's avg, min, earliest date), then JOIN it back so each "
                "row sits next to its group's value (e.g. flag rows above their department average). "
                "The output keeps the row grain; the aggregate is a lookup, not the final answer."
            ),
            "compound": (
                "\nSUBTYPE PIN — COMPOUND ELIGIBILITY. Roll up per entity in a CTE, then JOIN / "
                "qualify with a MULTI-condition filter (e.g. entities that did A at least N times "
                "AND never did B). The CTE produces the per-entity facts; the outer query keeps "
                "only entities meeting every condition."
            ),
        }
        base += _EJ[_ej]
    elif qtype == "dml":
        # dml_op is chosen randomly in generate_problem so each generation lands on
        # a different operation. If somehow not provided, default to UPDATE.
        op = (dml_op or "UPDATE").upper()
        # DELETE rotates across the seven single-statement DELETE cases at EQUAL
        # probability (mirrors the playbook's Single-Statement DELETE case containers:
        # conditional, duplicate rows, orphan rows, cross table, time-based pruning,
        # two-condition group+row, NULL-safe positive WHERE).
        _delete_cases = {
            "conditional":
                "CONDITIONAL DELETE - remove rows where one or more columns ON THE ROW "
                "meet a rule. Plain `DELETE FROM t WHERE col_a <op> val AND/OR col_b = "
                "'...';` with two or more conditions; no subquery needed.",
            "duplicate_rows":
                "DUPLICATE ROWS - keep one row per group, delete the rest: `DELETE FROM t "
                "WHERE pk NOT IN (SELECT MIN(pk) FROM t GROUP BY group_cols);` (MAX to keep "
                "the latest). The keep column MUST be the primary key so NOT IN is NULL-safe. "
                "Test data must have at least one group with 2+ rows.",
            "orphan_rows":
                "ORPHAN ROWS - delete rows whose foreign key has no matching parent: `DELETE "
                "FROM t WHERE fk NOT IN (SELECT pk FROM parent WHERE pk IS NOT NULL);` or NOT "
                "EXISTS. Schema MUST include a parent table and test data MUST contain at "
                "least one orphan (a fk with no parent row).",
            "cross_table":
                "CROSS-TABLE DELETE - delete rows where a RELATED row in another table meets "
                "a condition. Postgres: `DELETE FROM t USING other o WHERE t.fk = o.id AND "
                "o.status = '...';`  MySQL: `DELETE t FROM t JOIN other o ON t.fk = o.id WHERE "
                "o.status = '...';`. Schema MUST include the second table with the gating column.",
            "time_based":
                "TIME-BASED PRUNING - delete rows older than a cutoff: `DELETE FROM t WHERE "
                "created_at < CURRENT_DATE - N;` (older = smaller date = `<`). Use a literal "
                "interval, not a parameter. Test data must straddle the cutoff.",
            "two_condition":
                "TWO-CONDITION (group + row) - the GROUP must qualify AND the individual ROW "
                "must qualify, as two separate filters: `DELETE FROM t WHERE group_id IN "
                "(SELECT group_id FROM t GROUP BY group_id HAVING COUNT(*) >= N) AND "
                "row_status = '...';`. This is NOT the keep-MIN dedup shape - the group gate "
                "is a HAVING subquery and the row gate is a plain column condition. Test data "
                "must include a qualifying group whose rows mix exempt and non-exempt.",
            "null_safe_positive":
                "NULL-SAFE POSITIVE WHERE - a relevant column is NULLABLE, so the inverse "
                "`NOT IN (keep set)` form would break. The answer MUST write the WHERE for the "
                "rows to DELETE positively, e.g. `DELETE FROM t WHERE duration < 180 OR "
                "quality_flag IS NULL;`. FORBID the `WHERE pk NOT IN (SELECT ...)` inverse "
                "here. Test data MUST include at least one row with a NULL in the relevant column.",
        }
        _delete_case = subtype if subtype in _delete_cases else random.choice(list(_delete_cases))
        _delete_specific = (
            "Generate a DELETE problem. The answer_key is a single bare `DELETE` statement "
            "followed by a confirming SELECT. The prompt MUST say 'write a single DELETE "
            "statement'.\n"
            "USE THIS EXACT CASE (do not substitute another): " + _delete_cases[_delete_case]
        )
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
            "DELETE": _delete_specific,
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
        elif flavor == "consecutive_day_streak_per_entity":
            base += (
                "FLAVOR: consecutive_day_streak_per_entity (medium / hard only) -- per entity streak detection with DUPLICATE same day source rows that must be deduped FIRST, then HAVING COUNT(*) >= N gate, then EXISTS / IN membership semantics in the final SELECT. LeetCode #1454 Active Users shape.\n"
                "Hard requirements:\n"
                "1) Schema MUST contain TWO tables: a DIM entity table (id, name) and a FACT event table "
                "(entity_id, event_date) WHERE THE PROMPT EXPLICITLY STATES the fact table may contain "
                "DUPLICATE (entity_id, event_date) rows (the user can do the event multiple times in a day). "
                "Examples: Accounts(id, name) + Logins(id, login_date), Members(id, name) + Workouts("
                "member_id, workout_date), Customers(id, name) + Orders(id, order_date).\n"
                "2) The prompt asks for the entities (id + name) who have AT LEAST N consecutive days of "
                "activity in the fact table. Pick a small literal N: 5 (LeetCode default), 3, 4, 7. State "
                "the threshold explicitly in the prompt.\n"
                "3) The prompt MUST mention duplicate same day events to flag the dedupe step. Phrasing "
                "variants:\n"
                "   - 'The fact table may contain duplicate rows for the same (entity_id, date) because "
                "an entity can do the event multiple times in a day.'\n"
                "   - 'Users may log in multiple times in the same day, so duplicate (id, login_date) "
                "rows can appear.'\n"
                "4) The answer_key MUST follow the 4 CTE staircase pattern:\n"
                "   CTE 1 `base`: `SELECT DISTINCT entity_id, event_date FROM fact_table` (deduping FIRST).\n"
                "   CTE 2 `date_groups`: `SELECT entity_id, event_date - ROW_NUMBER() OVER (PARTITION BY "
                "entity_id ORDER BY event_date)::int AS grp FROM base`.\n"
                "   CTE 3 `streaks`: `SELECT entity_id FROM date_groups GROUP BY entity_id, grp HAVING "
                "COUNT(*) >= N`.\n"
                "   Final SELECT: `SELECT a.id, a.name FROM dim_table a WHERE EXISTS (SELECT 1 FROM "
                "streaks s WHERE s.entity_id = a.id) ORDER BY a.id;`. The `a.id IN (SELECT entity_id "
                "FROM streaks)` form is equally acceptable; the per user 2 stage aggregate form "
                "(streak_lengths -> per_user HAVING MAX >= N) is also acceptable.\n"
                "5) PARTITION BY entity_id is mandatory on the ROW_NUMBER window. Without it, the rn "
                "sequence runs across all entities globally and the date - rn grp collapses unrelated "
                "entities into the same streak.\n"
                "6) The FORBIDDEN anti pattern: `SELECT DISTINCT a.id, a.name FROM Accounts a JOIN "
                "date_groups d ON d.id = a.id GROUP BY a.id, a.name, grp HAVING COUNT(*) >= N`. This "
                "treats the symptom (duplicate output rows) with a cosmetic DISTINCT instead of fixing "
                "the grain of the final SELECT. Test data MUST be designed so this anti pattern fails "
                "without the DISTINCT (see requirement #7 below).\n"
                "7) Test data MUST include: (a) AT LEAST one entity with NO qualifying streak (must be "
                "excluded from output); (b) AT LEAST one entity with EXACTLY ONE qualifying streak "
                "(included once -- the simple case); (c) AT LEAST one entity with TWO OR MORE non "
                "overlapping qualifying streaks of >= N days each (this is the case that exposes the "
                "DISTINCT anti pattern: without DISTINCT or membership semantics, this entity appears "
                "MULTIPLE times in the output, once per streak); (d) AT LEAST one entity with DUPLICATE "
                "same day rows in the fact table (exposes the missing dedupe step -- without `SELECT "
                "DISTINCT id, event_date FROM Logins`, the duplicate day advances rn by 1 without "
                "advancing event_date, breaking the streak math).\n"
                "8) The example_output_rows MUST contain AT LEAST 1 entity but also be designed so the "
                "test data demonstrably exposes the duplicate streak case described in 7c above. The "
                "example shape can be smaller (one qualifying entity is fine) while the test data is "
                "the trap.\n"
                "9) The prompt MUST state the output columns (id, name) and the ORDER BY (typically "
                "id ASC). Set classification.output_shape to `fewer_rows`. classification.input_arrival "
                "= `join`."
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
        elif flavor == "extreme_exclusion":
            base += (
                "FLAVOR: extreme_exclusion (find the entities whose per-group metric is NEITHER the max NOR the min — both dialects, DENSE_RANK ASC + DENSE_RANK DESC pair).\n"
                "Hard requirements:\n"
                "1) Schema MUST have TWO tables: a DIM table holding the entities to be classified "
                "(activities, products, regions, departments) and a FACT table holding rows that "
                "JOIN to the dim via the entity key. The headline metric is the per-entity COUNT "
                "(or per-entity SUM) of fact rows — NOT a column already on the dim.\n"
                "2) The prompt asks for the entities whose participant/order/event count is "
                "NEITHER the maximum NOR the minimum across all entities. Phrasing variants:\n"
                "   - 'Find activities with neither the maximum nor the minimum number of participants.'\n"
                "   - 'Return products that are neither the best-selling nor the worst-selling.'\n"
                "   - 'Find regions whose total revenue is neither the highest nor the lowest.'\n"
                "3) The answer_key MUST use the DENSE_RANK ASC + DENSE_RANK DESC pair (both windows "
                "over the same per-entity metric, opposite directions), then filter where BOTH "
                "rn_asc > 1 AND rn_desc > 1. Canonical CTE staircase:\n"
                "   - CTE 1: per-entity COUNT/SUM by GROUP BY on the fact table.\n"
                "   - CTE 2: LEFT JOIN dim to CTE 1, COALESCE the count to 0 (defensive), then "
                "     two window functions: DENSE_RANK ASC and DENSE_RANK DESC over the count.\n"
                "   - Final SELECT: filter WHERE rn_asc > 1 AND rn_desc > 1.\n"
                "4) DENSE_RANK, NOT ROW_NUMBER. The prompt MUST be explicit that ties at the "
                "extremes are ALL excluded (e.g. 'if two activities tie for the maximum, exclude "
                "BOTH'). ROW_NUMBER would break ties arbitrarily and silently keep all-but-one of "
                "the tied min/max rows — design test data that exposes this if the user picks "
                "ROW_NUMBER. RANK also works in most cases; DENSE_RANK is the canonical pick "
                "because the phrase 'tied = same rank' reads cleanest in the WHERE clause.\n"
                "5) Test data MUST include at least one TIE somewhere (typically at the min or "
                "max) so the DENSE_RANK vs ROW_NUMBER trap is visible. Test data MUST also have "
                "more than 3 entities so the 'middle' result is non-trivial — at least 4 entities "
                "with at least 3 distinct count values is the minimum.\n"
                "6) Edge case: if every entity has the SAME count, every row's rn_asc = 1 AND "
                "rn_desc = 1, so the result is empty. The prompt does NOT need to enumerate this, "
                "but the test data must not accidentally land there.\n"
                "7) The prompt MUST explicitly state the output column(s) (usually just the entity "
                "name) and the ORDER BY (often 'any order' for this shape).\n"
                "8) Forbidden anti-patterns the prompt should design AGAINST:\n"
                "   - `WHERE n != (SELECT MIN(n) ...) AND n != (SELECT MAX(n) ...)`: works on "
                "     simple cases but rank-based phrasing is the lesson here.\n"
                "   - `WHERE n NOT IN (SELECT MIN(n) FROM ...) AND n NOT IN (SELECT MAX(n) FROM ...)`: "
                "     same as above.\n"
                "   - LIMIT/OFFSET tricks: not transferable, fail with ties.\n"
            )
        elif flavor == "extreme_exclusion_per_group":
            base += (
                "FLAVOR: extreme_exclusion_per_group (per partition DENSE_RANK ASC + DESC, then HAVING MIN across the entity's rows to enforce 'never extreme in ANY group' &mdash; both dialects, LeetCode #1412 Find the Quiet Students in All Exams shape).\n"
                "Hard requirements:\n"
                "1) Schema MUST have TWO tables: a DIM entity table (student_id + name; "
                "employee_id + name; player_id + name) and a FACT events table that has a "
                "GROUP COLUMN (exam_id, round_id, match_id, season_id) AND a metric column "
                "(score, time, points). The PRIMARY KEY on the fact table MUST be the pair "
                "(group_col, entity_id) so a given entity appears at most once per group, but "
                "can participate in many groups.\n"
                "2) The prompt asks for entities who, IN EVERY GROUP THEY PARTICIPATED IN, "
                "were NEITHER the maximum NOR the minimum on the metric. Phrasing variants:\n"
                "   - 'Find students who took at least one exam and were never the highest or "
                "lowest scorer in any of their exams.'\n"
                "   - 'Return employees who completed at least one project review and were "
                "never rated highest or lowest by their reviewers in any review.'\n"
                "   - 'Find players who appeared in at least one match and were never the "
                "MVP nor the worst performer in any match they played.'\n"
                "3) The prompt MUST explicitly require BOTH (a) 'participated in at least one "
                "group' (the dim entities with zero fact rows MUST be excluded), AND (b) "
                "'never extreme in ANY of their groups' (one extreme appearance in one group "
                "is enough to disqualify the entity).\n"
                "4) The answer_key MUST use the per partition DENSE_RANK pair followed by "
                "GROUP BY entity + HAVING MIN. Canonical CTE staircase:\n"
                "   - CTE 1 `base`: SELECT group_col, entity_id, DENSE_RANK() OVER "
                "(PARTITION BY group_col ORDER BY metric ASC) AS rn_asc, DENSE_RANK() OVER "
                "(PARTITION BY group_col ORDER BY metric DESC) AS rn_desc FROM fact_table.\n"
                "   - Final SELECT: JOIN dim ON dim.entity_id = base.entity_id (INNER, "
                "so entities with zero fact rows are excluded automatically); GROUP BY "
                "dim.entity_id, dim.name; HAVING MIN(rn_asc) > 1 AND MIN(rn_desc) > 1; "
                "ORDER BY entity_id.\n"
                "5) PARTITION BY group_col is MANDATORY on BOTH window functions. Without "
                "it, DENSE_RANK ranks across ALL fact rows together, and the answer becomes "
                "'never globally min or max,' which is a different (and easier) problem. "
                "Design test data so the global-min-only solution returns the WRONG rows.\n"
                "6) MIN(rn) > 1 is the canonical aggregate for 'FOR ALL rows of this entity, "
                "rn > 1.' Anti patterns explicitly forbidden because they look right but "
                "test EXISTS instead of FOR ALL:\n"
                "   - `BOOL_OR(rn_asc > 1)` reads as 'there exists at least one row where "
                "they weren't the min' &mdash; passes any entity who was extreme SOMETIMES, "
                "wrong.\n"
                "   - `NOT BOOL_OR(rn_asc = 1) AND NOT BOOL_OR(rn_desc = 1)` is correct "
                "(reads as 'NEVER was min and NEVER was max') and is an acceptable alternate "
                "form &mdash; the validator MUST accept this OR the MIN > 1 form.\n"
                "   - `MAX(CASE WHEN rn_asc = 1 OR rn_desc = 1 THEN 1 ELSE 0 END) = 0` is "
                "also correct and acceptable.\n"
                "7) Test data MUST include: (a) AT LEAST one entity participating in "
                "MULTIPLE groups who is NEVER extreme in any (the only one(s) that should "
                "appear in the output); (b) AT LEAST one entity who is extreme in SOME "
                "groups but not others (must be excluded &mdash; this is the case the BOOL_OR "
                "anti pattern would incorrectly INCLUDE); (c) AT LEAST one entity in the "
                "dim with ZERO fact rows (must be excluded by the INNER JOIN, NOT by an "
                "explicit filter); (d) AT LEAST one TIE at an extreme in some group (e.g. "
                "two students tied for highest in one exam, both must be flagged as extreme "
                "&mdash; tests DENSE_RANK vs ROW_NUMBER); (e) AT LEAST 3 distinct groups so "
                "the 'never in ANY' aggregate has work to do.\n"
                "8) DENSE_RANK, NOT ROW_NUMBER. With ties at an extreme, ROW_NUMBER picks "
                "ONE of the tied entities arbitrarily, so the OTHER tied entity's "
                "MIN(rn_asc) would still be 1 in some other row but might silently exceed 1 "
                "in the tied row &mdash; depending on tie breaking, an entity that tied for "
                "the extreme could pass the gate incorrectly. DENSE_RANK gives all tied "
                "rows the same rank, so every tied entity is correctly flagged.\n"
                "9) The prompt MUST explicitly state the output columns (typically entity "
                "id + entity name) and the ORDER BY (usually entity_id ASC). Output_shape "
                "= `fewer_rows`."
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
        # Flavor decides which pivot shape to generate. Two flavors at present:
        #   multi_column_pivot - classic long-to-wide with one CASE per target column
        #   signed_aggregate   - opposing categories (Buy/Sell, debit/credit, income/expense)
        #                        collapsed into a single net total via SUM(CASE +/- price).
        flavor = pivot_flavor or "multi_column_pivot"
        base += (
            "Build a PIVOT problem using PostgreSQL CASE expressions inside an "
            "aggregate. PostgreSQL has no native PIVOT keyword; the canonical approach "
            "is `aggfn(CASE WHEN ... THEN ... END)` in a GROUP BY query. The exact "
            f"shape is the '{flavor}' flavor (chosen by the harness this run).\n\n"
        )
        if flavor == "multi_column_pivot":
            base += (
                "FLAVOR: multi_column_pivot &mdash; classic long-to-wide reshape. One CASE "
                "expression per target column, all under one GROUP BY entity_key.\n\n"
                "PIVOT SOURCE TYPE -- rotate across generations to give the learner exposure "
                "to all three:\n"
                "  TYPE 1 (stored category column): the pivot column is a stored "
                "value_label column (region name, subject, severity tier). The CASE branches "
                "compare directly against the stored value.\n"
                "  TYPE 2 (DOW or month extracted from a DATE column): the pivot column is "
                "DERIVED from a date via TO_CHAR or EXTRACT. Examples: 'sales by category by "
                "day of week,' 'orders by region by month name,' 'sessions by plan by "
                "weekday.' At medium / hard difficulty, this TYPE is the default choice.\n"
                "  TYPE 3 (bucketed numeric range expressed as labels): the pivot column is "
                "a CASE on a numeric column (age band, salary tier, duration bucket). "
                "Functionally equivalent to TYPE 1 once the CASE assigns the label.\n\n"
                "When TYPE 2 is picked, the answer_key MUST use ONE of these forms for the "
                "day or month extraction (the prompt MUST not name a specific form; either "
                "is acceptable):\n"
                "  - `TO_CHAR(date_col, 'FMDay')` -- 'Monday', 'Tuesday', ... (FM strips "
                "padding; without FM the result is padded to 9 characters and silently "
                "fails string equality against literals).\n"
                "  - `TRIM(TO_CHAR(date_col, 'Day'))` -- same result, slightly noisier.\n"
                "  - `EXTRACT(ISODOW FROM date_col)` returning 1-7 (Mon-Sun), if the prompt "
                "phrasing allows numeric output instead of day name string in the CASE.\n"
                "  - `TO_CHAR(date_col, 'FMMonth')` / `TRIM(TO_CHAR(..., 'Month'))` for "
                "month name pivots; same padding rule as day name.\n"
                "When TYPE 2 is picked, the prompt MUST be designed so the TRAP fires: the "
                "test data MUST include AT LEAST one Monday, Tuesday, Thursday, Friday, "
                "Saturday, OR Sunday order (i.e., NOT just Wednesday data). A learner who "
                "uses `TO_CHAR(date, 'Day')` without the FM prefix will see every column "
                "except Wednesday (or September for month name pivots) come back as 0 "
                "because 'Wednesday' is the only 9 character English day name and matches "
                "literal 'Wednesday' without padding; 'September' is the only 9 character "
                "month name. This is the marquee learning lesson of TYPE 2.\n\n"
                "Hard requirements:\n"
                "1) Schema MUST contain ONE main long-format source table with shape "
                "(entity_key, category_column, value_column) for TYPE 1/3, OR (entity_key, "
                "date_column, value_column) for TYPE 2. Examples by type:\n"
                "   TYPE 1: monthly_sales(region, month_name, sales_amount), exam_scores("
                "student_id, subject, score), ticket_counts(team_id, severity, ticket_count).\n"
                "   TYPE 2: orders(order_id, item_category, order_date, quantity), sessions("
                "session_id, plan, session_ts, minutes), shipments(shipment_id, region, "
                "ship_date, units). For TYPE 2 schemas, include 1 small dim table with the "
                "entity_key so categories with zero rows still appear (LEFT JOIN from dim).\n"
                "   TYPE 3: employees(emp_id, dept_id, salary), patients(patient_id, "
                "condition, age). The CASE assigns the bucket label inline.\n"
                "2) The prompt MUST explicitly list the FIXED set of category values that "
                "become target columns (e.g., 'pivot the months Jan, Feb, Mar into "
                "columns jan_sales, feb_sales, mar_sales' or 'pivot into Monday, Tuesday, "
                "Wednesday, Thursday, Friday, Saturday, Sunday columns'). The category set "
                "is closed; the user is NOT expected to write dynamic SQL.\n"
                "3) The prompt MUST name each target column AND the aggregation function "
                "(SUM, MAX, MIN, COUNT, AVG). Forbidden: 'pivot the data' without naming "
                "columns; 'aggregate by month' without naming the function.\n"
                "4) The answer_key MUST use the form:\n"
                "   `aggfn(CASE WHEN category_expr = 'val_a' THEN value_column ELSE 0 END) AS col_a,`\n"
                "   `aggfn(CASE WHEN category_expr = 'val_b' THEN value_column ELSE 0 END) AS col_b,`\n"
                "   ... grouped by the entity key. For TYPE 2 problems, `category_expr` is "
                "`TO_CHAR(date_col, 'FMDay')` or equivalent (see source type guidance above). "
                "For TYPE 1, it's the stored column name. The `ELSE 0` form makes SUM-over-"
                "empty-group lands at 0 instead of NULL and removes the need for an outer "
                "COALESCE.\n"
                "5) For SUM and COUNT pivots, wrap with `COALESCE(..., 0)` ONLY if the "
                "prompt asks for 0 instead of NULL when an entity has no rows in that "
                "category AND the answer_key omits the `ELSE 0` form in CASE. The prompt "
                "MUST be explicit about NULL vs 0 expected output.\n"
                "6) Test data MUST include AT LEAST one entity that is missing rows for "
                "AT LEAST one category, so the user sees how the CASE+aggregation handles "
                "the empty bucket (NULL by default, 0 if COALESCE'd or ELSE 0 used). For "
                "TYPE 2 specifically, include AT LEAST one entity with ZERO rows at all in "
                "the fact table (so the LEFT JOIN from dim to fact is exercised).\n"
                "7) Test data MUST include AT LEAST one entity with MULTIPLE rows in the "
                "SAME category, so the aggregation actually does work (SUM combines them, "
                "MAX picks one, etc.). For TYPE 2, this means at least one entity with "
                "MULTIPLE orders on the same DOW or month.\n"
                "8) The prompt MUST explicitly state the full ordered output column list "
                "AND the ORDER BY clause for the final result.\n"
                "9) Set classification.output_shape to `fewer_rows` (one row per entity "
                "in the wide output)."
            )
        elif flavor == "signed_aggregate":
            base += (
                "FLAVOR: signed_aggregate &mdash; opposing categories collapsed into a "
                "SINGLE net total. Canonical LeetCode #1393 'Capital Gain/Loss' shape: "
                "Buy and Sell rows for each stock; the net is SUM of Sell prices minus "
                "SUM of Buy prices per stock. The pivot is conceptual (two categories "
                "into +/-), but the output is ONE column per entity, not multiple.\n\n"
                "Hard requirements:\n"
                "1) Schema MUST contain ONE main long-format source table with shape "
                "(entity_key, signed_category_column, value_column [, extra_dimension]). "
                "The signed_category_column has exactly TWO meaningful values that are "
                "OPPOSITES (Buy / Sell, debit / credit, income / expense, in / out, "
                "deposit / withdrawal, refund / charge, return / shipment). Examples: "
                "stock_trades(stock_name, operation, operation_day, price) with operation "
                "in (Buy, Sell); ledger_entries(account_id, entry_type, amount) with "
                "entry_type in (debit, credit); budget_lines(category_id, line_type, "
                "amount) with line_type in (income, expense). Optionally include 1 "
                "lookup table to name the entity.\n"
                "2) The prompt MUST state the BUSINESS meaning of the net (capital gain "
                "/ loss, net cash flow, net position, surplus / deficit) AND which "
                "category contributes POSITIVELY vs NEGATIVELY. Example: 'Sell increases "
                "capital, Buy decreases it'. Forbidden: 'compute the difference' without "
                "naming which side is positive.\n"
                "3) The prompt MUST name the SINGLE output column (e.g., "
                "`capital_gain_loss`, `net_amount`, `net_position`) and confirm that "
                "negative values are valid (loss is reported as a negative number).\n"
                "4) The answer_key MUST use the form (one column, two CASEs subtracted "
                "OR one CASE with both branches):\n"
                "   `SELECT entity_key,`\n"
                "   `       SUM(CASE WHEN cat = 'positive_val' THEN value ELSE 0 END`\n"
                "   `         - CASE WHEN cat = 'negative_val' THEN value ELSE 0 END) AS net`\n"
                "   `FROM t GROUP BY entity_key;`\n"
                "   The single-CASE alternative is equally acceptable:\n"
                "   `SUM(CASE WHEN cat = 'positive_val' THEN value`\n"
                "   `         WHEN cat = 'negative_val' THEN -value END) AS net`.\n"
                "5) Test data MUST include: (a) AT LEAST one entity with the positive "
                "side TOTAL GREATER than the negative side total (positive net); (b) AT "
                "LEAST one entity with the negative side total GREATER than the positive "
                "(negative net, loss); (c) AT LEAST one entity with MULTIPLE Buy / Sell "
                "or multiple debit / credit pairs so the SUM actually does work over a "
                "stack of rows. The example expected_output MUST contain both a positive "
                "and a negative net value, so the sign convention is visible.\n"
                "6) The prompt MUST be explicit about which entities to return. If the "
                "prompt requires ALL entities (including ones with no rows in either "
                "category), the schema MUST include the entity lookup as a separate dim "
                "table and the answer key MUST LEFT JOIN dim -> long table so an entity "
                "with zero rows still appears with net 0 (use COALESCE around the SUM).\n"
                "7) The prompt MUST explicitly state the ORDER BY for the final result. "
                "If the prompt says 'in any order' (LeetCode style), the answer key may "
                "omit ORDER BY, but the EXAMPLE output rows MUST be sortable to a "
                "deterministic order for grading.\n"
                "8) Forbidden anti-patterns: writing the answer as TWO joined subqueries "
                "(one for SUM of Buy, one for SUM of Sell) joined on entity_key. The "
                "whole point of this flavor is the conditional aggregation inside ONE "
                "GROUP BY scan. Self-joins on the entity_key with WHERE op = 'Buy' and a "
                "second copy WHERE op = 'Sell' are also forbidden &mdash; they're "
                "quadratic and miss the lesson.\n"
                "9) Set classification.output_shape to `fewer_rows` (one row per entity "
                "with the single net column)."
            )
        elif flavor == "membership_filter":
            base += (
                "FLAVOR: membership_filter &mdash; set membership gate using CASE inside "
                "an aggregate, applied in HAVING (not SELECT). The canonical shape: "
                "filter entities whose related rows ALL contain a required category set "
                "AND NONE contain a forbidden category set ('customers who bought A and "
                "B but not C', 'students enrolled in math AND english but not history', "
                "'patients with prescriptions for X AND Y but never Z'). LeetCode #1965 "
                "shape.\n\n"
                "Hard requirements:\n"
                "1) Schema MUST contain TWO tables: a dim entity table "
                "(entity_id, entity_name, ...) and a fact relations table "
                "(relation_id, entity_id, category_name, ...). Examples: "
                "customers(customer_id, customer_name) + orders(order_id, customer_id, "
                "product_name); students(student_id, student_name) + enrollments("
                "enrollment_id, student_id, course_name); patients(patient_id, "
                "patient_name) + prescriptions(rx_id, patient_id, drug_name).\n"
                "2) The prompt MUST explicitly list the REQUIRED categories (the ALL set) "
                "AND the FORBIDDEN categories (the NONE set) as fixed string literals. "
                "Examples: 'customers who bought products A AND B but did not buy "
                "product C'; 'students enrolled in math AND english AND science but NOT "
                "history'. Both sets are closed; no dynamic SQL needed. AT LEAST 2 "
                "required categories AND AT LEAST 1 forbidden category.\n"
                "3) The prompt MUST state the business motivation (recommend the "
                "forbidden product to qualifying customers, suggest the missing course, "
                "etc.) so the membership rule reads as a real query, not abstract set "
                "math.\n"
                "4) The answer_key MUST use one of TWO accepted forms (BOTH are correct; "
                "either is acceptable):\n"
                "   FORM A (BOOL_OR per category):\n"
                "     `SELECT e.entity_id, e.entity_name`\n"
                "     `FROM entity_table AS e`\n"
                "     `JOIN fact_table AS f ON f.entity_id = e.entity_id`\n"
                "     `GROUP BY e.entity_id, e.entity_name`\n"
                "     `HAVING BOOL_OR(f.category = 'A')`\n"
                "     `   AND BOOL_OR(f.category = 'B')`\n"
                "     `   AND NOT BOOL_OR(f.category = 'C')`\n"
                "     `ORDER BY e.entity_id;`\n"
                "   FORM B (MAX(CASE ... THEN 1 ELSE 0 END) per category):\n"
                "     `SELECT e.entity_id, e.entity_name`\n"
                "     `FROM entity_table AS e`\n"
                "     `JOIN fact_table AS f ON f.entity_id = e.entity_id`\n"
                "     `GROUP BY e.entity_id, e.entity_name`\n"
                "     `HAVING MAX(CASE WHEN f.category = 'A' THEN 1 ELSE 0 END) = 1`\n"
                "     `   AND MAX(CASE WHEN f.category = 'B' THEN 1 ELSE 0 END) = 1`\n"
                "     `   AND MAX(CASE WHEN f.category = 'C' THEN 1 ELSE 0 END) = 0`\n"
                "     `ORDER BY e.entity_id;`\n"
                "   The validator MUST accept either form. They produce identical rows; "
                "FORM A is Postgres native and reads as English, FORM B is portable "
                "across MySQL / Redshift / Snowflake / BigQuery.\n"
                "5) Test data MUST be designed so a NAIVE arithmetic SUM approach "
                "(`SUM(CASE WHEN required THEN 1 WHEN forbidden THEN -1 ELSE 0 END) = "
                "N`) silently fails. To achieve this, the test data MUST include: "
                "(a) AT LEAST one qualifying entity that bought ONE of the required "
                "categories MULTIPLE TIMES (e.g. bought A twice and B once, but never "
                "C) &mdash; the naive arithmetic gate excludes them; AND (b) AT LEAST "
                "one non qualifying entity that bought a required category EXTRA times "
                "to land at the arithmetic threshold despite owning the forbidden "
                "category (e.g. bought A twice, B once, C once: arithmetic sum = "
                "1+1+1-1 = 2, but the entity owns C and must be excluded). The "
                "MEMBERSHIP rule (existence flags) correctly accepts (a) and rejects "
                "(b); the COUNTING rule (arithmetic SUM) gets BOTH wrong.\n"
                "6) Test data MUST include AT LEAST one entity in the dim table that "
                "has no rows in the fact table (a customer with zero orders), to "
                "exercise the INNER JOIN behavior (they should NOT appear in the "
                "output, since you can't have bought A AND B with zero orders).\n"
                "7) Test data MUST include at least 1 'matches required, also has "
                "forbidden' entity (correctly excluded) AND at least 1 'matches "
                "required, none of forbidden' entity (correctly included) so the "
                "example output demonstrates both branches of the gate.\n"
                "8) Forbidden anti patterns: the SUM = N arithmetic gate described in "
                "requirement #5 above (counts purchases instead of presence; breaks on "
                "duplicates). Also forbidden: writing the answer as N separate "
                "subqueries (one per category) joined together &mdash; the whole point "
                "is one GROUP BY scan with one aggregate per category. Self joins on "
                "the fact table with WHERE clauses pinning each copy to one category "
                "are also forbidden (quadratic, misses the lesson).\n"
                "9) The prompt MUST state the ORDER BY for the final result (typically "
                "entity_id ASC). Set classification.output_shape to `fewer_rows` (one "
                "row per qualifying entity)."
            )
        elif flavor == "threshold_per_category":
            base += (
                "FLAVOR: threshold_per_category &mdash; numeric threshold gate across "
                "multiple categories in HAVING. Same technique family as "
                "membership_filter but the per category test is a NUMERIC threshold "
                "(SUM(CASE) &gt;= N) instead of an EXISTENCE flag (BOOL_OR). Canonical "
                "shape: 'customers who spent at least $X in EACH of June and July,' "
                "'employees who logged &gt;= 40 hours in EACH of Q1 and Q2,' 'students "
                "who scored &gt;= 70 on EACH of midterm and final.'\n\n"
                "Hard requirements:\n"
                "1) Schema MUST contain TWO or THREE tables: a dim entity table "
                "(customer_id, name; employee_id, name; student_id, name) + a fact table "
                "with a category column (month, quarter, exam_type) AND a value column "
                "to sum (revenue, hours, score) + OPTIONALLY a third price / multiplier "
                "lookup table (e.g. products.price so the spent value = quantity * price "
                "must be derived). Examples: customers + orders + products(price); "
                "employees + timesheets(hours, hourly_rate); students + exam_results.\n"
                "2) The prompt MUST explicitly list TWO to FOUR FIXED category values "
                "AND the per category threshold (e.g. 'spent at least $100 in EACH of "
                "June 2020 AND July 2020,' 'logged at least 40 hours in EACH of Q1 AND "
                "Q2 of 2024'). The threshold MAY be the same across categories or "
                "different (June &gt;= 100 AND July &gt;= 50); state both versions of "
                "the prompt explicitly. The category set is CLOSED.\n"
                "3) The prompt MUST state the business motivation: e.g. 'customers who "
                "kept spending across the summer,' 'consistent hour loggers,' 'students "
                "who maintained performance.' The 'EACH' / 'BOTH' wording is critical "
                "&mdash; if the prompt says 'OR' instead, the answer is a UNION not an "
                "AND, and the technique flips.\n"
                "4) The answer_key MUST follow the GROUP BY entity + HAVING with N "
                "separate SUM(CASE) expressions form:\n"
                "   `SELECT e.entity_id, e.name`\n"
                "   `FROM entity_table AS e`\n"
                "   `JOIN fact_table AS f USING (entity_id)`\n"
                "   `[JOIN price_table USING (...)]`\n"
                "   `GROUP BY e.entity_id, e.name`\n"
                "   `HAVING SUM(CASE WHEN cat = 'val_A' THEN value ELSE 0 END) &gt;= threshold_A`\n"
                "   `   AND SUM(CASE WHEN cat = 'val_B' THEN value ELSE 0 END) &gt;= threshold_B;`\n"
                "   The entity_id (NOT entity_id + category) is the GROUP BY grain so "
                "each customer / employee / student gets one row, and the per category "
                "SUMs sit as multiple aggregates on that same row.\n"
                "5) Test data MUST include: (a) AT LEAST one entity who passes the "
                "threshold in EVERY required category (qualifies, included); (b) AT "
                "LEAST one entity who passes in ONE category but FAILS in another "
                "(must be excluded; this is the canonical fail case the AND in HAVING "
                "catches); (c) AT LEAST one entity with rows in OTHER (non required) "
                "categories that also satisfy the threshold &mdash; those other "
                "category rows must NOT count toward the gate (the CASE WHEN filters "
                "them to ELSE 0).\n"
                "6) Forbidden anti patterns:\n"
                "   - GROUP BY (entity_id, category) + HAVING category = 'A' AND "
                "category = 'B': IMPOSSIBLE on any single row because a row's category "
                "can only equal one value. This is the most common learner mistake.\n"
                "   - Self joins (one copy WHERE cat = 'A', another WHERE cat = 'B') "
                "joined on entity: works but quadratic and misses the lesson.\n"
                "   - Subqueries (SELECT entity FROM ... WHERE cat = 'A' GROUP BY entity "
                "HAVING SUM &gt;= N) INTERSECTed: works but verbose for the simple case.\n"
                "7) The prompt MUST be explicit about whether 'OR rows' contribute or "
                "not. Default: only the per category SUM contributes (ELSE 0 in CASE). "
                "If the prompt instead asks 'spent at least $X across June and July "
                "combined,' the answer is one SUM with a WHERE filter, not CASE per "
                "category.\n"
                "8) Set classification.output_shape to `fewer_rows`. The output MUST "
                "have the entity_id + name columns only (NOT the per category sums) "
                "unless the prompt explicitly asks to return the breakdown too &mdash; "
                "in that case the answer key projects the same SUM(CASE) expressions "
                "in the SELECT as well.\n"
                "9) The prompt MUST state the ORDER BY for the final result (typically "
                "entity_id ASC; some prompts allow 'any order')."
            )
        # Common requirements applied to all flavors
        base += (
            "\n\nUniversal requirements (apply to whichever flavor was chosen):\n"
            "- classification.recipe = `reshape`, classification.input_arrival = "
            "`single_table` or `join`.\n"
            "- Valid PostgreSQL. Test data is larger and includes edge cases. The "
            "answer must return NON-EMPTY rows on both example and test data."
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
        _up_opts = ("drop", "keep", "aggregate")
        _up = subtype if subtype in _up_opts else random.choice(list(_up_opts))
        _UP = {
            "drop": (
                "\nSUBTYPE PIN — COLUMNS TO ROWS, DROP THE EMPTIES. Plain wide-to-long reshape: one "
                "SELECT per column with a literal label, stacked with UNION ALL. The prompt EXCLUDES "
                "NULL cells, so add WHERE col IS NOT NULL to each branch (or an outer WHERE value IS "
                "NOT NULL). Include a NULL cell in the data so the filter is exercised."
            ),
            "keep": (
                "\nSUBTYPE PIN — COLUMNS TO ROWS, KEEP THE EMPTIES. Same UNION ALL mechanic, but the "
                "prompt wants NULL cells KEPT as rows (e.g. a NULL reading is still a reading). Do NOT "
                "add the IS NOT NULL filter. Include a NULL cell and make the expected output retain "
                "that row with a NULL value."
            ),
            "aggregate": (
                "\nSUBTYPE PIN — UNPIVOT THEN AGGREGATE. After stacking the columns into long form in a "
                "CTE, a single GROUP BY rolls them up (COUNT / SUM across what were several columns). "
                "The answer is the aggregate, not the long rows themselves; filter NULLs first if a "
                "blank column should not count."
            ),
        }
        base += _UP[_up]
    elif qtype == "matchup_unpivot":
        base += (
            "Build a MATCHUP UNPIVOT problem using PostgreSQL or MySQL. The defining "
            "shape is a single wide row that holds BOTH sides of a head-to-head event, "
            "and the question is about each side individually, so the solver must split "
            "the row into one row per participant, score each side against its opponent, "
            "then regroup and aggregate per participant. This is NOT the plain `unpivot` "
            "qtype (one entity key, N value columns of the same measure -> label/value "
            "pairs). Here the two value columns belong to DIFFERENT entities and each "
            "split branch must carry its own value AND the opponent's.\n\n"
            "Hard requirements:\n"
            "1) Schema MUST contain ONE main matches/games table with shape "
            "(match_id, side_a_key, side_b_key, side_a_score, side_b_score [, event_date]). "
            "Examples: matches(match_id, host_team, guest_team, host_goals, guest_goals), "
            "games(game_id, home_id, away_id, home_pts, away_pts). The two key columns "
            "reference participants; the two score columns are each participant's own value.\n"
            "2) Schema SHOULD also contain a small dimension table (teams(team_id, "
            "team_name) or players(player_id, name)) so the final result can be reported "
            "by name and so a participant who NEVER played still appears.\n"
            "3) The answer_key MUST split the wide row with UNION ALL, one branch per "
            "side, each emitting (participant_key, own_score, opp_score):\n"
            "   `SELECT host_team AS team, host_goals AS gf, guest_goals AS ga FROM matches`\n"
            "   `UNION ALL`\n"
            "   `SELECT guest_team,        guest_goals,      host_goals       FROM matches`\n"
            "   then a per-row CASE deriving the result from own vs opponent (e.g. "
            "win -> 3, draw -> 1, loss -> 0), then GROUP BY participant with SUM/COUNT.\n"
            "4) If the prompt asks for every participant (including ones with zero games), "
            "the answer_key MUST drive off the dimension table with a LEFT JOIN to the "
            "unioned/aggregated results and COALESCE the metrics to 0.\n"
            "5) The prompt MUST state the scoring rule explicitly (what a win/draw/loss is "
            "worth, or which metric to total), the exact output column names, and the "
            "ORDER BY (typically points DESC then name/id ASC, or participant ASC).\n"
            "6) Test data MUST include: at least 3 participants, at least one draw (equal "
            "scores) so the tie branch of the CASE is exercised, and at least one "
            "participant who appears only as side B (to prove the UNION ALL captures both "
            "sides) -- and, if requirement 2 applies, one dimension-table participant with "
            "NO matches so the LEFT JOIN + COALESCE 0 is exercised.\n"
            "7) Do NOT solve this by referencing one side only or by a single GROUP BY on "
            "the wide table -- that silently drops every participant's away/guest games.\n"
            "8) Set classification.recipe to `normalize-bidirectional`, "
            "classification.input_arrival to `single_table` (the matches table is the "
            "source; the dimension join is a lookup), and use composite_moves to note the "
            "two moves: (a) unpivot the two sides via UNION ALL, (b) aggregate per "
            "participant. The row count after the split is 2x the matches, then collapses "
            "to one row per participant."
        )
    elif qtype == "gated_lookup":
        base += (
            "Build a GATED LOOKUP problem: a condition (threshold/flag) on an attribute "
            "in one table decides what value to take from a related table. This is NOT a "
            "sum/avg aggregate problem -- the core move is a cross-table CONDITION that "
            "gates a per-group pick. Pick ONE gate flavor and ONE pick flavor per "
            "generation so the user sees variety across runs.\n\n"
            "Hard requirements:\n"
            "1) Schema MUST have TWO tables sharing an entity key (e.g. product_id). "
            "Table A carries the GATE attribute -- a rating (1-5), score, boolean flag, "
            "status string, or qualifying date. Table B carries the VALUES to choose from "
            "-- prices, bids, amounts, or event dates -- and one entity MAY have MANY rows "
            "in table B (several prices per product).\n"
            "2) GATE flavor (choose one): a numeric threshold (rating >= 4), a boolean / "
            "status flag (is_active, status = 'approved'), a category whitelist, or a date "
            "window (signed up before a literal date). State the exact cutoff in the prompt.\n"
            "3) PICK flavor (choose one): the per-entity MIN or MAX of a table B value "
            "(cheapest price, highest bid), or the earliest / latest by date. The pick is "
            "per entity, so it is a top-1-per-group selection (MIN/MAX, or ROW_NUMBER "
            "PARTITION BY entity ORDER BY value then keep rn = 1). Do NOT make the headline "
            "metric a SUM or AVG -- that is a different qtype.\n"
            "4) FALLBACK when the gate FAILS (choose one and state it explicitly): output "
            "0, output NULL, or EXCLUDE the row entirely. If the fallback is 0 or NULL the "
            "answer uses a CASE (and every entity appears); if it EXCLUDES, the answer uses "
            "a WHERE (and only qualifying entities appear). Make the prompt unambiguous "
            "about which.\n"
            "5) The answer_key MUST: (a) bring the gate attribute onto the entity via a "
            "JOIN/lookup, (b) compute the per-entity pick from table B, (c) apply the gate "
            "as a CASE on the picked value (fallback 0/NULL) or as a WHERE (exclude). The "
            "gate must reference table A's attribute, not table B's value.\n"
            "6) Test data MUST include: at least one entity that PASSES the gate and has a "
            "clear winning pick, at least one entity that FAILS the gate (to exercise the "
            "fallback or exclusion), and at least one entity with MULTIPLE table B rows so "
            "the per-entity pick is non-trivial (the cheapest is not the only row).\n"
            "7) Common trap to design against: applying the gate to table B's value instead "
            "of table A's attribute, or picking before gating in a way that changes the "
            "fallback rows. The prompt MUST name the output columns and the ORDER BY.\n"
            "8) Set classification.recipe to `enrich-join`, classification.input_arrival to "
            "`join`, and use composite_moves to note the moves: (a) look up the gate "
            "attribute, (b) pick the per-entity target row, (c) gate with CASE or WHERE. "
            "Output is one row per entity (CASE fallback) or per qualifying entity (WHERE)."
        )
        # forced method subtype (maps to the playbook's Gated Lookup method leaves)
        _gl_dir = {
            "case_keep": "METHOD (use THIS): fallback is 0 or NULL so EVERY entity appears; gate with a CASE wrapped around the per-entity pick. State the fallback explicitly.",
            "gate_on": "METHOD (use THIS): put the gate (and any row filter on the joined table) in the JOIN ON so non-qualifiers drop BEFORE the aggregate; the LEFT JOIN still keeps every entity (0 / NULL where it failed).",
            "where_exclude": "METHOD (use THIS): only qualifying entities appear; the gate sits in WHERE, which turns the LEFT JOIN effectively INNER. State that non-qualifiers are excluded.",
            "distinct_on": "METHOD (use THIS, Postgres): the pick is the latest / earliest row per entity via DISTINCT ON (entity) ... ORDER BY entity, ts; the gate references table A's attribute.",
            "rownumber_pick": "METHOD (use THIS): you need the WHOLE row at the min / max (or pick by an ORDER, not a value); use ROW_NUMBER() OVER (PARTITION BY entity ORDER BY ...) kept at rn = 1, then gate.",
        }
        if subtype in _gl_dir:
            base += "\n\n" + _gl_dir[subtype]
    elif qtype == "left_join_on_filter":
        diff = (difficulty or "medium").lower()
        # Each shape is now a real subtype. When one is pinned (by the learner or by
        # the Random pre-pick in generate_problem) we force exactly that shape; when
        # subtype is absent we fall back to rotating A-F so the full range shows up.
        _shape_map = {
            "date_window": "A", "status_category": "B", "numeric_threshold": "C",
            "both_sides": "D", "sum_coalesce": "E", "existence_flag": "F",
        }
        _shape_names = {
            "A": "SHAPE A (right-side date window)",
            "B": "SHAPE B (right-side status / category equality)",
            "C": "SHAPE C (right-side numeric threshold)",
            "D": "SHAPE D (left filter in WHERE + right filter in ON)",
            "E": "SHAPE E (SUM / AVG aggregate with COALESCE)",
            "F": "SHAPE F (boolean / existence flag)",
        }
        _chosen_shape = _shape_map.get(subtype)
        if _chosen_shape:
            shape_hint = (
                f"Difficulty: `{diff}`. **BUILD {_shape_names[_chosen_shape]} ONLY.** "
                "The harness pinned this exact shape; construct that variant from the "
                "catalogue below and ignore every other shape.\n\n"
            )
        else:
            shape_hint = (
                f"Difficulty: `{diff}`. Pick ONE of SHAPES A-F below and ROTATE across "
                "runs so the user is not handed the same date-window count every time. "
                "Vary the RIGHT-side filter type, the aggregate, and whether a LEFT-side "
                "filter is also present.\n\n"
            )
        base += (
            "Build a LEFT JOIN problem that DRILLS filter placement around a join. "
            "Core teaching point, constant across every shape: a filter on the RIGHT "
            "(joined) table belongs in ON -- moving it to WHERE silently turns the LEFT "
            "JOIN into an INNER JOIN and drops left rows; a filter on the LEFT (driver) "
            "table belongs in WHERE -- putting it in ON does nothing because the LEFT "
            "JOIN keeps every left row regardless. Design the data so the difference is "
            "VISIBLE.\n\n"
            + shape_hint +
            "SHAPE A: Right-side DATE WINDOW (the classic)\n"
            "  - Right-table filter is a date range (orders in 2024, sessions in Q1).\n"
            "  - Aggregate: COUNT(right_id) of the qualifying rows; 0 when none.\n"
            "  - ON carries the join key AND the half-open date range "
            "(`>= DATE '2024-01-01' AND < DATE '2025-01-01'`).\n\n"
            "SHAPE B: Right-side STATUS / CATEGORY (no date at all)\n"
            "  - Right-table filter is a status or category equality "
            "(`status = 'completed'`, `channel = 'mobile'`, `type = 'refund'`).\n"
            "  - Aggregate: COUNT of the matching right rows per left entity; 0 when none.\n"
            "  - The ON carries the join key AND the status/category equality. No dates "
            "anywhere, so the user practices the trap on a plain equality filter.\n\n"
            "SHAPE C: Right-side NUMERIC THRESHOLD\n"
            "  - Right-table filter is a comparison on a numeric column "
            "(`amount > 50`, `rating >= 4`, `quantity >= 10`).\n"
            "  - Aggregate: COUNT of right rows over the threshold per left entity; 0 "
            "when none qualify.\n"
            "  - ON carries the join key AND the threshold comparison.\n\n"
            "SHAPE D: LEFT filter in WHERE + RIGHT filter in ON (both sides)\n"
            "  - The LEFT (driver) table has its OWN filter (employees hired in 2024, "
            "customers in a region, products that are active). That left-side filter "
            "MUST go in WHERE -- it really removes left rows, which is correct here.\n"
            "  - The RIGHT table ALSO has a filter (sessions in Q1, completed orders). "
            "That right-side filter MUST go in ON to keep the surviving left rows.\n"
            "  - The teaching point: the two filters go to DIFFERENT clauses. A left "
            "filter in ON is a silent no-op (the entity stays anyway); a right filter "
            "in WHERE silently drops kept entities. The prompt must clearly mark which "
            "condition is about the left entity and which is about the joined rows.\n"
            "  - Test data MUST include: at least one left entity that FAILS the left "
            "filter (must be absent from output), at least one left entity that PASSES "
            "the left filter but has only NON-qualifying right rows (must appear with 0), "
            "and ideally one that passes and has no right rows at all (also 0).\n\n"
            "SHAPE E: SUM / AVG aggregate with COALESCE (not COUNT)\n"
            "  - Right-side filter as in A/B/C, but the metric is a SUM or AVG of a "
            "right-table numeric column (total spend on 2024 completed orders, average "
            "rating of qualifying reviews).\n"
            "  - The answer_key MUST wrap the aggregate in `COALESCE(SUM(...), 0)` (or "
            "leave AVG as NULL if the prompt says so) so entities with no qualifying "
            "right row show 0 / NULL, not vanish.\n\n"
            "SHAPE F: Boolean / existence flag\n"
            "  - The output is a yes/no (or 1/0) per left entity: does this entity have "
            "ANY right row passing the filter? (any completed 2024 order, any Q1 "
            "session.)\n"
            "  - Express with `COUNT(right_id) > 0`, `BOOL_OR(...)`, or "
            "`MAX(CASE WHEN ... THEN 1 ELSE 0 END)` -- the filter still rides in ON so "
            "non-matching entities report false / 0 instead of dropping out.\n\n"
            "Universal hard requirements (apply to whichever shape was chosen):\n"
            "1) Schema MUST have a LEFT (driver) table whose every qualifying row must "
            "survive into the output -- customers, employees, developers, wards -- and a "
            "RIGHT table in a one-to-many relationship (orders, sessions, tasks, "
            "admissions).\n"
            "2) The prompt MUST require that every IN-SCOPE left entity appears in the "
            "output with 0 / NULL / false when it has no qualifying right row, and MUST "
            "name the output columns and the ORDER BY. State the keep-all requirement "
            "explicitly so the WHERE-trap form is provably wrong.\n"
            "3) Test data MUST include at least one left entity whose ONLY right rows "
            "FAIL the right-side filter (e.g. orders only in 2023) AND ideally one left "
            "entity with NO right rows at all. Both must still appear with 0 / false in "
            "the correct answer -- these are the rows the WHERE version wrongly drops.\n"
            "4) For COUNT shapes, COUNT a RIGHT-table column (`COUNT(o.order_id)`), NOT "
            "COUNT(*): COUNT(*) counts the single NULL-filled row of a non-matching "
            "entity as 1, reporting 1 instead of 0. COUNT(o.order_id) ignores the NULL.\n"
            "5) The answer_key (correct) MUST place every RIGHT-side filter in the ON "
            "clause alongside the join key, and every LEFT-side filter (SHAPE D only) in "
            "WHERE, then GROUP BY the left entity.\n"
            "6) Use a half-open date range (`>= start AND < next_period_start`) for any "
            "date window, never `BETWEEN ... AND end-1`.\n"
            "7) Set classification.recipe to `enrich-join`, classification.input_arrival "
            "to `join`. In composite_moves note: LEFT JOIN keep-all + filter(s) placed by "
            "which table they target + aggregate. Teaching point: right filter in ON "
            "keeps, right filter in WHERE drops; left filter belongs in WHERE."
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
        _do_hint = {
            "date_trunc_cohort": "**BUILD A DATE_TRUNC COHORT problem ONLY.** Bucket rows "
                "into month / week / quarter periods with DATE_TRUNC(...)::date, GROUP BY the "
                "bucket, and aggregate (count distinct days, sum revenue, etc.). Optionally a "
                "HAVING on the per-bucket aggregate.",
            "extract_component": "**BUILD AN EXTRACT-COMPONENT problem ONLY.** Pull a single "
                "date part with EXTRACT (DOW, YEAR, MONTH, or HOUR) and GROUP BY or FILTER on "
                "it (e.g. orders per day-of-week, busiest hour).",
            "date_arithmetic": "**BUILD A DATE-ARITHMETIC problem ONLY.** Add or subtract days / "
                "INTERVALs from a date (end_date = start_date + term_days, or filter against a "
                "LITERAL or data-derived cutoff like MAX(date) - 30). NEVER CURRENT_DATE.",
            "duration_between": "**BUILD A DURATION-BETWEEN problem ONLY.** Compute the elapsed "
                "time between two timestamps via subtraction + EXTRACT(EPOCH FROM (b - a)) / 3600 "
                "for hours (or / 86400 for days). A 'time-to-X' metric per entity.",
            "day_count_boundaries": "**BUILD AN INCLUSIVE-DAY-COUNT problem ONLY.** The teaching "
                "point is the off-by-one: a span from start to end is (end - start) + 1 days "
                "INCLUSIVE. Build a trial / stay / rental length where the +1 matters.",
        }.get(subtype)
        if _do_hint:
            base += _do_hint + " The harness pinned this exact shape; ignore the other shapes below.\n\n"
        base += (
            "Build a DATE OPERATIONS problem where date or timestamp manipulation is "
            "the CENTERPIECE of the solution, not incidental. Require AT LEAST ONE of "
            "these PostgreSQL date methods (rotate across runs):\n\n"
            "TECHNIQUES:\n"
            "  - DATE_TRUNC for cohort bucketing (`DATE_TRUNC('month', signup_ts)::date`, "
            "`DATE_TRUNC('week', order_date)`).\n"
            "  - EXTRACT for component access (`EXTRACT(YEAR FROM order_date)`, "
            "`EXTRACT(DOW FROM order_date)`, `EXTRACT(HOUR FROM event_ts)`).\n"
            "  - Date arithmetic: `date2 - date1` returns an integer day count; "
            "`date + INTERVAL '7 days'` returns a date/timestamp; `some_date - 30` is 30 days earlier.\n"
            "  - Inclusive day count gotcha: `Jan 10 - Jan 1 = 9` but the span is 10 days; "
            "use `(end - start) + 1`.\n"
            "  - EXTRACT(EPOCH FROM (end_ts - start_ts)) / 3600 for durations in hours.\n"
            "  - Cohort match: `DATE_TRUNC('month', a) = DATE_TRUNC('month', b)` (includes year).\n"
            "  - generate_series for a complete date spine over a LITERAL range.\n\n"
            "CRITICAL - NO CLOCK-RELATIVE DATES: Do NOT use CURRENT_DATE, NOW(), or "
            "CURRENT_TIMESTAMP anywhere (prompt, data, or answer_key). The data is static, so "
            "'last N days/months relative to today' filters return an EMPTY, non-reproducible "
            "result. For any 'recent' or 'older than N days' window, anchor the cutoff to a "
            "LITERAL date that exists in the data (e.g., `WHERE event_date < DATE '2024-03-01'`) "
            "OR derive it from the data (e.g., `(SELECT MAX(event_date) FROM events) - 30`, or "
            "`(SELECT DATE_TRUNC('month', MAX(signup_date)) FROM users) - INTERVAL '5 months'`). "
            "State the literal/derived cutoff in the prompt so the learner reproduces the same rows.\n\n"
            "Problem shapes to rotate through:\n"
            "  - 'Time-to-X in days/hours per user' (date subtraction + EXTRACT EPOCH).\n"
            "  - 'Monthly revenue by month' (DATE_TRUNC).\n"
            "  - 'Users whose last activity was before <literal cutoff>' (compare to a literal "
            "or to MAX(date) - N from the data, NEVER CURRENT_DATE).\n"
            "  - 'Busiest day-of-week per user' (EXTRACT DOW + GROUP BY).\n"
            "  - 'Average days between consecutive events per user' (LAG date + subtraction).\n"
            "  - 'Trial duration in days inclusive' (end - start + 1).\n"
            "  - 'Daily counts for every day in a LITERAL range incl. zero days' "
            "(generate_series + LEFT JOIN + COALESCE 0).\n\n"
            "Hard requirements:\n"
            "1) Schema has at least one DATE/TIMESTAMP column with realistic values.\n"
            "2) The prompt names the date method or phrases it so one method is obvious "
            "(e.g., 'group by month' => DATE_TRUNC; 'duration in hours' => EXTRACT EPOCH).\n"
            "3) State inclusive vs exclusive day counts when relevant.\n"
            "4) Any 'recent/older-than' cutoff is a LITERAL date or a data-derived MAX(date) "
            "expression, explicitly stated in the prompt. NEVER CURRENT_DATE / NOW().\n"
            "5) Column-driven interval: use `(col_value || ' days')::INTERVAL` or "
            "`some_date_col - col_value`. NEVER `INTERVAL 'col_value days'`.\n"
            "6) Test data includes boundary cases (month-end, year-end, the exact cutoff so "
            "`<` vs `<=` is visible) and the answer must return NON-EMPTY rows on both example "
            "and test data.\n"
            "7) The prompt states output column names AND the ORDER BY.\n"
            "8) Valid PostgreSQL (DATE/TIMESTAMP types).\n"
            "9) classification.recipe = `time-window`, input_arrival = `single_table` or "
            "`join`, output_shape per the result."
        )
    elif qtype == "series_generation":
        diff = (difficulty or "medium").lower()
        # Pre-roll: 25% of the time on medium / hard, bias the shape rotation
        # toward SHAPE F (active-in-period overlap). Reserved for medium / hard
        # only because the overlap predicate requires careful date arithmetic.
        force_shape_f = (diff in ("medium", "hard")) and (random.random() < 0.25)
        # On hard, bias the shape rotation toward SHAPE D (histogram with bounds-from-data
        # via a CTE staircase). On easy/medium, keep the original A/B/C rotation broad.
        if force_shape_f:
            shape_hint = (
                f"Difficulty: `{diff}`. **STRONG PREFERENCE: pick SHAPE F (active-in-"
                "period overlap)** for this generation. The harness rolled SHAPE F as "
                "the target shape; build the scenario around an entity with a created "
                "date + nullable ended date and ask how many were active in each "
                "period. This is the canonical 'monthly pipeline coverage' / 'active "
                "subscriptions per quarter' / 'open tickets per week' shape."
            )
        elif diff == "hard":
            shape_hint = (
                "Difficulty: `hard`. PREFER SHAPE D (histogram / distribution over an "
                "integer axis, bounds derived from MIN/MAX of a CTE) OR SHAPE E with a "
                "MULTI table join (label spine + CASE bucketing + dim entity) OR SHAPE "
                "F (active-in-period overlap). If you pick one of A/B/C, raise "
                "difficulty by adding a CTE staircase before the spine (intermediate "
                "per-entity aggregation that the spine then attaches to)."
            )
        elif diff == "easy":
            shape_hint = (
                f"Difficulty: `easy`. Pick from SHAPES A, B, or E (single table only). "
                "SHAPE E (label spine + CASE bucketing on a single fact table) is the "
                "lightest of these and reads cleanly at easy. SHAPE A (date spine + "
                "CROSS JOIN entities) is the second most common at easy. SHAPE F is "
                "reserved for medium / hard because the overlap predicate is too "
                "trappy at easy."
            )
        else:
            shape_hint = (
                f"Difficulty: `{diff}`. Pick from SHAPES A, B, C, D, E, or F as fits the "
                "scenario; SHAPE A (date spine + CROSS JOIN entities) is the most common "
                "at medium. SHAPE E with a dim entity table (one row per segment, then "
                "bucket the segment's metric) is a strong medium pick. SHAPE F (active-"
                "in-period overlap) fits when the fact table has a [start_date, "
                "end_date NULL-able] lifespan and the question is 'how many active per "
                "period'."
            )
        # Subtype override (nb01 Subtype dropdown / playbook Series Generation leaves):
        # when the learner picks a leaf, PIN the generation to that exact shape. Scenario
        # (industry context) and difficulty still apply on top of the forced shape.
        _sg_sub = {
            "full_date_spine":
                "Build EXACTLY SHAPE A: a date (or month / week) spine over a LITERAL range, "
                "CROSS JOIN every entity in a dim table, LEFT JOIN actuals, COALESCE 0 so every "
                "(entity, period) cell appears including the zero-activity ones.",
            "bounds_from_data":
                "Build EXACTLY SHAPE D: the spine bounds are DERIVED from the data (MIN / MAX, or "
                "0 .. MAX for a count histogram), NOT literal. Build a base CTE first, then "
                "generate_series((SELECT MIN ...), (SELECT MAX ...)); the spine hugs the data's own "
                "range (every week of the months covered, every integer count from the prompt's "
                "floor up to the busiest entity).",
            "filtered_entities":
                "Build EXACTLY the FILTERED variant of SHAPE A: only entities that DID SOMETHING in "
                "the window may appear, NOT every entity in the catalog. CROSS JOIN the spine to a "
                "FILTERED DISTINCT subquery (SELECT DISTINCT entity_id FROM fact WHERE in-window), "
                "then LEFT JOIN actuals. The trap to design around: CROSS JOINing the full dim table "
                "leaks inactive entities into the output.",
            "categorical_label_spine":
                "Build EXACTLY SHAPE E: the spine is a FIXED set of CATEGORICAL labels (bins, tiers, "
                "statuses) built inline with VALUES + a sort_order column, then LEFT JOIN a CASE that "
                "maps each fact row to a label. Half open `<` comparisons, COUNT(col) not COUNT(*), "
                "ORDER BY the integer sort_order.",
            "lateral_range_expansion":
                "Build EXACTLY SHAPE C: each source row carries its OWN [start_date, end_date]; "
                "CROSS JOIN LATERAL generate_series(t.start, t.end, INTERVAL '1 day')::date expands "
                "each row into one row per day, then aggregate. The ::date cast on the series output "
                "is required.",
            "period_overlap":
                "Build EXACTLY SHAPE F: a thing spans a range and counts as ACTIVE in every period it "
                "overlaps. Period spine + CROSS JOIN dim entities + LEFT JOIN fact with a HALF OPEN "
                "overlap predicate IN THE ON CLAUSE: created < period_start + 1 interval AND "
                "(ended IS NULL OR ended >= period_start). COUNT(fact.id) not COUNT(*); the predicate "
                "lives in ON, never WHERE.",
        }
        if subtype in _sg_sub:
            shape_hint = (
                f"Difficulty: `{diff}`. **FORCED SUBTYPE (the learner picked this leaf from the "
                f"Series Generation list): build EXACTLY this shape and no other.** {_sg_sub[subtype]} "
                f"Keep the chosen industry / scenario context, and scale complexity to `{diff}` "
                "(single table and a handful of rows on easy; multiple tables or a CTE staircase "
                "before the spine on hard) WITHOUT changing the shape."
            )
        base += (
            "Build a SERIES GENERATION problem where `generate_series` is the CENTERPIECE. "
            "The learner must manufacture a complete spine of rows and attach data to it. "
            "Pick ONE shape per generation (rotate across runs):\n\n"
            f"{shape_hint}\n\n"
            "SHAPE A: Date spine + CROSS JOIN entities + LEFT JOIN actuals (zero-fill)\n"
            "  - `generate_series(DATE '<lo>', DATE '<hi>', INTERVAL '1 day')::date` builds "
            "every day in a LITERAL range; CROSS JOIN the entity set, LEFT JOIN actuals, COALESCE 0.\n"
            "  - Use case: 'report every day in the range per entity, including days with 0'.\n"
            "  - Test data MUST leave at least one (entity, day) with no actuals so the 0-fill shows.\n\n"
            "SHAPE B: Integer / number series for fixed buckets\n"
            "  - `generate_series(1, 12)` (months), `generate_series(0, 23)` (hours), or N bins; "
            "LEFT JOIN counts so empty buckets still appear.\n\n"
            "SHAPE C: Per-row range expansion with CROSS JOIN LATERAL\n"
            "  - Each row has a [start_date, end_date]; expand into one row per day: "
            "`CROSS JOIN LATERAL generate_series(t.start_date, t.end_date, INTERVAL '1 day')::date AS d`.\n"
            "  - The `::date` cast on the series output is REQUIRED. `generate_series` with date "
            "inputs returns `timestamp without time zone`; without the cast the day column comes "
            "back as a timestamp like `2019-01-25 00:00:00`, which fails any equality compare "
            "against a true `date` column and shows up as the wrong dtype in expected_output.\n"
            "  - Common follow-on: `EXTRACT(YEAR FROM d)::int AS report_year` for per-year "
            "aggregates inside the period. The `::int` cast matters because EXTRACT returns "
            "numeric / double precision.\n"
            "  - Use case: 'expand each subscription/booking/sales period into the individual "
            "days it covers, then aggregate to month/year/week buckets'.\n\n"
            "SHAPE E: Literal label spine for categorical bins (VALUES + CASE bucketing + LEFT JOIN actuals)\n"
            "  - The spine is a fixed set of CATEGORICAL LABELS (bin names, severity tiers, "
            "plan names, status buckets, day-part labels), not dates or integers. Build the "
            "spine inline with `(VALUES ('label_a', 1), ('label_b', 2), ...) AS b(bin, "
            "sort_order)` carrying an integer sort_order column so the output is "
            "deterministic regardless of label format.\n"
            "  - Bucket source rows with a CASE expression using HALF OPEN intervals via "
            "`<` comparisons (NOT `BETWEEN`, which is inclusive on both ends and would "
            "double-count boundary values). LEFT JOIN spine to the bucketed subquery via "
            "`USING (bin)` so empty buckets land at COUNT 0.\n"
            "  - Use case: 'bucket session durations into 4 minute ranges,' 'classify "
            "salaries into Low / Mid / High tiers,' 'count tickets per severity bucket "
            "with all 4 tiers showing even if empty.'\n"
            "  - Difficulty knob:\n"
            "    * EASY: single fact table, bucket a numeric column into 3-5 bins. The "
            "Sessions duration bins shape is the canonical easy. ~5-15 source rows.\n"
            "    * MEDIUM: TWO tables -- a dim entity table (segment, plan, region) and a "
            "fact table -- bucket the per-entity metric into bins, with the count per bin "
            "summed across entities OR reported per (segment, bin) cell with a CROSS JOIN "
            "spine.\n"
            "    * HARD: THREE+ tables, the bucketing metric is computed via a CTE staircase "
            "(e.g. aggregate fact per entity, then bucket the aggregate, then LEFT JOIN the "
            "label spine). Or composite labels carrying TWO sort columns (e.g. age bucket "
            "AND gender) so the spine has age_label x gender_label cells via VALUES.\n"
            "  - Hard requirements specific to SHAPE E:\n"
            "    (a) The label spine is built inline via `VALUES (label, sort_order)` -- not "
            "as a separate CREATE TABLE. The answer_key MUST include the spine inline.\n"
            "    (b) The prompt MUST list the FIXED set of bin labels verbatim, in the "
            "intended output order. The CASE expression branches MUST emit those exact "
            "literal strings; any mismatch (extra space, different bracket character, plural "
            "vs singular) breaks the JOIN.\n"
            "    (c) The CASE uses `<` comparisons matching the half open interval convention "
            "the prompt describes ([0-5> means [0, 5), exclusive upper). Forbidden: BETWEEN "
            "across overlapping endpoints (CASE top-to-bottom evaluation hides the bug on "
            "small data, but real grading data will expose it).\n"
            "    (d) Test data MUST include AT LEAST one bin with ZERO matching source rows "
            "so the LEFT JOIN's zero-fill behavior is exercised. The expected output for "
            "that bin MUST be 0 (not NULL, not missing).\n"
            "    (e) `COUNT(s.source_col)` not `COUNT(*)`. After a LEFT JOIN the NULL-filled "
            "rows for empty buckets would land at 1 with COUNT(*).\n"
            "    (f) ORDER BY the integer sort_order column on the spine, NOT the label "
            "string. Lexicographic sort puts '15 or more' before '[0-5>' (digits sort below "
            "brackets in ASCII).\n\n"
            "SHAPE D (hard): Histogram / distribution over an integer axis, with PROMPT-LITERAL lower bound + data-derived upper bound\n"
            "  - The output is a HISTOGRAM: one row per possible integer count (visits-per-day, "
            "    transactions-per-visit, items-per-order, errors-per-session). The bucket nobody "
            "    hit must still appear as 0. Example: 'how many users did 0, 1, 2, 3 transactions "
            "    in one visit, with the empty bucket showing 0'.\n"
            "  - Structure: a `base` CTE first computes the per-entity COUNT (typically a LEFT "
            "    JOIN parent->child + COUNT(child.col) so no-child entities land at 0). Then a "
            "    `spine` CTE: `generate_series(<LOWER from prompt>, (SELECT MAX(count) FROM "
            "    base))`. Then the final SELECT does `spine LEFT JOIN base ON base.count = "
            "    spine.bucket` + GROUP BY spine + COUNT(base.col).\n"
            "  - LOWER BOUND: read the prompt. Most histogram prompts state a LITERAL lower bound "
            "    (counts start at 0, months at 1, hours at 0, quartiles at 1). Use `0` or `1` as "
            "    a literal in `generate_series`. Do NOT default to `(SELECT MIN(count) FROM base)`: "
            "    on test data where every entity hit at least one event, MIN > 0 and the spine "
            "    silently skips the 0 / 1 buckets that the prompt requires. The prompt MUST be "
            "    explicit (in plain English) about where the histogram axis starts.\n"
            "  - UPPER BOUND: `(SELECT MAX(count) FROM base)` so the spine right-sizes to the "
            "    busiest entity in this dataset. Do NOT hardcode the upper bound &mdash; the test "
            "    data may have a busier entity than the example data.\n"
            "  - Why NOT `COUNT(*)` in either CTE: both LEFT JOINs introduce NULL rows that "
            "    `COUNT(*)` would count as 1. Always `COUNT(col)` after a LEFT JOIN.\n"
            "  - Test data MUST: (a) include at least one gap bucket between the lower bound and "
            "    MAX (an integer NO entity hit) so the spine's value is visible; (b) be designed "
            "    so the lower bound from the prompt is HIGHER than MIN(count) in the example data "
            "    (e.g. example data has zero-count visits but test data does not), so a learner "
            "    who codes `(SELECT MIN(count) FROM base)` passes the example and fails the test.\n"
            "  - Reference shape (canonical example):\n"
            "      Tables: parent(entity_id, ...) + child(entity_id, ...) with possible "
            "      uniqueness guarantee in the prompt.\n"
            "      Prompt: 'For every integer count from 0 (inclusive) to the largest number of "
            "      <events> any <entity> did, return the count of <entities> that hit that exact "
            "      number &mdash; including counts that nobody hit, which must appear as 0.' "
            "      The phrase 'from 0' (or 'from 1', 'from the lowest possible value') is what "
            "      tells the learner to hardcode the lower bound.\n"
            "      Expected output: 2-column histogram with at least one zero-row bucket; the "
            "      lowest output row's bucket value matches the literal in the prompt, NOT MIN "
            "      of the data.\n\n"
            "SHAPE F (medium / hard): Active-in-period overlap (period spine x entity dim + overlap LEFT JOIN)\n"
            "  - The fact table holds entities with a CREATED date and a NULLABLE ENDED / WON / "
            "CLOSED date. The question is HOW MANY ENTITIES WERE ACTIVE in each period (month, "
            "week, quarter) over a fixed window. An entity is active in period P if it overlaps "
            "P at all (created BY P's end AND not closed BEFORE P's start).\n"
            "  - Structure: period spine via generate_series + CROSS JOIN dim entity table + "
            "LEFT JOIN fact table with the OVERLAP predicate IN THE ON CLAUSE (not WHERE):\n"
            "    ```\n"
            "    LEFT JOIN fact f\n"
            "      ON f.entity_id = e.entity_id\n"
            "     AND f.created_date <  m.period_start + INTERVAL '1 month'\n"
            "     AND (f.ended_date IS NULL OR f.ended_date >= m.period_start)\n"
            "    ```\n"
            "  - Use case: 'active opportunities per (sales_team, month),' 'open tickets per "
            "(team, week),' 'subscriptions per (plan_tier, quarter),' 'employees on payroll per "
            "(department, month),' 'active contracts per (region, quarter).'\n"
            "  - Hard requirements specific to SHAPE F:\n"
            "    (a) Schema MUST contain TWO tables: a dim entity table (entity_id, "
            "entity_name) and a fact table (record_id, entity_id, created_date, "
            "ended_date NULLABLE, plus 1-2 attribute columns). The ended_date column MUST be "
            "nullable AND the test data MUST include both still-active (ended IS NULL) and "
            "closed (ended IS NOT NULL) rows.\n"
            "    (b) The OVERLAP predicate sits IN THE ON CLAUSE of the LEFT JOIN, never in "
            "the WHERE. Moving it to WHERE drops the zero-fill rows (the LEFT JOIN's NULL "
            "row gets rejected by a WHERE check), and Channel-style teams with no fact rows "
            "vanish from the output. This is the canonical lesson of SHAPE F.\n"
            "    (c) The predicate uses HALF OPEN form for the created-date bound: "
            "`created_date < period_start + INTERVAL '1 month'` (born by month end). NOT "
            "`<= last_day_of_month` (works but requires computing the last day explicitly).\n"
            "    (d) The predicate uses `IS NULL OR >= period_start` for the ended-date "
            "bound (open OR closed at/after period start). FORBIDDEN: just `>= period_start` "
            "without the IS NULL branch (filters out all still-open entities, the most "
            "important set).\n"
            "    (e) COUNT(f.record_id) NOT COUNT(*). After LEFT JOIN with no overlap match, "
            "the NULL row would count as 1 with COUNT(*); zero cells would show 1.\n"
            "    (f) Test data MUST include: AT LEAST one (entity, period) cell with NO "
            "overlapping fact rows so the zero fill is exercised; AT LEAST one fact row that "
            "SPANS multiple periods (created in one, closed in a later one, so it appears in "
            "the active count for each of those periods); AT LEAST one fact row with "
            "ended_date IS NULL (still active, must count in every period from its creation "
            "forward through the window's end); AT LEAST one fact row that EXITS during the "
            "window (closed mid window, counts in the periods up through its close, drops "
            "off after).\n"
            "    (g) The period spine bound is the FIRST day of the LAST period in the "
            "window, not the last day: `generate_series(DATE 'X-01-01', DATE 'X-06-01', "
            "INTERVAL '1 month')` emits 6 rows for Jan-Jun. Setting the upper bound to "
            "'X-06-30' also emits 6 rows but reads as if you might get 7.\n"
            "    (h) The prompt MUST motivate WHY active-in-period (not point-in-time) is "
            "the right metric: e.g. 'pipeline coverage,' 'workload during the period,' "
            "'subscribers at any point in the month.' If the question is 'who was active "
            "AT EXACTLY month start' that's a point-in-time test, not overlap, and the "
            "predicate simplifies; do NOT use SHAPE F for those.\n"
            "    (i) Output columns MUST be (entity_id, period_start::date, "
            "active_count::int). The period_start column MUST be cast to ::date in the "
            "spine (generate_series with date inputs returns timestamp).\n\n"
            "Hard requirements:\n"
            "1) The series bounds are LITERAL dates/numbers OR derived from MIN/MAX of the data "
            "(e.g., `(SELECT MIN(event_date) FROM t)` .. `(SELECT MAX(event_date) FROM t)`). "
            "For SHAPE D the bounds MUST come from `(SELECT MIN(count) FROM base)` / "
            "`(SELECT MAX(count) FROM base)` — not hardcoded. "
            "NEVER use CURRENT_DATE, NOW(), or CURRENT_TIMESTAMP: the data is static and a "
            "clock-relative range returns an empty, non-reproducible result.\n"
            "2) The prompt explicitly motivates WHY the series is needed (missing days/buckets "
            "must still appear), names the output columns, and states the ORDER BY.\n"
            "3) For SHAPES A, B, and D the answer_key uses COALESCE(..., 0) so missing slots "
            "show 0 (or relies on `COUNT(col)` which already lands at 0); the prompt is explicit "
            "about 0 vs NULL.\n"
            "4) `generate_series(...)` stands alone (no FROM table appended) so it is not emitted "
            "once per row of another table. For SHAPE D the two subqueries inside generate_series "
            "MUST be wrapped in their own parentheses: "
            "`generate_series((SELECT MIN(c) FROM base), (SELECT MAX(c) FROM base))`.\n"
            "5) Valid PostgreSQL. Test data is larger and includes the gap/edge cases. The answer "
            "must return NON-EMPTY rows on both example and test data.\n"
            "6) DATE TYPED COLUMNS in expected_output: any column that comes from the "
            "`generate_series` date spine OR from a per-row expansion of a date range MUST be "
            "reported in expected_output with data type `date` (NOT `timestamp`, NOT `text`). "
            "The answer key MUST cast the series output with `::date` (e.g. "
            "`generate_series(...)::date AS d` or `d::date` in the SELECT). Without the cast the "
            "column comes back as a timestamp, which (a) fails dtype assertions, (b) breaks "
            "downstream JOINs against true date columns, and (c) shows confusing "
            "`2019-01-25 00:00:00` values in the example output instead of `2019-01-25`. For "
            "year/month/week extractions derived from the spine (e.g. `EXTRACT(YEAR FROM d)`), "
            "report the dtype as `int` after casting `::int` to avoid the numeric / double "
            "precision return of EXTRACT.\n"
            "7) classification.recipe = `reshape`, input_arrival = `join` (spine CROSS JOIN "
            "entities, or spine LEFT JOIN base CTE for SHAPE D), output_shape = `same_rows` for "
            "spines / `fewer_rows` for histograms collapsed by GROUP BY."
        )
    elif qtype == "window_running_total":
        agg = subtype if subtype in ("SUM", "AVG", "COUNT") else random.choice(["SUM", "AVG", "COUNT"])
        _agg_examples = {
            "SUM": "running revenue per region by day, cumulative messages per user",
            "AVG": "average score to date per student, cumulative average order value "
                   "per customer (the expanding-window average, NOT a fixed rolling window)",
            "COUNT": "cumulative number of orders to date per customer, running count of "
                     "sign-ups per cohort",
        }
        base += (
            f"WINDOW RUNNING TOTAL — the answer MUST use a cumulative (expanding) window "
            f"aggregate built on `{agg}`: "
            f"`{agg}(col) OVER (PARTITION BY group_col ORDER BY order_col ROWS BETWEEN "
            "UNBOUNDED PRECEDING AND CURRENT ROW)` or the equivalent shorthand "
            f"`{agg}(col) OVER (PARTITION BY ... ORDER BY ...)`. The defining trait is the "
            "EXPANDING frame (everything from the start of the partition up to the current "
            "row), which is what makes it cumulative. A self-join solution is NOT "
            "acceptable.\n"
            f"- This generation uses `{agg}`. Pick a time series scenario from the chosen "
            f"domain that fits it: {_agg_examples[agg]}.\n"
            + (
                "- Because this is AVG, the running value is the average of every row so far, "
                "and it CHANGES each row. Do NOT make it a fixed trailing window (that is the "
                "sliding-window qtype) and do NOT make it the whole-partition average (that is "
                "the benchmark-compare qtype). The ORDER BY + UNBOUNDED PRECEDING is what "
                "separates this from those two.\n"
                if agg == "AVG" else
                "- Because this is COUNT, count a non-NULL column or use COUNT(*) over the "
                "expanding frame so the running tally grows by one per qualifying row.\n"
                if agg == "COUNT" else
                ""
            )
            + "- Schema: 1-2 tables with a date or timestamp column, a partition column "
            "(category/region/user_id), and a metric to accumulate.\n"
            "- Example data: 6-10 rows across 2-3 partitions so the per-group reset is visible.\n"
            f"- Output: one row per input row (or per day) with the cumulative {agg.lower()} "
            "metric.\n"
            "- classification.recipe = `time-window`."
        )
    elif qtype == "window_lag_lead":
        base += (
            "COMPARE TO PREVIOUS / NEXT ROW (row-compare) — a single table with an ordering "
            "column; each row is compared to the row immediately before or after it in that "
            "ORDER BY (or two rows are paired by role). This is sequential neighbour "
            "comparison, NOT a foreign-key lookup to another table.\n"
            "- Schema: 1 table with an order column (event_ts / day / id) and, where the "
            "subtype needs it, a partition column (user_id / entity_id) and a metric.\n"
            "- Example data: 6-10 rows; at least one partition with multiple rows so a "
            "neighbour exists, and at least one partition-edge row whose neighbour is NULL "
            "— the answer_key MUST handle that edge correctly.\n"
            "- classification.recipe = `row-compare`."
        )
        # Subtype pin (None -> random among the four). Mirrors the playbook's
        # Compare > "Compare to the previous or next row" strategy leaves 1:1.
        _rc_opts = ("neighbour_value", "gap_delta", "fixed_run", "pair_by_role")
        _rc = subtype if subtype in _rc_opts else random.choice(list(_rc_opts))
        _RC = {
            "neighbour_value": (
                "\nSUBTYPE PIN — COMPARE TO NEIGHBOUR'S VALUE. Pull the previous (or next) "
                "row's value onto the current row with LAG / LEAD OVER (PARTITION BY k ORDER "
                "BY t), then TEST it (bigger / smaller / equal): e.g. 'rising', 'higher than "
                "the day before', 'same as the previous row'. The first row's LAG is NULL so "
                "the comparison is NULL and the row drops from WHERE — usually intended. "
                "Pitfall to design in: without PARTITION BY, one group's last row is compared "
                "to the next group's first row."
            ),
            "gap_delta": (
                "\nSUBTYPE PIN — GAP / DELTA TO THE NEIGHBOUR. Subtract the neighbour's value "
                "from the current row: t - LAG(t) OVER (PARTITION BY k ORDER BY t) — days "
                "since last, time between events, change from prior. The first row of each "
                "partition has no neighbour so its result stays NULL; the answer must NOT "
                "COALESCE that to 0 (that fakes a zero gap). Include a partition edge (NULL) "
                "row in the data."
            ),
            "fixed_run": (
                "\nSUBTYPE PIN — FIXED-LENGTH RUN OF N ROWS. A row qualifies only when several "
                "rows in a row line up (e.g. the same value three times running). Check the "
                "row BEFORE and the row AFTER, not just one side: val = LAG(val) AND val = "
                "LEAD(val) OVER (ORDER BY id). Both partition ends are NULL so edge rows can "
                "never anchor a full block. (For runs of UNKNOWN length, that is gaps-and-"
                "islands, a different recipe.)"
            ),
            "pair_by_role": (
                "\nSUBTYPE PIN — PAIR TWO ROWS BY ROLE. The two rows are NOT neighbours in "
                "time; they play different roles (a start and an end). Match them by a shared "
                "key and a role label and combine, e.g. MAX(CASE WHEN role='end' THEN t END) "
                "- MAX(CASE WHEN role='start' THEN t END) AS duration, GROUP BY key (or an "
                "equivalent self-join). Design in a key with a missing start/end (CASE -> "
                "NULL) and watch for a key with more than one start/end pair (pre-aggregate "
                "per pair first)."
            ),
        }
        base += _RC[_rc]
    elif qtype == "window_top_n_per_group":
        base += (
            "WINDOW TOP-N PER GROUP — the answer MUST use ROW_NUMBER (or RANK / DENSE_RANK) "
            "OVER (PARTITION BY group ORDER BY metric DESC) in a CTE or subquery, then "
            "filter `rn <= N` in the outer query. Window functions cannot be referenced "
            "directly in WHERE, so the CTE/subquery wrapper is required.\n"
            "- Pick a scenario from the chosen domain: top 3 products per category, most "
            "recent order per customer, second-highest salary per department.\n"
            "- Schema: 1-2 tables. Include at least one group with MORE rows than N so the "
            "filter is exercised, and at least one group with FEWER rows than N so the "
            "answer correctly returns all of that group's rows.\n"
            "- Pick a concrete N (e.g., top 3) and state it explicitly in the prompt.\n"
            "- Include at least one tie in the ordering metric so the learner has to "
            "consider ROW_NUMBER vs RANK vs DENSE_RANK behavior; the prompt should specify "
            "which tie-breaking behavior the answer needs.\n"
            "- classification.recipe = `rank-partition`."
        )
        # Subtype pin — mirrors the playbook's Rank Within Groups to Select Top-N leaves
        # (None -> random among the five). top1-by-value / top1-by-date / topN / nth / special.
        _tn_opts = ("top1_by_value", "top1_by_date", "topn", "nth", "special")
        _tn = subtype if subtype in _tn_opts else random.choice(list(_tn_opts))
        _TN = {
            "top1_by_value": (
                "\nSUBTYPE PIN — TOP 1 BY VALUE. Return exactly ONE row per group: the row with "
                "the highest (or lowest) metric. Rank with ROW_NUMBER() OVER (PARTITION BY group "
                "ORDER BY metric DESC) and filter rn = 1. State the tie rule in the prompt "
                "(ROW_NUMBER keeps one winner; RANK / DENSE_RANK keep all tied winners) and include "
                "at least one group with a tie on the top metric so the rule actually matters."
            ),
            "top1_by_date": (
                "\nSUBTYPE PIN — TOP 1 BY DATE. Return ONE row per group chosen by a timestamp or "
                "date column, NOT by a value metric: the most recent (or earliest) event per "
                "entity. Rank with ROW_NUMBER() OVER (PARTITION BY group ORDER BY event_date DESC) "
                "and filter rn = 1; the other columns ride along from that row. Include a group "
                "with rows on different dates so 'most recent' is unambiguous, and at least one "
                "tie on the date so the answer needs an explicit tiebreaker."
            ),
            "topn": (
                "\nSUBTYPE PIN — TOP N (N > 1). Return the top N rows per group with a concrete N "
                "stated in the prompt (e.g., top 3). Rank in a CTE, filter rn <= N. Include one "
                "group with MORE than N rows (so the filter cuts) and one group with FEWER than N "
                "rows (so the answer returns all of them). Put a tie at the N boundary so the "
                "choice of ROW_NUMBER vs RANK vs DENSE_RANK changes the result."
            ),
            "nth": (
                "\nSUBTYPE PIN — NTH POSITION (exactly N). Return only the row at a SPECIFIC rank, "
                "not the top N: the 2nd most recent activity, the 3rd highest salary per "
                "department, etc. Rank in a CTE, then filter rn = N (a single position), NOT "
                "rn <= N. A group with fewer than N rows returns NO row. Name the exact position "
                "in the prompt and include at least one group with fewer than N rows so the empty "
                "case is exercised."
            ),
            "special": (
                "\nSUBTYPE PIN — SPECIAL RANK PATTERN. Do NOT produce a plain top N. Build ONE of: "
                "(a) per-group MEDIAN via paired DENSE_RANK ASC + DESC (or PERCENTILE_CONT); "
                "(b) a THRESHOLD read off a rank — take the metric value of the Nth-ranked row in "
                "each group and use it as a cutoff for the rest; (c) a RANK DELTA — the gap between "
                "a row's metric and the next rank's metric within the group (LAG over the ranked "
                "rows); or (d) ASC / DESC EXCLUSION — drop each group's min and max by ranking from "
                "both ends and keeping the middle. Every variant partitions the rank window BY the "
                "group. classification.recipe stays `rank-partition`."
            ),
        }
        base += _TN[_tn]
    elif qtype == "point_in_time":
        base += (
            "POINT IN TIME (as-of lookup) — a single history table of rows stamped with an "
            "effective / as-of date; return the value IN EFFECT as of a cutoff date. The core "
            "move is ROW_NUMBER() OVER (PARTITION BY entity ORDER BY effective_date DESC) kept "
            "at rn = 1, restricted to rows on or before the cutoff (the date guard). The "
            "teaching point is the 'no history yet' case so the answer does not silently drop "
            "rows.\n"
            "- Schema: 1 history table with an entity key, a value column, and an effective_date.\n"
            "- Example data: 6-10 rows; at least one entity with several dated rows (including "
            "one AFTER the cutoff so the date guard must drop it) and one entity whose only row "
            "is after the cutoff (the no-history case).\n"
        )
        _pit_opts = ("asof_single", "default_no_history", "fill_forward")
        _pit = subtype if subtype in _pit_opts else random.choice(list(_pit_opts))
        _PIT = {
            "asof_single": (
                "\nSUBTYPE PIN — AS OF A SINGLE CUTOFF. Use ONE literal cutoff date. Rank each "
                "entity's rows newest-first among rows WHERE effective_date <= cutoff, keep "
                "rn = 1. An entity whose only row is after the cutoff simply drops (it has no "
                "value as of that date). Design in a future-dated row the date guard must "
                "exclude. classification.recipe = `rank-partition`."
            ),
            "default_no_history": (
                "\nSUBTYPE PIN — DEFAULT WHEN NO HISTORY. Same as-of rank, but EVERY entity must "
                "appear. Build the entity list with DISTINCT key FROM the history table (keeps "
                "it single-table), LEFT JOIN the ranked rows with rn = 1 in the JOIN ON (so "
                "no-history entities survive), then COALESCE the missing value to a stated "
                "default (or leave NULL if the prompt says so). At least one entity must have "
                "no row on/before the cutoff so the default path is exercised. "
                "classification.recipe = `rank-partition`."
            ),
            "fill_forward": (
                "\nSUBTYPE PIN — FILL FORWARD OVER A DATE SPINE. Output a value for EVERY day in "
                "a range. Build a date spine (generate_series in Postgres; a recursive CTE date "
                "spine in MySQL), then for each spine day take the most recent value on/before "
                "it (an as-of subquery: ORDER BY effective_date DESC LIMIT 1). Days with no row "
                "of their own inherit the last known value; a day before the first row is NULL. "
                "Design in at least one gap day that must inherit the prior value. "
                "classification.recipe = `time-window`."
            ),
        }
        base += _PIT[_pit]
    elif qtype == "window_sliding":
        base += (
            "WINDOW SLIDING (moving / rolling) — the answer MUST use a windowed aggregate "
            "with an EXPLICIT FRAME clause: `ROWS BETWEEN n PRECEDING AND CURRENT ROW` "
            "(or RANGE BETWEEN INTERVAL 'n days' PRECEDING AND CURRENT ROW in Postgres). "
            "A self-join solution is NOT acceptable.\n"
            "- Pick a scenario from the chosen domain: 7-day rolling average of daily "
            "signups, trailing 28-day active users, moving sum of revenue per region.\n"
            "- State the window size in business terms (e.g., '7-day rolling average').\n"
            "- Schema: 1 table with a date column and a metric column. The data MUST be "
            "ordered/orderable by the date column with NO gaps that would invalidate a "
            "row-based frame (or the prompt must say to fill gaps first).\n"
            "- Example data: 8-12 rows so partial windows at the start AND a full window "
            "at the end are both visible.\n"
            "- classification.recipe = `time-window`."
        )
    elif qtype == "window_first_last":
        base += (
            "WINDOW FIRST_VALUE / LAST_VALUE — the answer MUST use FIRST_VALUE and/or "
            "LAST_VALUE OVER (PARTITION BY group ORDER BY order_col [FRAME]). The frame "
            "matters: the DEFAULT frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT "
            "ROW`, which makes LAST_VALUE return the CURRENT ROW's value, not the "
            "partition's true last value. To get the partition last, the frame MUST be "
            "`ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`. The prompt should "
            "force the learner to think about this by requiring BOTH first AND last value "
            "per partition.\n"
            "- Pick a scenario from the chosen domain: opening/closing balance per "
            "account, first/last touchpoint per session, starting/ending state per thread.\n"
            "- Schema: 1 table with a partition column, an order column (timestamp), and a "
            "value column.\n"
            "- Example data: 6-10 rows across 2-3 partitions so the first/last per group "
            "is meaningfully different from the row-wise behavior.\n"
            "- classification.recipe = `rank-partition`."
        )
    elif qtype == "window_frames":
        base += (
            "WINDOW FRAME CLAUSES — the learner is drilling explicit frame "
            "syntax. The answer key MUST include an EXPLICIT frame clause "
            "(`ROWS BETWEEN ... AND ...` or `RANGE BETWEEN ... AND ...`); "
            "do NOT rely on default frames. The prompt MUST state the frame "
            "behavior in business terms so the learner has a concrete target "
            "to map onto frame syntax.\n"
            "- Pick ONE frame configuration and base the problem on it. Vary "
            "across generations to give the learner exposure to all of:\n"
            "    * ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW (running total)\n"
            "    * ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING (whole partition; needed for LAST_VALUE)\n"
            "    * ROWS BETWEEN N PRECEDING AND CURRENT ROW (trailing window)\n"
            "    * ROWS BETWEEN CURRENT ROW AND N FOLLOWING (look-ahead window)\n"
            "    * ROWS BETWEEN N PRECEDING AND N FOLLOWING (centered window)\n"
            "    * ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING (equivalent to LAG, for contrast)\n"
            "    * RANGE BETWEEN INTERVAL 'N days' PRECEDING AND CURRENT ROW (date-based vs row-based — Postgres only)\n"
            "- The prompt MUST also clearly distinguish between the wrong-frame and right-frame interpretations. State the EXACT behavior expected (e.g., \"include the current row and the 2 preceding rows\" vs \"the 3 preceding rows EXCLUDING the current\") so a learner who guesses the wrong frame gets a wrong answer and learns the distinction.\n"
            "- Schema: 1 table with a partition column (user_id / category / region), an order column (date or sequence), and a metric column.\n"
            "- Example data: 6-10 rows across 1-2 partitions, designed so the partial-window-at-start and complete-window cases are both visible.\n"
            "- For variants involving LAST_VALUE or NTH_VALUE, the prompt should require BOTH first AND last (or 1st AND Nth) so the learner cannot get away with default frame on LAST_VALUE.\n"
            "- For ROWS vs RANGE variants: design data with at least one tie or gap in the ORDER BY column so the two frame types diverge. Prompt must specify which behavior is wanted.\n"
            "- classification.recipe = `time-window`.\n"
            "- Hints should progressively reveal: (1) name the conceptual frame (e.g. \"trailing 3 rows including current\"); (2) name the frame keywords (ROWS / RANGE / UNBOUNDED / N PRECEDING / N FOLLOWING / CURRENT ROW); (3) show the exact frame clause."
        )
        # Subtype pin (None -> random between the two frame families).
        _fr = subtype if subtype in ("rows_between", "range_between") else random.choice(["rows_between", "range_between"])
        _FR = {
            "rows_between": (
                "\nSUBTYPE PIN — ROWS BETWEEN (row-count frame). The frame MUST be a ROWS frame "
                "that counts PHYSICAL rows. Pick ONE of: UNBOUNDED PRECEDING AND CURRENT ROW, "
                "N PRECEDING AND CURRENT ROW, CURRENT ROW AND N FOLLOWING, N PRECEDING AND N "
                "FOLLOWING, or UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING. Do NOT use RANGE. "
                "The teaching point is that ROWS counts a fixed number of rows regardless of "
                "ties in the ORDER BY value."
            ),
            "range_between": (
                "\nSUBTYPE PIN — RANGE BETWEEN (value / interval frame). The frame MUST be a RANGE "
                "frame keyed on the ORDER BY VALUE, not on row count: use RANGE BETWEEN INTERVAL "
                "'N days' PRECEDING AND CURRENT ROW (Postgres, on a date metric) or a numeric "
                "value range. Rows that are PEERS (the same ORDER BY value) share one frame. "
                "Design the data with at least one tie or date gap so RANGE diverges from the "
                "equivalent ROWS frame, and make that divergence the explicit point of the prompt."
            ),
        }
        base += _FR[_fr]
    elif qtype == "window_benchmark_compare":
        agg = subtype if subtype in ("AVG", "MIN", "MAX") else random.choice(["AVG", "AVG", "MIN", "MAX"])  # AVG weighted: it is the common case
        base += (
            f"WINDOW BENCHMARK + COMPARE — the answer MUST put a WHOLE-GROUP benchmark on "
            f"every row with `{agg}(metric) OVER (PARTITION BY group_col)` that has NO "
            "ORDER BY (so the implicit frame is the entire partition), then COMPARE each "
            "row's own value against that benchmark in the OUTER query.\n"
            "- The defining trait is the MISSING ORDER BY: with no ORDER BY the window "
            "covers the whole group, so the benchmark is identical on every row of the "
            "group. Adding an ORDER BY would turn it into a cumulative running aggregate "
            "(a DIFFERENT qtype) — the answer MUST NOT have one here.\n"
            "- The benchmark MUST be computed in a CTE or subquery and the comparison "
            "applied in the OUTER query, because a window function cannot be referenced in "
            "WHERE or in the same-level SELECT's WHERE. This CTE-wrapper requirement is a "
            "core teaching point: a naive `WHERE metric > AVG(metric) OVER (...)` is a "
            "syntax error.\n"
            "- Pick a scenario from the chosen domain where 'above / below the group "
            "average' is the question: employees paid above their department average, "
            "products priced above their category average, stores with revenue above the "
            "region average. For MIN / MAX variants: rows that match the group's best / "
            "worst value.\n"
            "- The prompt MUST state whether to keep rows ABOVE, BELOW, or EQUAL to the "
            "benchmark, and whether to also OUTPUT the benchmark column. Name the output "
            "columns and the ORDER BY.\n"
            "- Schema: 1-2 tables with a partition column (department / category / region) "
            "and a numeric metric. A 'whole population' variant is allowed too: "
            f"`{agg}(metric) OVER ()` with an empty partition compares each row to the "
            "OVERALL average across all rows — state which one the prompt wants.\n"
            "- Example data: 6-12 rows across 2-3 groups, with at least one row clearly "
            "above and one clearly below each group's benchmark so the filter is exercised, "
            "and ideally one row exactly equal to test the boundary.\n"
            "- Use a comparison that handles the equal case per the prompt (`>` vs `>=`). "
            "If the metric can be NULL, the prompt must say how NULLs are treated (AVG OVER "
            "ignores NULLs; a NULL row compared to the benchmark yields UNKNOWN and is "
            "dropped by a strict comparison).\n"
            "- classification.recipe = `time-window`."
        )
    elif qtype == "window_sessionization":
        base += (
            "WINDOW SESSIONIZATION — the answer MUST detect sessions by gap. Pattern: in a "
            "first CTE, use LAG over (PARTITION BY user_id ORDER BY event_ts) to find the "
            "time gap to the previous event per user; flag each row with `new_session_flag "
            "= CASE WHEN previous_ts IS NULL OR event_ts - previous_ts > INTERVAL 'N "
            "minutes' THEN 1 ELSE 0 END`; in a second CTE, assign session_id via "
            "`SUM(new_session_flag) OVER (PARTITION BY user_id ORDER BY event_ts ROWS "
            "BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`. Then GROUP BY user_id, "
            "session_id to roll up per-session metrics if needed.\n"
            "- Pick a scenario from the chosen domain: group user clicks into 30-minute "
            "sessions, group sensor readings into runs separated by 5-minute gaps, group "
            "messages into conversation threads by silence.\n"
            "- State the gap threshold explicitly in the prompt (e.g., '30 minutes').\n"
            "- Schema: 1 events table with user_id (or entity_id), event_ts, plus any "
            "per-event attributes the per-session aggregate needs.\n"
            "- Example data: at least 2 users with at least 5 events each, timestamps "
            "designed so multiple sessions per user exist AND at least one session contains "
            "multiple events.\n"
            "- classification.recipe = `time-window`."
        )
        # Subtype pin — output shape (None -> random among the three). Mirrors the playbook's
        # three sessionization output-shape containers (per session / per person / per event).
        _shape = subtype if subtype in ("one_per_session", "one_per_person", "one_per_event") else random.choice(["one_per_session", "one_per_person", "one_per_event"])
        _SESS = {
            "one_per_session": (
                "\nOUTPUT SHAPE PIN — ONE ROW PER SESSION. After assigning session_id, GROUP BY "
                "user_id, session_id and roll up per-session metrics: session_start = MIN(event_ts), "
                "session_end = MAX(event_ts), event count, etc. Output carries user_id + session_id "
                "+ the metric(s). A session belongs to a person, so session_id appears next to the "
                "person id. session_start / session_end come free from the GROUP BY (MIN / MAX), NOT "
                "a window function."
            ),
            "one_per_person": (
                "\nOUTPUT SHAPE PIN — ONE ROW PER PERSON. After assigning session_id, aggregate AGAIN "
                "per user (a SECOND GROUP BY): number of sessions, longest session, average events "
                "per session, etc. Output carries user_id + a number; there is NO session_id column "
                "in the result. The shape is two stacked roll-ups: per (user, session) first, then "
                "per user."
            ),
            "one_per_event": (
                "\nOUTPUT SHAPE PIN — ONE ROW PER EVENT. Keep EVERY original event row and just label "
                "it with its session_id (the cumulative SUM of the new-session flag). Do NOT do a "
                "final GROUP BY; the output row count EQUALS the input row count."
            ),
        }
        base += _SESS[_shape]
    elif qtype == "root_cause_analysis":
        # Difficulty-aware scenario rotation. Each generation picks ONE archetype.
        # Easy = single CTE chain, single bug source. Medium = 2-3 CTEs, one
        # cross-check. Hard = 4+ CTEs, multi-source comparison or time-window math.
        diff = (difficulty or "medium").lower()
        # Archetype hint rotates across generations so retries see variety.
        _RCA_ARCHETYPES = [
            "metric_drop_dimension",   # day-over-day drop, find which dimension drives it
            "duplicate_inflation",     # count inflated, find the rows / join causing it
            "missing_rows_antijoin",   # report total < expected, find missing via EXCEPT
            "null_propagation",        # NULL appearing in output, trace upstream source
            "date_timezone_bug",       # off-by-one daily count from UTC vs local boundary
            "stale_snapshot",          # yesterday's snapshot didn't refresh some rows
            "two_source_mismatch",     # source A vs source B disagree on KPI, find diff
        ]
        archetype = subtype if subtype in _RCA_ARCHETYPES else random.choice(_RCA_ARCHETYPES)
        base += (
            "Build a ROOT CAUSE ANALYSIS problem: the analyst is handed a SYMPTOM "
            "(a metric is off) and must write SQL that PINPOINTS the root cause, not "
            "just reports the headline number. The answer query produces ONE or A FEW "
            "rows that name exactly which dimension / row / table introduced the bug. "
            "Postgres ONLY.\n\n"
            f"ARCHETYPE this generation: `{archetype}`.\n"
            f"DIFFICULTY: `{diff}`.\n\n"
            "Hard requirements:\n"
            "1) PROMPT must open with a 2-3 sentence SCENARIO in plain English: a "
            "named team / product / report saw a SPECIFIC symptom (revenue down X% on "
            "a specific day, customer count inflated by Y, total < expected by Z, an "
            "output column NULL for some rows, daily count off by one, snapshot stale). "
            "The scenario is the SYMPTOM, NOT the cause.\n"
            "2) PROMPT must then state the QUESTION the analyst must answer with SQL — "
            "the question must be DIAGNOSTIC (\"which dimension is responsible,\" \"find "
            "the rows causing duplication,\" \"identify records missing from destination,\" "
            "\"trace which upstream table introduced the NULLs,\" \"find the time-boundary "
            "rows,\" \"find rows not refreshed,\" \"pinpoint rows where A and B disagree\"). "
            "The output is a SMALL result set that NAMES the cause, not a metric.\n"
            "3) SCHEMA: 2-4 tables, < 30 rows of seed data total, small enough that the "
            "answer is visually verifiable. Tables must be plausibly real (sales, orders, "
            "user activity, inventory, refresh jobs). Use Postgres types (DATE, TIMESTAMP, "
            "TIMESTAMPTZ, NUMERIC, TEXT).\n"
            "4) SEED DATA must contain a PLANTED BUG that matches the archetype. The bug "
            "must be detectable by the answer_key but NOT obvious from a casual SELECT *. "
            "Examples:\n"
            "   * metric_drop_dimension: one product_category drops by 80% on the symptom "
            "     day; others are flat. Day-over-day breakdown surfaces the category.\n"
            "   * duplicate_inflation: one customer has 3 rows in a dim table (data load "
            "     issue); joining inflates that customer's metric 3x. GROUP BY + HAVING "
            "     COUNT > 1 on the dim table surfaces it.\n"
            "   * missing_rows_antijoin: orders table has 10 rows, fact_orders has 9; one "
            "     order_id is missing. EXCEPT or NOT EXISTS surfaces it.\n"
            "   * null_propagation: a LEFT JOIN to a dim table has no row for one entity, "
            "     so the output's region column is NULL; the answer traces the missing dim "
            "     row by joining and filtering WHERE dim.x IS NULL.\n"
            "   * date_timezone_bug: events stored in TIMESTAMPTZ, the report uses "
            "     date_trunc('day', event_ts) (server tz) but the spec wanted local tz; "
            "     2-3 events near midnight land on the wrong day. The answer compares the "
            "     two date_trunc results and surfaces the boundary rows.\n"
            "   * stale_snapshot: snapshot.updated_at < refresh_started_at for some rows; "
            "     answer filters WHERE updated_at < (SELECT MAX(refresh_started_at) FROM "
            "     refresh_log) - INTERVAL '1 day' to surface them.\n"
            "   * two_source_mismatch: source_a.metric != source_b.metric for some keys; "
            "     answer is a FULL JOIN + WHERE a.metric IS DISTINCT FROM b.metric to "
            "     return the differing rows side by side.\n"
            "5) ANSWER_KEY must be a single Postgres SQL block (CTE chain allowed, no "
            "temp tables, no DO blocks). It must EXERCISE the archetype's canonical "
            "Postgres feature:\n"
            "   * CTE chain (WITH ... AS) for stepwise investigation\n"
            "   * Window functions (LAG / LEAD / SUM OVER) for current-vs-prior comparison\n"
            "   * EXCEPT / INTERSECT for set comparison (missing rows / present in both)\n"
            "   * DISTINCT ON (key) ORDER BY ts DESC for latest-per-group\n"
            "   * COALESCE / NULLIF for NULL substitution / divide-by-zero guard\n"
            "   * generate_series for time-axis fill (find days with no rows)\n"
            "   * date_trunc / AT TIME ZONE for date / boundary bugs\n"
            "6) EXPECTED OUTPUT is a SMALL result set (1-5 rows usually) that NAMES THE "
            "CAUSE: the offending category, the duplicated customer_id, the missing "
            "order_id, the rows whose region is NULL with the missing dim_id, the two "
            "boundary timestamps with both date_trunc results, the stale row's id and "
            "updated_at, or the keys where source_a and source_b differ with both values "
            "side by side. NOT a single scalar; the analyst should see the bug rows.\n"
            "7) PROMPT must also include a 2-3 sentence EXPLANATION (separate field "
            "`rca_explanation`) of WHY the diagnosis works — which feature surfaced the "
            "bug and why a naive query would have missed it. This explanation is for the "
            "user AFTER they submit; do not give it away in hints.\n"
            "8) DIFFICULTY shaping:\n"
            "   * easy: single archetype, 1 CTE in the answer, < 15 seed rows, 2 tables, "
            "     bug is on a single row in a single column.\n"
            "   * medium: 2-3 CTEs (e.g. compute the metric, compute the breakdown, "
            "     surface the diff), 3 tables, 15-25 seed rows. May combine window "
            "     functions with a GROUP BY.\n"
            "   * hard: 4+ CTEs, may need EXCEPT or FULL JOIN across two tables, 25-30 "
            "     seed rows across 3-4 tables. Bug may be a multi-row pattern (e.g. ALL "
            "     rows from one upstream source are stale, not just one).\n"
            "9) Hints (3 progressive): (a) name the archetype in plain words; (b) name the "
            "Postgres feature(s) the answer uses without naming the column; (c) sketch the "
            "CTE outline (e.g. \"CTE1: per-day total. CTE2: LAG to compare. CTE3: filter to "
            "rows where the drop exceeds threshold\").\n"
            "10) Composite_moves should list the diagnostic moves (e.g. "
            "['per-day rollup', 'LAG for day-over-day diff', 'rank dimensions by largest "
            "diff', 'filter to top contributor']). Set classification.input_arrival to "
            "`single_table` or `join` based on the schema; classification.recipe to "
            "`row-compare` (for metric drop / two-source) or `enrich-join` (for missing-"
            "rows / null-propagation) or `delete-duplicates` (for duplicate_inflation).\n"
            "11) CRITICAL anti-pattern to avoid: do NOT make the answer a single SELECT "
            "that just reports the broken metric (\"daily revenue is $X\"). The whole "
            "POINT of this qtype is the diagnostic shape — the answer surfaces the bug "
            "ROWS, not the broken metric."
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

    # Reject clock-relative date functions: the example data is static, so these make
    # the expected output empty and non-reproducible across runs.
    _blob = " ".join([
        answer, schema,
        problem.get("example_input_data", "") or "",
        problem.get("test_data", "") or "",
        problem.get("prompt", "") or "",
    ]).upper()
    for _tok in ("CURRENT_DATE", "CURRENT_TIMESTAMP", "LOCALTIMESTAMP", "LOCALTIME", "NOW(", "GETDATE(", "SYSDATE"):
        if _tok in _blob:
            return False, (
                f"Clock-relative date '{_tok}' is not allowed. The example data is static, so a "
                f"filter relative to today returns an empty, non-reproducible result. Anchor date "
                f"windows to literal dates that exist in the data (e.g., WHERE d >= DATE '2024-01-01'), "
                f"or derive the reference date from the data "
                f"(e.g., (SELECT MAX(signup_date) FROM users) - INTERVAL '5 months')."
            )

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
    if len(problem["example_output_rows"]) == 0:
        return False, (
            "Answer key produced ZERO rows on the example data. The expected output must be "
            "non-empty so the learner can verify their result. Use literal or data-derived date "
            "bounds (never CURRENT_DATE) and design the example data so the answer returns rows."
        )

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
    if len(problem["test_expected_rows"]) == 0:
        return False, (
            "Answer key produced ZERO rows on the hidden test data. Design the test data so the "
            "answer returns rows, and avoid CURRENT_DATE-style filters."
        )

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
    scenario_mode: Optional[str] = None,
    difficulty: Optional[str] = None,
    subtype: Optional[str] = None,
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

    # Resolve meta qtypes (window_random, random_any) to a concrete qtype.
    # Both the original (what the user picked) and the resolved (what
    # actually got generated) are stored in _meta below.
    original_qtype = qtype
    _WINDOW_VARIANTS = [
        "window_running_total", "window_lag_lead", "window_top_n_per_group",
        "window_sliding", "window_first_last", "window_sessionization",
        "window_frames", "window_benchmark_compare",
    ]
    _RANDOM_ANY_EXCLUDED = {
        "recursive_cte",  # explicitly excluded per user's preference
        "dml",            # superseded by dml_update / dml_delete / dml_insert
        "window_random",  # meta — would infinite-loop
        "random_any",     # meta — would infinite-loop
    }
    if qtype == "window_random":
        qtype = random.choice(_WINDOW_VARIANTS)
        print(f"window_random resolved to: {qtype}")
    elif qtype == "random_any":
        pool = [k for k, v in QUESTION_TYPES.items()
                if k not in _RANDOM_ANY_EXCLUDED
                and not v.get("hidden_in_picker")
                and dialect in v["dialects"]]
        if not pool:
            print(f"random_any has no eligible qtype for dialect {dialect}")
            return None
        qtype = random.choice(pool)
        print(f"random_any resolved to: {qtype}")

    if dialect not in QUESTION_TYPES[qtype]["dialects"]:
        print(f"Question type '{qtype}' is not supported in dialect '{dialect}'.")
        return None

    last_error = None
    scenario = _pick_scenario(qtype, industry=scenario_mode)  # pick once so retries refine the same scenario; industry-aware
    # For dml, pick which operation (UPDATE / DELETE / INSERT) once so retries stay
    # consistent. Each option has equal probability.
    # Determine the underlying DML operation. For the three split qtypes the
    # operation is fixed; for legacy "dml" it's random.
    _dml_op_map = {"dml_update": "UPDATE", "dml_delete": "DELETE", "dml_insert": "INSERT"}
    if qtype in _dml_op_map:
        dml_op = _dml_op_map[qtype]
        qtype_for_guidance = "dml"  # share the existing dml prompt path
    elif qtype == "dml":
        dml_op = random.choice(["UPDATE", "DELETE", "INSERT"])
        qtype_for_guidance = "dml"
    elif qtype == "delete_duplicates":
        dml_op = "DELETE"            # it IS a delete, but uses its own guidance branch
        qtype_for_guidance = "delete_duplicates"
    else:
        dml_op = None
        qtype_for_guidance = qtype
    # For union_islands, pick which flavor of gaps-and-islands once so retries stay
    # consistent. Flavors:
    #   date_calendar              - dates with no missing days expected; uses date - rn_per_state
    #   date_sequence              - dates with possible missing days; uses rn_overall - rn_per_state
    #   integer_seq                - integer ids in a single table; uses id - rn (no UNION)
    #   partitioned_status_periods - per-entity timelines, two source tables UNION'd by status,
    #                                BOTH windows partitioned by entity key
    #   consecutive_day_streak_per_entity - per entity streak detection with duplicate same
    #                                day source rows + HAVING COUNT >= N gate + EXISTS / IN
    #                                membership semantics. LeetCode #1454 Active Users shape.
    #                                MEDIUM / HARD only (too many traps for easy).
    islands_flavor = None
    if qtype == "union_islands" and subtype:
        islands_flavor = subtype
    elif qtype == "union_islands":
        _diff = (difficulty or "medium").lower()
        if _diff == "easy":
            islands_flavor = random.choice([
                "date_calendar", "date_sequence", "integer_seq", "partitioned_status_periods"
            ])
        else:
            islands_flavor = random.choice([
                "date_calendar", "date_sequence", "integer_seq",
                "partitioned_status_periods", "consecutive_day_streak_per_entity"
            ])
    # For percentile_metrics, pick a flavor based on dialect (PERCENTILE_CONT is
    # Postgres-only; NTILE and PERCENT_RANK work in both):
    #   percentile_aggregate - PERCENTILE_CONT/DISC for median, P75, P90, P95, P99 (Postgres only)
    #   ntile_buckets        - NTILE(n) for quartile/decile bucketing (both dialects)
    #   top_n_percent        - PERCENT_RANK or ROW_NUMBER/COUNT for top X% selection (both dialects)
    #   extreme_exclusion    - DENSE_RANK ASC + DESC pair, filter where neither rank = 1 to
    #                          exclude the min cluster AND the max cluster (both dialects).
    #                          Output is the "middle" entities; canonical LeetCode #1149 shape.
    percentile_flavor = None
    if qtype == "percentile_metrics" and subtype:
        percentile_flavor = subtype
    elif qtype == "percentile_metrics":
        if dialect == "postgresql":
            percentile_flavor = random.choice(["percentile_aggregate", "ntile_buckets", "top_n_percent", "extreme_exclusion", "extreme_exclusion_per_group"])
        else:
            percentile_flavor = random.choice(["ntile_buckets", "top_n_percent", "extreme_exclusion", "extreme_exclusion_per_group"])
    # For pivot, pick a flavor:
    #   multi_column_pivot     - classic long-to-wide reshape (jan_sales, feb_sales, ...)
    #   signed_aggregate       - opposing categories collapsed into a single net total
    #                            (Buy/Sell -> capital_gain_loss; debit/credit -> net_amount).
    #                            Canonical LeetCode #1393 shape.
    #   membership_filter      - CASE in HAVING gate ("bought ALL of X, NONE of Y") via
    #                            BOOL_OR or MAX(CASE ... THEN 1 ELSE 0 END) per category.
    #                            Canonical LeetCode #1965 shape.
    #   threshold_per_category - SUM(CASE) >= N in HAVING as a numeric threshold gate
    #                            across multiple categories (spent >= $100 in June AND July).
    #                            Canonical LeetCode #1607 / #1581 shape.
    pivot_flavor = None
    if qtype == "pivot" and subtype:
        pivot_flavor = subtype
    elif qtype == "pivot":
        pivot_flavor = random.choice([
            "multi_column_pivot", "signed_aggregate",
            "membership_filter", "threshold_per_category"
        ])
    # If the learner left Subtype on Random (subtype is None) and this qtype has a
    # SUBTYPES menu, pick ONE now so the guidance pins it AND _meta records what it
    # landed on (so the notebook can show "Random -> <chosen>" instead of blank).
    # union_islands / percentile_metrics / pivot are skipped here — they already pick
    # and record their own (dialect-aware) flavor field above.
    _FLAVOR_QTYPES = {"union_islands", "percentile_metrics", "pivot"}
    if subtype is None and qtype in SUBTYPES and qtype not in _FLAVOR_QTYPES:
        subtype = random.choice([s for s, _ in SUBTYPES[qtype]])
    for attempt in range(1, max_retries + 1):
        if on_attempt:
            try:
                on_attempt(attempt, max_retries, last_error)
            except Exception:
                pass

        user_prompt = _topic_specific_guidance(qtype_for_guidance, dialect, scenario=scenario, dml_op=dml_op, islands_flavor=islands_flavor, percentile_flavor=percentile_flavor, difficulty=difficulty, pivot_flavor=pivot_flavor, subtype=subtype)
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
            "original_qtype": original_qtype,  # what the picker said; differs from question_type when a meta qtype resolved
            "dialect": dialect,
            "difficulty": difficulty or "moderate",
            "scenario_mode": scenario_mode or "random",
            "generated_at": datetime.now().isoformat(),
            "problem_id": uuid.uuid4().hex[:12],
            "validation_attempts": attempt,
            "scenario": scenario,
            "dml_op": dml_op,  # None for non-dml types; UPDATE/DELETE/INSERT for dml
            "islands_flavor": islands_flavor,  # None for non-union_islands; date_calendar/date_sequence/integer_seq/partitioned_status_periods otherwise
            "percentile_flavor": percentile_flavor,  # None for non-percentile_metrics; percentile_aggregate/ntile_buckets/top_n_percent otherwise
            "pivot_flavor": pivot_flavor,  # None for non-pivot; multi_column_pivot/signed_aggregate/membership_filter/threshold_per_category otherwise
            "subtype": subtype,  # forced subtype (None = random within the qtype)
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
You are a SQL coach grading a student's six-step problem analysis. The student
fills out a diagnostic worksheet BEFORE writing SQL. The worksheet walks them
from mapping the inputs/output (Step 1), classifying how data arrives (Step 2),
naming the shape and recipe (Step 3), eliminating decision-tree branches
(Step 4), grabbing a recipe template and adapting from a similar problem
(Step 5), to a sanity-check of failure modes (Step 6). Give terse, encouraging
feedback that points at exactly what to rethink.

Output MUST be a single JSON object inside a ```json fenced block:
{
  "paraphrase_feedback": "1-2 sentences on whether their restatement captures the goal",
  "step1_feedback": "1-2 sentences on whether the input tables, output columns, and grain are right",
  "grain_correct": true | false,
  "row_direction_correct": true | false,
  "input_correct": true | false,
  "input_feedback": "1 sentence on the Step 2 input classification (single table / join / reshape / etc.)",
  "recipe_correct": true | false,
  "shape_feedback": "1 sentence on the Step 3 named shape and recipe choice",
  "moves_feedback": "1-2 sentences on whether their move sequence is reasonable",
  "step4_feedback": "1-2 sentences on whether the branches they ruled out and the remaining branch make sense",
  "step5_feedback": "1-2 sentences on the recipe template, similar problem pick, and adaptations list",
  "step6_feedback": "1-2 sentences on whether the failure mode and chosen sanity checks fit this problem",
  "overall": "one short sentence summary"
}

Hard rules:
- Be terse, lay language, no metaphors.
- Treat near-correct answers as correct (e.g., "row filter" matches "row-filter").
- Skip blank fields gracefully: if a field is empty, say "left blank" rather than marking it wrong, and set its *_correct flag to false only when an actual answer is wrong.
- Do NOT show the answer or write SQL for them.
- Do NOT mention any commercial brand or practice-platform names.
"""


def grade_diagnostic(problem: Dict[str, Any], answers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    user_prompt = f"""Problem prompt:
{problem.get('prompt', '')}

Answer key classification (do not reveal to student):
{json.dumps(problem.get('classification', {}), indent=2)}

Reference answer key (do not reveal; use only to judge the student):
{problem.get('answer_key', '')}

Student worksheet:

Paraphrase / restated prompt: {answers.get('paraphrase', '')}

STEP 1 — Map the inputs and output
- Input table(s) and columns: {answers.get('input_map', '')}
- Output columns: {answers.get('output_columns', '')}
- Output grain (what is one row): {answers.get('output_grain', '')}
- Row count direction (fewer / same / single value): {answers.get('row_direction', '')}

STEP 2 — Classify the inputs
- How does data arrive: {answers.get('input_arrival', '')}

STEP 3 — Name the shape
- Named shape ("this is a __ because __"): {answers.get('named_shape', '')}
- Recipe category: {answers.get('recipe', '')}
- Composite moves in order: {answers.get('composite_moves', '')}

STEP 4 — Walk the decision tree by elimination
- Branches ruled out (and why): {answers.get('ruled_out', '')}
- Remaining branch(es): {answers.get('remaining_branch', '')}

STEP 5 — Grab the recipe, adapt from a linked problem
- Recipe template: {answers.get('recipe_template', '')}
- Most similar linked problem: {answers.get('similar_problem', '')}
- Adaptations needed (keys, columns, filters, output, edge cases): {answers.get('adaptations', '')}

STEP 6 — Sanity check
- Failure mode for this branch: {answers.get('failure_mode', '')}
- Sanity checks they ticked: {answers.get('sanity_checks', '')}
- Red flags they ticked: {answers.get('red_flags', '')}

Grade the student.
"""
    text = _call_claude(DIAGNOSTIC_SYSTEM, user_prompt, max_tokens=1400)
    return _extract_json(text)


WALKTHROUGH_SYSTEM = """\
You are a SQL coach. The student is about to fill out a six-step diagnostic
worksheet for the problem below. Produce a worked answer for each field so the
student can read it, then paraphrase it in their own words. Keep every field to
one or two short sentences in lay language. This is the analysis ONLY — do NOT
write the final SQL solution.

Output MUST be a single JSON object inside a ```json fenced block:
{
  "w_paraphrase": "the prompt restated plainly",
  "w_input_map": "the input table(s) and the columns that matter",
  "w_output_columns": "the columns the output should have",
  "w_grain": "what one output row represents",
  "w_row_direction": "fewer | same | single value (pick one) and why",
  "w_input_arrival": "single table | join 2+ | reshape (pick one) and why",
  "w_named_shape": "this is a <recipe> because <one reason>",
  "w_recipe": "the recipe category id (e.g. group-aggregate)",
  "w_moves": "the moves in order, one short line each",
  "w_ruled_out": "two branches to rule out and why",
  "w_remaining": "the branch that survives",
  "w_recipe_template": "the skeleton shape of the query in words, not full SQL",
  "w_similar_problem": "what kind of prior problem this most resembles",
  "w_adaptations": "join keys, columns, filters, output, edge cases to adapt",
  "w_failure_mode": "the most likely way this branch goes wrong",
  "w_checks": "the 2-3 sanity checks that matter most here"
}

Hard rules:
- Lay language, no metaphors, no commercial brand names.
- Analysis only. Never paste the final SQL solution.
"""


def walkthrough_diagnostic(problem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Worked answers for each diagnostic step, for Walkthrough mode. Analysis
    only — no final SQL."""
    user_prompt = f"""Problem prompt:
{problem.get('prompt', '')}

Answer key classification (use to ground your worked answers):
{json.dumps(problem.get('classification', {}), indent=2)}

Produce the worked diagnostic worksheet for this problem.
"""
    text = _call_claude(WALKTHROUGH_SYSTEM, user_prompt, max_tokens=1400)
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


def list_problems(outputs_dir: str, dialect: Optional[str] = None, qtype: Optional[str] = None, subtype: Optional[str] = None) -> List[Dict[str, str]]:
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
            if subtype and meta.get("subtype") != subtype:
                continue
            out.append({
                "path": path,
                "title": p.get("title", fname),
                "dialect": meta.get("dialect", ""),
                "qtype": meta.get("question_type", ""),
                "subtype": meta.get("subtype", ""),
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
# Error tracking (failed submits) + review
# ============================================================

def effective_subtype(meta: Dict[str, Any]) -> Optional[str]:
    """The subtype that was actually used, looking through the flavor fields that
    union_islands / percentile_metrics / pivot record under their own keys."""
    return (meta.get("subtype") or meta.get("islands_flavor")
            or meta.get("percentile_flavor") or meta.get("pivot_flavor"))


def log_error(problem: Dict[str, Any], user_solution: str, failure_kind: str,
              outputs_dir: str, error_message: Optional[str] = None,
              your_columns: Optional[List[str]] = None,
              your_rows: Optional[List[List[Any]]] = None) -> str:
    """Record a FAILED submit so it can be reviewed later.

    failure_kind: 'sql_error' (query threw) or 'wrong_answer' (ran but result mismatched).
    Captures the full problem context (including answer_key = the correct solution),
    the exact SQL the learner submitted, and either the error message or the
    expected-vs-yours result so the review notebook has everything in one place.
    One JSON file per failure (so re-submitting logs every attempt).
    """
    os.makedirs(outputs_dir, exist_ok=True)
    meta = problem.get("_meta", {})
    pid = meta.get("problem_id", uuid.uuid4().hex[:12])
    ts = datetime.now()
    record = {
        "logged_at": ts.isoformat(),
        "failure_kind": failure_kind,
        # --- pattern tags (for grouping / recommendations) ---
        "problem_id": pid,
        "question_type": meta.get("question_type"),
        "original_qtype": meta.get("original_qtype"),
        "subtype": effective_subtype(meta),
        "scenario": meta.get("scenario"),
        "difficulty": meta.get("difficulty"),
        "dialect": meta.get("dialect"),
        "recipe": (problem.get("classification", {}) or {}).get("recipe"),
        # --- problem context + the correct answer ---
        "title": problem.get("title"),
        "prompt": problem.get("prompt"),
        "schema_ddl": problem.get("schema_ddl"),
        "answer_key": problem.get("answer_key"),
        "test_expected_columns": problem.get("test_expected_columns"),
        "test_expected_rows": problem.get("test_expected_rows"),
        # --- what the learner did + what went wrong ---
        "user_solution": user_solution,
        "error_message": error_message,
        "your_columns": your_columns,
        "your_rows": your_rows,
    }
    fname = f"{ts.strftime('%Y%m%d_%H%M%S')}_{ts.microsecond:06d}_{pid}_{uuid.uuid4().hex[:4]}.json"
    path = os.path.join(outputs_dir, fname)
    with open(path, "w") as f:
        json.dump(record, f, indent=2, default=str)
    return path


def load_errors(errors_dir: str, qtype: Optional[str] = None,
                subtype: Optional[str] = None,
                failure_kind: Optional[str] = None) -> List[Dict[str, Any]]:
    """Load all logged failures, newest first, optionally filtered."""
    if not os.path.isdir(errors_dir):
        return []
    recs = []
    for fn in os.listdir(errors_dir):
        if not fn.endswith(".json"):
            continue
        try:
            with open(os.path.join(errors_dir, fn)) as f:
                recs.append(json.load(f))
        except Exception:
            continue
    if qtype:
        recs = [r for r in recs if r.get("question_type") == qtype]
    if subtype:
        recs = [r for r in recs if r.get("subtype") == subtype]
    if failure_kind:
        recs = [r for r in recs if r.get("failure_kind") == failure_kind]
    recs.sort(key=lambda r: r.get("logged_at", ""), reverse=True)
    return recs


def summarize_errors(records: List[Dict[str, Any]]) -> Dict[str, "pd.DataFrame"]:
    """Aggregate logged failures into count tables for the review notebook."""
    if not records:
        empty = pd.DataFrame()
        return {"total": 0, "by_type": empty, "by_pattern": empty, "by_kind": empty}
    df = pd.DataFrame([{
        "question_type": r.get("question_type"),
        "subtype": r.get("subtype") or "(none)",
        "failure_kind": r.get("failure_kind"),
        "difficulty": r.get("difficulty"),
    } for r in records])
    by_type = (df.groupby("question_type").size()
                 .reset_index(name="failures").sort_values("failures", ascending=False))
    by_pattern = (df.groupby(["question_type", "subtype"]).size()
                    .reset_index(name="failures").sort_values("failures", ascending=False))
    by_kind = (df.groupby("failure_kind").size()
                 .reset_index(name="failures").sort_values("failures", ascending=False))
    return {"total": len(records), "by_type": by_type,
            "by_pattern": by_pattern, "by_kind": by_kind}


def recommend_practice(records: List[Dict[str, Any]], top: int = 5) -> List[Dict[str, Any]]:
    """Rank (type, subtype) patterns by how often they fail — what to drill next.
    Each row is annotated with its playbook pointer (tab / recipe / leaf)."""
    s = summarize_errors(records)
    if not s["total"]:
        return []
    rows = s["by_pattern"].head(top).to_dict("records")
    for r in rows:
        sub = None if r.get("subtype") in (None, "(none)") else r["subtype"]
        r["playbook"] = playbook_pointer(r.get("question_type"), sub)
    return rows


# --- Where each qtype / subtype lives in sql_problem_patterns.html ---
# qtype -> (tab id, recipe-or-leaf anchor, human breadcrumb)
_PB_QTYPE = {
    "filter_strategies":        ("tab-single", "row-filter",        "Single-Table › Filter"),
    "anti_join":                ("tab-single", "rf-leaf-antijoin",  "Single-Table › Filter › Anti-join"),
    "scalar_extract":           ("tab-single", "scalar-extract",    "Single-Table › Scalar"),
    "percentile_metrics":       ("tab-single", "rank-percentile",   "Single-Table › Rank & Percentile"),
    "window_running_total":     ("tab-single", "time-window",       "Single-Table › Window"),
    "window_lag_lead":          ("tab-single", "row-compare",       "Single-Table › Compare › Compare to the previous or next row"),
    "window_sliding":           ("tab-single", "time-window",       "Single-Table › Window (sliding)"),
    "window_first_last":        ("tab-single", "time-window",       "Single-Table › Window (FIRST / LAST_VALUE)"),
    "window_sessionization":    ("tab-single", "time-window",       "Single-Table › Window (sessionization)"),
    "window_frames":            ("tab-single", "time-window",       "Single-Table › Window (frame clauses)"),
    "window_benchmark_compare": ("tab-single", "time-window",       "Single-Table › Window (group benchmark)"),
    "window_edge":              ("tab-single", "time-window",       "Single-Table › Window"),
    "union_islands":            ("tab-single", "row-compare",       "Single-Table › Compare › Gaps-and-Islands"),
    "date_operations":          ("tab-single", "date-operations",   "Single-Table › Date Operations"),
    "gated_lookup":             ("tab-multi",  "gated-lookup",      "Multi-Table › Gated Lookup"),
    "window_top_n_per_group":   ("tab-multi",  "rank-partition",    "Multi-Table › Rank Within Groups to Select Top-N"),
    "point_in_time":            ("tab-single", "point-in-time",     "Single-Table › Point in Time"),
    "delete_duplicates":        ("tab-single", "delete-duplicates", "Single-Table › Dedup"),
    "left_join_on_filter":      ("tab-multi",  "filtered-join",     "Multi-Table › Filtered Join (ON vs WHERE)"),
    "matchup_unpivot":          ("tab-multi",  "matchup-leaderboard","Multi-Table › Matchup & Leaderboard"),
    "pivot":                    ("tab-reshape","reshape-pivot",     "Reshape › Pivot"),
    "unpivot":                  ("tab-reshape","reshape-unpivot",   "Reshape › Unpivot"),
    "series_generation":        ("tab-reshape","reshape-series-generation","Reshape › Series Generation"),
    "enrich_join":              ("tab-multi",  "enrich-join",       "Multi-Table › Look Up Columns"),
    "cross_join":               ("tab-reshape","reshape-cross-join","Reshape › Cross Join"),
    "dml":                      ("tab-procedural","topic-dml",      "Procedures › Updates, Deletes, Inserts"),
    "dml_update":               ("tab-procedural","topic-dml",      "Procedures › Updates, Deletes, Inserts"),
    "dml_delete":               ("tab-procedural","topic-dml",      "Procedures › Updates, Deletes, Inserts"),
    "dml_insert":               ("tab-procedural","topic-dml",      "Procedures › Updates, Deletes, Inserts"),
    "do_block":                 ("tab-procedural","topic-dml",      "Procedures › Updates, Deletes, Inserts (DO block)"),
    "do_block_queue":           ("tab-procedural","topic-dml",      "Procedures › Updates, Deletes, Inserts (DO block)"),
    "returns_table":            ("tab-procedural","topic-functions","Procedures › Functions (RETURNS TABLE)"),
    "returns_scalar":           ("tab-procedural","topic-functions","Procedures › Functions (RETURNS scalar)"),
    "recursive_cte":            ("tab-procedural","topic-recursive-queries","Procedures › Recursive Queries"),
    "root_cause_analysis":      ("tab-diagnostic", None,            "Diagnostic Process"),
    "select_analytical":        ("tab-diagnostic", None,            "Diagnostic Process"),
}
# (qtype, subtype) -> leaf anchor + leaf label, overriding the recipe-level anchor above
_PB_SUBTYPE = {
    ("anti_join", "not_exists"):     ("rf-antijoin-notexists", "NOT EXISTS"),
    ("anti_join", "left_join_null"): ("rf-antijoin-leftnull",  "LEFT JOIN … IS NULL"),
    ("anti_join", "not_in"):         ("rf-antijoin-notin",     "NOT IN"),
    ("filter_strategies", "comparison"): ("rf-leaf-compare",    "Comparison"),
    ("filter_strategies", "null_aware"): ("rf-leaf-null",       "NULL-aware"),
    ("filter_strategies", "pattern"):    ("rf-leaf-pattern",    "Pattern matching"),
    ("filter_strategies", "membership"): ("rf-leaf-membership", "Membership (IN / EXISTS)"),
    ("filter_strategies", "anti_join"):  ("rf-leaf-antijoin",   "Anti-join"),
    ("scalar_extract", "single_aggregate"): ("sc-leaf-aggregate", "Single aggregate"),
    ("scalar_extract", "top1"): ("sc-leaf-top1", "Top-1 row"),
    ("scalar_extract", "nth"):  ("sc-leaf-nth",  "Nth value"),
    ("scalar_extract", "ratio"):("sc-leaf-ratio","Ratio / percentage"),
    ("gated_lookup", "case_keep"):     ("gl-leaf-case",      "CASE around the aggregate"),
    ("gated_lookup", "gate_on"):       ("gl-leaf-onclause",  "Gate in the JOIN ON"),
    ("gated_lookup", "rownumber_pick"):("gl-leaf-rownumber", "ROW_NUMBER + rn = 1"),
    ("left_join_on_filter", "date_window"):      ("ea-leaf-leftjoin-on",   "Right-side date window"),
    ("left_join_on_filter", "status_category"):  ("fj-leaf-status",        "Right-side status / category"),
    ("left_join_on_filter", "numeric_threshold"):("fj-leaf-threshold",     "Right-side numeric threshold"),
    ("left_join_on_filter", "both_sides"):       ("fj-leaf-bothsides",     "Left in WHERE + right in ON"),
    ("left_join_on_filter", "sum_coalesce"):     ("fj-leaf-sumcoalesce",   "SUM / AVG with COALESCE"),
    ("left_join_on_filter", "existence_flag"):   ("fj-leaf-existence",     "Boolean / existence flag"),
    ("date_operations", "date_trunc_cohort"):    ("do-leaf-trunc",      "DATE_TRUNC cohort buckets"),
    ("date_operations", "extract_component"):    ("do-leaf-extract",    "EXTRACT a date component"),
    ("date_operations", "date_arithmetic"):      ("do-leaf-arithmetic", "Date arithmetic / cutoffs"),
    ("date_operations", "duration_between"):     ("do-leaf-duration",   "Duration between timestamps"),
    ("date_operations", "day_count_boundaries"): ("do-leaf-daycount",   "Inclusive vs exclusive day count"),
    ("union_islands", "integer_seq"):                    ("gi-leaf-int",        "Consecutive integer ids"),
    ("union_islands", "date_calendar"):                  ("gi-leaf-date-nogap", "Consecutive calendar dates, no gaps"),
    ("union_islands", "date_sequence"):                  ("gi-leaf-date-gap",   "Consecutive dates with gaps"),
    ("union_islands", "partitioned_status_periods"):     ("gi-leaf-entity",     "Per-entity island timelines"),
    ("union_islands", "consecutive_day_streak_per_entity"): ("gi-leaf-entity",  "Per-entity day streak"),
    ("window_lag_lead", "neighbour_value"): ("rc-leaf-neighbor-value", "Compare to neighbour's value"),
    ("window_lag_lead", "gap_delta"):       ("rc-leaf-gap-delta",       "Gap / delta to the neighbour"),
    ("window_lag_lead", "fixed_run"):       ("rc-leaf-fixed-run",       "Fixed-length run of N rows"),
    ("window_lag_lead", "pair_by_role"):    ("rc-leaf-pair-role",       "Pair two rows by role"),
    ("pivot", "multi_column_pivot"):     ("pv-leaf-stored",    "Long to wide pivot"),
    ("pivot", "signed_aggregate"):       ("pv-leaf-signed",    "Signed aggregate (net of opposing categories)"),
    ("pivot", "membership_filter"):      ("pv-leaf-membership","Set membership: has ALL / NONE"),
    ("pivot", "threshold_per_category"): ("pv-leaf-threshold", "Threshold per category"),
    ("unpivot", "drop"):      ("up-leaf-drop",      "Columns to rows, drop the empties"),
    ("unpivot", "keep"):      ("up-leaf-keep",      "Columns to rows, keep the empties"),
    ("unpivot", "aggregate"): ("up-leaf-aggregate", "Unpivot then aggregate"),
    ("enrich_join", "straight_lookup"): ("ej-leaf-lookup",   "Straight lookup / enrich"),
    ("enrich_join", "self_join"):       ("ej-leaf-selfjoin", "Self-join: one table, two roles"),
    ("enrich_join", "cross_join"):      ("ej-leaf-cross",    "Cross join: all combinations"),
    ("enrich_join", "per_group"):       ("ej-leaf-pergroup", "Match each row to a per-group value"),
    ("enrich_join", "compound"):        ("ej-leaf-compound", "Compound eligibility"),
    ("delete_duplicates", "keep_min_id"): ("dd-leaf-minid",    "Keep the lowest id (NOT IN MIN)"),
    ("delete_duplicates", "self_join"):   ("dd-leaf-selfjoin", "Self-join delete (remove the higher-id twin)"),
    ("delete_duplicates", "row_number"):  ("dd-leaf-rownumber","ROW_NUMBER then delete rn > 1"),
    ("point_in_time", "asof_single"):        ("pit-leaf-asof",    "As of a single cutoff date"),
    ("point_in_time", "default_no_history"): ("pit-leaf-default", "Default when no history"),
    ("point_in_time", "fill_forward"):       ("pit-leaf-fill",    "Fill forward over a date spine"),
    ("window_top_n_per_group", "top1_by_value"): ("rp-multi-top1-by-value", "Top 1 by value"),
    ("window_top_n_per_group", "top1_by_date"):  ("rp-multi-top1-by-date",  "Top 1 by date"),
    ("window_top_n_per_group", "topn"):          ("rp-multi-topn",          "Top N"),
    ("window_top_n_per_group", "nth"):           ("rp-multi-nth",           "Nth position"),
    ("window_top_n_per_group", "special"):       ("rp-multi-special",       "Special rank patterns"),
}


def playbook_pointer(qtype: Optional[str], subtype: Optional[str] = None) -> Optional[Dict[str, str]]:
    """Map an engine qtype/subtype to its home in sql_problem_patterns.html.
    Returns {'tab', 'anchor', 'label'} or None if the qtype has no recipe home."""
    base = _PB_QTYPE.get(qtype)
    if not base:
        return None
    tab, anchor, label = base
    leaf = _PB_SUBTYPE.get((qtype, subtype))
    if leaf:
        anchor, leaf_label = leaf
        label = f"{label} › {leaf_label}"
    return {"tab": tab, "anchor": anchor, "label": label}


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
    """Split a prompt into a bulleted list, with support for nested structure.

    Two formats are recognized within a single prompt:

    1. Markdown-style nested markers ``•`` / ``-`` / ``+``: when the prompt
       contains a ``•`` bullet, everything before it is rendered as intro
       sentences, and the ``•``-marked sections become a 3-level nested
       ``<ul>`` (•=parent, -=section, +=item).

    2. Inline numbered steps like ``(1) ... (2) ... (3) ...`` within a
       single sentence: the text before the first marker becomes the parent
       bullet's text (header), and each numbered step is rendered as a
       nested ``<ol>`` item. The ``(N)`` prefix is stripped because
       ``<ol>`` auto-numbers.
    """
    if not prompt:
        return ''
    text = prompt.strip()

    # ---- Markdown-style nested bullets (•, -, +) ------------------------
    # Targeted fallback: do_block_queue prompts should use '•' for top-level
    # event rules, but generators sometimes substitute '-' (ambiguous with
    # sub-sections). Detect the canonical phrases the generator emits at
    # top level and promote those '-' to '•' so the parser can nest correctly.
    # Run BEFORE the bullet detection so the fallback can succeed.
    if '•' not in text and '●' not in text:
        text = _re.sub(
            r'(^|\s)-\s+(When\s+`event_type`|Events\s+that\s+fail\s+their\s+preconditions)',
            r'\1• \2',
            text,
        )

    # Trigger when we see a top-level bullet character preceded by whitespace
    # (or start of string) and followed by whitespace. The canonical marker
    # is ``•`` (Unicode bullet). ``●`` (filled circle) is accepted as a
    # fallback. ``*`` is NOT a top-level marker here — it appears too often
    # in SQL text like ``SELECT *`` and ``col * 0.20`` to be reliable.
    bullet_re = _re.compile(r'(?:^|\s)[•●]\s+')
    if bullet_re.search(text):
        first = bullet_re.search(text)
        intro = text[:first.start()].strip()
        body = text[first.start():].strip()

        # Render intro as plain sentence bullets (no (N) detection here —
        # intro sentences in this format are descriptive prose only).
        intro_html = ''
        if intro:
            raw = _re.split(r'(?<=[.!?])\s+', intro)
            sentences = [s.strip() for s in raw if s.strip()]
            intro_html = ''.join(
                f'<li style="margin-bottom:4px;">{s}</li>' for s in sentences
            )

        # Parse the body. Top-level items split on '•', sub-sections on '-',
        # leaf items on '+'. Each marker must be preceded by whitespace or
        # string start, and followed by whitespace, so they don't collide
        # with math operators or hyphens inside text.
        dash_re = _re.compile(r'(?:^|\s)-\s+')
        plus_re = _re.compile(r'(?:^|\s)\+\s+')

        def _split(pattern, s):
            parts = pattern.split(s)
            return [p.strip() for p in parts if p.strip()]

        top_items = _split(bullet_re, body)
        body_parts = []
        for top in top_items:
            sub_items = _split(dash_re, top)
            top_header = sub_items[0] if sub_items else ''
            sub_sections = sub_items[1:]

            sub_parts = []
            for sub in sub_sections:
                leaves = _split(plus_re, sub)
                sub_header = leaves[0] if leaves else ''
                leaf_items = leaves[1:]
                leaf_html = ''
                if leaf_items:
                    leaf_lis = ''.join(
                        f'<li style="margin-bottom:2px;">{li}</li>'
                        for li in leaf_items
                    )
                    leaf_html = (
                        f'<ul style="line-height:1.5; margin:2px 0 0 22px; '
                        f'padding-left:0;">{leaf_lis}</ul>'
                    )
                sub_parts.append(
                    f'<li style="margin-bottom:2px;">{sub_header}{leaf_html}</li>'
                )

            sub_html = ''
            if sub_parts:
                sub_html = (
                    f'<ul style="line-height:1.5; margin:4px 0 0 18px; '
                    f'padding-left:0;">{"".join(sub_parts)}</ul>'
                )
            body_parts.append(
                f'<li style="margin-bottom:6px;">{top_header}{sub_html}</li>'
            )

        body_html = (
            f'<ul style="line-height:1.6; margin:0 0 8px 18px; padding-left:0;">'
            f'{"".join(body_parts)}</ul>'
        )

        if intro_html:
            return (
                f'<ul style="line-height:1.6; margin:0 0 8px 18px; padding-left:0;">'
                f'{intro_html}</ul>{body_html}'
            )
        return body_html

    # ---- Inline numbered steps "1. ... 2. ... 3. ..." (digit + period) ----
    # Generators emit a numbered rule list inside the prompt (common for DO
    # block / DML problems). The plain sentence splitter shatters these because
    # it breaks on the period right after each number, leaving "1." "2." as
    # their own bullets. Detect a CONSECUTIVE run (1., 2., 3., ...) and render
    # it as an <ol>; prose before the run becomes intro bullets and prose after
    # the last step becomes trailing bullets. A marker is a small integer
    # followed by a period and a space, preceded by string start or whitespace;
    # decimals ("0.10") and "DECIMAL(10,2)" never match because they have no
    # space after the period.
    _num_re = _re.compile(r'(?:^|\s)(\d{1,2})\.\s+')
    _num_matches = list(_num_re.finditer(text))
    _run = []
    _expected = 1
    for _m in _num_matches:
        if int(_m.group(1)) == _expected:
            _run.append(_m)
            _expected += 1
    if len(_run) >= 2:
        def _sent_list(s):
            return [x.strip() for x in _re.split(r'(?<=[.!?])\s+', s) if x.strip()]

        intro = text[:_run[0].start()].strip()
        steps = []
        for _i, _m in enumerate(_run):
            _start = _m.end()
            _end = _run[_i + 1].start() if _i + 1 < len(_run) else len(text)
            steps.append(text[_start:_end].strip())
        # The last step segment may carry trailing prose after its first
        # sentence (e.g. "... 'gold'. Write a DO block ..."). Peel it off.
        trailing = ''
        if steps:
            _last_parts = _re.split(r'(?<=[.!?])\s+', steps[-1], maxsplit=1)
            if len(_last_parts) == 2:
                steps[-1] = _last_parts[0].strip()
                trailing = _last_parts[1].strip()

        step_lis = ''.join(
            f'<li style="margin-bottom:3px;">{st.rstrip(". ")}.</li>'
            for st in steps if st
        )
        ol_html = (
            f'<ol style="line-height:1.6; margin:4px 0 8px 24px; '
            f'padding-left:18px;">{step_lis}</ol>'
        )

        html = ''
        intro_sents = _sent_list(intro) if intro else []
        if intro_sents:
            head = intro_sents[-1]
            pre = intro_sents[:-1]
            if pre:
                html += (
                    '<ul style="line-height:1.6; margin:0 0 4px 18px; '
                    'padding-left:0;">'
                    + ''.join(f'<li style="margin-bottom:4px;">{s}</li>' for s in pre)
                    + '</ul>'
                )
            html += f'<div style="margin:0 0 2px 4px;">{head}</div>'
        html += ol_html
        trailing_sents = _sent_list(trailing) if trailing else []
        if trailing_sents:
            html += (
                '<ul style="line-height:1.6; margin:0 0 8px 18px; '
                'padding-left:0;">'
                + ''.join(f'<li style="margin-bottom:4px;">{s}</li>' for s in trailing_sents)
                + '</ul>'
            )
        return html

    # ---- No markdown bullets: sentence split + (N) numbered step detect -
    raw = _re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in raw if s.strip()]

    def _render_sentence(s: str) -> str:
        markers = _re.findall(r'\(\d+\)', s)
        if len(markers) >= 2:
            parts = _re.split(r'\(\d+\)\s*', s)
            header = parts[0].rstrip(' ;').rstrip()
            steps = []
            for p in parts[1:]:
                step = p.strip().rstrip(';').rstrip(' ').rstrip('.')
                if step:
                    steps.append(step)
            if steps:
                steps_html = ''.join(
                    f'<li style="margin-bottom:2px;">{step}</li>' for step in steps
                )
                return (
                    f'<li style="margin-bottom:4px;">{header}'
                    f'<ol style="margin:4px 0 0 24px; padding-left:18px;">{steps_html}</ol>'
                    f'</li>'
                )
        return f'<li style="margin-bottom:4px;">{s}</li>'

    items = ''.join(_render_sentence(s) for s in sentences)
    return f'<ul style="line-height:1.6; margin:0 0 8px 18px; padding-left:0;">{items}</ul>'


# ============================================================
# Pharmacy Claims Analytical SQL drill extension
# Originally lived in nb02_drill_utils.py. Moved here so that
# nb01_sql_practice.ipynb can offer pharmacy domain drills
# alongside its generic question type catalog.
# ============================================================

import random as _pharm_random

PHARMACY_CATEGORIES = {
    "pharmacy_sql": {
        "label": "1. Pharmacy Claims Analytical SQL",
        "description": "SQL on pharmacy claim, event, patient, prescriber, payer data.",
        "kind": "sql",
        "subtopics": {
            "adjudication_funnel": {
                "label": "Adjudication funnel (submit -> reject -> recycle -> pay)",
                "base_qtype": "select_analytical",
            },
            "cohort_retention": {
                "label": "Cohort retention (refill rate at 30/60/90 days)",
                "base_qtype": "select_analytical",
            },
            "window_event_log": {
                "label": "Window functions on event logs",
                "base_qtype": "window_edge",
            },
            "reject_pareto": {
                "label": "Reject taxonomy pareto (top N reject codes)",
                "base_qtype": "select_analytical",
            },
            "segment_performance": {
                "label": "Segment performance (drug class, payer, channel)",
                "base_qtype": "select_analytical",
            },
            "time_to_fill": {
                "label": "Time to fill aggregation (median, percentile)",
                "base_qtype": "select_analytical",
            },
            "net_acceptance_rate": {
                "label": "Net Acceptance Rate ((paid - reversed) / submitted)",
                "base_qtype": "select_analytical",
            },
            "reversal_rate": {
                "label": "Reversal rate analysis (reversed / paid, by reason)",
                "base_qtype": "select_analytical",
            },
            "adherence_pdc": {
                "label": "Patient adherence via PDC (Proportion of Days Covered)",
                "base_qtype": "select_analytical",
            },
        },
    },
}


# ---- Pharmacy domain scenarios ----

PHARMACY_SCENARIOS = [
    # Pharmacy operations
    "a digital pharmacy tracking prescription submissions through PBM adjudication",
    "a same day medication delivery service tracking on-time delivery performance",
    "a pharmacy auto-recycling workflow that retries rejected claims with corrected fields",
    "a prescription refill adherence program tracking 30/60/90 day refill rates",
    "a prior authorization (PA) cycle time tracking system across payers",
    "a formulary substitution program suggesting covered alternatives at point of fill",
    "a pharmacy fulfillment economics tracker for revenue per dispensed script",
    "a pharmacy manual touch volume tracker measuring care team intervention rate",
    "a script abandonment surveillance system tracking patients who never picked up filled prescriptions",
    "a fertility medication delivery program tracking time to first dose for IVF cycles",
    # At-home diagnostics
    "an at-home diagnostic test kit ordering platform tracking kit shipped, returned, results released",
    "a genomics sequencing service tracking sample receipt to results turnaround time",
    "a hormone health test kit subscription tracking adherence to repeat-test cadence",
    # Telehealth and care coordination
    "a telehealth visit completion funnel from booking to provider sign-off",
    "a clinical engagement program tracking patient outreach response rates by channel",
    "a care coordination platform tracking handoffs between provider, pharmacy, and patient",
    # B2B platform / API
    "a B2B pharmacy API platform tracking partner integration health and claim throughput",
    "an enterprise wellness contract tracking covered employee utilization across services",
    "a payer integration eligibility check service tracking real-time eligibility latency",
    # Patient experience
    "a patient app onboarding funnel tracking signup to first prescription transferred",
    "a patient adherence intervention tracking which nudge channels move refill behavior",
    # Supply chain (cross-cutting)
    "a pharmacy inventory and fill rate tracker by drug class and warehouse",
    "a NADAC vs paid amount spread tracker by drug, payer, and channel",
]

def _pick_pharmacy_scenario() -> str:
    return _pharm_random.choice(PHARMACY_SCENARIOS)


# ---- Pharmacy subtopic guidance ----

PHARMACY_SUBTOPIC_GUIDANCE = {
    "adjudication_funnel": "Build a sequential FORWARD funnel problem on a pharmacy claim event log.\n"
        "Schema MUST include a claim_events table with columns like claim_id, event_type "
        "(values include 'submitted', 'rejected', 'recycled', 'paid', and at least one "
        "non-funnel event like 'reversed' and/or 'dispensed'), event_ts.\n"
        "FUNNEL STAGES — the prompt MUST specify exactly which event types ARE part of the "
        "funnel and which are NOT:\n"
        "  - Forward funnel stages (in order): submitted, rejected, recycled, paid\n"
        "  - NON-funnel events that exist in the data but MUST BE EXCLUDED from the funnel: "
        "reversed, dispensed (and any other event types). Reversed is a backwards financial "
        "adjustment, not a forward stage. Dispensed is a downstream fulfillment event, not "
        "part of adjudication.\n"
        "The prompt MUST contain explicit language like: 'Only include these four event types "
        "in the funnel: submitted, rejected, recycled, paid. The data also contains reversed "
        "and dispensed events — exclude them from this analysis.' This prevents users from "
        "reasonably interpreting the data and getting penalized for including reversed as "
        "a 5th stage.\n"
        "DATA REQUIREMENT: example_input_data and test_data MUST include at least one "
        "'reversed' event AND at least one 'dispensed' event so the user's WHERE filter is "
        "actually exercised. A user solution that forgets to filter will fail correctly.\n"
        "OTHER EDGE CASES TO INCLUDE: at least one claim that was rejected, recycled, then "
        "paid (forces first-event-of-type logic, not raw counts).\n"
        "BUSINESS CONTEXT FOR THE GLOSSARY/CALC SECTIONS: explain that this is a forward "
        "funnel only. Reversals belong in a separate metric (Net Acceptance Rate = "
        "(paid - reversed) / submitted, OR a standalone Reversal Rate = reversed / paid). "
        "Dispensed events belong in a separate Time-to-Fill or fulfillment funnel. "
        "Conflating these into one funnel produces conversion rates that are arithmetically "
        "fine but operationally meaningless.",
    "cohort_retention": "Build a cohort retention problem on prescription refill data. KEEP IT SIMPLE — this "
        "subtopic has historically failed validation because the LLM mis-traces the rate math. "
        "Use the simplified shape below verbatim.\n\n"
        "SCHEMA (use exactly this shape):\n"
        "  CREATE TABLE prescriptions (\n"
        "      rx_id INT PRIMARY KEY,\n"
        "      patient_id VARCHAR(10) NOT NULL,\n"
        "      drug_class VARCHAR(50) NOT NULL,\n"
        "      fill_date DATE NOT NULL,\n"
        "      days_supply INT NOT NULL\n"
        "  );\n\n"
        "METRIC DEFINITION (use this verbatim — do NOT vary):\n"
        "  refill_rate_at_N_days = (count of DISTINCT patients who have any fill_date "
        "satisfying fill_date > first_fill_date AND fill_date <= first_fill_date + N days) "
        "/ (count of DISTINCT patients in the prescriptions table)\n"
        "Where first_fill_date per patient = MIN(fill_date) across all that patient's rows.\n"
        "The first fill itself does NOT count toward the refill (strict greater-than).\n"
        "A patient with multiple refills inside the window still counts ONCE.\n\n"
        "OUTPUT SHAPE: a single row with three columns:\n"
        "  refill_rate_30d, refill_rate_60d, refill_rate_90d\n"
        "(all DECIMAL, rounded to 4 places). NO cohort grouping — one row total.\n\n"
        "EXAMPLE INPUT DATA (use exactly 4 patients, exactly these fills, so the math is "
        "trivially traceable):\n"
        "  Patient P001: fills on 2024-01-01, 2024-01-20            → first=01-01, refill at 19d\n"
        "  Patient P002: fills on 2024-01-01, 2024-02-15            → first=01-01, refill at 45d\n"
        "  Patient P003: fills on 2024-01-01, 2024-03-25            → first=01-01, refill at 84d\n"
        "  Patient P004: fills on 2024-01-01 (only one fill)        → no refill\n\n"
        "EXPECTED REFILL RATES (compute these by hand and use them for example_output_rows):\n"
        "  refill_rate_30d = 1/4 = 0.2500  (only P001 refilled within 30 days of their first fill)\n"
        "  refill_rate_60d = 2/4 = 0.5000  (P001 and P002 refilled within 60 days)\n"
        "  refill_rate_90d = 3/4 = 0.7500  (P001, P002, P003 refilled within 90 days)\n\n"
        "ANSWER KEY SHAPE (use this CTE pattern):\n"
        "  WITH first_fills AS (\n"
        "    SELECT patient_id, MIN(fill_date) AS first_fill_date FROM prescriptions GROUP BY patient_id\n"
        "  ),\n"
        "  refilled_within AS (\n"
        "    SELECT\n"
        "      ff.patient_id,\n"
        "      MAX(CASE WHEN p.fill_date > ff.first_fill_date AND p.fill_date <= ff.first_fill_date + INTERVAL '30 days' THEN 1 ELSE 0 END) AS r30,\n"
        "      MAX(CASE WHEN p.fill_date > ff.first_fill_date AND p.fill_date <= ff.first_fill_date + INTERVAL '60 days' THEN 1 ELSE 0 END) AS r60,\n"
        "      MAX(CASE WHEN p.fill_date > ff.first_fill_date AND p.fill_date <= ff.first_fill_date + INTERVAL '90 days' THEN 1 ELSE 0 END) AS r90\n"
        "    FROM first_fills ff\n"
        "    LEFT JOIN prescriptions p ON p.patient_id = ff.patient_id\n"
        "    GROUP BY ff.patient_id\n"
        "  )\n"
        "  SELECT\n"
        "    ROUND(SUM(r30)::numeric / COUNT(*), 4) AS refill_rate_30d,\n"
        "    ROUND(SUM(r60)::numeric / COUNT(*), 4) AS refill_rate_60d,\n"
        "    ROUND(SUM(r90)::numeric / COUNT(*), 4) AS refill_rate_90d\n"
        "  FROM refilled_within;\n\n"
        "TEST DATA: 6 patients, fill patterns chosen so the rates are different from example "
        "(e.g., 2/6, 4/6, 5/6). Include at least one realistic edge case (a patient with "
        "back-to-back fills inside 30 days — must still count once) per the EDGE CASE "
        "REQUIREMENT.\n\n"
        "DO NOT add cohort grouping. DO NOT add segmentation by drug_class. The simplified "
        "single-row output dramatically reduces the LLM's chance of arithmetic errors.",
    "window_event_log": "Build a window function problem on a pharmacy event log. The answer MUST require a window "
        "function (LAG, LEAD, ROW_NUMBER, SUM OVER, AVG OVER) with a non-trivial partition or frame "
        "specification. Common shapes: time-between-events per claim using LAG over event_ts, "
        "running cumulative dispensed value per patient using SUM OVER PARTITION BY patient_id, "
        "or first / last event per claim using ROW_NUMBER PARTITION BY claim_id ORDER BY event_ts. "
        "The prompt should make it clear why a window function is the right tool (vs a self join "
        "or GROUP BY).",
    "reject_pareto": "Build a Pareto / top-N problem on pharmacy reject codes. Schema includes a claims table "
        "with reject_code, reject_reason, claim_id, drug_class, payer. Use realistic NCPDP-style "
        "reject category names (PA required, formulary not covered, refill too soon, days supply "
        "exceeded, DUR reject, COB stale). The prompt asks for top N reject codes by volume AND "
        "their cumulative percentage, with WINDOW SUM for the running total. Include at least one "
        "reject code with only 1 or 2 occurrences to test that ordering and tie handling are right.",
    "segment_performance": "Build a segment performance comparison problem. KEEP IT SIMPLE — this subtopic has "
        "historically failed validation when the LLM tries to add HAVING filters or multi-"
        "dimension grouping with insufficient data. Use the simplified shape below verbatim.\n\n"
        "SCHEMA (use exactly this shape):\n"
        "  CREATE TABLE claims (\n"
        "      claim_id VARCHAR(10) PRIMARY KEY,\n"
        "      patient_id VARCHAR(10) NOT NULL,\n"
        "      drug_class VARCHAR(50) NOT NULL,\n"
        "      reject_code VARCHAR(10)  -- nullable; NULL means paid on first submit\n"
        "  );\n\n"
        "METRIC DEFINITION (use this verbatim — no other variants):\n"
        "  First Pass Acceptance Rate (FPAR) BY drug_class =\n"
        "    (count of claims with reject_code IS NULL) / (count of claims) — per drug_class group\n\n"
        "OUTPUT SHAPE: one row per drug_class with three columns:\n"
        "  drug_class, total_claims, first_pass_acceptance_rate\n"
        "Order by first_pass_acceptance_rate ASC (worst-performing class first — the operational "
        "view that surfaces where to invest).\n\n"
        "NO HAVING FILTER. NO multi-dimension GROUP BY (do not group by drug_class AND payer). "
        "The simpler shape eliminates the row-count mismatch that kept failing validation. "
        "Multi-dim and HAVING variants belong in a separate, more advanced subtopic — not here.\n\n"
        "EXAMPLE INPUT DATA (use exactly 8 claims across 3 drug classes, hand-traceable):\n"
        "  C001, P001, GLP-1 agonists, NULL                  -- paid\n"
        "  C002, P002, GLP-1 agonists, NULL                  -- paid\n"
        "  C003, P003, GLP-1 agonists, '75 - Prior Auth'     -- rejected\n"
        "  C004, P004, statins, NULL                         -- paid\n"
        "  C005, P005, statins, NULL                         -- paid\n"
        "  C006, P006, statins, NULL                         -- paid\n"
        "  C007, P007, fertility medications, '70 - Not Cov' -- rejected\n"
        "  C008, P008, fertility medications, '75 - Prior Auth' -- rejected\n\n"
        "EXPECTED OUTPUT (compute these by hand and use them as example_output_rows):\n"
        "  fertility medications | 2 | 0.0000   (0 paid out of 2)\n"
        "  GLP-1 agonists        | 3 | 0.6667   (2 paid out of 3)\n"
        "  statins               | 3 | 1.0000   (3 paid out of 3)\n"
        "Note: ordered by FPAR ASC, so fertility (0.0000) is first, statins (1.0000) is last.\n\n"
        "ANSWER KEY SHAPE (use this single-SELECT pattern):\n"
        "  SELECT\n"
        "    drug_class,\n"
        "    COUNT(*) AS total_claims,\n"
        "    ROUND(\n"
        "      SUM(CASE WHEN reject_code IS NULL THEN 1 ELSE 0 END)::numeric / COUNT(*),\n"
        "      4\n"
        "    ) AS first_pass_acceptance_rate\n"
        "  FROM claims\n"
        "  GROUP BY drug_class\n"
        "  ORDER BY first_pass_acceptance_rate ASC, drug_class ASC;\n"
        "The drug_class ASC tiebreaker makes ties in FPAR deterministic.\n\n"
        "TEST DATA: 12-16 claims across 4 drug classes. Choose values so the FPAR rates are "
        "DIFFERENT from the example (otherwise the user's correct query passes the example "
        "but might miss an edge in test). Include at least one realistic edge case from the "
        "rotation list (a NULL reject_code on a claim that was rejected then paid via recycle, "
        "OR a drug_class with all-paid behavior to test the 1.0000 boundary).\n\n"
        "BEFORE CLAIMING example_output_rows: count paid (NULL reject_code) and total per "
        "drug_class by hand. Confirm the math BEFORE writing the JSON. The most common failure "
        "mode is claiming 2 output rows when GROUP BY actually produces a different count.",
    "time_to_fill": "Build a time-to-fill aggregation problem. KEEP IT SIMPLE — this subtopic has historically "
        "failed because PERCENTILE_CONT does linear interpolation that's hard to hand-trace. Use "
        "the simplified shape below verbatim. The data sizes are chosen so percentiles land on "
        "EXACT row positions (no interpolation), making the expected output trivially verifiable.\n\n"
        "SCHEMA (use exactly this shape — single table with submit_ts and dispense_ts on the same row):\n"
        "  CREATE TABLE prescriptions (\n"
        "      rx_id INT PRIMARY KEY,\n"
        "      drug_class VARCHAR(50) NOT NULL,\n"
        "      submit_ts TIMESTAMP NOT NULL,\n"
        "      dispense_ts TIMESTAMP NOT NULL\n"
        "  );\n\n"
        "METRIC DEFINITIONS (use verbatim — no other variants):\n"
        "  time_to_fill_minutes = EXTRACT(EPOCH FROM (dispense_ts - submit_ts)) / 60.0\n"
        "  median_time_to_fill_minutes = PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY time_to_fill_minutes)\n"
        "  p75_time_to_fill_minutes = PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY time_to_fill_minutes)\n"
        "  mean_time_to_fill_minutes = AVG(time_to_fill_minutes)\n\n"
        "OUTPUT SHAPE: one row per drug_class with four columns:\n"
        "  drug_class, median_time_to_fill_minutes, p75_time_to_fill_minutes, mean_time_to_fill_minutes\n"
        "All time columns rounded to 2 decimal places. Order by drug_class ASC.\n\n"
        "EXAMPLE INPUT DATA (use exactly 10 prescriptions across 2 drug classes, 5 each — these "
        "exact gap minutes make PERCENTILE_CONT land on exact integers):\n"
        "  GLP-1 agonists, submit 08:00:00, gaps: 30, 60, 90, 120, 150 minutes\n"
        "  statins,        submit 08:00:00, gaps: 15, 30, 45, 60, 240 minutes (240 is the outlier)\n"
        "Concretely (rx_id, drug_class, submit_ts, dispense_ts):\n"
        "  1, GLP-1 agonists, 2025-01-15 08:00:00, 2025-01-15 08:30:00\n"
        "  2, GLP-1 agonists, 2025-01-15 08:00:00, 2025-01-15 09:00:00\n"
        "  3, GLP-1 agonists, 2025-01-15 08:00:00, 2025-01-15 09:30:00\n"
        "  4, GLP-1 agonists, 2025-01-15 08:00:00, 2025-01-15 10:00:00\n"
        "  5, GLP-1 agonists, 2025-01-15 08:00:00, 2025-01-15 10:30:00\n"
        "  6, statins,        2025-01-15 08:00:00, 2025-01-15 08:15:00\n"
        "  7, statins,        2025-01-15 08:00:00, 2025-01-15 08:30:00\n"
        "  8, statins,        2025-01-15 08:00:00, 2025-01-15 08:45:00\n"
        "  9, statins,        2025-01-15 08:00:00, 2025-01-15 09:00:00\n"
        "  10, statins,       2025-01-15 08:00:00, 2025-01-15 12:00:00\n\n"
        "EXPECTED OUTPUT (compute by hand and use as example_output_rows):\n"
        "PERCENTILE_CONT math reminder: with N=5 sorted values v0,v1,v2,v3,v4:\n"
        "  - p50 position = 0.5 * (5-1) = 2.0 → exactly v2 (3rd value, 1-indexed)\n"
        "  - p75 position = 0.75 * (5-1) = 3.0 → exactly v3 (4th value, 1-indexed)\n"
        "GLP-1 agonists sorted gaps: 30, 60, 90, 120, 150\n"
        "  median = 90, p75 = 120, mean = (30+60+90+120+150)/5 = 90\n"
        "statins sorted gaps: 15, 30, 45, 60, 240\n"
        "  median = 45, p75 = 60, mean = (15+30+45+60+240)/5 = 78\n"
        "Final example_output_rows (ordered by drug_class ASC):\n"
        "  GLP-1 agonists | 90.00 | 120.00 | 90.00\n"
        "  statins        | 45.00 |  60.00 | 78.00\n"
        "Notice the statins drug class shows median (45) MUCH lower than mean (78) — that's the "
        "outlier-skew lesson the recipe demonstrates.\n\n"
        "ANSWER KEY SHAPE (use this exact pattern):\n"
        "  WITH gaps AS (\n"
        "    SELECT\n"
        "      drug_class,\n"
        "      EXTRACT(EPOCH FROM (dispense_ts - submit_ts)) / 60.0 AS gap_minutes\n"
        "    FROM prescriptions\n"
        "  )\n"
        "  SELECT\n"
        "    drug_class,\n"
        "    ROUND(PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY gap_minutes)::numeric, 2) AS median_time_to_fill_minutes,\n"
        "    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY gap_minutes)::numeric, 2) AS p75_time_to_fill_minutes,\n"
        "    ROUND(AVG(gap_minutes)::numeric, 2) AS mean_time_to_fill_minutes\n"
        "  FROM gaps\n"
        "  GROUP BY drug_class\n"
        "  ORDER BY drug_class ASC;\n\n"
        "TEST DATA: 16 prescriptions across 4 drug classes, 4 prescriptions each. Use 4 values per "
        "class so percentiles still land on clean positions: with N=4, p50 = position 1.5 "
        "(interpolate between v1 and v2), p75 = position 2.25 (interpolate between v2 and v3 — "
        "still tractable). Pick gap minutes that produce easy interpolation results (e.g., 30, 60, "
        "90, 120 → p50 = 75, p75 = 97.5). Include at least one drug class with an outlier so the "
        "median-vs-mean gap is visible.\n\n"
        "BEFORE CLAIMING example_output_rows: sort each drug class's gap_minutes by hand, then for "
        "each percentile compute the position formula `p * (N-1)` and pick the value at that index. "
        "If position is an integer, the value is exact. If position is fractional, interpolate "
        "between the two surrounding values. Only after writing down the trace, fill in the JSON.\n\n"
        "DO NOT use multi-dimension grouping (drug_class AND payer). DO NOT add HAVING filters. "
        "DO NOT use 4 or 6 values per class in the example data — stick with 5 so percentiles "
        "land cleanly. Test data may use 4.",
    "net_acceptance_rate": "Build a Net Acceptance Rate problem. This is the financially-honest version of "
        "First Pass Acceptance Rate — it accounts for reversed (B2) claims that were paid "
        "but later voided.\n\n"
        "METRIC DEFINITION (industry standard, use verbatim):\n"
        "  Net Acceptance Rate = (count of distinct claims with a paid event - count of "
        "distinct claims with a reversed event) / count of distinct submitted claims\n"
        "Computed at the CLAIM level, not the event level. A claim that was paid then "
        "reversed has BOTH a paid event and a reversed event in the log; it should net to 0 "
        "in the numerator.\n\n"
        "SCHEMA: claim_events table with claim_id, event_type "
        "('submitted', 'paid', 'reversed', plus other types in the data), event_ts, "
        "optionally payer_id or drug_class for segmentation.\n\n"
        "PROMPT MUST EXPLICITLY:\n"
        "  - Define Net Acceptance Rate by formula and note the difference vs FPAR\n"
        "  - Tell the user to compute at the claim level (distinct claim_ids with each event)\n"
        "  - Specify segmentation if any (by payer or drug_class is common; pick one)\n\n"
        "ANSWER SHAPE: a single CTE per event type counting distinct claims, then a final "
        "SELECT computing (paid_count - reversed_count)::numeric / submitted_count, ROUND to "
        "4 decimals, with optional GROUP BY for the segmentation dim.\n\n"
        "DATA REQUIREMENTS: example_input_data MUST include at least one claim that was "
        "paid AND later reversed (so the user's WHERE / DISTINCT logic is exercised). "
        "test_data MUST include the same edge case AND at least one claim with two reversal "
        "events (to confirm DISTINCT claim_id is correct, not a raw event count).\n\n"
        "BUSINESS CONTEXT FOR GLOSSARY/CALC: Net Acceptance Rate is the metric Finance uses "
        "for revenue forecasting. FPAR overstates revenue when reversals are common (e.g., "
        "patients who don't pick up specialty drugs). Industry benchmarks: retail 90-95%, "
        "specialty 80-90%.",
    "reversal_rate": "Build a Reversal Rate analysis problem. Reversals are the operational signal that "
        "something went wrong AFTER a paid claim — the patient didn't pick up, the script "
        "was returned to stock, the prescriber canceled, or there was a billing correction.\n\n"
        "METRIC DEFINITION (industry standard, use verbatim):\n"
        "  Reversal Rate = count of distinct claims with a reversed event / count of "
        "distinct claims with a paid event\n"
        "Optionally segmented by reversal_reason (most pharmacy systems capture a reason "
        "code on the reversal — common values: 'patient_no_show', 'returned_to_stock', "
        "'prescriber_cancellation', 'billing_correction', 'duplicate_fill').\n\n"
        "SCHEMA: claim_events with claim_id, event_type, event_ts, AND a reversal_reason "
        "VARCHAR column that is NULL for non-reversal events and a real value on reversal "
        "events. (Schema uses NOT NULL only on claim_id and event_type.)\n\n"
        "PROMPT MUST EXPLICITLY:\n"
        "  - Define Reversal Rate by formula\n"
        "  - Ask for the rate either overall OR broken out by reversal_reason (pick one)\n"
        "  - State the standard reversal reasons in the prompt so the user knows the domain\n"
        "  - Specify the date window if any (e.g., 'reversals occurring within 30 days of "
        "the paid event' is a common operational restriction; or 'all reversals' is fine "
        "for the simpler version)\n\n"
        "ANSWER SHAPE: distinct count of paid claims as the denominator, distinct count of "
        "reversed claims (optionally GROUP BY reason) as the numerator, ROUND to 4 decimals.\n\n"
        "DATA REQUIREMENTS: example_input_data MUST include at least one paid-but-not-"
        "reversed claim (so denominator > numerator) and reversed claims spanning at least "
        "two different reversal_reason values.\n\n"
        "BUSINESS CONTEXT: Industry benchmarks for retail pharmacy reversal rate: 5-12%. "
        "Patient no-show is typically the largest category (40-60% of reversals). Specialty "
        "pharmacy reversal rates can exceed 15% due to high-cost drugs and PA churn. "
        "A reversal rate climbing above benchmark is an early warning of fulfillment, "
        "engagement, or formulary issues.",
    "adherence_pdc": "Build a patient adherence problem using PDC (Proportion of Days Covered), the "
        "industry-standard adherence measure used by CMS for Medicare Star Ratings.\n\n"
        "METRIC DEFINITION (CMS standard, use verbatim):\n"
        "  PDC for a patient and a drug_class over a measurement period =\n"
        "    (count of unique days within the measurement period that the patient had "
        "medication on hand) / (length of the measurement period in days)\n"
        "Capped at 1.0 (a patient cannot be more than 100% covered).\n"
        "Adherent threshold: PDC >= 0.80 (CMS Star Ratings cutoff).\n\n"
        "SIMPLIFICATION FOR SQL DRILL: instead of computing day-by-day coverage with "
        "overlapping fills (which requires a calendar table or generate_series), use the "
        "MPR-style approximation that is acceptable for most SQL drills:\n"
        "  PDC ≈ LEAST(SUM(days_supply) / measurement_period_days, 1.0)\n"
        "Where measurement_period_days is fixed in the prompt (e.g., 365 days for an "
        "annual PDC).\n\n"
        "SCHEMA: prescriptions with rx_id, patient_id, drug_class, fill_date, days_supply.\n\n"
        "PROMPT MUST EXPLICITLY:\n"
        "  - Define PDC by formula\n"
        "  - State the measurement_period_days value (use 365 for an annual measure, 90 for "
        "a quarterly measure)\n"
        "  - State the drug_class scope (compute PDC per patient per drug_class, OR for one "
        "specific drug_class — pick one)\n"
        "  - Mention the 0.80 adherent threshold and ask the user to also produce an "
        "adherent_flag column (1 if PDC >= 0.80, else 0)\n\n"
        "OUTPUT SHAPE: one row per (patient_id, drug_class) with columns:\n"
        "  patient_id, drug_class, total_days_supply, pdc, adherent_flag\n"
        "PDC rounded to 4 decimals.\n\n"
        "ANSWER SHAPE: a single GROUP BY on patient_id and drug_class summing days_supply, "
        "with LEAST(SUM(days_supply)::numeric / 365, 1.0) for PDC, and a CASE for "
        "adherent_flag.\n\n"
        "DATA REQUIREMENTS: example_input_data MUST include at least one patient who is "
        "adherent (PDC >= 0.80) and at least one who is not. test_data MUST also include a "
        "patient with sum(days_supply) > measurement_period (to exercise the LEAST cap) per "
        "the EDGE CASE REQUIREMENT.\n\n"
        "BUSINESS CONTEXT FOR GLOSSARY/CALC: PDC is the metric CMS uses for Medicare Part D "
        "Star Ratings. Plans are scored on the share of members who hit PDC >= 0.80 for "
        "diabetes medications, statins, RAS antagonists. High PDC predicts lower hospital "
        "admissions and lower total cost of care. Pharmacy operations teams use PDC to "
        "trigger adherence outreach (refill reminders, transfer to 90-day supply, "
        "synchronization).",
}


# ---- Pharmacy SQL generator system prompt ----

PHARMACY_SQL_GENERATOR_SYSTEM = GENERATOR_SYSTEM + """

ADDITIONAL CONTEXT FOR THIS DRILL:
- The learner is preparing for a Staff Product Analyst interview in the pharmacy /
  digital health space (digital pharmacy operations, at-home diagnostics, telehealth,
  care coordination).
- DO NOT use any specific company names in prompts, scenarios, glossaries, or examples.
  Use generic descriptors like "a digital pharmacy", "a B2B pharmacy API platform",
  "an at-home diagnostic service", "a telehealth platform", etc. NEVER mention real
  pharmacy or healthcare company names (no Fuze Health, FuzeRx, Truepill, Alto,
  LetsGetChecked, CVS, Walgreens, Express Scripts, OptumRx, etc).
- Use realistic pharmacy / care / diagnostics / telehealth domain terminology in the
  table names, column names, and prompt wording.
- Realistic fact table names: claims, claim_events, prescriptions, fills,
  test_kit_orders, telehealth_visits, patient_outreach, deliveries.
- Realistic dim names: dim_drug, dim_payer, dim_patient, dim_pharmacy, dim_prescriber,
  dim_test_kit_type, dim_geography.
- Use real NCPDP-style reject category language WITHOUT claiming exact NCPDP fidelity:
  'PA required', 'formulary not covered', 'refill too soon', 'days supply exceeded',
  'DUR reject', 'COB stale', 'NDC not covered', 'plan limitations exceeded'.
- Drug class examples: GLP-1 agonists, oral contraceptives, statins, fertility meds
  (gonadotropins, progesterone), HIV PrEP, mental health (SSRI), oncology infusion.
- Patient outcome columns: time_to_fill, days_supply, abandoned_flag, refill_at_30d.
- Do NOT use generic e-commerce, ride-share, or social media scenarios.

INSERT FORMAT REQUIREMENT (HARD RULE):
- Every INSERT statement in example_input_data and test_data MUST include the explicit
  column list:  INSERT INTO <table> (col1, col2, col3) VALUES (...);
- Do NOT emit `INSERT INTO <table> VALUES (...)` without the column list. The notebook
  renderer requires the column list to display the data as an HTML table.

INSERT TUPLE LENGTH CONSISTENCY (HARD RULE):
- Every row tuple in a multi-row VALUES clause MUST have EXACTLY the same number of
  values as the column list and as every other row tuple. Postgres rejects with
  "VALUES lists must all be the same length" if any row tuple length differs.
- Before emitting the INSERT, count the columns in the column list and confirm every
  parenthesized row tuple has that exact count.
- Example of the failure mode to AVOID:
    INSERT INTO claims (claim_id, rx_number, patient_id, drug_class)
    VALUES ('C001', 'RX1', 'P1', 'GLP-1'),
           ('C002', 'RX2', 'P2'),                           -- WRONG: only 3 values
           ('C003', 'RX3', 'P3', 'statins', 'extra');       -- WRONG: 5 values

SCHEMA-DATA CONSISTENCY (HARD RULE):
- If a column is declared NOT NULL in CREATE TABLE, NEVER INSERT NULL into that column
  in example_input_data or test_data. The script will fail to load and the problem is
  unsolvable.
- If a column is declared as PRIMARY KEY, all values for that column across all INSERT
  statements MUST be unique and non-NULL.
- If a foreign key is declared, every value inserted into the child column MUST exist
  in the parent table FIRST (load parent rows before child rows in the script).
- If a CHECK constraint is declared, every inserted value must satisfy it.
- If the problem requires NULLs in the data (NULL handling drills, missing data drills),
  the relevant column MUST be declared as nullable in the schema (omit NOT NULL).
  Do not declare NOT NULL and then "demonstrate" NULL handling — that crashes the loader.
- Always load tables in dependency order: parent dims first, then facts that reference them.

ADDITIONAL JSON FIELDS REQUIRED FOR THIS NOTEBOOK:
The standard schema from the parent system prompt still applies, but you MUST also include
these two additional top-level keys in the JSON object:

  "glossary": [
    {"term": "adjudication", "definition": "the real-time decision the PBM makes on whether to pay a submitted prescription claim and how much"},
    {"term": "recycle", "definition": "resubmitting a previously rejected claim after fixing the issue (e.g., adding a prior authorization)"},
    {"term": "submitted (event)", "definition": "the moment the pharmacy first transmits the claim to the PBM"},
    {"term": "<other domain or method term used in the prompt>", "definition": "<one-sentence lay explanation>"}
  ],

  "calculation_explanation": "A 3-6 step plain-language walkthrough of HOW to compute the answer. FORMAT REQUIREMENT: each step MUST be on its own line, prefixed with a number followed by a period and a space ('1. ', '2. ', etc), with a literal newline between steps. Do NOT put all steps on one line — that breaks the renderer. Avoid SQL syntax. Do NOT give away the exact code, but DO explain the conceptual approach. Correct format example (newlines shown literally):\n  1. For each claim, find the first time each event type happened.\n  2. Count how many distinct claims have at least one event of each type.\n  3. For each stage after the first, divide its count by the prior stage's count to get the conversion rate.\n  4. Order the output by funnel stage sequence.",

  "interpretation_example": "A model interpretation of the example_output_rows for THIS specific problem. 3-5 bullets. SAME FORMAT REQUIREMENT as calculation_explanation: one bullet per line, each prefixed with '- ' and a literal newline between bullets. Each bullet should: (a) read the actual numbers literally first, (b) interpret what the numbers suggest about underlying business behavior, (c) where relevant, compare to industry benchmarks (FPAR 75-85% retail, refill rate 30d 60-80% chronic, abandonment 8-15%, etc), (d) flag ambiguities or concerns. Do NOT use vague phrases like 'this suggests opportunity'. Be specific. Example for an adjudication funnel where output shows submitted=10, paid=6:\n  - 60% of claims paid (6 of 10) — below the 75-85% retail FPAR benchmark, suggesting a process gap.\n  - 30% of claims rejected (3 of 10) and only 67% recycled, leaving 1 unrecovered rejection.\n  - The recycle success rate of 67% is plausible if PA-required is the dominant reject reason; lower if it's refill-too-soon.\n  - The drop from rejected (3) to paid-after-recycle (2) is the operational opportunity to size next.",

  "recommendation_example": "A model recommendation grounded in pharmacy industry standard practice. 3-5 bullets. SAME FORMAT REQUIREMENT: one bullet per line, each prefixed with '- ' and a literal newline between bullets. Each bullet should: (a) start with an action verb (Trigger, Investigate, Implement, Add, Review), (b) name the OWNING stakeholder (Pharmacy Ops, Care Coordination, Finance, Quality team, Product, Engineering), (c) reference an industry-standard practice or framework (PA team triage, medication synchronization, 90-day supply transfer, adherence outreach trigger, Star Ratings, PDC threshold, refill cliff intervention), (d) include at least one 'what to monitor next' item with a concrete metric and direction. Do NOT recommend generic things like 'investigate further' or 'iterate'. Example:\n  - Trigger PA-team triage (Pharmacy Ops): the 1 unrecovered rejection per 10 submits implies meaningful daily volume — route PA-required rejects to a dedicated team within 1 hour of reject.\n  - Implement automated formulary substitution (Engineering + Care): for formulary-not-covered rejects, propose covered alternatives at point of fill; benchmark for retail is 50-70% acceptance.\n  - Re-baseline FPAR for this product line (Finance + Product): the 60% rate may be acceptable for specialty but is a red flag for retail; segment the dashboard accordingly.\n  - Monitor weekly: track FPAR trend by reject reason and watch for the 30-day rolling average crossing 75% (the lower retail benchmark)."

Glossary rules:
- Include 4 to 8 glossary entries.
- Cover: any industry term (e.g., adjudication, formulary, prior auth, NADAC, PBM,
  refill too soon, time to fill, abandonment), each distinct event_type value used in
  the data (submitted, rejected, recycled, paid, dispensed, reversed, delivered),
  any analytical method term (e.g., funnel conversion, cohort retention, window
  function, Kaplan-Meier, percentile_cont, SCD Type 2), and any segmentation
  dimension worth knowing (e.g., drug class, payer, channel).
- Definitions must be ONE sentence each, in plain English a non-pharmacy reader can follow.
- Do NOT define generic SQL keywords (SELECT, JOIN, GROUP BY).

Calculation explanation rules:
- 3 to 6 numbered steps.
- Conceptual, not syntactic.
- Should help a learner who knows SQL but does not yet know the domain decide on the right
  shape (CTE, window, GROUP BY, etc.).
- Do NOT include the literal SQL — that is what answer_key is for.

============================================================
TERMINOLOGY ACCURACY MANDATE — HARD RULE FOR ALL CATEGORIES
============================================================

All metric names, technical terms, schema names, reject codes, drug names, and benchmark
numbers used anywhere in the problem MUST reflect ACTUAL industry practice. DO NOT invent
or paraphrase standard terminology. DO NOT hallucinate concepts, frameworks, or numbers.

If you are unsure whether a term, code, or benchmark is real, DO NOT use it. Substitute
something from the approved lists below or omit the detail entirely.

----- PHARMACY ADJUDICATION METRIC NAMES -----
Use these names verbatim in prompts when the problem computes them. Do NOT invent
synonyms like "claim acceptance percentage" or "successful adjudication ratio".
- First Pass Acceptance Rate (FPAR) = paid_on_first_submit / total_submitted
- Net Acceptance Rate = (total_paid - total_reversed) / total_submitted
- Recycle Success Rate = paid_after_recycle / total_recycled
- Abandonment Rate = scripts_never_dispensed_within_N_days / total_submitted
- Manual Touch Rate = manual_interventions per 1000 scripts
- Time to Fill = minutes from submit to dispense (use MEDIAN, not AVG, for skewed data)
- Time to PA Approval = minutes/hours from PA-required reject to next paid event
- Days Supply on Hand = patient adherence proxy (PDC > 80% is the standard adherence cutoff)

----- NCPDP TRANSACTION CODES (the source-of-truth field shape) -----
Colloquial event_type names are fine in the data, but the GLOSSARY field MUST mention the
NCPDP code mapping so the learner sees the source-of-truth. Do NOT invent codes.
- B1 = billing / first submit
- B2 = reversal of paid claim
- B3 = rebill / recycle of rejected claim

----- NCPDP REJECT CODES (only these, with these names) -----
Use the format `'<code> - <official name>'` when populating reject_code values:
- 70 - Product/Service Not Covered
- 75 - Prior Authorization Required
- 76 - Plan Limitations Exceeded
- 79 - Refill Too Soon
- 88 - DUR Reject (Drug Utilization Review — interaction, duplicate therapy, dose limits)
- M/I family - Missing/Invalid data field (e.g., M/I Days Supply, M/I Quantity Dispensed)
- 65 - Patient Not Covered
- 41 - Submit Bill To Other Processor (COB / coordination of benefits)
DO NOT invent reject codes outside this list.

----- REALISTIC BENCHMARKS (when prompts mention current or target metric values) -----
Use ranges in this list. Do NOT invent benchmarks like "lift FPAR from 30% to 50%".
- Retail/digital pharmacy FPAR: 75 to 85%
- Specialty pharmacy FPAR: 60 to 75% (more PA)
- Net Acceptance Rate retail: 90 to 95%
- Recycle Success Rate by category: PA-required 60-80% (with PA team), formulary
  substitution 50-70%, refill-too-soon ~5% (most can't be recycled, they wait)
- Abandonment rate retail: 8 to 15%; specialty 15 to 30%
- Adjudication response time: under 2 seconds end-to-end
- Time to fill at-counter retail: 15 to 60 min; same-day delivery: 1 to 24 hours
- Manual touch rate: typical 30 to 100 per 1000 scripts depending on PA volume

----- DRUG CLASSES (real names only) -----
GLP-1 agonists, oral contraceptives, statins, fertility medications (gonadotropins,
progesterone, leuprolide), HIV PrEP, SSRIs, SNRIs, oncology infusion, biologics,
ADHD stimulants, anticoagulants (DOACs, warfarin), insulin, diabetes orals (metformin,
SGLT2 inhibitors), respiratory inhalers (ICS, LABA, SABA), opioids, ADHD non-stimulants.
DO NOT invent drug class names.

----- DBT AND MODELING VOCABULARY (only these, only with these meanings) -----
- sources, staging (stg_), intermediate (int_), marts
- materializations: table, view, incremental, ephemeral
- SCD Type 2 fields: valid_from, valid_to, is_current
- star schema terminology: fact tables (one row per business event), dimension tables,
  surrogate keys, natural keys, conformed dimensions, junk dimensions
- dbt features: ref(), source(), tests (unique, not_null, accepted_values, relationships),
  exposures, snapshots, seeds
DO NOT invent dbt project structure, materialization options, or test types.

----- TABLE AND COLUMN NAMING CONVENTIONS -----
Use snake_case for all table and column names. Use these realistic shapes:
- Fact tables: claims, claim_events, prescriptions, fills, dispenses, deliveries,
  test_kit_orders, telehealth_visits, patient_outreach
- Dim tables: dim_drug, dim_payer, dim_pharmacy, dim_prescriber, dim_patient,
  dim_geography, dim_test_kit_type, dim_diagnosis
- Standard column names: claim_id, rx_number, patient_id, prescriber_id, payer_id,
  ndc (National Drug Code, 11-digit), drug_class, days_supply, quantity_dispensed,
  fill_date, submit_ts, dispense_ts, reject_code, paid_amount, ingredient_cost,
  dispensing_fee, copay, valid_from, valid_to, is_current

============================================================
EDGE CASE REQUIREMENT FOR test_data — HARD RULE
============================================================

Every test_data MUST include AT LEAST ONE realistic edge case. Pick the one that fits
the problem; if none fits, the problem may not be a good drill. Rotate across problems
so the learner sees all of them eventually:
- A REVERSAL: an event_type='reversed' (B2) record after a 'paid' event for the same claim
- A PARTIAL APPROVAL: a claim with both 'paid' and 'rejected' events on the same submit_ts
  (paid for some days_supply, rejected for the rest)
- A MULTI-CLAIM PRESCRIPTION: two claim_ids that share the same rx_number (rebill with
  new claim_id, OR a partial-fill split)
- A LATE-ARRIVING EVENT: an event_ts after the analytical cutoff date in the prompt
- A NULL-BEARING FIELD: a NULL in a column the answer_key must explicitly handle
- A DUPLICATE FIRST EVENT: same claim_id with two 'submitted' events at different ts
  (so first-occurrence logic must be exercised)

The answer_key MUST produce correct test_expected_rows DESPITE this edge case. If the
answer_key produces wrong output on the edge case, the answer_key is buggy and the
problem fails validation — fix the answer_key, do not weaken the test_data.

============================================================
ANTI-HALLUCINATION RULE FOR ALL DOMAIN CONTENT
============================================================

If you find yourself generating any of these, STOP and substitute from the approved lists:
- A metric name not on the metric list above
- A reject code number or name not on the reject code list above
- A drug class not on the drug class list above
- A benchmark number outside the benchmark ranges above
- A dbt vocabulary term not on the dbt list above
- An NCPDP transaction code not in (B1, B2, B3) — there are others (S1, P1, etc.) but
  use only the three above unless you can name the real code's purpose
- A "framework" or "methodology" name (e.g., "the McKinsey adjudication framework",
  "the AHA pharmacy operations standard") — these are usually not real

When in doubt, use plainer descriptive language instead of inventing branded terminology.
"""


# ---- Pharmacy category helper accessors ----

def pharmacy_category_keys() -> List[str]:
    return list(PHARMACY_CATEGORIES.keys())


def pharmacy_subtopic_keys(category: str) -> List[str]:
    return list(PHARMACY_CATEGORIES[category]["subtopics"].keys())


def pharmacy_subtopic_label(category: str, subtopic: str) -> str:
    return PHARMACY_CATEGORIES[category]["subtopics"][subtopic]["label"]


def pharmacy_base_qtype(category: str, subtopic: str) -> Optional[str]:
    return PHARMACY_CATEGORIES[category]["subtopics"][subtopic].get("base_qtype")


# ---- Pharmacy SQL drill generator ----

def _build_pharmacy_user_prompt(category: str, subtopic: str, dialect: str,
                                scenario: str, last_error: Optional[str] = None) -> str:
    """Compose the per attempt user prompt for a pharmacy SQL drill."""
    base_qt = pharmacy_base_qtype(category, subtopic)
    guidance = _topic_specific_guidance(base_qt, dialect, scenario=scenario)
    guidance += "\n\n--- SUBTOPIC FRAMING (this is the most important guidance) ---\n"
    guidance += PHARMACY_SUBTOPIC_GUIDANCE.get(subtopic, "")
    guidance += (
        f"\n\nLearner is drilling: {PHARMACY_CATEGORIES[category]['label']} -> "
        f"{pharmacy_subtopic_label(category, subtopic)}\n"
    )
    if last_error:
        guidance += (
            "\n\n!!! PREVIOUS ATTEMPT FAILED VALIDATION !!!\n"
            f"{last_error}\n\n"
            "MANDATORY FIX PROTOCOL read carefully:\n\n"
            "If the failure is 'Could not parse JSON from response.':\n"
            "  - Emit ONE single ```json fenced block. NO prose before, NO prose after, NO "
            "second code block. First non whitespace must be `{`, last must be `}`.\n"
            "  - Tighten the response to fit within 4000 tokens: cap CREATE TABLE at 2 tables, "
            "cap example_input_data at 8 rows, cap test_data at 18 rows, keep glossary at 4 "
            "entries, keep calculation_explanation at 3 to 4 steps.\n"
            '  - Inside JSON strings escape internal double quotes as \\" and use literal '
            "\\n for newlines.\n\n"
            "If the failure is a SCHEMA CONSTRAINT VIOLATION (NOT NULL, PRIMARY KEY, FOREIGN "
            "KEY, CHECK):\n"
            "  - Either remove the constraint from CREATE TABLE, OR fix the data so every "
            "inserted row satisfies the constraint.\n"
            "  - Load parent dim tables BEFORE child fact tables in the script.\n\n"
            "If the failure is 'LLM claimed example_output_rows differ from actual':\n"
            "  - Your answer_key SQL produced one result and your claimed example_output_rows "
            "showed another. They MUST agree. Either copy the validator's actual values into "
            "example_output_rows, OR rewrite the answer_key SQL until it produces the claimed "
            "values. Do NOT change both sides.\n\n"
            "BEFORE EMITTING THE NEW JSON: walk through example_input_data row by row in your "
            "head applying the answer_key's logic step by step. Confirm the trace produces "
            "example_output_rows EXACTLY.\n"
        )
    guidance += "\n\nReturn the JSON object now."
    return guidance


def _canonical_pharmacy_value(v) -> str:
    """Normalize a cell value for tolerant comparison between LLM claim and DB output."""
    import decimal
    if v is None:
        return "NULL"
    if isinstance(v, str):
        s = v.strip()
        if s in ("", "None", "NULL", "null", "<NA>", "nan", "NaN"):
            return "NULL"
        try:
            f = float(s)
            if f.is_integer():
                return str(int(f))
            return f"{f:.6g}"
        except (ValueError, TypeError):
            return s
    if isinstance(v, (int, float, decimal.Decimal)):
        try:
            f = float(v)
            if f.is_integer():
                return str(int(f))
            return f"{f:.6g}"
        except Exception:
            return str(v)
    return str(v)


def _validate_pharmacy_problem_strict(parsed: Dict[str, Any]) -> Tuple[bool, str]:
    """Strict validator. Runs the standard sql_practice_utils validation, then also
    verifies the LLM's CLAIMED example_output matches what the answer_key actually
    produces. If they differ, the LLM did not trace its own answer carefully and
    the user would be graded against silently wrong expected output."""
    claimed_cols = list(parsed.get("example_output_columns") or [])
    claimed_rows = [list(r) if isinstance(r, list) else [r]
                    for r in (parsed.get("example_output_rows") or [])]
    ok, err = _validate_problem(parsed)
    if not ok:
        return False, err
    actual_cols = list(parsed.get("example_output_columns") or [])
    actual_rows = parsed.get("example_output_rows") or []
    if not claimed_cols and not claimed_rows:
        return True, "Valid (no LLM claim to verify; accepted DB derived output)."
    if claimed_cols and claimed_cols != actual_cols:
        return False, (
            f"LLM claimed example_output_columns disagree with answer_key actual output.\n"
            f"  Claimed: {claimed_cols}\n  Actual:  {actual_cols}\n"
            f"Re trace the answer_key against example_input_data and align the claimed columns."
        )
    if len(claimed_rows) != len(actual_rows):
        return False, (
            f"LLM claimed {len(claimed_rows)} example output rows but the answer_key actually "
            f"produces {len(actual_rows)}. Re trace the answer_key row by row against the "
            f"example_input_data."
        )
    mismatches = []
    for i, (cr, ar) in enumerate(zip(claimed_rows, actual_rows)):
        if len(cr) != len(ar):
            mismatches.append(f"row {i}: claimed {len(cr)} cells, actual {len(ar)} cells")
            continue
        for j, (cv, av) in enumerate(zip(cr, ar)):
            if _canonical_pharmacy_value(cv) != _canonical_pharmacy_value(av):
                col_label = actual_cols[j] if j < len(actual_cols) else f"col{j}"
                mismatches.append(
                    f"row {i} col '{col_label}': claimed {cv!r}, actual {av!r}"
                )
    if mismatches:
        head = mismatches[:6]
        more = len(mismatches) - len(head)
        msg = (
            "LLM claimed example_output_rows differ from what the answer_key actually "
            "produces. Specific mismatches:\n"
        )
        msg += "\n".join(f"  - {m}" for m in head)
        if more > 0:
            msg += f"\n  ... and {more} more cell mismatches"
        msg += (
            "\nRe trace the answer_key against example_input_data row by row. Either fix the "
            "answer_key or fix the claimed example_output_rows so they agree."
        )
        return False, msg
    return True, "Valid (claimed and actual outputs match)."


def generate_pharmacy_problem(category: str, subtopic: str, dialect: str = "postgresql",
                              max_retries: int = 6, on_attempt=None) -> Optional[Dict[str, Any]]:
    """Generate a pharmacy SQL drill problem and validate it via the sandbox harness."""
    scenario = _pick_pharmacy_scenario()
    base_qt = pharmacy_base_qtype(category, subtopic)
    last_error = None
    for attempt in range(1, max_retries + 1):
        if on_attempt:
            try:
                on_attempt(attempt, max_retries, last_error)
            except Exception:
                pass
        user_prompt = _build_pharmacy_user_prompt(category, subtopic, dialect, scenario, last_error)
        text = _call_claude(PHARMACY_SQL_GENERATOR_SYSTEM, user_prompt, max_tokens=4000)
        parsed = _extract_json(text)
        if not parsed:
            last_error = "Could not parse JSON from response."
            continue
        parsed["_meta"] = {
            "category": category,
            "subtopic": subtopic,
            "kind": "sql",
            "question_type": base_qt,
            "dialect": dialect,
            "scenario": scenario,
            "generated_at": datetime.now().isoformat(),
            "problem_id": uuid.uuid4().hex[:12],
            "validation_attempts": attempt,
            "notebook": "nb01_sql_practice",
        }
        ok, err = _validate_pharmacy_problem_strict(parsed)
        if ok:
            return parsed
        last_error = err
    print(f"Pharmacy generation failed validation after {max_retries} attempts. Last error: {last_error}")
    return None

