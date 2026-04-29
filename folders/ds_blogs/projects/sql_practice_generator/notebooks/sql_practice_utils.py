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
}


RECIPE_VOCAB = [
    "row-filter", "group-aggregate", "scalar-extract", "rank-partition",
    "row-transform", "row-compare", "time-window", "normalize-bidirectional",
    "delete-duplicates", "enrich-join", "enrich-aggregate", "reshape",
    "function-wrapped", "do-block-sequential",
]


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
"""


def _topic_specific_guidance(qtype: str, dialect: str, scenario: str = None, dml_op: str = None) -> str:
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
            "The user must write a `DO $$ DECLARE ... BEGIN ... END $$;` block "
            "that mutates one of the tables, followed by a trailing "
            "`SELECT * FROM target ORDER BY ...;` so the test harness sees output. "
            "answer_key must include both the DO block and the trailing SELECT."
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
            "shape — add a state-dependent guard that requires reading the row's current value.\n"
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
            "RETURNS TABLE column shadowing."
        )
    elif qtype == "returns_scalar":
        base += (
            "Function returns a scalar (e.g., INT, NUMERIC). Use `RETURN ( ... );` not `RETURN QUERY`. "
            "The answer_key calls the function via `SELECT fn_name(args) AS result;`."
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
                "toggles) so the CASE branches do meaningful work."
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
    for attempt in range(1, max_retries + 1):
        if on_attempt:
            try:
                on_attempt(attempt, max_retries, last_error)
            except Exception:
                pass

        user_prompt = _topic_specific_guidance(qtype, dialect, scenario=scenario, dml_op=dml_op)
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
