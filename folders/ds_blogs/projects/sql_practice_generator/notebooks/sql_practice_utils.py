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


def _topic_specific_guidance(qtype: str, dialect: str, scenario: str = None) -> str:
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
    elif qtype == "returns_table":
        base += (
            "The schema_ddl should END with a `CREATE OR REPLACE FUNCTION fn_name(...) "
            "RETURNS TABLE (...) AS $$ BEGIN RETURN QUERY ( /* placeholder */ ); END; "
            "$$ LANGUAGE plpgsql;` scaffold so the user fills in the inner SELECT. "
            "test_data invokes the function with concrete arguments via a final "
            "`SELECT * FROM fn_name(arg1, arg2);` in the answer_key."
        )
    elif qtype == "returns_scalar":
        base += (
            "Function returns a scalar (e.g., INT, NUMERIC). Use `RETURN ( ... );` not `RETURN QUERY`. "
            "The answer_key calls the function via `SELECT fn_name(args) AS result;`."
        )
    elif qtype == "recursive_cte":
        base += "The answer_key must use `WITH RECURSIVE`."
    elif qtype == "dml":
        base += (
            "Answer_key must include the UPDATE/DELETE/INSERT statement(s) followed by "
            "a `SELECT * FROM target ORDER BY ...;` that produces test_expected_rows."
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
    for attempt in range(1, max_retries + 1):
        if on_attempt:
            try:
                on_attempt(attempt, max_retries, last_error)
            except Exception:
                pass

        user_prompt = _topic_specific_guidance(qtype, dialect, scenario=scenario)
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
