"""Build nb02_fuze_interview_drills.ipynb by emitting JSON cells.

Lives at build/build_nb02.py inside the sql_practice_generator project folder
(committed alongside the notebook so the source survives Cowork session boundaries).

All Python source for cells is held in triple-single-quoted strings
so we can use triple-double-quotes freely inside (for JS/CSS blocks).
"""
import json
import os

CELLS = []

# Code-toggle button HTML — rendered at the top of each code cell. Auto-hides
# the cell's input area on first render; clicking the button toggles it. Works
# in both JupyterLab (.jp-Cell / .jp-Cell-inputWrapper) and classic Notebook
# (.cell / .input). The button text reflects current state (▲ Hide / ▼ Show).
_TOGGLE_BTN_HTML = (
    '<button class="cw-code-toggle" '
    'onclick="(function(btn){'
    "var cell = btn.closest('.jp-Cell, .cell');"
    "if (!cell) return;"
    "var input = cell.querySelector('.jp-Cell-inputWrapper, .input');"
    "if (!input) return;"
    "var hidden = input.style.display === 'none';"
    "input.style.display = hidden ? '' : 'none';"
    "btn.textContent = hidden ? '\\u25B2 Hide code' : '\\u25BC Show code';"
    '})(this); return false;" '
    'style="background:#0969da; color:white; padding:5px 12px; '
    'border:none; border-radius:4px; cursor:pointer; font-size:12px; '
    'margin-bottom:8px;">▲ Hide code</button>'
    '<script>(function(){'
    "var s = document.currentScript;"
    "if (!s) return;"
    "setTimeout(function(){"
    "var cell = s.closest('.jp-Cell, .cell');"
    "if (!cell) return;"
    "var input = cell.querySelector('.jp-Cell-inputWrapper, .input');"
    "if (!input) return;"
    "input.style.display = 'none';"
    "var btn = cell.querySelector('.cw-code-toggle');"
    "if (btn) btn.textContent = '\\u25BC Show code';"
    "}, 80);"
    '})();</script>'
)


def _toggle_prefix() -> str:
    """Return Python source that, when executed in a cell, displays the code-
    toggle button. Uses repr() so all escaping is automatic — the HTML string
    becomes a single Python literal."""
    return (
        "from IPython.display import HTML as _HTML_toggle, display as _display_toggle\n"
        f"_display_toggle(_HTML_toggle({_TOGGLE_BTN_HTML!r}))\n\n"
    )


def md(src):
    CELLS.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": src.splitlines(keepends=True),
    })


def code(src, hidden=False, with_toggle=True):
    """Append a code cell. When `with_toggle=True` (default), prepends a
    code-toggle button that auto-hides the cell's input on render and lets
    the user toggle it on demand. When `hidden=True`, ALSO sets the cell
    metadata `jupyter.source_hidden=true` as a redundant fallback for
    environments that honor it (some JupyterLab versions, Notebook 7+)."""
    if with_toggle:
        src = _toggle_prefix() + src
    metadata = {}
    if hidden:
        metadata["jupyter"] = {"source_hidden": True}
        metadata["collapsed"] = True
    CELLS.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": metadata,
        "outputs": [],
        "source": src.splitlines(keepends=True),
    })


# ============================================================
# Cell 0 — Intro
# ============================================================
md('''# Analyst Interview Drills (nb02)

Claude-powered drill notebook for analyst interview prep. Pick a category, generate a problem grounded in that category's subtopic, then submit your answer for grading.

The pharmacy claims analytical SQL category lives in `nb01_sql_practice.ipynb` now; this notebook focuses on the broader analyst interview surface area.

**Four categories with nested subtopics:**

1. Data Transformation Modeling — schema design (KPI form, the centerpiece), dimensional modeling (build fact + dim hands-on), SCD Type 2 (history maintenance hands-on), dbt tests + macros (YAML/Jinja syntax)
2. Critical Reasoning SQL — ambiguous metrics, missing data, edge cases, clarify then query, outliers, broken query critique
3. Understanding Product Metrics & KPIs — markdown answers graded against a rubric (mirrors Product Analytics Academy exercises)
4. Version Control (Git workflows for analytics) — branching strategy, merge conflict resolution, rebase vs merge, PR critique, commit hygiene, revert strategy, git state diagnose

**Workflow:** pick category + subtopic → generate problem (or replay a saved one) → diagnose (Modeling Diagnostic supports markdown + ASCII for non SQL drills) → write SQL or markdown → submit for grading → next.
''')


# ============================================================
# Cell 1 — Setup
# ============================================================
code('''# ── Setup ──
import os, sys, json, uuid
from pathlib import Path
from datetime import datetime
from IPython.display import display, HTML, clear_output, Javascript
import ipywidgets as widgets
import pandas as pd

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(Path(os.getcwd()).parent / ".env")
except Exception:
    pass

# Reload module imports so edits to .py files take effect on cell re-run
sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
for mod in ["nb02_drill_utils", "sql_practice_utils", "sandbox"]:
    if mod in sys.modules:
        del sys.modules[mod]
import nb02_drill_utils as dru
import sandbox as sbx

# Paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
GEN_DIR = os.path.join(PROJECT_ROOT, "data", "outputs", "generated_problems")
SOLVED_DIR = os.path.join(PROJECT_ROOT, "data", "outputs", "solved")
SESSIONS_DIR = os.path.join(PROJECT_ROOT, "data", "outputs", "sessions")
for d in [GEN_DIR, SOLVED_DIR, SESSIONS_DIR]:
    os.makedirs(d, exist_ok=True)

# Init Claude
claude_ready = dru.init_claude()

# Check sandboxes
pg_ok, pg_msg = sbx.check_postgres()
my_ok, my_msg = sbx.check_mysql()
print(f"PostgreSQL: {pg_msg}")
print(f"MySQL:      {my_msg}")
if not pg_ok:
    print("\\nPostgres unreachable. SQL categories require it. Run `docker compose up -d` from project root.")
    print("(KPI category works without Postgres.)")

# Shared state across cells
STATE = {
    "problem": None,
    "hint_index": 0,
    "last_action": None,
}

# Stop JupyterLab keyboard manager from grabbing Shift+Enter / Cmd+Z inside textareas.
# Shift+Enter runs the cell (wipes widgets); we BOTH preventDefault and stopPropagation so
# the keystroke never reaches Jupyter — works for SQL editor, diagnostic fields, KPI markdown,
# interpretation/recommendation/modeling fields, and any other textarea in the notebook.
display(Javascript("""
  document.addEventListener("keydown", function(e) {
    var inField = (e.target.tagName === "TEXTAREA" || e.target.tagName === "INPUT");
    if (!inField) return;
    if (e.shiftKey && e.key === "Enter") {
      e.preventDefault();
      e.stopPropagation();
    }
    var modifier = e.metaKey || e.ctrlKey;
    if (modifier && (e.key === "z" || e.key === "Z")) {
      e.stopPropagation();
    }
  }, true);
"""))

# Auto-resize ALL textareas to fit their content as the user types — applies globally
# to .diagnose-textarea, .sql-code-editor, .kpi-md-editor textareas. Listens for input
# events and grows the textarea height to match scrollHeight.
display(Javascript("""
  (function() {
    function autoResize(ta) {
      // Save current scroll position so the page doesn't jump when we resize
      var scrollTop = window.scrollY;
      ta.style.height = "auto";
      // Add a small buffer so the last line isn't clipped
      ta.style.height = (ta.scrollHeight + 2) + "px";
      window.scrollTo({ top: scrollTop });
    }
    function attach(ta) {
      if (ta.dataset.autoResizeAttached) return;
      ta.dataset.autoResizeAttached = "1";
      ta.style.overflow = "hidden";
      ta.addEventListener("input", function() { autoResize(ta); });
      // Initial sizing in case there's already content (e.g., /* notes */ scaffold)
      setTimeout(function() { autoResize(ta); }, 50);
    }
    function poll() {
      document.querySelectorAll(
        ".diagnose-textarea textarea, .sql-code-editor textarea, .kpi-md-editor textarea"
      ).forEach(attach);
    }
    poll();
    setInterval(poll, 1000);
  })();
"""))
''')


# ============================================================
# Cell 2 — Picker header
# ============================================================
md('''## 1. Pick a problem

Pick a category, then pick a subtopic, then either generate a new problem or replay a saved one.
''')


# ============================================================
# Cell 3 — Picker (nested dropdowns + Generate)
# ============================================================
code('''# ── Problem Picker ──

category_dd = widgets.Dropdown(
    options=[(dru.CATEGORIES[k]["label"], k) for k in dru.category_keys()],
    value=dru.category_keys()[0],
    description="Category:",
    style={"description_width": "90px"},
    layout=widgets.Layout(width="560px"),
)

def _subtopic_options(cat):
    return [(dru.subtopic_label(cat, s), s) for s in dru.subtopic_keys(cat)]

subtopic_dd = widgets.Dropdown(
    options=_subtopic_options(category_dd.value),
    value=dru.subtopic_keys(category_dd.value)[0],
    description="Subtopic:",
    style={"description_width": "90px"},
    layout=widgets.Layout(width="720px"),
)

dialect_dd = widgets.Dropdown(
    options=[("PostgreSQL", "postgresql")],
    value="postgresql",
    description="Dialect:",
    style={"description_width": "90px"},
    layout=widgets.Layout(width="320px"),
)

source_radio = widgets.RadioButtons(
    options=[("New (generate)", "new"), ("Saved (replay)", "saved")],
    value="new",
    description="Source:",
    style={"description_width": "90px"},
    layout=widgets.Layout(width="320px"),
)

# Scenario anchor dropdown — pick Random (any industry), My App, or a
# specific industry vertical. When set to "booedup" the generator also
# injects the rich BooedUp app context (collections, features, metrics).
scenario_dd = widgets.Dropdown(
    options=[
        ("🎲 Random (any industry)", "random"),
        ("🎯 My App (BooedUp dating app)", "booedup"),
        ("Consumer Social (dating, social, video, podcast)", "consumer_social"),
        ("Marketplace (rideshare, delivery, listings)", "marketplace"),
        ("Ecommerce (D2C, fashion, grocery)", "ecommerce"),
        ("Fintech (neobank, BNPL, robo, crypto)", "fintech"),
        ("B2B SaaS (CRM, PM, HR, observability)", "b2b_saas"),
        ("Productivity & Media (notes, streaming, news)", "productivity_media"),
        ("Health & Wellness (telehealth, fitness, sleep)", "health_wellness"),
        ("Gaming (mobile, console)", "gaming"),
        ("Education (courses, language, tutoring)", "education"),
        ("Pharmacy & Care (digital pharmacy, diagnostics)", "pharmacy_care"),
    ],
    value="random",
    description="Scenario:",
    style={"description_width": "90px"},
    layout=widgets.Layout(width="480px"),
)
# Alias so any code path that still references scenario_radio.value keeps working.
scenario_radio = scenario_dd

saved_dd = widgets.Dropdown(
    options=[("— pick a saved problem —", None)],
    description="Saved:",
    style={"description_width": "90px"},
    layout=widgets.Layout(width="720px", display="none"),
)

generate_btn = widgets.Button(description="Generate Problem", button_style="primary",
                              layout=widgets.Layout(width="200px", height="34px"))
status_out = widgets.Output()
problem_out = widgets.Output()

def refresh_saved_list(*_):
    items = dru.list_problems(GEN_DIR, category=category_dd.value, subtopic=subtopic_dd.value)
    opts = [("— pick a saved problem —", None)] + [
        (f"{p['generated_at'][:16]} · {p['title']}", p["path"]) for p in items
    ]
    saved_dd.options = opts
    saved_dd.value = None

def on_category_change(change):
    new_cat = change["new"]
    subtopic_dd.options = _subtopic_options(new_cat)
    subtopic_dd.value = dru.subtopic_keys(new_cat)[0]
    if dru.category_kind(new_cat) == "kpi":
        dialect_dd.layout.display = "none"
    else:
        dialect_dd.layout.display = "flex"
    refresh_saved_list()

def on_subtopic_change(change):
    refresh_saved_list()

def on_source_change(change):
    if change["new"] == "saved":
        saved_dd.layout.display = "flex"
        refresh_saved_list()
    else:
        saved_dd.layout.display = "none"

category_dd.observe(on_category_change, names="value")
subtopic_dd.observe(on_subtopic_change, names="value")
source_radio.observe(on_source_change, names="value")

# ----- Renderers (centralized in dru so cell 7 reuses them) -----
def render_problem(p):
    with problem_out:
        clear_output(wait=True)
        kind = p.get("_meta", {}).get("kind", "sql")
        if kind == "sql":
            display(HTML(dru.render_sql_problem(p, compact=False)))
        else:
            display(HTML(dru.render_kpi_problem(p, compact=False)))

def _attempt_progress(attempt, total, last_error):
    with status_out:
        if last_error:
            print(f"Attempt {attempt-1}/{total} failed validation:\\n{last_error[:1500]}")
            print(f"Retrying (attempt {attempt}/{total}) ...")
        else:
            label = dru.subtopic_label(category_dd.value, subtopic_dd.value)
            print(f"Generating: {label} (attempt {attempt}/{total}) ...")

def on_generate(b):
    with status_out:
        clear_output(wait=True)
        if source_radio.value == "saved":
            path = saved_dd.value
            if not path:
                print("Pick a saved problem first.")
                return
            print("Loading saved problem ...")
            problem = dru.load_problem(path)
        else:
            problem = dru.generate_problem(
                category_dd.value, subtopic_dd.value,
                dialect=dialect_dd.value,
                on_attempt=_attempt_progress,
                scenario_mode=scenario_radio.value,
            )
            if not problem:
                print("Generation failed. Click Generate to try again.")
                return
            saved = dru.save_problem(problem, GEN_DIR)
            print(f"Saved: {os.path.basename(saved)}")
            attempts = problem.get("_meta", {}).get("validation_attempts", 1)
            print(f"(passed validation on attempt {attempts})")
        STATE["problem"] = problem
        STATE["hint_index"] = 0
        try:
            refresh_reminder()
        except NameError:
            pass
        kind = problem.get("_meta", {}).get("kind", "sql")
        subtopic_for_hooks = problem.get("_meta", {}).get("subtopic", "")
        try:
            switch_editor_for_kind(kind)
        except NameError:
            pass
        except Exception as e:
            print(f"[switch_editor_for_kind error] {type(e).__name__}: {e}")
        try:
            apply_subtopic_editor_override(subtopic_for_hooks)
        except NameError:
            pass
        except Exception as e:
            print(f"[apply_subtopic_editor_override error] {type(e).__name__}: {e}")
        # Refresh the schema_design form (dim checkboxes, SCD per dim, metrics
        # classifier, source column classifier, etc). Surface any error so we can
        # diagnose if the dynamic widgets fail to populate.
        try:
            refresh_subtopic_form()
        except NameError:
            print("[refresh_subtopic_form] not yet defined — run the diagnostic-form cell above")
        except Exception as e:
            import traceback
            print(f"[refresh_subtopic_form error] {type(e).__name__}: {e}")
            traceback.print_exc()
        # Pre-populate the editor: SQL gets a /* notes */ scaffold; KPI gets a markdown scaffold
        try:
            if kind == "sql":
                code_ta.value = "/* notes */\\n\\n"
            else:
                markdown_ta.value = ""
        except NameError:
            pass
        if kind == "sql":
            try:
                sbx.reset(dialect_dd.value)
                sbx.execute_script(dialect_dd.value, problem.get("schema_ddl", ""))
                sbx.execute_script(dialect_dd.value, problem.get("example_input_data", ""))
                print("Sandbox loaded with example data.")
            except Exception as e:
                print(f"Sandbox load error: {e}")
        render_problem(problem)

generate_btn.on_click(on_generate)

display(widgets.VBox([
    category_dd,
    subtopic_dd,
    widgets.HBox([dialect_dd, source_radio]),
    scenario_dd,
    saved_dd,
    generate_btn,
    status_out,
    problem_out,
]))
''')


# ============================================================
# Cell 4 — Diagnostic header
# ============================================================
md('''## 2. Response Builder

Four accordions, one per category. When you generate a problem, the matching accordion auto opens and shows the response form tailored to your subtopic.

- **1. Data Transformation Modeling** — Modeling Diagnostic (grain, joins, materialization, dbt layer, tests) for `dimensional_modeling`, `scd_type_2`, `dbt_tests_macros`; the 11 field Schema Design Response Form for `schema_design`; or the new Multiple Choice quiz for `multiple_choice`.
- **2. Critical Reasoning SQL** — Structural Diagnostic (paraphrase, classify shape, list moves) for all six SQL execution subtopics. Use it as a warm up before scrolling to Section 3 to write the SQL.
- **3. Understanding Product Metrics & KPIs** — Business Analysis (interpret expected output + recommend an action) for the 10 markdown subtopics; or the Multiple Choice quiz for `multiple_choice`.
- **4. Version Control (Git workflows)** — 6 field Version Control Response Form for the seven git subtopics; or the Multiple Choice quiz for `multiple_choice`.

**Multiple Choice drills** (new) — 8 questions per drill mixing MCQ, True/False, and ordering questions. Tests the standard interview vocabulary for each category. Submit to get a score and per question explanations.

**Solve vs Walkthrough mode** — most response forms support both. Solve mode = try blind. Walkthrough mode = the worked answer appears in each field's hint area so you can read it, then paraphrase it in your own words below to lock it in. Schema Design has this today; other forms will gain it over time.
''')


# ============================================================
# Cell 5 — Diagnostic form
# ============================================================
code('''# ── Diagnostic Form (SQL only) ──

import sql_practice_utils as spu_for_recipes

paraphrase_ta = widgets.Textarea(
    placeholder="Restate the prompt in your own words ...",
    layout=widgets.Layout(width="100%", min_height="110px"),
    description="Paraphrase:",
    style={"description_width": "110px"},
)
paraphrase_ta.add_class("diagnose-textarea")

input_dd = widgets.Dropdown(
    options=[("— pick —", ""),
             ("Single table", "single_table"),
             ("Join 2+", "join"),
             ("Union", "union"),
             ("Procedural", "procedural"),
             ("Fact + dim(s) (star)", "fact_plus_dims"),
             ("SCD Type 2 dim", "scd2_dim"),
             ("Event log", "event_log")],
    description="Input:",
    style={"description_width": "110px"},
    layout=widgets.Layout(width="500px"),
)

output_dd = widgets.Dropdown(
    options=[("— pick —", ""),
             ("Fewer rows", "fewer_rows"),
             ("Same rows", "same_rows"),
             ("Single value", "single_value"),
             ("State mutation", "state_mutation"),
             ("Scalar return", "scalar_return"),
             ("Table return", "table_return"),
             ("Rate per group", "rate_per_group"),
             ("Running cumulative", "running_cumulative"),
             ("Percentile per group", "percentile_per_group"),
             ("Time-bound joined", "time_bound_joined")],
    description="Output shape:",
    style={"description_width": "110px"},
    layout=widgets.Layout(width="500px"),
)

# Recipe dropdown — pull base vocab from sql_practice_utils, then add modeling-specific options
_modeling_recipes = ["fact-dim-join", "scd2-time-bound-join", "lag-gap",
                      "percentile-aggregate", "rate-calc", "having-filter"]
_all_recipes = list(spu_for_recipes.RECIPE_VOCAB) + _modeling_recipes
recipe_dd = widgets.Dropdown(
    options=[("— pick —", "")] + [(r, r) for r in _all_recipes],
    description="Recipe:",
    style={"description_width": "110px"},
    layout=widgets.Layout(width="500px"),
)

moves_ta = widgets.Textarea(
    placeholder="Move 1: ...\\nMove 2: ...",
    layout=widgets.Layout(width="100%", min_height="90px"),
    description="Moves:",
    style={"description_width": "110px"},
)
moves_ta.add_class("diagnose-textarea")

# --- Business analysis (interpretation + recommendation) practice ---
interpretation_ta = widgets.Textarea(
    placeholder="Read the EXPECTED OUTPUT and write 3-5 bullets:\\n- read the actual numbers literally\\n- interpret what they suggest about underlying behavior\\n- compare to industry benchmarks (FPAR 75-85% retail, etc) where relevant\\n- flag any concerns or ambiguities",
    layout=widgets.Layout(width="100%", min_height="120px"),
    description="Interpret:",
    style={"description_width": "110px"},
)
interpretation_ta.add_class("diagnose-textarea")

recommendation_ta = widgets.Textarea(
    placeholder="Based on your interpretation, write 3-5 recommendation bullets:\\n- start each with an action verb (Trigger / Implement / Investigate / Add)\\n- name the owning stakeholder (Product, Engineering, Analytics, Finance, GTM)\\n- reference an industry-standard practice or framework relevant to the problem domain\\n- include at least one 'what to monitor next' with a concrete metric and direction",
    layout=widgets.Layout(width="100%", min_height="140px"),
    description="Recommend:",
    style={"description_width": "110px"},
)
recommendation_ta.add_class("diagnose-textarea")

# --- Modeling-focused diagnostic fields ---
materialization_dd = widgets.Dropdown(
    options=[("— pick —", ""), ("table", "table"), ("view", "view"),
             ("incremental", "incremental"), ("ephemeral", "ephemeral"),
             ("snapshot", "snapshot"), ("N/A (ad-hoc query)", "na")],
    description="Materialize:",
    style={"description_width": "110px"},
    layout=widgets.Layout(width="400px"),
)

materialization_rationale_ta = widgets.Textarea(
    placeholder="Why this materialization? Reference query frequency, data volume, freshness needs, build cost.",
    layout=widgets.Layout(width="100%", min_height="70px"),
    description="...because:",
    style={"description_width": "110px"},
)
materialization_rationale_ta.add_class("diagnose-textarea")

grain_ta = widgets.Textarea(
    placeholder="State BOTH grains:\\n  Input grain: one row per ___ (the source table)\\n  Output grain: one row per ___ (what your final SELECT or proposed table returns)\\nMost interview gotchas come from confusing the two — call them out separately.\\n\\nMarkdown and ASCII tables welcome (e.g., a 2-column 'input grain | output grain' table).",
    layout=widgets.Layout(width="100%", min_height="80px"),
    description="Grain:",
    style={"description_width": "110px"},
)
grain_ta.add_class("diagnose-textarea")

join_strategy_ta = widgets.Textarea(
    placeholder="If multi-table: which table is LEFT and why? Which is RIGHT? Sequence + key columns at each step. LEFT vs INNER and why.\\n\\nFor schema_design / dimensional_modeling problems: ASCII star schema sketches welcome — e.g.\\n   dim_drug    dim_payer\\n        \\\\   /\\n      fact_claim --- dim_patient\\n        /\\n   dim_prescriber\\n\\nIf single-table aggregation with no joins: just say 'N/A — single-table aggregation' and you'll get full marks.",
    layout=widgets.Layout(width="100%", min_height="100px"),
    description="Joins:",
    style={"description_width": "110px"},
)
join_strategy_ta.add_class("diagnose-textarea")

# Free-form design notes — for schema_design / dimensional_modeling problems where
# Grain + Joins + Tests don't capture everything. Fact column splits, SCD type
# assignments per dim, idempotency logic, ASCII diagrams all live here. Graded as
# its own modeling axis when non-empty.
design_notes_ta = widgets.Textarea(
    placeholder=(
        "Free-form modeling scratch space (markdown, ASCII, tables all welcome).\\n\\n"
        "Use this for things that don't fit Grain/Joins/Tests:\\n"
        "  - Fact columns table (column | type | source | notes)\\n"
        "  - SCD type per dim with one-line rationale (Type 1 vs Type 2 vs Type 0)\\n"
        "  - Idempotency logic (how does the model handle paid-then-reversed?)\\n"
        "  - ASCII star schema sketch (fact in center, dims branching out)\\n"
        "  - Edge cases (late-arriving events, drug NDC reassignment, multi-fill)\\n\\n"
        "Skip this for SQL-execution drills (Tab 1 analytical SQL). Best for schema_design, "
        "dimensional_modeling, scd_type_2."
    ),
    layout=widgets.Layout(width="100%", min_height="160px"),
    description="Design notes:",
    style={"description_width": "110px"},
)
design_notes_ta.add_class("diagnose-textarea")

# dbt layer dropdown with inline definitions to reinforce learning
dbt_layer_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("source — raw landed table from upstream system", "source"),
        ("staging (stg_) — minimal cleanup: rename, cast, filter test rows", "stg"),
        ("intermediate (int_) — reusable joins/window functions between layers", "int"),
        ("mart (mart_) — business-facing aggregations, KPIs, end-user output", "mart"),
        ("snapshot — SCD Type 2 history maintenance via dbt snapshot block", "snapshot"),
        ("N/A — ad-hoc analytical query, not a dbt model", "na"),
    ],
    description="dbt layer:",
    style={"description_width": "110px"},
    layout=widgets.Layout(width="640px"),
)

# Test coverage: pure HTML reference table (top) + SelectMultiple picker (bottom).
# Splitting the visual reference from the input widget avoids ipywidgets HBox layout
# issues that broke the previous all-in-one table.
_dbt_test_specs = [
    # (name, description, when_to_use, package)
    ("unique",                              "Every value in the column is distinct",                            "Primary keys, surrogate keys, single-column grain",        "dbt-core (built-in)"),
    ("not_null",                            "Column has no NULL values",                                        "Required FKs, grain columns, mandatory business fields",   "dbt-core (built-in)"),
    ("accepted_values",                     "Column only contains values from a specified list",                "Enum-style columns: event_type, status, channel, tier",    "dbt-core (built-in)"),
    ("relationships",                       "Foreign key has a matching value in the referenced table",         "Every fact FK should reference a valid dim row",           "dbt-core (built-in)"),
    ("expression_is_true",                  "Arbitrary boolean check on a row or aggregate",                    "Range checks (paid_amount >= 0), cross-column rules",      "dbt_utils"),
    ("unique_combination_of_columns",       "A combination of columns is unique (composite key)",               "Composite grain (e.g., one row per patient + drug_class)", "dbt_utils"),
    ("not_null_proportion",                 "Percentage of NULLs in column must be below a threshold",          "Optional fields where SOME NULLs are OK (notes, comments)", "dbt_utils"),
    ("recency",                             "Most recent record must be within N hours/days",                   "Pipeline freshness on event tables",                       "dbt_utils"),
    ("accepted_range",                      "Numeric column must fall within a min/max range",                  "Days_supply (1-365), age (0-120), dose validations",       "dbt_utils"),
    ("expect_column_values_to_be_between",  "Column values must fall within an inclusive range",                "Same as accepted_range, more expressive syntax",           "dbt_expectations"),
    ("expect_column_values_to_match_regex", "String column matches a regex pattern",                            "NDC format (11 digits), email format, NPI format",         "dbt_expectations"),
    ("expect_column_values_to_be_of_type",  "Column data type matches the declared type (INT, DATE, etc.)",     "Schema enforcement: counts must be INT, event_date must be DATE", "dbt_expectations"),
    ("expect_table_row_count_to_be_between","Table row count must fall within expected bounds",                 "Sanity check after refresh: too few = upstream broke",     "dbt_expectations"),
    ("expect_compound_columns_to_be_unique","Compound columns are unique (composite key alternative)",          "Same as unique_combination_of_columns, different package", "dbt_expectations"),
    ("root_models (project audit)",         "Flags models with no upstream source/ref (orphan models)",         "Project-level health check, run periodically",             "dbt_project_evaluator"),
    ("undocumented_models (project audit)", "Flags models without descriptions in schema.yml",                  "Project-level documentation hygiene",                      "dbt_project_evaluator"),
    ("custom singular test",                ".sql file in tests/ that returns rows when the test FAILS",        "Business rule too specific for a generic test",            "your project (custom)"),
    ("custom generic test",                 "Reusable macro returning rows on FAIL, parameterized in YAML",     "Same custom rule applied to multiple columns",             "your project (custom)"),
]

# Single GridBox table — all checkboxes + cells live in ONE shared grid so
# every row's columns auto-align, and the GridBox itself owns the only scrollbar.
# Previous VBox-of-HBox attempts produced one scrollbar per row and broken column
# alignment because each row's inner CSS grid computed widths independently.
def _pkg_color(pkg):
    return {
        "dbt-core (built-in)":      "#1a7f37",
        "dbt_utils":                "#2563a8",
        "dbt_expectations":         "#8b3a0e",
        "dbt_project_evaluator":    "#6f42c1",
        "your project (custom)":    "#a37f00",
    }.get(pkg, "#555")

_dbt_cb_widgets = {}
_dbt_caption = widgets.HTML(
    "<div style='font-weight:600; font-size:13px; color:#0c447c; margin-top:6px;'>"
    "dbt tests reference (check the rows you'd add — scroll inside the box):"
    "</div>"
)

# Build a flat list of children for the grid: header row first (5 cells), then
# 5 cells per data row (1 checkbox + 4 HTML cells). GridBox auto-wraps based on
# grid_template_columns count.
_grid_children = []

# Header row — 5 cells (first one is empty spacer above checkbox column)
_HEADER_STYLE = (
    "padding:8px 10px; background:#f6f8fa; border-bottom:2px solid #2d2d2d; "
    "font-size:11px; text-transform:uppercase; letter-spacing:0.04em; "
    "font-weight:600; color:#1a1a1a; box-sizing:border-box;"
)
_grid_children.append(widgets.HTML(f"<div style='{_HEADER_STYLE}'>&nbsp;</div>"))
for _label in ("dbt test", "Description", "When to use", "Package"):
    _grid_children.append(widgets.HTML(f"<div style='{_HEADER_STYLE}'>{_label}</div>"))

# Data rows
_CELL_BASE = (
    "padding:6px 10px; border-bottom:1px solid #eee; font-size:12px; "
    "box-sizing:border-box; overflow-wrap:anywhere; word-break:break-word;"
)
for name, desc, when, pkg in _dbt_test_specs:
    color = _pkg_color(pkg)
    cb = widgets.Checkbox(
        value=False,
        indent=False,
        layout=widgets.Layout(
            width="auto", min_width="0",
            margin="0", padding="6px 8px 6px 12px",
        ),
    )
    _dbt_cb_widgets[name] = cb
    _grid_children.append(cb)
    _grid_children.append(widgets.HTML(
        f"<div style='{_CELL_BASE}'>"
        f"<code style='background:#fdf2e9; color:#b33000; padding:1px 5px; "
        f"border-radius:3px; font-size:12px;'>{name}</code></div>"
    ))
    _grid_children.append(widgets.HTML(
        f"<div style='{_CELL_BASE} color:#1a1a1a;'>{desc}</div>"
    ))
    _grid_children.append(widgets.HTML(
        f"<div style='{_CELL_BASE} color:#444;'>{when}</div>"
    ))
    _grid_children.append(widgets.HTML(
        f"<div style='{_CELL_BASE} color:{color}; font-style:italic; font-size:11px;'>{pkg}</div>"
    ))

test_coverage_table = widgets.GridBox(
    children=_grid_children,
    layout=widgets.Layout(
        grid_template_columns="40px 22% 28% 30% auto",
        grid_gap="0",
        width="100%",
        max_height="340px",
        overflow_y="auto",
        overflow_x="hidden",
        border="1px solid #d0d7de",
        border_radius="6px",
        margin="2px 0 0 0",
    ),
)

test_coverage_details_ta = widgets.Textarea(
    placeholder="For each test you selected, state which COLUMN it applies to (e.g., 'unique on event_date', 'not_null on patient_id') and for custom tests, describe the business rule.",
    layout=widgets.Layout(width="100%", min_height="70px"),
    description="...details:",
    style={"description_width": "110px"},
)
test_coverage_details_ta.add_class("diagnose-textarea")

feedback_btn = widgets.Button(description="Get Structural Feedback", button_style="info",
                              layout=widgets.Layout(width="220px", height="34px"))
modeling_feedback_btn = widgets.Button(description="Get Modeling Feedback", button_style="primary",
                                       layout=widgets.Layout(width="220px", height="34px"))
business_feedback_btn = widgets.Button(description="Get Business Feedback", button_style="warning",
                                       layout=widgets.Layout(width="220px", height="34px"))
feedback_out = widgets.Output()
modeling_feedback_out = widgets.Output()
business_feedback_out = widgets.Output()

def fmt_check(ok, label, msg):
    badge = ('<span style="color:#1a7f37; font-weight:600;">correct</span>' if ok
             else '<span style="color:#cf222e; font-weight:600;">rethink</span>')
    return f"<li><strong>{label}:</strong> {badge} — {msg}</li>"

def on_feedback(b):
    with feedback_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p:
            print("Generate a problem first."); return
        if p.get("_meta", {}).get("kind") != "sql":
            print("Diagnostic form is for SQL problems. KPI problems are graded by the markdown editor below.")
            return
        answers = {
            "paraphrase": paraphrase_ta.value,
            "input_arrival": input_dd.value,
            "output_shape": output_dd.value,
            "recipe": recipe_dd.value,
            "composite_moves": moves_ta.value,
        }
        print("Asking Claude to grade ...")
        result = dru.grade_diagnostic(p, answers)
        clear_output(wait=True)
        if not result:
            print("Grading failed."); return
        html = '<div style="border:1px solid #d0d7de; border-radius:6px; padding:14px; background:#f6f8fa;">'
        html += '<h4 style="margin:0 0 10px;">Diagnostic Feedback</h4>'
        html += '<ul style="line-height:1.7; margin:0 0 0 18px;">'
        html += f'<li><strong>Paraphrase:</strong> {result.get("paraphrase_feedback","")}</li>'
        html += fmt_check(result.get("input_classification_correct", False), "Input",
                          result.get("input_classification_feedback",""))
        html += fmt_check(result.get("output_shape_correct", False), "Output shape",
                          result.get("output_shape_feedback",""))
        html += fmt_check(result.get("recipe_correct", False), "Recipe",
                          result.get("recipe_feedback",""))
        html += f'<li><strong>Moves:</strong> {result.get("composite_moves_feedback","")}</li>'
        html += "</ul>"
        html += f'<p style="margin:10px 0 0; font-style:italic; color:#57606a;">{result.get("overall","")}</p>'
        html += "</div>"
        display(HTML(html))

feedback_btn.on_click(on_feedback)

def on_business_feedback(b):
    with business_feedback_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p:
            print("Generate a problem first."); return
        if not (interpretation_ta.value or "").strip() and not (recommendation_ta.value or "").strip():
            print("Write your interpretation and recommendation first, then click Get Business Feedback.")
            return
        print("Asking Claude to grade interpretation + recommendation ...")
        result = dru.grade_interpretation_recommendation(
            p, interpretation_ta.value or "", recommendation_ta.value or ""
        )
        clear_output(wait=True)
        if not result:
            print("Grading failed."); return
        display(HTML(dru.interp_rec_grade_to_html(result)))

business_feedback_btn.on_click(on_business_feedback)

def on_modeling_feedback(b):
    with modeling_feedback_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p:
            print("Generate a problem first."); return
        # Gather checked dbt tests from the table of Checkbox widgets
        selected_tests = [name for name, cb in _dbt_cb_widgets.items() if cb.value]
        test_coverage_combined = ""
        if selected_tests:
            test_coverage_combined = "Selected tests: " + ", ".join(selected_tests)
        if (test_coverage_details_ta.value or "").strip():
            sep = "\\n" if test_coverage_combined else ""
            test_coverage_combined += sep + "Details: " + test_coverage_details_ta.value.strip()

        answers = {
            "materialization": materialization_dd.value,
            "materialization_rationale": materialization_rationale_ta.value,
            "grain": grain_ta.value,
            "join_strategy": join_strategy_ta.value,
            "dbt_layer": dbt_layer_dd.value,
            "test_coverage": test_coverage_combined,
            "design_notes": design_notes_ta.value,
        }
        # Require at least one non-empty modeling field
        if not any(str(v).strip() for v in answers.values()):
            print("Fill in at least one modeling field, then click Get Modeling Feedback.")
            return
        print("Asking Claude to grade modeling choices ...")
        result = dru.grade_modeling_diagnostic(p, answers)
        clear_output(wait=True)
        if not result:
            print("Grading failed."); return
        display(HTML(dru.modeling_grade_to_html(result)))

modeling_feedback_btn.on_click(on_modeling_feedback)

# Generic diagnostics — three independent accordion panels (Structural /
# Modeling / Business). Each panel is collapsible with its own feedback
# button INSIDE the panel. All collapsed by default so the user can expand
# only the block(s) relevant to the current problem.

_structural_panel = widgets.VBox([
    widgets.HTML("<div style='font-size:12px; color:#57606a; margin-bottom:6px;'>Paraphrase the prompt, classify input/output shape, name the recipe and moves. Best for SQL execution drills as a warm-up before writing the query.</div>"),
    paraphrase_ta, input_dd, output_dd, recipe_dd, moves_ta,
    feedback_btn, feedback_out,
])

_modeling_panel = widgets.VBox([
    widgets.HTML("<div style='font-size:12px; color:#57606a; margin-bottom:6px;'>Materialization, grain, joins, dbt layer, tests, free-form design notes. Best for Tab 2 modeling problems. For Tab 1 analytical SQL, mark dbt layer + materialization as N/A. Markdown and ASCII diagrams welcome in the text fields.</div>"),
    materialization_dd, materialization_rationale_ta,
    grain_ta, join_strategy_ta,
    design_notes_ta,
    dbt_layer_dd,
    _dbt_caption, test_coverage_table, test_coverage_details_ta,
    modeling_feedback_btn, modeling_feedback_out,
])

_business_panel = widgets.VBox([
    widgets.HTML("<div style='font-size:12px; color:#57606a; margin-bottom:6px;'>Read the EXPECTED OUTPUT above, then fill in both fields. Peek at the model interpretation/recommendation in the problem block only after your first attempt.</div>"),
    interpretation_ta, recommendation_ta,
    business_feedback_btn, business_feedback_out,
])

# NOTE: the schema_design form (4th panel) is built later in this same cell;
# we wire it into the accordion below AFTER all schema_design widgets exist.
# For now, the accordion is created with the 3 generic panels and a placeholder
# for the 4th; we'll replace the 4th child after the schema_design code block.

_schema_design_panel_placeholder = widgets.VBox([
    widgets.HTML("<i>Schema design form is being built below in this cell — "
                 "this placeholder will be replaced when the cell finishes running.</i>")
])
_vc_panel_placeholder = widgets.VBox([
    widgets.HTML("<i>Version control response form is being built below in this cell — "
                 "this placeholder will be replaced when the cell finishes running.</i>")
])

# === 4 panel category-organized response builder ===========================
# Each category panel is a VBox whose .children list is repopulated by
# _populate_category_panels() (defined later in this cell) when the active
# problem changes. The legacy form widgets get assigned as panel children.

_panel_tm = widgets.VBox([widgets.HTML(
    "<i style='color:#57606a;'>Generate a problem under "
    "<b>1. Data Transformation Modeling</b> to load the response form here.</i>"
)])
_panel_cr = widgets.VBox([widgets.HTML(
    "<i style='color:#57606a;'>Generate a problem under "
    "<b>2. Critical Reasoning SQL</b> to load the response form here.</i>"
)])
_panel_pk = widgets.VBox([widgets.HTML(
    "<i style='color:#57606a;'>Generate a problem under "
    "<b>3. Understanding Product Metrics &amp; KPIs</b> to load the response form here.</i>"
)])
_panel_vc = widgets.VBox([widgets.HTML(
    "<i style='color:#57606a;'>Generate a problem under "
    "<b>4. Version Control</b> to load the response form here.</i>"
)])

_generic_diagnostics_accordion = widgets.Accordion(
    children=[_panel_tm, _panel_cr, _panel_pk, _panel_vc],
)
_generic_diagnostics_accordion.set_title(0, "1. Data Transformation Modeling")
_generic_diagnostics_accordion.set_title(1, "2. Critical Reasoning SQL")
_generic_diagnostics_accordion.set_title(2, "3. Understanding Product Metrics & KPIs")
_generic_diagnostics_accordion.set_title(3, "4. Version Control (Git workflows)")
_generic_diagnostics_accordion.selected_index = None  # all collapsed by default

# Wrap in a VBox so refresh_subtopic_form() can toggle visibility on the container
_generic_diagnostics_box = widgets.VBox([_generic_diagnostics_accordion])
display(_generic_diagnostics_box)


# ============================================================
# SUBTOPIC-SPECIFIC FORM: schema_design (11-field universal spec)
# Generalizable across all schema_design problem shapes (claim-level fact,
# model layer design, SCD classification, fact/dim split, multi-grain).
# Some fields are dynamic (rebuild on state change):
#   - field 4 dim_joins: checkboxes built from problem.candidate_dimensions
#   - field 5 scd_per_dim: dropdowns built from currently-checked dims
#   - field 6 conformed_dims: same as field 5, derived from checked dims
#   - field 7 models: multi-row builder with add/remove
#   - field 8 tests_per_model: rebuilds from field 7 models list
# ============================================================

# Mode toggle — Solve (try blind) vs Walkthrough (answers shown, paraphrase to learn)
sd2_mode_toggle = widgets.ToggleButtons(
    options=[
        ('🧠 Solve mode (try blind)', 'solve'),
        ('📖 Walkthrough mode (read answer, paraphrase to lock in)', 'walkthrough'),
    ],
    value='solve',
    description='Mode:',
    style={'description_width': '60px', 'button_width': '320px'},
    layout=widgets.Layout(margin='8px 0 12px 0'),
)


# Shared mutable state for dynamic fields (preserved across rebuilds so the
# user's picks aren't lost when checkboxes toggle)
_sd2_state = {
    "dim_checkboxes": {},        # dim_name -> Checkbox
    "scd_dropdowns": {},         # dim_name -> Dropdown (current widgets)
    "scd_picks": {},             # dim_name -> "type0|type1|type2|"
    "conformed_checkboxes": {},  # dim_name -> Checkbox
    "conformed_picks": {},       # dim_name -> bool
    "models": [],                # [{name, layer, mat}]
    "test_selections": {},       # model_name -> [test_label]
    "test_custom": {},           # model_name -> str
    "translate_dropdowns": {},   # ask_idx -> Dropdown (translate-the-asks exercise)
    "translate_picks": {},       # ask_idx -> "measure|fk|attr|timestamp|combo" (legacy)
    "translate_decomp_widgets": {},  # ask_idx -> dict of Text widgets {numerator, denominator, filter_dim, drilldown, timestamp}
    "translate_decomp": {},      # ask_idx -> dict {numerator, denominator, filter_dim, drilldown, timestamp}
    # Metrics classifier widgets (Step 2 / Grain panel) — populated by _sd2_rebuild_metrics_box.
    # Each ask -> dict of {unit, agg, filter_dim, drilldown, ingredients} widget references.
    "metrics_widgets": {},
    # Source column classifier widgets (Step 6 / Fact columns panel) — populated by _sd2_rebuild_srccols_box.
    # (table_name, col_name) -> dict of {per_grain, role, include} widget references.
    "srccols_widgets": {},
    "mode": "solve",             # 'solve' or 'walkthrough'
    "generic_hints": {},         # field_id -> generic hint HTML (cached for solve mode)
    "problem_hints": {},         # field_id -> problem-specific hint HTML (from field_hints)
    "worked_examples_raw": {},   # field_id -> raw worked example string (from problem)
}


# ============================================================
# Concept primer (definitions of data engineering terms used in the form)
# ============================================================

def _sd2_concept_block(title, body_html, example_html=None):
    """One collapsible concept entry — a <details> element styled with a blue caret.
    Optionally includes a concrete example block beneath the definition."""
    example_block = ""
    if example_html:
        example_block = (
            f'<div style="margin-top:8px; padding:8px 12px; background:#f0f7ff; '
            f'border-left:2px solid #0969da; border-radius:3px; font-size:12px; '
            f'line-height:1.55;"><strong style="color:#0969da;">Example:</strong> '
            f'{example_html}</div>'
        )
    return widgets.HTML(
        f'<details style="margin: 4px 0; border-left: 3px solid #0969da; '
        f'padding-left: 10px;">'
        f'<summary style="cursor: pointer; color: #0969da; font-weight: 600; font-size: 13px;">'
        f'{title}</summary>'
        f'<div style="margin-top: 6px; font-size: 12.5px; line-height: 1.55;">{body_html}{example_block}</div>'
        f'</details>'
    )


_sd2_concept_primer = widgets.VBox([
    widgets.HTML(
        '<div style="background:linear-gradient(135deg,#fff8e6 0%,#fff3d4 100%); '
        'border:1px solid #d1a72a; border-radius:6px; padding:14px 16px; '
        'margin:6px 0 12px 0; font-size:12.5px; line-height:1.6;">'
        '<div style="font-weight:700; font-size:14px; color:#7a5a00; margin-bottom:8px;">'
        "⭐ Kimball's 4-step dimensional design process — the spine of this form</div>"
        '<div style="margin-bottom:8px;">Use these 4 steps in order, every time. Most '
        'modeling bugs trace back to skipping or rushing one. The accordion fields below '
        "map to the 4 steps so you can&#39;t skip them:</div>"
        '<table style="width:100%; border-collapse:collapse; font-size:12px; '
        'line-height:1.5; margin-top:6px;">'
        '<thead><tr style="background:#f8efd0;">'
        '<th style="text-align:left; padding:6px 8px; border-bottom:1px solid #d1a72a; width:40px;">Step</th>'
        '<th style="text-align:left; padding:6px 8px; border-bottom:1px solid #d1a72a;">Decision</th>'
        '<th style="text-align:left; padding:6px 8px; border-bottom:1px solid #d1a72a;">Form fields that ground this step</th>'
        '</tr></thead><tbody>'
        '<tr><td style="padding:6px 8px; border-bottom:1px solid #ecdfb0; font-weight:700; color:#7a5a00;">1</td>'
        '<td style="padding:6px 8px; border-bottom:1px solid #ecdfb0;"><strong>Pick the business process</strong> '
        '(the noun: claims, prescriptions, partner messages, fulfillment events).</td>'
        '<td style="padding:6px 8px; border-bottom:1px solid #ecdfb0;">Field 1 — Business process</td></tr>'
        '<tr><td style="padding:6px 8px; border-bottom:1px solid #ecdfb0; font-weight:700; color:#7a5a00;">2</td>'
        '<td style="padding:6px 8px; border-bottom:1px solid #ecdfb0;"><strong>Declare the grain</strong> '
        '("one row per ___"). The atomic level your fact stores.</td>'
        '<td style="padding:6px 8px; border-bottom:1px solid #ecdfb0;">Field 2 — Grain</td></tr>'
        '<tr><td style="padding:6px 8px; border-bottom:1px solid #ecdfb0; font-weight:700; color:#7a5a00;">3</td>'
        '<td style="padding:6px 8px; border-bottom:1px solid #ecdfb0;"><strong>Identify the dimensions</strong> '
        '(the "by X" filters and drill-downs — patient, drug, payer, channel, date).</td>'
        '<td style="padding:6px 8px; border-bottom:1px solid #ecdfb0;">Field 6 — Dim joins, plus the SCD &amp; conformed-dim sub-fields</td></tr>'
        '<tr><td style="padding:6px 8px; font-weight:700; color:#7a5a00;">4</td>'
        '<td style="padding:6px 8px;"><strong>Identify the facts</strong> (the measures: counts, sums, '
        'derived timestamps — the raw ingredients of every metric).</td>'
        '<td style="padding:6px 8px;">Field 3 — Fact columns, plus Field 4 — Key strategy</td></tr>'
        '</tbody></table>'
        '<div style="margin-top:10px; padding:8px 10px; background:#fff; border-left:2px solid #d1a72a; '
        'border-radius:3px; font-size:11.5px; color:#57606a;">'
        '<strong>Why this order matters:</strong> grain depends on the chosen process; dims must support '
        'the grain you picked; facts are the columns that survive that grain. Re-ordering these steps '
        "is the #1 cause of fact tables that can&#39;t answer the asks they were supposed to."
        '</div>'
        '</div>'
    ),
    widgets.HTML(
        '<div style="font-weight:600; font-size:14px; color:#0c447c; margin-top:6px;">'
        '🧭 How to construct a fact table from stakeholder asks</div>'
        '<div style="font-size:12.5px; line-height:1.6; margin:6px 0 8px 0;">'
        'Read the stakeholder context in the prompt. For EACH ask, decide what it maps to:'
        '<ol style="margin:6px 0 6px 18px; padding-left:0;">'
        '<li><strong>Metric</strong> ("response rate", "messages sent", "median time to fill") '
        '→ measure column on the fact (count, sum, ratio).</li>'
        '<li><strong>"by X" or filter X</strong> ("by channel", "by condition cohort", '
        '"per care team member") → FK column on the fact pointing at dim_X.</li>'
        '<li><strong>Drill-down attribute</strong> ("see by patient demographic") → an attribute '
        'on the joined dim, NOT a column on the fact.</li>'
        '<li><strong>Supporting timestamp</strong> ("median time to first response") → '
        'first_response_ts column on the fact, derived as MIN(event_ts) over events.</li>'
        '</ol>'
        'Then pick the GRAIN (lowest level supporting all metrics), write columns: '
        '<strong>1 PK or composite key + N FKs + M measures + supporting timestamps</strong>, '
        'and sanity check: can you answer EVERY ask with this fact + listed dims? If no, '
        'a column is missing.'
        '</div>'
    ),
    widgets.HTML(
        '<div style="font-weight:600; font-size:13px; color:#0c447c; margin-top:8px;">'
        'Concepts reference (click to expand):</div>'
    ),
    _sd2_concept_block(
        "Grain",
        "What does ONE row in your output represent. Most modeling bugs trace back to "
        "fuzzy grain. Always state grain as 'one row per ___'. Lower grain (more detailed) "
        "supports more reporting; higher grain (more aggregated) is faster to query.",
        "<strong>Examples by problem type:</strong><br>"
        "&bull; Claim-level fact: 'one row per <code>claim_id</code>' (~15M rows/year)<br>"
        "&bull; Patient-month adherence: 'one row per <code>patient_id</code> per <code>year_month</code>'<br>"
        "&bull; Daily channel rollup: 'one row per <code>patient_id</code> per <code>event_date</code> per <code>channel</code>'<br>"
        "&bull; Dim_patient: 'one row per <code>patient_id</code>' (with SCD-2: one row per patient per attribute version)<br>"
        "<strong>Tell from the prompt:</strong> if it says '~15M rows after 1 year' or 'one row per X', that's the grain. Read those signals carefully — they're rarely accidental."
    ),
    _sd2_concept_block(
        "Fact vs dim — the most important distinction",
        "Fact tables hold measures (counts, sums, ratios) at a defined grain, plus FK columns "
        "pointing at dim tables. Dim tables hold context (who, what, when) — a row per business "
        "entity (one row per patient, one row per drug). "
        "<strong>The most common mistake is pivoting a categorical dimension into separate "
        "columns</strong> (e.g., sms_count, email_count, phone_count instead of one count column "
        "+ a channel FK). Don't do this. Keep channel as ONE column on the fact and let dim_channel "
        "carry attributes.",
        "<strong>Example — claim-level fact:</strong><br>"
        "<code>fact_claim</code> stores: <code>claim_id</code> (PK), <code>patient_id</code> (FK), "
        "<code>drug_id</code> (FK), <code>payer_id</code> (FK), <code>first_submit_ts</code>, "
        "<code>paid_ts</code>, <code>reversed_ts</code>, <code>gross_paid_amount</code>, <code>net_paid_amount</code>, <code>final_status</code>.<br>"
        "<code>dim_drug</code> stores: <code>drug_id</code> (PK), <code>drug_name</code>, <code>drug_class</code>, <code>generic_flag</code>.<br>"
        "<strong>WRONG:</strong> <code>fact_claim</code> with <code>statin_count</code>, <code>biologic_count</code>, <code>opioid_count</code> as columns — that pivots drug_class out of the dim into the fact."
    ),
    _sd2_concept_block(
        "Raw measure vs derived metric — what belongs on the fact",
        "Fact tables store the RAW INGREDIENTS of metrics, not the metrics themselves. Rates and "
        "ratios are computed by the dashboard or BI layer. The fact stores counts, sums, and "
        "timestamps — the dashboard divides them.",
        "<strong>Example — First Pass Acceptance Rate:</strong><br>"
        "<strong>WRONG (the fact stores the rate):</strong> <code>fact_partner_health</code> with column "
        "<code>fpar</code> (DECIMAL). Now the rate is frozen at the grain you chose; you can't slice differently.<br>"
        "<strong>RIGHT (the fact stores raw counts at claim grain):</strong> <code>fact_claim</code> with "
        "columns <code>was_submitted</code> (1/0), <code>was_paid_first_submit</code> (1/0). Dashboard "
        "computes <code>SUM(was_paid_first_submit) / SUM(was_submitted)</code> grouped by partner_id, "
        "drug_class, payer, etc — any way you want to slice."
    ),
    _sd2_concept_block(
        "Star schema",
        "A central fact table with FKs radiating out to surrounding dim tables. Joins are "
        "always fact-to-dim, never dim-to-dim. Easy to understand, easy to query, easy for BI tools.",
        "<pre style='background:#fff; padding:6px; margin:0; font-size:11px;'>"
        "    dim_drug    dim_payer<br>"
        "         \\\\     /<br>"
        "       fact_claim --- dim_patient<br>"
        "         /     \\\\<br>"
        "    dim_date     dim_prescriber"
        "</pre>"
        "Five dims, one fact. Every dashboard slice is fact-LEFT-JOIN-dim."
    ),
    _sd2_concept_block(
        "SCD types (Slowly Changing Dimensions)",
        "Applies to <strong>DIMS, not facts</strong>. How does a dim handle attribute changes "
        "over time?<br>"
        "<strong>Type 0</strong> — Immutable. Never changes (e.g., date dimension).<br>"
        "<strong>Type 1</strong> — Overwrite. Keeps only the latest value (e.g., dim_prescriber NPI is stable).<br>"
        "<strong>Type 2</strong> — Track history. Adds a new row with valid_from / valid_to / is_current "
        "when an attribute changes (e.g., dim_payer plan-year boundary, dim_patient address change).<br>"
        "Use Type 2 when historical reports need to reflect the value that was true AT THE TIME "
        "of the fact event.",
        "<strong>Example — dim_payer Type 2:</strong> patient P001's plan changed from 'Medicare' to "
        "'Medicare Advantage' on 2025-01-01.<br>"
        "Before: <code>(payer_sk=1, payer_id=PY01, plan='Medicare', valid_from=2024-01-01, valid_to=2024-12-31, is_current=false)</code><br>"
        "After: <code>(payer_sk=2, payer_id=PY01, plan='Medicare Advantage', valid_from=2025-01-01, valid_to=NULL, is_current=true)</code><br>"
        "A claim from 2024-06-15 joins to payer_sk=1 (the row valid at submit_ts), so historical reports "
        "still show the correct plan."
    ),
    _sd2_concept_block(
        "Surrogate vs natural key",
        "<strong>Natural key</strong>: use the source system's existing ID directly (claim_id, patient_id) "
        "as the table's PK. Simplest when the source ID is stable, unique, and meaningful in BI tools.<br>"
        "<strong>Surrogate key</strong>: generate a new INT or hash ID just for this table (claim_sk). "
        "Use when source IDs are unstable, multiple sources collide, OR you need a stable join key for "
        "SCD-2 dims (where the same patient_id needs multiple rows over time).<br>"
        "<strong>Composite natural key</strong>: two or more columns together form the unique key "
        "(claim_id + fill_seq when multi-fill prescriptions exist).<br>"
        "<strong>Important:</strong> the FACT's key strategy and a dim's SCD-2 strategy are "
        "DIFFERENT decisions. Don't mix them up.",
        "<strong>Example — fact_claim natural key:</strong> <code>claim_id</code> from PBM is unique "
        "and stable, so use it directly: <code>PRIMARY KEY (claim_id)</code>.<br>"
        "<strong>Example — dim_patient surrogate key (Type 2):</strong> patient P001 might have 3 rows "
        "over time as their address changes. <code>patient_sk</code> (1, 2, 3) is the PK; <code>patient_id</code> "
        "(P001, P001, P001) is a regular column."
    ),
    _sd2_concept_block(
        "Conformed dim",
        "A dim table that's reused across MULTIPLE fact tables. Same dim_patient feeds fact_claim AND "
        "fact_telehealth_visit, so both join to the SAME table. Stops you from building two slightly "
        "different patient tables that drift apart. Only relevant if the problem proposes more than one fact.",
        "<strong>Example:</strong> <code>dim_patient</code> is used by <code>fact_claim</code> (for adherence "
        "metrics), <code>fact_telehealth_visit</code> (for engagement), AND <code>fact_kit_order</code> (for "
        "diagnostics). All three facts JOIN <code>dim_patient.patient_id</code>. If two teams built two "
        "different patient dims, the cohort definitions would drift apart and your engagement metric "
        "wouldn't tie out with your adherence metric."
    ),
    _sd2_concept_block(
        "Idempotency / re-run safety",
        "If you re-run your model, does it produce the same result regardless of when? "
        "Critical for: (a) reversal handling — when a paid claim is later reversed, the fact row "
        "should reflect the reversal; (b) reprocessing — if the dbt run fails halfway and you "
        "re-run, you don't get duplicate rows or stale data.<br>"
        "<strong>Strategies:</strong> MERGE/UPSERT on grain key (overwrite when source changes), "
        "window-function rebuild over event log, append-only fact + view that nets corrections, "
        "or full table rebuild every run.",
        "<strong>Example — claim with reversal:</strong> claim_id=C001 is paid for $100 on 2025-03-10, "
        "then reversed on 2025-03-25.<br>"
        "MERGE on claim_id: re-run on 2025-03-26 finds the reversal in source events, UPDATES the "
        "fact row to <code>gross_paid_amount=100, net_paid_amount=0, final_status='reversed'</code>. "
        "Re-running tomorrow produces the same row — idempotent."
    ),
    _sd2_concept_block(
        "Late-arriving facts / out-of-order events",
        "What happens when a record arrives AFTER its period closed? Common when an event log "
        "has eventual consistency or when a reversal lands 30 days after the original payment.<br>"
        "<strong>Re-state closed periods</strong>: rebuild affected partitions; period totals stay "
        "correct but historical reports change.<br>"
        "<strong>Append correction row</strong>: original row stays, inverse row added; reports stay "
        "reproducible but require netting at query time.<br>"
        "<strong>Snapshot lock-in</strong>: don't update closed periods; reports are reproducible "
        "but become inaccurate over time.",
        "<strong>Example — reversal arriving 30 days late:</strong> March 2025 closed reporting on "
        "April 1. On April 12, a reversal event lands for a claim originally paid March 15.<br>"
        "Re-state: rebuild March's partition. March FPAR drops; finance has to re-publish the report.<br>"
        "Append correction: add a correction row dated April 12 that nets the original $100. March "
        "report stays the same; April absorbs the correction."
    ),
    _sd2_concept_block(
        "Materialization (table / view / incremental / ephemeral / snapshot)",
        "How dbt persists a model.<br>"
        "<strong>table</strong>: full table built every run. Good for moderate-size aggregations "
        "queried frequently.<br>"
        "<strong>view</strong>: virtual; logic re-runs at query time. Good for thin transforms with "
        "low query volume.<br>"
        "<strong>incremental</strong>: only new/changed rows added each run. Good for large append-only "
        "event logs queried frequently.<br>"
        "<strong>ephemeral</strong>: inlined as a CTE; nothing persisted. Good for thin reusable logic.<br>"
        "<strong>snapshot</strong>: SCD-2 history maintained automatically by dbt. Used for slowly-"
        "changing dim tables, NOT for facts.",
        "<strong>Examples by volume + frequency:</strong><br>"
        "&bull; 50K events/day, hourly dashboard, 5M rows/year &rarr; <code>incremental</code> with merge predicate on grain key<br>"
        "&bull; 1K rows/day, daily report &rarr; <code>table</code> (full rebuild is cheap)<br>"
        "&bull; Ad-hoc query, low volume &rarr; <code>view</code><br>"
        "&bull; Reusable join used by 3 marts &rarr; <code>ephemeral</code> (inlined as CTE)<br>"
        "&bull; <code>dim_payer</code> tracking plan changes &rarr; <code>snapshot</code>"
    ),
    _sd2_concept_block(
        "dbt layers (source / staging / intermediate / mart)",
        "Layered transformation:<br>"
        "<strong>source</strong>: raw landed table from upstream system. No transformation.<br>"
        "<strong>staging (stg_)</strong>: minimal cleanup — rename columns, cast types, filter test rows. "
        "ONE-to-ONE with source tables. Don't put business rules here.<br>"
        "<strong>intermediate (int_)</strong>: reusable joins or window functions between layers. "
        "Bridge logic that multiple marts need.<br>"
        "<strong>mart (mart_)</strong>: business-facing aggregations and KPIs. End-user output. "
        "This is where business rules live.",
        "<strong>Example layer flow:</strong><br>"
        "&bull; <code>source: raw_pharmacy.claim_events_raw</code> (raw landed)<br>"
        "&bull; <code>stg_claim_events</code>: rename columns, cast types, filter test rows (one-to-one with source)<br>"
        "&bull; <code>int_claim_collapsed</code>: window functions to extract first_submit_ts, paid_ts, "
        "reversed_ts per claim_id (event-grain → claim-grain transform)<br>"
        "&bull; <code>fact_claim</code>: joins int_claim_collapsed to dims, computes gross_paid_amount, "
        "net_paid_amount, final_status (the user-facing fact)"
    ),
    _sd2_concept_block(
        "Join types (LEFT vs INNER)",
        "<strong>LEFT JOIN</strong>: keeps all rows from the LEFT (fact) table, even if the dim has "
        "no match. Use when the fact must be preserved in full and a missing dim FK is OK.<br>"
        "<strong>INNER JOIN</strong>: drops rows where either side has no match. Use when a missing "
        "dim FK signals a data quality problem and you want those rows excluded.<br>"
        "Default for fact-to-dim: LEFT JOIN. The fact is the source of truth; you don't want a missing "
        "dim row to silently drop facts from your dashboard.",
        "<strong>Example:</strong> 1000 claims in <code>fact_claim</code>, 5 of them have a "
        "<code>prescriber_id</code> not yet in <code>dim_prescriber</code> (new prescriber on-boarded yesterday).<br>"
        "<code>LEFT JOIN dim_prescriber</code>: dashboard shows 1000 claims; 5 with NULL prescriber name. Visible problem.<br>"
        "<code>INNER JOIN dim_prescriber</code>: dashboard shows 995 claims. 5 silently dropped. Bad."
    ),
    _sd2_concept_block(
        "dbt tests (the standard set)",
        "<strong>unique</strong>: every value in the column is distinct. Use on grain keys.<br>"
        "<strong>not_null</strong>: column has no NULL. Use on grain keys, FKs, mandatory fields.<br>"
        "<strong>accepted_values</strong>: column only holds values from a list. Use on enums "
        "(event_type, status, channel).<br>"
        "<strong>relationships</strong>: every FK has a matching value in the referenced dim. "
        "Use on every fact FK pointing at a dim.<br>"
        "<strong>expression_is_true</strong> (dbt_utils): arbitrary boolean check. Use for cross-column "
        "rules like 'net_paid_amount &lt;= gross_paid_amount' or 'paid_ts &gt;= submit_ts'.",
        "<strong>Example — fact_claim test pack:</strong><br>"
        "&bull; <code>unique</code> on <code>claim_id</code><br>"
        "&bull; <code>not_null</code> on <code>claim_id</code>, <code>first_submit_ts</code>, <code>patient_id</code><br>"
        "&bull; <code>relationships</code> on <code>patient_id → dim_patient.patient_id</code><br>"
        "&bull; <code>accepted_values</code> on <code>final_status</code> in (paid, reversed, rejected, submitted)<br>"
        "&bull; <code>expression_is_true</code>: <code>net_paid_amount &lt;= gross_paid_amount</code><br>"
        "&bull; <code>expression_is_true</code>: <code>paid_ts &gt;= first_submit_ts</code> when paid_ts is not null"
    ),
], layout=widgets.Layout(
    border="1px solid #d0d7de",
    border_radius="6px",
    padding="12px 14px",
    margin="0 0 12px 0",
    background_color="#f6f8fa",
))


# ---- Per-field hint widgets (HTML, populated dynamically from problem.field_hints) ----
def _make_hint_widget(generic_text):
    """A small bordered HTML block that shows a generic hint by default, replaced
    with a problem-specific hint when refresh_subtopic_form() loads a problem."""
    return widgets.HTML(
        f'<div class="sd2-field-hint" style="background:#eef5fc; border-left:3px solid #0969da; '
        f'padding:8px 12px; margin-bottom:8px; font-size:12.5px; line-height:1.5; border-radius:3px;">'
        f'<strong>Hint:</strong> {generic_text}</div>'
    )

# Worked-example reveal widgets — one per field. Default is "no example yet";
# rebuild on problem load from problem.worked_example_per_field. Collapsed by
# default so the user attempts blind first; click to peek.
def _make_worked_example_widget():
    return widgets.HTML(
        '<details style="margin: 0 0 6px 0; border-left: 3px solid #1a7f37; padding-left: 10px;">'
        '<summary style="cursor: pointer; color: #1a7f37; font-weight: 600; font-size: 12.5px;">'
        '💡 Show example answer for this problem (peek when stuck — try blind first)</summary>'
        '<div style="margin-top: 6px; font-size: 12px; color: #57606a; padding: 8px 10px; '
        'background: #f0f8f0; border-radius: 3px;"><i>No worked example available — older '
        'problem format. Try the form on your own and use the grader feedback to learn.</i>'
        '</div></details>'
    )

sd2_example_grain = _make_worked_example_widget()
sd2_example_fact_columns = _make_worked_example_widget()
sd2_example_key = _make_worked_example_widget()
sd2_example_dim_joins = _make_worked_example_widget()
sd2_example_scd = _make_worked_example_widget()
sd2_example_conformed = _make_worked_example_widget()
sd2_example_models = _make_worked_example_widget()
sd2_example_tests = _make_worked_example_widget()
sd2_example_idempotency = _make_worked_example_widget()
sd2_example_late_arriving = _make_worked_example_widget()
sd2_example_edge = _make_worked_example_widget()


sd2_hint_business_process = _make_hint_widget(
    "Name the real-world activity this fact table measures, in one sentence. "
    "Examples: 'a patient receiving an outreach message via SMS, email, or in-app' / "
    "'a claim being adjudicated by the PBM' / 'a kit being shipped to a patient and returned for results.' "
    "Anchors every later decision — every fact column, FK, and measure should serve this activity."
)
sd2_example_business_process = _make_worked_example_widget()


# Business Process noun-finder helper
sd2_bp_finder_btn = widgets.Button(
    description="Find candidate nouns from the asks",
    button_style="info",
    layout=widgets.Layout(width="280px"),
)
sd2_bp_finder_out = widgets.Output()

def _on_bp_find_nouns(b):
    p = STATE.get("problem") or {}
    asks = p.get("stakeholder_asks", []) or []
    with sd2_bp_finder_out:
        clear_output(wait=True)
        if not asks:
            print("No stakeholder asks loaded. Generate a problem first.")
            return
        # Heuristic: extract candidate nouns by finding common pharmacy/healthcare nouns
        # in each ask. The user picks one as the business process subject.
        candidates = []
        common_nouns = ["claim", "message", "kit", "prescription", "patient", "visit",
                        "test", "order", "dispense", "fill", "event", "shipment", "appointment"]
        seen = set()
        for ask in asks:
            ask_lower = ask.lower()
            for n in common_nouns:
                if n in ask_lower and n not in seen:
                    candidates.append(n)
                    seen.add(n)
        print("Candidate nouns found in the stakeholder asks:")
        if candidates:
            for c in candidates:
                print(f"  - {c}")
            print()
            print("Pick the noun that appears in MOST asks. If two appear, the FINER one usually")
            print("wins (e.g., 'kit' is finer than 'patient' since one patient has many kits).")
            print("Then write the full business process in the textarea below.")
        else:
            print("No common nouns found — read the asks carefully and pick the noun that")
            print("appears in all of them. Write the business process in the textarea below.")

sd2_bp_finder_btn.on_click(_on_bp_find_nouns)

sd2_bp_finder_box = widgets.VBox([
    widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:8px 12px; margin-bottom:6px; font-size:12.5px; line-height:1.5; border-radius:3px;'>"
        "<strong>Noun finder.</strong> Click to extract candidate business nouns from the stakeholder asks. The noun that appears in MOST asks is the subject of your business process."
        "</div>"
    ),
    sd2_bp_finder_btn,
    sd2_bp_finder_out,
])


# The grader docks "business process" when only the activity is stated. It also
# wants the BUSINESS OUTCOME — the question the fact is built to answer. Split
# into two textareas so the user thinks about both.
sd2_business_process_activity_ta = widgets.Textarea(
    placeholder=(
        "ACTIVITY — the real-world thing being tracked. One sentence.\\n\\n"
        "Examples:\\n"
        "  - A claim moving through PBM adjudication (submitted, paid, rejected, reversed)\\n"
        "  - An order moving through fulfillment (placed, shipped, delivered, dosed)\\n"
        "  - A patient receiving an outreach message via SMS, email, or in-app"
    ),
    layout=widgets.Layout(width="100%", min_height="60px"),
    description="(a) Activity:",
    style={"description_width": "150px"},
)
sd2_business_process_activity_ta.add_class("diagnose-textarea")

sd2_business_process_outcome_ta = widgets.Textarea(
    placeholder=(
        "OUTCOME — the business question(s) this fact is built to answer. One sentence.\\n\\n"
        "Read the stakeholder asks and infer the OUTCOME they all serve. Examples:\\n"
        "  - Measure claim throughput and reversal rate to negotiate better partner terms\\n"
        "  - Measure delivery SLA and dose adherence to assess clinical program effectiveness\\n"
        "  - Measure patient engagement and channel response rates to optimize outreach mix\\n\\n"
        "The grader rewards naming the OUTCOME, not just the activity."
    ),
    layout=widgets.Layout(width="100%", min_height="60px"),
    description="(b) Outcome:",
    style={"description_width": "150px"},
)
sd2_business_process_outcome_ta.add_class("diagnose-textarea")

# Backward-compat shim: existing code reads sd2_business_process_ta.value as a
# single string. Provide a virtual view that concatenates activity + outcome.
class _SD2BusinessProcessShim:
    @property
    def value(self):
        a = (sd2_business_process_activity_ta.value or "").strip()
        o = (sd2_business_process_outcome_ta.value or "").strip()
        if a and o:
            return f"Activity: {a}\\n\\nOutcome: {o}"
        return a or o
    @value.setter
    def value(self, v):
        # Best-effort restore from a saved single-string value
        text = str(v or "")
        if not text:
            sd2_business_process_activity_ta.value = ""
            sd2_business_process_outcome_ta.value = ""
            return
        # If it parses as our split format, restore both halves.
        if "Activity:" in text and "Outcome:" in text:
            try:
                parts = text.split("Outcome:", 1)
                act = parts[0].replace("Activity:", "").strip()
                out = parts[1].strip()
                sd2_business_process_activity_ta.value = act
                sd2_business_process_outcome_ta.value = out
                return
            except Exception:
                pass
        # Fallback: drop into activity, leave outcome empty.
        sd2_business_process_activity_ta.value = text
        sd2_business_process_outcome_ta.value = ""

sd2_business_process_ta = _SD2BusinessProcessShim()


sd2_hint_grain = _make_hint_widget(
    "State the OUTPUT grain explicitly. If the prompt asks for daily aggregates, your grain "
    "is one row per day per [the most-detailed slice]. Justify why this grain (not a finer or "
    "coarser one) supports the asks."
)
sd2_hint_fact_columns = _make_hint_widget(
    "List the columns you'd put on the fact: PK + FKs to each dim + measure columns + "
    "supporting timestamps. Look at the stakeholder asks — each metric becomes ONE measure "
    "column. Don't pivot a category (channel, status) into multiple columns."
)
sd2_hint_key = _make_hint_widget(
    "This is the FACT'S key strategy, not a dim's SCD-2 strategy. Ask: is the natural key "
    "(e.g., claim_id) stable, unique at the grain, and good enough?"
)
sd2_hint_dim_joins = _make_hint_widget(
    "For each 'by X' or 'filter by X' in the stakeholder asks, you need to join dim_X. "
    "Pick checkboxes for every dim that supports a stated ask."
)
sd2_hint_scd = _make_hint_widget(
    "SCD types apply to DIMS, not facts. For each dim you picked, ask: do attributes change "
    "over time? Does the report need to reflect the value AT THE TIME of the fact event? "
    "If yes → Type 2. If no → Type 1."
)
sd2_hint_conformed = _make_hint_widget(
    "Only relevant when the problem mentions multiple facts. If the prompt only asks for ONE "
    "fact table, mark this N/A in the rationale."
)
sd2_hint_models = _make_hint_widget(
    "Add one row per dbt model you'd build. Typical: src_X (source) → stg_X (staging cleanup) → "
    "fact_X (mart, your output). Pick layer + materialization for each."
)
sd2_hint_tests = _make_hint_widget(
    "For each model in field 7, pick at least 2 tests. Always include unique + not_null on the "
    "grain key. Add relationships to every dim FK. Custom singular test for any business rule "
    "that doesn't fit a standard test (e.g., gross >= net)."
)
sd2_hint_idempotency = _make_hint_widget(
    "If your fact aggregates events (counts, sums), can you safely re-run the model? Picks: "
    "MERGE/UPSERT (overwrite at the grain) or window-function rebuild are typical for aggregated "
    "facts. Snapshot is for SCD-2 dims, not aggregated facts."
)
sd2_hint_late_arriving = _make_hint_widget(
    "If the prompt says events arrive out of order or late, this matters. Pick a strategy and "
    "name the trade-off (consistency vs reproducibility)."
)
sd2_hint_edge = _make_hint_widget(
    "List the tricky scenarios you'd test for. The prompt often embeds an explicit edge question "
    "('how would you handle X?') — answer THAT one specifically here, plus 2 to 3 more you'd watch for."
)


# ---- Pitfall callouts (red-bordered, per high-risk field) ----
def _make_pitfall_widget(title, body):
    return widgets.HTML(
        f'<div style="background:#fbe9e7; border-left:3px solid #c62828; '
        f'padding:8px 12px; margin-bottom:8px; font-size:12.5px; line-height:1.5; border-radius:3px;">'
        f'<strong style="color:#c62828;">⚠ Common pitfall — {title}:</strong> {body}</div>'
    )

sd2_pitfall_fact_columns = _make_pitfall_widget(
    "don't pivot a dimension into separate columns",
    "If the stakeholder said 'by channel,' that's a filter dimension — keep ONE channel column "
    "on the fact and let dim_channel carry the attributes. Pivoting channel into "
    "<code>sms_sent</code>, <code>email_sent</code>, <code>phone_sent</code> creates a sparse, "
    "inflexible schema and is the most common schema design mistake at all levels."
)
sd2_pitfall_key = _make_pitfall_widget(
    "fact key vs dim SCD-2 key are different decisions",
    "This panel is about the FACT'S primary key (e.g., claim_id directly, or a surrogate claim_sk). "
    "Don't confuse it with whether dim_payer is SCD Type 2 (that's field 5). The fact rarely needs "
    "SCD-2; dims do."
)
sd2_pitfall_scd = _make_pitfall_widget(
    "SCD types apply to dims, not facts",
    "If you find yourself saying 'this fact is Type 2,' stop. Facts use Type-1-style updates "
    "(MERGE) or append-only patterns. SCD types describe how a dim handles attribute changes. "
    "Pick a type for each dim, not for the fact."
)


# ---- Field 2 template (always visible inside Field 2 panel) ----
# Two parts: a proper HTML table for visual reference, AND a copyable markdown
# source block for pasting into the textarea.
sd2_field2_template = widgets.HTML(
    '<details style="margin: 6px 0 8px 0; border-left: 3px solid #1a7f37; padding-left: 10px;">'
    '<summary style="cursor: pointer; color: #1a7f37; font-weight: 600; font-size: 13px;">'
    '📋 Suggested fact column template (click to expand)</summary>'
    '<div style="margin-top: 10px;">'
    '<div style="font-size: 12px; color: #57606a; margin-bottom: 6px;">'
    'Visual reference — what the fact column table should look like:'
    '</div>'
    '<table style="width:100%; border-collapse:collapse; font-size:12.5px; margin-bottom:12px;">'
    '<thead><tr style="background:#f6f8fa; border-bottom:2px solid #d0d7de;">'
    '<th style="padding:6px 10px; text-align:left;">column</th>'
    '<th style="padding:6px 10px; text-align:left;">type</th>'
    '<th style="padding:6px 10px; text-align:left;">role</th>'
    '<th style="padding:6px 10px; text-align:left;">source / how derived</th>'
    '</tr></thead><tbody>'
    '<tr style="border-bottom:1px solid #e0e0e0;">'
    '<td style="padding:6px 10px;"><code>___</code></td>'
    '<td style="padding:6px 10px;">VARCHAR / INT</td>'
    '<td style="padding:6px 10px;">grain key (PK)</td>'
    '<td style="padding:6px 10px;">matches the grain stated in field 1</td></tr>'
    '<tr style="border-bottom:1px solid #e0e0e0;">'
    '<td style="padding:6px 10px;"><code>___</code></td>'
    '<td style="padding:6px 10px;">VARCHAR</td>'
    '<td style="padding:6px 10px;">FK to dim_X</td>'
    '<td style="padding:6px 10px;">from source column <code>___</code></td></tr>'
    '<tr style="border-bottom:1px solid #e0e0e0;">'
    '<td style="padding:6px 10px;"><code>___</code></td>'
    '<td style="padding:6px 10px;">VARCHAR</td>'
    '<td style="padding:6px 10px;">FK to dim_Y</td>'
    '<td style="padding:6px 10px;">from source column <code>___</code></td></tr>'
    '<tr style="border-bottom:1px solid #e0e0e0;">'
    '<td style="padding:6px 10px;"><code>messages_sent</code></td>'
    '<td style="padding:6px 10px;">INT</td>'
    '<td style="padding:6px 10px;">measure: count</td>'
    '<td style="padding:6px 10px;">COUNT(events WHERE event_type=sent) over the grain</td></tr>'
    '<tr style="border-bottom:1px solid #e0e0e0;">'
    '<td style="padding:6px 10px;"><code>responses_received</code></td>'
    '<td style="padding:6px 10px;">INT</td>'
    '<td style="padding:6px 10px;">measure: count</td>'
    '<td style="padding:6px 10px;">COUNT(events WHERE event_type=response_received) over the grain</td></tr>'
    '<tr style="border-bottom:1px solid #e0e0e0;">'
    '<td style="padding:6px 10px;"><code>first_response_ts</code></td>'
    '<td style="padding:6px 10px;">TIMESTAMP</td>'
    '<td style="padding:6px 10px;">supporting timestamp</td>'
    '<td style="padding:6px 10px;">MIN(event_ts) WHERE event_type=response_received over the grain</td></tr>'
    '</tbody></table>'
    '<div style="font-size: 12px; color: #57606a; margin: 12px 0 6px 0;">'
    'Markdown source — copy this into the textarea below and replace the placeholders:'
    '</div>'
    '<pre style="background:#1e1e1e; color:#d4d4d4; padding:10px 12px; border-radius:4px; '
    'font-size:11.5px; line-height:1.55; overflow-x:auto; margin:0;">'
    '| column | type | role | source / how derived |\\n'
    '|---|---|---|---|\\n'
    '| ___ | VARCHAR / INT | grain key (PK) | matches the grain stated in field 1 |\\n'
    '| ___ | VARCHAR | FK to dim_X | from source column ___ |\\n'
    '| ___ | VARCHAR | FK to dim_Y | from source column ___ |\\n'
    '| messages_sent | INT | measure: count | COUNT(events WHERE event_type=sent) over the grain |\\n'
    '| responses_received | INT | measure: count | COUNT(events WHERE event_type=response_received) over the grain |\\n'
    '| first_response_ts | TIMESTAMP | supporting timestamp | MIN(event_ts) WHERE event_type=response_received over the grain |'
    '</pre>'
    '<div style="font-size: 12px; color: #57606a; margin-top: 8px;">'
    'Replace <code>___</code> with column names + types specific to your problem. '
    'Number of measure rows = number of metrics the stakeholder asked for. '
    'Number of FK rows = number of dims you picked in field 4.'
    '</div></div></details>'
)


# ---- Translate-the-asks pre-form exercise (DYNAMIC — built from problem.stakeholder_asks) ----
sd2_translate_box = widgets.VBox([
    widgets.HTML("<i>Generate a schema_design problem to see the stakeholder asks here.</i>")
])

# ---- Field 1: Grain ----
sd2_input_grain_ta = widgets.Textarea(
    placeholder=(
        "INPUT grain (the source you read FROM): 'one row per ___'.\\n"
        "Example: 'one row per claim_event' (state-change log, ~50K rows/day).\\n"
        "Required when the model collapses event-grain to entity-grain."
    ),
    layout=widgets.Layout(width="100%", min_height="60px"),
    description="Input grain:",
    style={"description_width": "120px"},
)
sd2_input_grain_ta.add_class("diagnose-textarea")

sd2_grain_ta = widgets.Textarea(
    placeholder=(
        "OUTPUT grain (the fact you produce): 'one row per ___'.\\n"
        "Example: 'one row per claim_id' (~15M rows/year).\\n"
        "If you collapsed event-grain to entity-grain, call out the grain shift "
        "in your rationale (input → output).\\n"
        "Most modeling bugs trace back to fuzzy grain — be explicit."
    ),
    layout=widgets.Layout(width="100%", min_height="90px"),
    description="Output grain:",
    style={"description_width": "120px"},
)
sd2_grain_ta.add_class("diagnose-textarea")

# ---- Field 2: Fact columns ----
sd2_fact_cols_ta = widgets.Textarea(
    placeholder=(
        "What columns the fact (or main output) table stores. Markdown table "
        "preferred:\\n"
        "| column | type | source / how derived |\\n"
        "|---|---|---|\\n"
        "| claim_id | VARCHAR | grain key |\\n"
        "| first_submit_ts | TIMESTAMP | MIN(event_ts) WHERE event_type='submitted' |\\n"
        "| paid_ts | TIMESTAMP | MAX(event_ts) WHERE event_type='paid' |\\n"
        "| gross_paid_amount | NUMERIC | SUM(paid_amount) over paid events |\\n"
        "| net_paid_amount | NUMERIC | gross minus reversed amount |\\n"
        "| final_status | VARCHAR | derived classification |\\n\\n"
        "For drills that aren't building a fact (e.g., pure SCD classification), "
        "type 'N/A — this drill is about dim modeling, not fact columns.'"
    ),
    layout=widgets.Layout(width="100%", min_height="200px"),
    description="Fact cols:",
    style={"description_width": "120px"},
)
sd2_fact_cols_ta.add_class("diagnose-textarea")

# ---- Field 3: Surrogate vs natural key ----
sd2_key_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Natural key (e.g., claim_id used directly as PK)", "natural"),
        ("Surrogate key (generated, e.g., claim_sk INT IDENTITY)", "surrogate"),
        ("Composite natural key (e.g., (claim_id, fill_seq))", "composite"),
        ("SCD-2 surrogate (valid_from/valid_to/is_current on dim)", "scd2_surrogate"),
        ("No key needed (purely event-level, no fact-style PK)", "none"),
        ("N/A — not relevant to this drill", "na"),
        ("Other (explain in rationale)", "other"),
    ],
    description="Key strategy:",
    style={"description_width": "120px"},
    layout=widgets.Layout(width="700px"),
)
sd2_key_rationale_ta = widgets.Textarea(
    placeholder=(
        "1-2 sentences. When is each appropriate?\\n"
        "  - Natural key: when the source ID is stable, unique, and meaningful in BI tools.\\n"
        "  - Surrogate: when natural key changes over time, comes from multiple sources, "
        "or you need to track SCD-2 history on a dim.\\n"
        "  - Composite: when no single column is unique on its own."
    ),
    layout=widgets.Layout(width="100%", min_height="80px"),
    description="...because:",
    style={"description_width": "120px"},
)
sd2_key_rationale_ta.add_class("diagnose-textarea")

# ---- Field 4: Dim joins (DYNAMIC — checkboxes built from problem.candidate_dimensions) ----
sd2_dim_box = widgets.VBox([
    widgets.HTML("<i>No problem loaded. Generate a schema_design problem to see candidate dims.</i>")
])

# ---- Field 5: SCD per dim (DYNAMIC — dropdowns built from checked dims in field 4) ----
sd2_scd_box = widgets.VBox([
    widgets.HTML("<i>Pick dims in field 4 first; SCD dropdowns appear here per dim.</i>")
])
sd2_scd_rationale_ta = widgets.Textarea(
    placeholder=(
        "Optional: 1 sentence per dim explaining the SCD pick.\\n"
        "Example:\\n"
        "  dim_payer Type 2 — plan-year boundaries change formulary, historical claims "
        "must reflect the plan active at submit_ts.\\n"
        "  dim_prescriber Type 1 — NPI is stable; no need to track."
    ),
    layout=widgets.Layout(width="100%", min_height="100px"),
    description="Rationale:",
    style={"description_width": "120px"},
)
sd2_scd_rationale_ta.add_class("diagnose-textarea")

# ---- Field 6: Conformed dims (DYNAMIC — checkboxes from checked dims in field 4) ----
sd2_conformed_box = widgets.VBox([
    widgets.HTML(
        "<div style='font-size:12px; color:#57606a; margin-bottom:6px;'>"
        "Only relevant if the problem proposes multiple facts. Mark all N/A for single-fact drills."
        "</div>"
        "<i>Pick dims in field 4 first; conformed checkboxes appear here.</i>"
    )
])
sd2_conformed_rationale_ta = widgets.Textarea(
    placeholder=(
        "If the problem mentions multiple facts (e.g., fact_claim AND fact_telehealth_visit), "
        "which dims should both join to the SAME table? That's the conformed dim concept.\\n"
        "Type 'N/A — single-fact drill' if not relevant."
    ),
    layout=widgets.Layout(width="100%", min_height="80px"),
    description="Rationale:",
    style={"description_width": "120px"},
)
sd2_conformed_rationale_ta.add_class("diagnose-textarea")

# ---- Field 7: Models (multi-row builder) ----
sd2_models_box = widgets.VBox([])
sd2_add_model_btn = widgets.Button(
    description="+ Add model row",
    button_style="info",
    layout=widgets.Layout(width="180px"),
)

# ---- Field 8: dbt tests per model (DYNAMIC) ----
sd2_tests_box = widgets.VBox([
    widgets.HTML("<i>Add models in field 7 first; per-model test panels appear here.</i>")
])

# ---- Field 9: Idempotency / re-run safety ----
sd2_idem_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("MERGE / UPSERT on grain key (overwrite row when source changes)", "merge"),
        ("Window function rebuild (LAST_VALUE / ROW_NUMBER, full refresh)", "window"),
        ("Append-only fact + view that nets out corrections", "append_view"),
        ("dbt snapshot (SCD Type 2 on the fact itself)", "snapshot"),
        ("Full table rebuild every run", "full_rebuild"),
        ("N/A — one-shot ad-hoc query", "na"),
        ("Other (explain in rationale)", "other"),
    ],
    description="Strategy:",
    style={"description_width": "120px"},
    layout=widgets.Layout(width="800px"),
)
sd2_idem_rationale_ta = widgets.Textarea(
    placeholder=(
        "If you re-run this model, does it produce the same result regardless of when?\\n"
        "Specifically: if a 'paid' event was reversed, does the fact row reflect the "
        "reversal or stay stale? Explain how your strategy preserves audit trail "
        "(gross) while updating the operational view (net)."
    ),
    layout=widgets.Layout(width="100%", min_height="100px"),
    description="...because:",
    style={"description_width": "120px"},
)
sd2_idem_rationale_ta.add_class("diagnose-textarea")

# ---- Field 10: Late-arriving / out-of-order events ----
sd2_late_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Re-state closed periods (rebuild affected partitions)", "restate"),
        ("Append a correction row (original row stays, inverse added)", "correction_row"),
        ("Lock-in snapshot at period close, don't update history", "snapshot_lock"),
        ("dbt incremental with merge predicate on (grain_key, event_ts)", "merge_predicate"),
        ("N/A — static data, no late arrivals possible", "na"),
        ("Other (explain in rationale)", "other"),
    ],
    description="Strategy:",
    style={"description_width": "120px"},
    layout=widgets.Layout(width="800px"),
)
sd2_late_rationale_ta = widgets.Textarea(
    placeholder=(
        "Trade-offs:\\n"
        "  - Consistency (period totals stay correct) vs reproducibility (closed periods don't change)\\n"
        "  - Storage cost (correction rows accumulate) vs simplicity (one row per claim)\\n"
        "  - Query complexity (view must net corrections) vs upstream complexity (rebuilds)"
    ),
    layout=widgets.Layout(width="100%", min_height="100px"),
    description="...because:",
    style={"description_width": "120px"},
)
sd2_late_rationale_ta.add_class("diagnose-textarea")

# ---- Field 11: Edge cases — categorized checkbox picker (NO text fields) ----
# For each category, the user gets a list of canned scenarios as checkboxes.
# Tick all that apply. The grader receives the ticked labels per category.
# Must address at least 2 categories (per rubric). No text input — pure picks.

_SD2_EDGE_CATEGORIES = [
    ("duplicates",
     "Duplicates",
     "Same source row appears twice (retry, network glitch).",
     [
         "Dedupe by event_id (deterministic PK) in staging",
         "Idempotent MERGE on primary key — same row updates, no duplication",
         "Window-rebuild approach — re-derive entity row from full event log on each run",
         "Hash of (event_type + entity_id + event_ts) when no event_id exists",
     ]),
    ("out_of_order",
     "Out-of-order events",
     "Events arrive in the wrong sequence (e.g., approval before submit ts).",
     [
         "Order events by event_ts in the int_ model before pivoting",
         "Use MIN(event_ts) for first_submit_ts so order doesn't matter",
         "Use LAST_VALUE / MAX(event_ts) for terminal-state timestamps",
         "Flag and quarantine rows where derived ts ordering is invalid",
     ]),
    ("null_handling",
     "NULL handling",
     "Required fields that arrive empty or NULL.",
     [
         "Missing FK — join to 'Unknown' surrogate row in the dim",
         "Missing event_ts — drop row, surface in dq_failures",
         "Missing required column — fail row via dbt not_null test",
         "Optional column NULL — pass through, dashboard handles via COALESCE",
     ]),
    ("boundary",
     "Boundary conditions",
     "Events on the exact boundary of a period.",
     [
         "Plan-year boundary — join SCD-2 dim version active at submit_ts",
         "Midnight cutoff — use event_ts not event_date for accurate grain",
         "Fiscal quarter close — use dim_date.fiscal_quarter, not calendar quarter",
         "Daylight savings — store all timestamps in UTC, convert at display layer",
     ]),
    ("failure_events",
     "Failure events",
     "Events signaling a failure (rejected, denied, message_failed).",
     [
         "Include in submission count, exclude from success/approval count",
         "Track as separate indicator column on fact (was_rejected, was_denied)",
         "Exclude entirely — only successful entities count per business rule",
         "Surface as final_status enum on the fact for slicing",
     ]),
    ("multiple_same_type",
     "Multiple events of the same type",
     "Same entity emits the same event_type more than once.",
     [
         "Take earliest — first_<event>_ts = MIN(event_ts WHERE event_type=...)",
         "Take latest — last_<event>_ts = MAX(event_ts WHERE event_type=...)",
         "Count occurrences — <event>_count = COUNT events of that type",
         "Aggregate amounts — gross_paid_amount = SUM(paid_amount)",
     ]),
    ("source_retries",
     "Source-system retries / late corrections",
     "Same logical event re-published; corrections arrive after pipeline run.",
     [
         "Dedupe in staging by event_id, ingestion order doesn't matter",
         "Track retry_count column when retries are business-meaningful",
         "Late correction triggers MERGE on entity row (not append)",
         "Snapshot fact + as_of_date when historical reproducibility is required",
     ]),
]

# Each category id -> SelectMultiple of canned scenarios + a checkbox "applies"
# Use SelectMultiple for compact multi-pick. Saved state and grader payload
# read from sd2_state['edge_picks'][cat_id] -> list of selected option strings.
_sd2_edge_cat_widgets = {}  # cat_id -> SelectMultiple widget
_sd2_edge_applies_widgets = {}  # cat_id -> Checkbox "applies to this problem"

for cat_id, cat_label, cat_prompt, options in _SD2_EDGE_CATEGORIES:
    applies_cb = widgets.Checkbox(
        value=False,
        description=f"Yes, '{cat_label}' applies to this fact design",
        indent=False,
        layout=widgets.Layout(width="100%"),
    )
    _sd2_edge_applies_widgets[cat_id] = applies_cb

    sel = widgets.SelectMultiple(
        options=options,
        rows=min(len(options), 5),
        description="Tick all that apply:",
        style={"description_width": "150px"},
        layout=widgets.Layout(width="100%"),
    )
    _sd2_edge_cat_widgets[cat_id] = sel

# Backward-compat: sd2_edge_ta exists in the response builder but is no longer
# rendered as a text input. We keep a hidden textarea to preserve the response
# contract (the grader still receives 'edge_cases' string built from picks).
sd2_edge_ta = widgets.Textarea(value="", layout=widgets.Layout(display="none"))

# Build the edge-case panel content (HTML cards + checkbox + multi-select)
_sd2_edge_panel_children = [
    widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; "
        "padding:10px 14px; margin-bottom:10px; font-size:12.5px; line-height:1.55; "
        "border-radius:3px;'>"
        "<strong>Address at least 2 categories.</strong> For each category that applies, "
        "tick the 'applies' checkbox AND select one or more canned scenarios that match "
        "your fact design. No typing — pure picks. The grader rewards specific picks that "
        "match the fact-design choices you made in earlier fields."
        "</div>"
    ),
]
for cat_id, cat_label, cat_prompt, _options in _SD2_EDGE_CATEGORIES:
    _sd2_edge_panel_children.append(widgets.HTML(
        f"<div style='font-weight:600; font-size:13px; color:#0c447c; margin-top:14px;'>"
        f"{cat_label}</div>"
        f"<div style='font-size:12.5px; color:#444; margin-bottom:6px;'>{cat_prompt}</div>"
    ))
    _sd2_edge_panel_children.append(_sd2_edge_applies_widgets[cat_id])
    _sd2_edge_panel_children.append(_sd2_edge_cat_widgets[cat_id])
# Problem-aware suggested-categories banner. Scans the loaded problem's prompt
# and stakeholder asks for keywords that flag edge cases the user is likely to
# need. Updated by _sd2_refresh_edge_suggestions() on problem load.
sd2_edge_suggestions_html = widgets.HTML(
    "<div style='background:#fff8e6; border-left:3px solid #d1a72a; padding:10px 14px; "
    "margin:6px 0 10px 0; font-size:12.5px; line-height:1.55; border-radius:3px;'>"
    "<strong>Suggested categories will appear here once a problem is loaded.</strong></div>"
)

def _sd2_refresh_edge_suggestions():
    """Scan the loaded problem for keywords that signal which edge case categories
    are likely relevant. Render a banner naming the 2-4 most likely categories so
    the user knows which to focus on."""
    p = STATE.get("problem") or {}
    if not p:
        sd2_edge_suggestions_html.value = (
            "<div style='background:#fff8e6; border-left:3px solid #d1a72a; padding:10px 14px; "
            "margin:6px 0 10px 0; font-size:12.5px; line-height:1.55; border-radius:3px;'>"
            "<strong>Generate a problem to see suggested edge case categories.</strong></div>"
        )
        return
    blob_parts = [(p.get("prompt") or ""), (p.get("schema_ddl") or "")]
    asks = p.get("stakeholder_asks", []) or []
    if isinstance(asks, list):
        blob_parts.extend([str(a) for a in asks])
    blob = " ".join(blob_parts).lower()

    # Keyword signals per category. Each suggestion includes a problem-tied
    # nudge in plain language so the user understands WHY the category matters.
    rules = [
        ("duplicates",
         ["retry", "duplicate", "deduplicate", "event_id", "primary key"],
         "Source has event_id PRIMARY KEY — dedupe by event_id is the standard pattern."),
        ("out_of_order",
         ["out of order", "out-of-order", "ordering", "sequence", "timestamp before",
          "event_ts", "lifecycle", "state change", "state changes", "approval before",
          "reversal", "late event"],
         "Event log with multiple state changes per entity — events can arrive out of order."),
        ("null_handling",
         ["null", "missing", "optional", "nullable", "may be null", "can be null",
          "patient_id", "payer_id", "fk", "foreign key"],
         "Source has nullable FK columns — missing FKs need a join-to-Unknown strategy."),
        ("boundary",
         ["boundary", "midnight", "fiscal", "quarter", "plan-year", "plan year",
          "year boundary", "month-end", "timezone"],
         "Time-bucket boundaries (plan-year, fiscal-quarter, midnight) need explicit handling for grain integrity."),
        ("failure_events",
         ["rejected", "denied", "failed", "failure", "error", "reversal",
          "reversed", "cancelled", "canceled"],
         "Source emits failure/cancellation events — decide whether they count toward submission, success, or are excluded."),
        ("multiple_same_type",
         ["multiple", "more than one", "twice", "many", "several", "outreach",
          "submitted, paid", "events", "attempts", "retries"],
         "Same entity emits the same event_type multiple times — pick MIN/MAX/COUNT semantics."),
        ("source_retries",
         ["retry", "republish", "late", "correction", "amendment", "restate",
          "amend", "reprocess"],
         "Late corrections / retries / restatements — decide MERGE vs append vs snapshot semantics."),
    ]

    matched = []  # list of (cat_id, label, reason, hits)
    label_lookup = {cid: lbl for (cid, lbl, _prompt, _opts) in _SD2_EDGE_CATEGORIES}
    for cat_id, kws, reason in rules:
        hits = [kw for kw in kws if kw in blob]
        if hits:
            matched.append((cat_id, label_lookup.get(cat_id, cat_id), reason, hits))

    if not matched:
        sd2_edge_suggestions_html.value = (
            "<div style='background:#fff8e6; border-left:3px solid #d1a72a; padding:10px 14px; "
            "margin:6px 0 10px 0; font-size:12.5px; line-height:1.55; border-radius:3px;'>"
            "<strong>No problem-specific category signals detected.</strong> Pick at least 2 "
            "categories below — the rubric requires explicit edge-case coverage for full credit."
            "</div>"
        )
        return

    # Sort by signal strength (number of hits)
    matched.sort(key=lambda x: -len(x[3]))
    top = matched[:4]
    rows_html = "".join(
        f"<li style='margin:4px 0;'><strong>{lbl}</strong> — {reason} "
        f"<span style='color:#8b949e; font-size:11px;'>(matched: {', '.join(hits[:3])})</span></li>"
        for (_cid, lbl, reason, hits) in top
    )
    sd2_edge_suggestions_html.value = (
        "<div style='background:#fff8e6; border-left:3px solid #d1a72a; padding:10px 14px; "
        "margin:6px 0 10px 0; font-size:12.5px; line-height:1.55; border-radius:3px;'>"
        "<strong>👉 Suggested categories for THIS problem</strong> "
        "<span style='color:#8b949e; font-size:11px;'>(based on prompt keyword scan)</span>"
        f"<ul style='margin:6px 0 4px 18px;'>{rows_html}</ul>"
        "<div style='font-size:11.5px; color:#57606a; margin-top:6px;'>"
        "Tick the &#39;applies&#39; checkbox AND select 1-2 canned scenarios for each. "
        "The grader rewards explicit picks that match the problem&#39;s actual mechanics."
        "</div></div>"
    )

# Insert the suggestions banner at the top of the edge-case panel.
_sd2_edge_panel_children.insert(0, sd2_edge_suggestions_html)
sd2_edge_panel_box = widgets.VBox(_sd2_edge_panel_children)

# ---- Grader button + output ----
sd2_grade_btn = widgets.Button(
    description="Get Schema Design Feedback",
    button_style="success",
    layout=widgets.Layout(width="280px", height="36px"),
)
sd2_grade_out = widgets.Output()


# ============================================================
# Dynamic rebuild functions
# ============================================================

def _sd2_rebuild_dim_box():
    """Build dim_joins as per-dim collapsible blocks (Approach 2).
    Top-level checkbox: 'use this dim — yes/no.' When checked, the panel
    expands to show that dim's attributes as a sub-table with usage dropdown."""
    p = STATE.get("problem") or {}
    candidates = p.get("candidate_dimensions", []) or []
    _sd2_state["dim_checkboxes"] = {}
    _sd2_state["dim_attr_widgets"] = {}  # dim_name -> {attr_name: (checkbox, usage_dd)}
    rows = []
    if not candidates:
        rows.append(widgets.HTML(
            "<i>No candidate_dimensions in this problem. Pick from the standard "
            "pharmacy dim roster manually in your rationale.</i>"
        ))
    for d in candidates:
        if not isinstance(d, dict):
            continue
        name = d.get("name", "?")
        key = d.get("key", "?")
        desc = d.get("description", "")
        attrs = d.get("attributes", []) or []
        # If candidate dim doesn't list attributes, parse them from the description
        # heuristically (split on commas)
        if not attrs and desc:
            attrs = [a.strip() for a in desc.split(",") if a.strip()]

        cb = widgets.Checkbox(
            value=False,
            description=f"{name}  (key: {key})",
            indent=False,
            layout=widgets.Layout(width="100%"),
        )
        cb.observe(_sd2_on_dim_checked, names="value")
        _sd2_state["dim_checkboxes"][name] = cb
        rows.append(cb)
        if desc:
            rows.append(widgets.HTML(
                f"<div style='margin: 0 0 6px 28px; font-size: 12px; color: #57606a;'>"
                f"{desc}</div>"
            ))

        # Per-attribute table (visible only conceptually — dropdowns are static)
        _sd2_state["dim_attr_widgets"][name] = {}
        if attrs:
            attr_rows = [widgets.HTML(
                "<div style='margin: 4px 0 4px 28px; font-size: 12px; color: #444; "
                "font-weight: 600;'>Attributes — pick which to use and how:</div>"
            )]
            for attr in attrs[:10]:  # cap at 10 attributes
                attr_label = attr if len(attr) < 80 else attr[:77] + "..."
                attr_cb = widgets.Checkbox(
                    value=False,
                    description=attr_label,
                    indent=False,
                    layout=widgets.Layout(width="60%", margin="0 0 0 28px"),
                )
                usage_dd = widgets.Dropdown(
                    options=[
                        ("usage", ""),
                        ("group by", "group_by"),
                        ("filter", "filter"),
                        ("drill-down attribute", "attr"),
                        ("display only", "display"),
                        ("not used", "not_used"),
                    ],
                    layout=widgets.Layout(width="200px"),
                )
                _sd2_state["dim_attr_widgets"][name][attr] = (attr_cb, usage_dd)
                attr_rows.append(widgets.HBox([attr_cb, usage_dd]))
            attr_box = widgets.VBox(attr_rows, layout=widgets.Layout(margin="0 0 6px 0"))
            rows.append(attr_box)
    sd2_dim_box.children = rows


def _sd2_on_dim_checked(change):
    """Triggered when any dim checkbox toggles. Rebuild SCD per-dim AND
    conformed checkboxes."""
    _sd2_rebuild_scd_box()
    _sd2_rebuild_conformed_box()


def _sd2_rebuild_scd_box():
    """Build per-dim SCD walkthrough. Restructured so the default landing place
    is Type 1 (overwrite) — users must justify Type 2 with an explicit
    historical-reproducibility need. Type 0 is rare; reserved for truly static
    dims like dim_date.

    Decision tree per dim:
      Q1: Does this dim have ANY attribute that changes over time?
        - "No, never changes (static reference like dim_date)" -> Type 0
        - "Maybe small updates (e.g., a typo correction, a renamed label)" -> Type 1
        - "Yes, attributes do change over time" -> ask Q2
      Q2 (only if Q1=yes): Does the dashboard need historical reports to show the
          value that was TRUE AT THE TIME of the fact event (not just latest)?
        - "No, dashboard only needs current value" -> Type 1 (overwrite)
        - "Yes, historical reports must reflect what was true at fact time" -> Type 2
    """
    rows = []
    _sd2_state["scd_dropdowns"] = {}
    for name, cb in _sd2_state["dim_checkboxes"].items():
        if not cb.value:
            continue
        # Header for this dim
        rows.append(widgets.HTML(
            f"<div style='font-weight:600; font-size:13px; color:#0c447c; margin-top:10px;'>"
            f"<code>{name}</code> — SCD type walkthrough</div>"
        ))
        # Wrapping HTML labels above each dropdown so questions display fully.
        q1_label = widgets.HTML(
            f"<div style='font-size:12.5px; font-weight:600; margin:6px 0 2px 0; line-height:1.5;'>"
            f"Q1 for <code>{name}</code>: Does this dim have ANY attribute that changes over time?"
            f"</div>"
        )
        q1 = widgets.Dropdown(
            options=[
                ("— pick —", ""),
                ("No, never changes (truly static reference like dim_date)", "static"),
                ("Maybe small corrections (typos, renames) but business meaning is stable", "stable"),
                ("Yes, real attribute changes happen over time", "changes"),
            ],
            description="",
            layout=widgets.Layout(width="100%"),
        )
        q2_label = widgets.HTML(
            f"<div style='font-size:12.5px; font-weight:600; margin:6px 0 2px 0; line-height:1.5;'>"
            f"Q2 for <code>{name}</code> (only if Q1=Yes): Does the dashboard need historical reports "
            f"to show the value that was TRUE AT THE TIME of the fact event (not just the current value)?"
            f"</div>"
        )
        q2 = widgets.Dropdown(
            options=[
                ("— pick —", ""),
                ("No — dashboard only needs the latest/current value", "latest"),
                ("Yes — historical reports must reflect the value AT THE TIME of the fact event", "history"),
            ],
            description="",
            layout=widgets.Layout(width="100%"),
        )
        # Per-dim SCD dropdown (the answer)
        scd_dd = widgets.Dropdown(
            options=[
                ("— pick —", ""),
                ("Type 0 — Immutable (never updates, e.g., dim_date)", "type0"),
                ("Type 1 — Overwrite (keep latest value only — DEFAULT for most dims)", "type1"),
                ("Type 2 — Track history (valid_from/valid_to/is_current — only when historical reproducibility matters)", "type2"),
            ],
            description=f"{name} type:",
            style={"description_width": "180px"},
            layout=widgets.Layout(width="900px"),
        )
        prev = _sd2_state["scd_picks"].get(name, "")
        if prev:
            scd_dd.value = prev
        def _on_scd_change(change, dim_name=name):
            _sd2_state["scd_picks"][dim_name] = change["new"]
        scd_dd.observe(_on_scd_change, names="value")
        _sd2_state["scd_dropdowns"][name] = scd_dd

        # Apply button per dim
        apply_btn = widgets.Button(
            description=f"Apply for {name}",
            button_style="info",
            layout=widgets.Layout(width="220px"),
        )
        apply_out = widgets.Output()

        def _on_apply(b, dim_name=name, q1_w=q1, q2_w=q2, scd_w=scd_dd, out_w=apply_out):
            q1v = q1_w.value
            q2v = q2_w.value
            if not q1v:
                with out_w:
                    clear_output(wait=True)
                    print(f"Answer Q1 for {dim_name}.")
                return
            # Branch on Q1
            if q1v == "static":
                rec, label, defn = (
                    "type0",
                    "Type 0 — Immutable",
                    "Type 0 means: this dim never changes for the same business entity. "
                    "No history tracking, no overwrites. Reserved for truly static reference "
                    "data like dim_date (calendar attributes don't change). Rarely the right "
                    "choice for business dims."
                )
            elif q1v == "stable":
                rec, label, defn = (
                    "type1",
                    "Type 1 — Overwrite",
                    "Type 1 means: when the source updates an attribute (typo correction, "
                    "rename, classification change), the dim row gets overwritten with the new "
                    "value. Old value is gone. This is the DEFAULT for most dims. Picked because "
                    "the changes you described (typos, renames) don't carry historical meaning — "
                    "the dashboard just needs the current value."
                )
            else:  # changes
                if not q2v:
                    with out_w:
                        clear_output(wait=True)
                        print(f"Answer Q2 for {dim_name}.")
                    return
                if q2v == "latest":
                    rec, label, defn = (
                        "type1",
                        "Type 1 — Overwrite",
                        "Type 1 — even though attributes change, the dashboard only needs the "
                        "current value. Old values get overwritten on each refresh. This is the "
                        "RIGHT default whenever historical reproducibility isn't required. "
                        "Type 2 is overkill if the metric doesn't care what the value was at "
                        "the time of the fact event."
                    )
                else:
                    rec, label, defn = (
                        "type2",
                        "Type 2 — Track history",
                        "Type 2 — required because historical reports MUST show the value "
                        "that was true AT THE TIME of the fact event. The dim stores multiple "
                        "rows per business entity, each with valid_from/valid_to/is_current "
                        "columns. The fact joins to the dim row valid at the fact's event_ts. "
                        "Pick this only when you have a clear historical-reproducibility need: "
                        "plan-year boundaries, formulary changes, segment reclassifications. "
                        "Defaulting to Type 2 across all dims wastes storage and complicates joins."
                    )
            scd_w.value = rec
            _sd2_state["scd_picks"][dim_name] = rec
            with out_w:
                clear_output(wait=True)
                print(f"Recommended for {dim_name}: {label}\\n\\n{defn}")
        apply_btn.on_click(_on_apply)

        rows.append(q1_label)
        rows.append(q1)
        rows.append(q2_label)
        rows.append(q2)
        rows.append(apply_btn)
        rows.append(apply_out)
        rows.append(scd_dd)
    if not rows:
        rows.append(widgets.HTML(
            "<i>Pick dims in field 3 first; SCD walkthroughs appear here per dim.</i>"
        ))
    sd2_scd_box.children = rows


def _sd2_rebuild_conformed_box():
    """Build conformed-dim checkboxes for currently-checked dims in field 4."""
    rows = [widgets.HTML(
        "<div style='font-size:12px; color:#57606a; margin-bottom:6px;'>"
        "Only relevant if the problem proposes multiple facts. Mark all N/A for single-fact drills."
        "</div>"
    )]
    _sd2_state["conformed_checkboxes"] = {}
    any_dim = False
    for name, cb in _sd2_state["dim_checkboxes"].items():
        if not cb.value:
            continue
        any_dim = True
        prev = _sd2_state["conformed_picks"].get(name, False)
        conformed_cb = widgets.Checkbox(
            value=prev,
            description=name,
            indent=False,
            layout=widgets.Layout(width="100%"),
        )
        def _on_conformed_change(change, dim_name=name):
            _sd2_state["conformed_picks"][dim_name] = change["new"]
        conformed_cb.observe(_on_conformed_change, names="value")
        _sd2_state["conformed_checkboxes"][name] = conformed_cb
        rows.append(conformed_cb)
    if not any_dim:
        rows.append(widgets.HTML(
            "<i>Pick dims in field 4 first; conformed checkboxes appear here.</i>"
        ))
    sd2_conformed_box.children = rows


def _sd2_make_model_row(initial=None):
    """Create one model row (HBox of name TextInput + purpose Dropdown +
    layer Dropdown + mat Dropdown + Remove btn). The purpose dropdown teaches
    the layer mapping: when the user picks a purpose, the layer is auto-suggested."""
    initial = initial or {}
    # continuous_update=False so the value only fires on focus-out / Enter,
    # not on every keystroke. Prevents the test_selections dict from
    # accumulating stale entries for partial names like 'm', 'ma', 'mar', ...
    name_ta = widgets.Text(
        value=initial.get("name", ""),
        placeholder="model_name (e.g., fact_claim)",
        layout=widgets.Layout(width="200px"),
        continuous_update=False,
    )
    purpose_dd = widgets.Dropdown(
        options=[
            ("purpose", ""),
            ("Raw landing (pass-through from source)", "raw"),
            ("Data cleaning (rename, cast, dedup)", "cleaning"),
            ("Data transformation (pivot, grain shift, reusable joins)", "transformation"),
            ("Business rules + dim joins (granular fact)", "fact"),
            ("Aggregation + KPI rollup (pre-aggregated mart)", "aggregation"),
            ("SCD-2 history maintenance (snapshot)", "snapshot"),
            ("Other (explain in rationale)", "other"),
        ],
        value=initial.get("purpose", ""),
        layout=widgets.Layout(width="280px"),
        tooltip="Pick the purpose; the layer dropdown is auto-suggested from this.",
    )
    layer_dd = widgets.Dropdown(
        options=[
            ("layer", ""),
            ("source", "source"),
            ("staging stg_", "stg"),
            ("intermediate int_", "int"),
            ("mart fct_", "fct"),
            ("mart mart_", "mart"),
            ("snapshot", "snapshot"),
        ],
        value=initial.get("layer", ""),
        layout=widgets.Layout(width="140px"),
    )
    mat_dd = widgets.Dropdown(
        options=[
            ("materialization", ""),
            ("table", "table"),
            ("view", "view"),
            ("incremental", "incremental"),
            ("ephemeral", "ephemeral"),
            ("snapshot", "snapshot"),
            ("N/A", "na"),
        ],
        value=initial.get("mat", ""),
        layout=widgets.Layout(width="160px"),
    )
    remove_btn = widgets.Button(
        description="✕",
        button_style="danger",
        layout=widgets.Layout(width="40px"),
        tooltip="Remove this model row",
    )

    # Auto-suggest layer when purpose changes
    _purpose_to_layer = {
        "raw": "source",
        "cleaning": "stg",
        "transformation": "int",
        "fact": "fct",
        "aggregation": "mart",
        "snapshot": "snapshot",
        "other": "",
    }
    def _on_purpose_change(change, layer_widget=layer_dd):
        suggested = _purpose_to_layer.get(change["new"], "")
        if suggested and not layer_widget.value:
            layer_widget.value = suggested
    purpose_dd.observe(_on_purpose_change, names="value")

    row = widgets.HBox([name_ta, purpose_dd, layer_dd, mat_dd, remove_btn])
    row._sd2_model_widgets = (name_ta, layer_dd, mat_dd, purpose_dd)

    def _on_remove(b):
        children = list(sd2_models_box.children)
        for i, child in enumerate(children):
            if child is row:
                children.pop(i)
                sd2_models_box.children = tuple(children)
                _sd2_sync_models()
                _sd2_rebuild_tests_box()
                break
    remove_btn.on_click(_on_remove)

    def _on_field_change(change):
        _sd2_sync_models()
        _sd2_rebuild_tests_box()
    name_ta.observe(_on_field_change, names="value")
    layer_dd.observe(_on_field_change, names="value")
    mat_dd.observe(_on_field_change, names="value")

    return row


def _sd2_sync_models():
    """Read current model rows into _sd2_state['models'].
    Each row's _sd2_model_widgets tuple is (name, layer, mat, purpose)."""
    models = []
    for row in sd2_models_box.children:
        if hasattr(row, "_sd2_model_widgets"):
            widgets_tuple = row._sd2_model_widgets
            name_ta = widgets_tuple[0]
            layer_dd = widgets_tuple[1]
            mat_dd = widgets_tuple[2]
            purpose_dd = widgets_tuple[3] if len(widgets_tuple) > 3 else None
            models.append({
                "name": (name_ta.value or "").strip(),
                "layer": layer_dd.value,
                "mat": mat_dd.value,
                "purpose": purpose_dd.value if purpose_dd is not None else "",
            })
    _sd2_state["models"] = models


def _sd2_on_add_model(b):
    children = list(sd2_models_box.children)
    children.append(_sd2_make_model_row())
    sd2_models_box.children = tuple(children)
    _sd2_sync_models()
    _sd2_rebuild_tests_box()
sd2_add_model_btn.on_click(_sd2_on_add_model)


def _sd2_rebuild_translate_box():
    """Build the granular translate-the-asks pre-form exercise. Each stakeholder ask
    is decomposed into the design pieces that compose it: Numerator (measure on
    fact), Denominator (measure on fact, for rates), Filter dim (FK on fact),
    Drill-down attribute (column on a joined dim), and Supporting timestamp
    (timestamp column on fact). Empty fields = not relevant for this ask."""
    p = STATE.get("problem") or {}
    asks = p.get("stakeholder_asks", []) or []
    _sd2_state["translate_decomp_widgets"] = {}
    if not asks:
        sd2_translate_box.children = [widgets.HTML(
            "<i>No stakeholder_asks in this problem (older problem format). The translate "
            "exercise is unavailable; go straight to the form below.</i>"
        )]
        return
    rows = [widgets.HTML(
        "<div style='font-size:12.5px; color:#57606a; margin-bottom:8px; line-height:1.55;'>"
        "For each stakeholder ask, decompose it into the design pieces it requires. "
        "Fill what applies, leave the rest blank. This primes you for the main form: "
        "<strong>Numerator/Denominator</strong> become measure columns on the fact, "
        "<strong>Filter dim</strong> becomes an FK on the fact, <strong>Drill-down "
        "attribute</strong> lives on the joined dim (NOT on the fact), and "
        "<strong>Supporting timestamp</strong> is a derived ts column on the fact "
        "(e.g., <code>first_response_ts</code>)."
        "</div>"
    )]

    field_specs = [
        ("numerator", "Numerator",
         "Count or sum on the fact (e.g., count(*) where reply_within_24h=1)"),
        ("denominator", "Denominator",
         "Count or sum on the fact for the base of a rate (e.g., count(*) of all messages). Leave blank if not a rate."),
        ("filter_dim", "Filter dim (FK)",
         "Dim used to slice/filter (e.g., dim_channel, dim_condition_cohort). Becomes an FK on fact."),
        ("drilldown", "Drill-down attribute",
         "Attribute on a joined dim used to break out the metric (e.g., dim_patient.age_band). NOT a column on fact."),
        ("timestamp", "Supporting timestamp",
         "Derived timestamp on fact (e.g., first_response_ts = MIN(event_ts) WHERE event_type='reply'). Leave blank if not a timing question."),
    ]

    for idx, ask in enumerate(asks):
        rows.append(widgets.HTML(
            f"<div style='font-size:13px; margin-top:14px; line-height:1.5; "
            f"padding:8px 12px; background:#f6f8fa; border-left:3px solid #0969da; "
            f"border-radius:3px;'>"
            f"<strong>Ask {idx + 1}:</strong> {ask}</div>"
        ))
        ask_widgets = {}
        prev_decomp = _sd2_state["translate_decomp"].get(idx, {}) or {}
        for field_key, field_label, field_help in field_specs:
            txt = widgets.Text(
                description=field_label,
                placeholder=field_help,
                style={"description_width": "150px"},
                layout=widgets.Layout(width="780px"),
                continuous_update=False,
            )
            prev_val = prev_decomp.get(field_key, "") if isinstance(prev_decomp, dict) else ""
            if prev_val:
                txt.value = prev_val
            def _on_decomp_change(change, ask_idx=idx, fk=field_key):
                bucket = _sd2_state["translate_decomp"].setdefault(ask_idx, {})
                bucket[fk] = change["new"]
            txt.observe(_on_decomp_change, names="value")
            ask_widgets[field_key] = txt
            rows.append(txt)
        rows.append(widgets.HTML(
            "<div style='font-size:11.5px; color:#8b949e; margin:4px 0 0 8px;'>"
            "<em>Tip: most rate-style asks need numerator + denominator + at least one filter dim. "
            "Most timing asks need a supporting timestamp + filter dim. Most demographic "
            "breakouts need a drill-down attribute, no new fact column.</em>"
            "</div>"
        ))
        _sd2_state["translate_decomp_widgets"][idx] = ask_widgets
    sd2_translate_box.children = rows


_SD2_HINT_WIDGETS = {}        # field_id -> hint HTML widget (lazy populated)
_SD2_EXAMPLE_WIDGETS = {}     # field_id -> example HTML widget (lazy populated)


def _sd2_init_widget_maps():
    """Populate the field-id -> widget maps once (after widgets exist)."""
    global _SD2_HINT_WIDGETS, _SD2_EXAMPLE_WIDGETS
    _SD2_HINT_WIDGETS = {
        "business_process": sd2_hint_business_process,
        "grain": sd2_hint_grain,
        "fact_columns": sd2_hint_fact_columns,
        "key_strategy": sd2_hint_key,
        "dim_joins": sd2_hint_dim_joins,
        "scd_per_dim": sd2_hint_scd,
        "conformed_dims": sd2_hint_conformed,
        "models": sd2_hint_models,
        "tests": sd2_hint_tests,
        "idempotency": sd2_hint_idempotency,
        "late_arriving": sd2_hint_late_arriving,
        "edge_cases": sd2_hint_edge,
    }
    _SD2_EXAMPLE_WIDGETS = {
        "business_process": sd2_example_business_process,
        "grain": sd2_example_grain,
        "fact_columns": sd2_example_fact_columns,
        "key_strategy": sd2_example_key,
        "dim_joins": sd2_example_dim_joins,
        "scd_per_dim": sd2_example_scd,
        "conformed_dims": sd2_example_conformed,
        "models": sd2_example_models,
        "tests": sd2_example_tests,
        "idempotency": sd2_example_idempotency,
        "late_arriving": sd2_example_late_arriving,
        "edge_cases": sd2_example_edge,
    }


def _sd2_cache_problem_content():
    """Read field_hints and worked_example_per_field from the loaded problem
    and cache them in _sd2_state. Called once on problem load. Mode rendering
    then pulls from these caches without re-parsing problem JSON each time."""
    p = STATE.get("problem") or {}
    hints = p.get("field_hints", {}) or {}
    examples = p.get("worked_example_per_field", {}) or {}
    _sd2_state["problem_hints"] = {fid: (hints.get(fid) or "").strip() for fid in _SD2_HINT_WIDGETS}
    _sd2_state["worked_examples_raw"] = {fid: (examples.get(fid) or "").strip() for fid in _SD2_EXAMPLE_WIDGETS}


# Generic fallback hints (used in solve mode when problem has no field_hints)
_SD2_GENERIC_HINTS = {
    "business_process": (
        "Name the real-world activity this fact table measures, in one sentence. "
        "Anchors every later decision — every fact column should serve this activity."
    ),
    "grain": (
        "State the OUTPUT grain explicitly. If the prompt says '~15M rows after 1 year' "
        "or 'one row per X', that IS the grain. Justify why this grain (not a finer or "
        "coarser one) supports the asks."
    ),
    "fact_columns": (
        "List the columns you'd put on the fact: PK + FKs to each dim + measure columns + "
        "supporting timestamps. Each metric becomes ONE measure column. Don't pivot a "
        "category (channel, status) into multiple columns."
    ),
    "key_strategy": (
        "This is the FACT'S key strategy, not a dim's SCD-2 strategy. Ask: is the natural "
        "key (e.g., claim_id) stable, unique at the grain, and good enough?"
    ),
    "dim_joins": (
        "For each 'by X' or 'filter by X' in the stakeholder asks, you need to join dim_X. "
        "Pick checkboxes for every dim that supports a stated ask."
    ),
    "scd_per_dim": (
        "SCD types apply to DIMS, not facts. For each dim you picked, ask: do attributes "
        "change over time? Does the report need to reflect the value AT THE TIME of the "
        "fact event? If yes → Type 2. If no → Type 1."
    ),
    "conformed_dims": (
        "Only relevant when the problem mentions multiple facts. If the prompt only asks "
        "for ONE fact table, mark this N/A in the rationale."
    ),
    "models": (
        "Add one row per dbt model you'd build. Typical: src_X (source) → stg_X (staging "
        "cleanup) → fact_X (mart, your output). Pick layer + materialization for each."
    ),
    "tests": (
        "For each model in field 7, pick at least 2 tests. Always include unique + not_null "
        "on the grain key. Add relationships to every dim FK. Custom singular test for any "
        "business rule that doesn't fit a standard test (e.g., gross >= net)."
    ),
    "idempotency": (
        "If your fact aggregates events, can you safely re-run the model? Picks: MERGE/UPSERT "
        "(overwrite at the grain) or window-function rebuild are typical. Snapshot is for "
        "SCD-2 dims, not aggregated facts."
    ),
    "late_arriving": (
        "If the prompt says events arrive out of order or late, this matters. Pick a strategy "
        "and name the trade-off (consistency vs reproducibility)."
    ),
    "edge_cases": (
        "List the tricky scenarios you'd test for. The prompt often embeds an explicit edge "
        "question — answer that one, plus 2 to 3 more you'd watch for."
    ),
}


def _sd2_apply_mode():
    """Re-render hint and example widgets based on current mode.
    Solve mode: hint = generic or problem-specific; example = collapsible reveal.
    Walkthrough mode: hint = full worked example formatted as 'Answer + Why';
                       example reveal hidden (redundant).

    Defensive: always re-cache problem content from STATE.problem first so we
    don't depend on refresh_subtopic_form() having run already. This covers the
    edge case where the user toggles mode after a problem is loaded but the
    refresh hooks haven't fired (e.g., loaded via saved-dropdown, or if the
    forward-reference try/except suppressed an error)."""
    if not _SD2_HINT_WIDGETS:
        _sd2_init_widget_maps()
    mode = _sd2_state.get("mode", "solve")

    # Always re-pull from STATE.problem so the cache reflects the current problem
    p = STATE.get("problem") or {}
    if p:
        _sd2_cache_problem_content()
    problem_hints = _sd2_state.get("problem_hints", {}) or {}
    worked = _sd2_state.get("worked_examples_raw", {}) or {}

    # Case 1: no problem loaded yet
    if not p:
        for fid, hint_w in _SD2_HINT_WIDGETS.items():
            hint_w.value = (
                '<div style="background:#fff8c5; border-left:3px solid #d4a72c; '
                'padding:10px 14px; margin-bottom:8px; font-size:13px; line-height:1.55; '
                'border-radius:3px;"><strong>👉 No problem loaded yet.</strong><br>'
                'Click <strong>Generate Problem</strong> in section 1 to create a schema_design '
                f'problem. Then this hint area will show a {("worked answer + lay-language rationale" if mode == "walkthrough" else "problem-specific hint")} '
                'for THIS specific problem.</div>'
            )
            ex_w = _SD2_EXAMPLE_WIDGETS.get(fid)
            if ex_w is not None:
                ex_w.value = ""
        try:
            if mode == "walkthrough":
                sd2_grade_btn.description = "Check Understanding"
            else:
                sd2_grade_btn.description = "Get Schema Design Feedback"
        except Exception:
            pass
        return

    # Case 2: problem loaded but missing worked_example_per_field entirely
    # (older format from before walkthrough mode was added). Show distinctive
    # message in walkthrough mode.
    has_any_worked = any((v or "").strip() for v in worked.values())
    if mode == "walkthrough" and not has_any_worked:
        for fid, hint_w in _SD2_HINT_WIDGETS.items():
            hint_w.value = (
                '<div style="background:#fbe9e7; border-left:3px solid #c62828; '
                'padding:10px 14px; margin-bottom:8px; font-size:13px; line-height:1.55; '
                'border-radius:3px;">'
                '<strong style="color:#c62828;">⚠ This problem has no worked examples '
                '(older format).</strong><br>'
                'Walkthrough mode needs <code>worked_example_per_field</code> data, which '
                'is only emitted by the latest generator. Either:<br>'
                '&nbsp;&nbsp;&bull; Switch back to <strong>Solve mode</strong> and use the '
                'generic hints + collapsible example reveals, OR<br>'
                '&nbsp;&nbsp;&bull; <strong>Generate a fresh problem</strong> in section 1 — '
                'new problems include the walkthrough data.<br><br>'
                f'Generic guidance for this field: {_SD2_GENERIC_HINTS.get(fid, "")}'
                '</div>'
            )
            ex_w = _SD2_EXAMPLE_WIDGETS.get(fid)
            if ex_w is not None:
                ex_w.value = ""
        try:
            sd2_grade_btn.description = "Check Understanding"
        except Exception:
            pass
        return

    for fid, hint_w in _SD2_HINT_WIDGETS.items():
        ex_w = _SD2_EXAMPLE_WIDGETS.get(fid)
        problem_hint = problem_hints.get(fid, "")
        worked_raw = worked.get(fid, "")
        worked_html = worked_raw.replace(chr(10), "<br>") if worked_raw else ""

        if mode == "walkthrough" and worked_raw:
            # Hint area shows the worked example (Answer + Why) prominently
            hint_w.value = (
                f'<div style="background:#f0f8f0; border-left:4px solid #1a7f37; '
                f'padding:10px 14px; margin-bottom:8px; font-size:12.5px; line-height:1.6; '
                f'border-radius:3px;">'
                f'<div style="font-weight:600; color:#1a7f37; margin-bottom:6px; font-size:13px;">'
                f'📖 Walkthrough — read the answer, then paraphrase in your own words below'
                f'</div>'
                f'<div>{worked_html}</div>'
                f'</div>'
            )
            # Hide the redundant example reveal
            if ex_w is not None:
                ex_w.value = ""
        elif mode == "walkthrough":
            # Walkthrough requested but no worked example available
            hint_w.value = (
                '<div style="background:#fbe9e7; border-left:3px solid #c62828; '
                'padding:8px 12px; margin-bottom:8px; font-size:12.5px; line-height:1.5; '
                'border-radius:3px;"><strong style="color:#c62828;">⚠ No worked example '
                'available for this field on this problem (older format). Try Solve mode '
                'or fall back to the generic hint:</strong><br><br>'
                f'{_SD2_GENERIC_HINTS.get(fid, "")}'
                '</div>'
            )
            if ex_w is not None:
                ex_w.value = ""
        else:
            # Solve mode — generic or problem-specific hint, example reveal collapsed
            if problem_hint:
                hint_w.value = (
                    f'<div class="sd2-field-hint" style="background:#fff8e1; border-left:3px solid #f9a825; '
                    f'padding:8px 12px; margin-bottom:8px; font-size:12.5px; line-height:1.5; border-radius:3px;">'
                    f'<strong>👉 Hint for THIS problem:</strong> {problem_hint}'
                    f'<div style="font-size:11.5px; color:#57606a; margin-top:6px; font-style:italic;">'
                    f'Generic guidance: {_SD2_GENERIC_HINTS.get(fid, "")}</div>'
                    f'</div>'
                )
            else:
                hint_w.value = (
                    f'<div class="sd2-field-hint" style="background:#eef5fc; border-left:3px solid #0969da; '
                    f'padding:8px 12px; margin-bottom:8px; font-size:12.5px; line-height:1.5; border-radius:3px;">'
                    f'<strong>Hint:</strong> {_SD2_GENERIC_HINTS.get(fid, "")}</div>'
                )
            # Restore the example reveal (collapsed by default)
            if ex_w is not None:
                if worked_raw:
                    ex_w.value = (
                        '<details style="margin: 0 0 6px 0; border-left: 3px solid #1a7f37; padding-left: 10px;">'
                        '<summary style="cursor: pointer; color: #1a7f37; font-weight: 600; font-size: 12.5px;">'
                        '💡 Show example answer for this problem (peek when stuck — try blind first)</summary>'
                        '<div style="margin-top: 6px; font-size: 12.5px; line-height: 1.55; padding: 10px 12px; '
                        'background: #f0f8f0; border-radius: 3px; border-left: 2px solid #1a7f37;">'
                        f'{worked_html}'
                        '</div></details>'
                    )
                else:
                    ex_w.value = (
                        '<details style="margin: 0 0 6px 0; border-left: 3px solid #1a7f37; padding-left: 10px;">'
                        '<summary style="cursor: pointer; color: #1a7f37; font-weight: 600; font-size: 12.5px;">'
                        '💡 Show example answer for this problem (peek when stuck — try blind first)</summary>'
                        '<div style="margin-top: 6px; font-size: 12px; color: #57606a; padding: 8px 10px; '
                        'background: #f0f8f0; border-radius: 3px;"><i>No worked example available for this '
                        'field on this problem (older format).</i>'
                        '</div></details>'
                    )

    # Update the grade button label to match mode
    try:
        if mode == "walkthrough":
            sd2_grade_btn.description = "Check Understanding"
            sd2_grade_btn.tooltip = "Grade your paraphrase against the worked example"
        else:
            sd2_grade_btn.description = "Get Schema Design Feedback"
            sd2_grade_btn.tooltip = "Grade your design against the rubric"
    except Exception:
        pass


def _sd2_on_mode_change(change):
    _sd2_state["mode"] = change["new"]
    _sd2_apply_mode()


sd2_mode_toggle.observe(_sd2_on_mode_change, names="value")


def _sd2_update_worked_examples():
    """Cache raw worked examples from the problem and re-render via apply_mode."""
    _sd2_cache_problem_content()
    _sd2_apply_mode()


def _sd2_update_field_hints():
    """Cache problem-specific hints and re-render via apply_mode."""
    _sd2_cache_problem_content()
    _sd2_apply_mode()


def _sd2_apply_saved_responses(saved_responses):
    """Populate the schema_design form from a previously-saved attempt dict.
    Called from refresh_subtopic_form() AFTER all dynamic widgets have been
    rebuilt, so the dim checkboxes, scd dropdowns, and model rows exist."""
    if not isinstance(saved_responses, dict):
        return

    # Plain text / textarea fields
    sd2_business_process_ta.value = str(saved_responses.get("business_process", "") or "")
    sd2_grain_ta.value = str(saved_responses.get("grain", "") or "")
    sd2_fact_cols_ta.value = str(saved_responses.get("fact_columns", "") or "")
    sd2_key_rationale_ta.value = str(saved_responses.get("key_rationale", "") or "")
    sd2_scd_rationale_ta.value = str(saved_responses.get("scd_rationale", "") or "")
    sd2_conformed_rationale_ta.value = str(saved_responses.get("conformed_rationale", "") or "")
    sd2_idem_rationale_ta.value = str(saved_responses.get("idempotency_rationale", "") or "")
    sd2_late_rationale_ta.value = str(saved_responses.get("late_arriving_rationale", "") or "")
    # Edge cases — restore checkbox + selected scenarios per category
    saved_edge_cats = saved_responses.get("edge_cases_per_category", {}) or {}
    saved_edge_applies = saved_responses.get("edge_cases_applies", {}) or {}
    for cat_id, sel_widget in _sd2_edge_cat_widgets.items():
        # Saved value may be: a list (new format), a string (old format), or missing
        saved_val = saved_edge_cats.get(cat_id, None)
        if isinstance(saved_val, list):
            valid = [v for v in saved_val if v in (sel_widget.options or ())]
            try:
                sel_widget.value = tuple(valid)
            except Exception:
                pass
        # Old text format — best effort: skip restoring picks (no clean mapping)
    for cat_id, applies_cb in _sd2_edge_applies_widgets.items():
        applies_cb.value = bool(saved_edge_applies.get(cat_id, False))

    # Dropdowns — set value if it's a valid option for that dropdown
    def _safe_set_dd(dd, val):
        if not val:
            return
        try:
            valid_values = [v for _label, v in dd.options]
            if val in valid_values:
                dd.value = val
        except Exception:
            pass

    _safe_set_dd(sd2_key_dd, saved_responses.get("key_strategy", ""))
    _safe_set_dd(sd2_idem_dd, saved_responses.get("idempotency_strategy", ""))
    _safe_set_dd(sd2_late_dd, saved_responses.get("late_arriving_strategy", ""))

    # Dim joins — check the boxes for previously-picked dims
    saved_dims = saved_responses.get("dim_joins", []) or []
    for dim_name, cb in _sd2_state.get("dim_checkboxes", {}).items():
        cb.value = dim_name in saved_dims
    # Trigger SCD + conformed box rebuild based on restored dim picks
    _sd2_rebuild_scd_box()
    _sd2_rebuild_conformed_box()

    # SCD per dim — restore picks (preserve in state, then re-render)
    saved_scd = saved_responses.get("scd_per_dim", {}) or {}
    for dim, val in saved_scd.items():
        _sd2_state["scd_picks"][dim] = val
    # Apply to the live dropdowns (rebuild already pulled from scd_picks, but re-set to be safe)
    for dim, dd in _sd2_state.get("scd_dropdowns", {}).items():
        if dim in saved_scd:
            try:
                _safe_set_dd(dd, saved_scd[dim])
            except Exception:
                pass

    # Conformed dims — check boxes for previously-picked
    saved_conformed = saved_responses.get("conformed_dims", []) or []
    for dim_name, cb in _sd2_state.get("conformed_checkboxes", {}).items():
        cb.value = dim_name in saved_conformed

    # Models — rebuild rows from saved list
    saved_models = saved_responses.get("models", []) or []
    if saved_models:
        sd2_models_box.children = []
        rows = []
        for m in saved_models:
            row = _sd2_make_model_row(initial=m)
            rows.append(row)
        sd2_models_box.children = tuple(rows)
        _sd2_sync_models()
        _sd2_rebuild_tests_box()

    # Tests per model — restore selections + custom text
    saved_tests = saved_responses.get("tests_per_model", {}) or {}
    saved_custom = saved_responses.get("tests_custom_per_model", {}) or {}
    _sd2_state["test_selections"] = {k: list(v) for k, v in saved_tests.items()}
    _sd2_state["test_custom"] = dict(saved_custom)
    _sd2_rebuild_tests_box()

    # Translate-the-asks picks (legacy single-dropdown format)
    saved_translate = saved_responses.get("translate_picks", {}) or {}
    norm_picks = {}
    for k, v in saved_translate.items():
        try:
            norm_picks[int(k)] = v
        except (ValueError, TypeError):
            norm_picks[k] = v
    _sd2_state["translate_picks"] = norm_picks

    # Translate-the-asks decomposition (granular per-ask sub-fields)
    saved_decomp = saved_responses.get("translate_decomp", {}) or {}
    norm_decomp = {}
    for k, v in saved_decomp.items():
        try:
            norm_decomp[int(k)] = dict(v) if isinstance(v, dict) else {}
        except (ValueError, TypeError):
            norm_decomp[k] = dict(v) if isinstance(v, dict) else {}
    _sd2_state["translate_decomp"] = norm_decomp
    _sd2_rebuild_translate_box()

    # Mode — restore the toggle
    saved_mode = saved_responses.get("mode", "solve")
    if saved_mode in ("solve", "walkthrough"):
        try:
            sd2_mode_toggle.value = saved_mode
            _sd2_state["mode"] = saved_mode
        except Exception:
            pass


def _sd2_rebuild_tests_box():
    """Build dbt tests panel for each named model in field 7."""
    _sd2_state["test_selections"] = _sd2_state.get("test_selections", {}) or {}
    _sd2_state["test_custom"] = _sd2_state.get("test_custom", {}) or {}
    rows = []
    # Static reminder callout — the standard fact test pack
    rows.append(widgets.HTML(
        "<div style='background:#f0f8f0; border-left:3px solid #1a7f37; "
        "padding:10px 14px; margin-bottom:10px; font-size:12.5px; line-height:1.55; "
        "border-radius:3px;'>"
        "<strong>Standard fact test pack — always include these on any <code>fct_</code> model:</strong>"
        "<ul style='margin:6px 0 0 18px; padding:0;'>"
        "<li><code>unique</code> on the grain key (e.g., claim_id, message_id)</li>"
        "<li><code>not_null</code> on the grain key</li>"
        "<li><code>not_null</code> on key timestamps the metrics need (e.g., sent_ts is the denominator for response rate)</li>"
        "<li><code>relationships</code> from each FK to its dim (one test per dim picked in field 3)</li>"
        "</ul>"
        "<div style='margin-top:6px;'>Then ADD design-specific custom checks "
        "(<code>gross_paid &gt;= net_paid</code>, <code>paid_ts &gt;= submit_ts</code>, etc).</div>"
        "</div>"
    ))
    test_options = [
        "unique on grain key",
        "not_null on grain key",
        "not_null on key timestamp(s)",
        "relationships to dim tables (FK integrity)",
        "accepted_values on enum/status column",
        "expression_is_true: range or business rule",
        "expression_is_true: chronology (e.g., paid_ts >= submit_ts)",
        "expect_column_values_to_match_regex (NDC, NPI format)",
        "expect_table_row_count_to_be_between (sanity check)",
    ]
    has_named = False
    for m in _sd2_state.get("models", []):
        name = m.get("name", "").strip()
        if not name:
            continue
        has_named = True
        rows.append(widgets.HTML(
            f"<div style='font-weight:600; margin-top:10px; "
            f"color:#0c447c;'>Tests for <code>{name}</code></div>"
        ))
        prev_sel = _sd2_state["test_selections"].setdefault(name, [])
        for t in test_options:
            cb = widgets.Checkbox(
                value=t in prev_sel,
                description=t,
                indent=False,
                layout=widgets.Layout(width="100%"),
            )
            def _on_test_change(change, model_name=name, test_label=t):
                sels = _sd2_state["test_selections"].setdefault(model_name, [])
                if change["new"] and test_label not in sels:
                    sels.append(test_label)
                elif not change["new"] and test_label in sels:
                    sels.remove(test_label)
            cb.observe(_on_test_change, names="value")
            rows.append(cb)
        custom_ta = widgets.Textarea(
            value=_sd2_state["test_custom"].get(name, ""),
            placeholder=(
                f"Custom singular test for {name}: a .sql file in tests/ that returns "
                f"rows when the test FAILS. Describe the business rule and SQL shape."
            ),
            layout=widgets.Layout(width="100%", min_height="60px"),
            description="Custom:",
            style={"description_width": "80px"},
        )
        custom_ta.add_class("diagnose-textarea")
        def _on_custom_change(change, model_name=name):
            _sd2_state["test_custom"][model_name] = change["new"]
        custom_ta.observe(_on_custom_change, names="value")
        rows.append(custom_ta)
    if not has_named:
        rows.append(widgets.HTML(
            "<i>Add a model in field 7 (with a name) first; per-model test panels appear here.</i>"
        ))
    sd2_tests_box.children = rows


# ============================================================
# Build accordion
# ============================================================

# Kimball-aligned panel order:
# 0 — Business process (NEW)
# 1 — Grain
# 2 — Dim joins
# 3 — SCD per dim
# 4 — Conformed dims
# 5 — Fact columns
# 6 — Surrogate vs natural key
# 7 — Models
# 8 — dbt tests per model
# 9 — Re-run safety
# 10 — Late-arriving / out-of-order events
# 11 — Edge cases
# ============================================================
# DECISION TREE WALKTHROUGHS
# Three steps each get a yes/no decision walkthrough that pre-fills the
# existing dropdown + rationale textarea: Surrogate vs natural key (4 Qs),
# Re-run safety (5 Qs), Late-arriving (4 Qs). Each walkthrough is a small
# VBox of dropdowns + a "Apply recommendation" button + an output area.
# ============================================================

# ----- Surrogate vs natural key walkthrough -----
sd2_dt_surr_q1 = widgets.Dropdown(
    options=[("— pick —", ""), ("Yes", "yes"), ("No", "no")],
    description="Q1: Source has a single column unique at the grain?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_surr_q2 = widgets.Dropdown(
    options=[("— pick —", ""), ("Yes", "yes"), ("No", "no")],
    description="Q2: That ID is stable (not renumbered/recycled)?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_surr_q3 = widgets.Dropdown(
    options=[("— pick —", ""), ("Yes", "yes"), ("No", "no")],
    description="Q3: Combining multiple sources with overlapping IDs?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_surr_q4 = widgets.Dropdown(
    options=[("— pick —", ""), ("Yes", "yes"), ("No", "no")],
    description="Q4: Building a DIM with attribute changes over time (SCD-2)?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_surr_btn = widgets.Button(
    description="Apply recommendation",
    button_style="info",
    layout=widgets.Layout(width="240px"),
)
sd2_dt_surr_out = widgets.Output()

def _on_surr_recommend(b):
    q1, q2, q3, q4 = sd2_dt_surr_q1.value, sd2_dt_surr_q2.value, sd2_dt_surr_q3.value, sd2_dt_surr_q4.value
    if not all([q1, q2, q3, q4]):
        with sd2_dt_surr_out:
            clear_output(wait=True)
            print("Answer all four questions before applying.")
        return
    if q4 == "yes":
        rec, label, rationale = (
            "scd2_surrogate",
            "SCD-2 surrogate",
            "Surrogate key with valid_from/valid_to/is_current. Required because this dim tracks attribute changes over time, so the same business entity needs multiple rows. The natural key alone can't be unique across versions."
        )
    elif q1 == "no":
        rec, label, rationale = (
            "composite",
            "Composite natural key",
            "Two or more columns together form the unique key. No single column is unique at the grain on its own."
        )
    elif q2 == "no":
        rec, label, rationale = (
            "surrogate",
            "Surrogate key",
            "Generate a new ID just for this table because the source ID is unstable (gets renumbered/recycled). The surrogate stays stable even when the source ID changes."
        )
    elif q3 == "yes":
        rec, label, rationale = (
            "surrogate",
            "Surrogate key (or composite natural key)",
            "Multiple source systems with overlapping IDs would collide if you used the natural key directly. Either generate a surrogate (globally unique across sources) or use a composite (system_id + source_id)."
        )
    else:
        rec, label, rationale = (
            "natural",
            "Natural key",
            "Use the source's existing ID directly. It's unique at the grain, stable across time, and from a single source. No need to generate a surrogate."
        )
    sd2_key_dd.value = rec
    sd2_key_rationale_ta.value = rationale
    with sd2_dt_surr_out:
        clear_output(wait=True)
        print(f"Recommended: {label}\\n\\n{rationale}\\n\\n(dropdown and rationale below have been pre-filled)")

sd2_dt_surr_btn.on_click(_on_surr_recommend)

sd2_dt_surr_box = widgets.VBox([
    widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:8px 12px; margin-bottom:6px; font-size:12.5px; line-height:1.5; border-radius:3px;'>"
        "<strong>Decision walkthrough.</strong> Answer the four questions; the form picks the right key strategy and pre-fills the dropdown + rationale."
        "</div>"
    ),
    sd2_dt_surr_q1,
    sd2_dt_surr_q2,
    sd2_dt_surr_q3,
    sd2_dt_surr_q4,
    sd2_dt_surr_btn,
    sd2_dt_surr_out,
])


# ----- Re-run safety walkthrough -----
sd2_dt_idem_q1 = widgets.Dropdown(
    options=[("— pick —", ""), ("Yes", "yes"), ("No", "no")],
    description="Q1: Will this fact rebuild on a schedule (every hour/day/week)?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_idem_q2 = widgets.Dropdown(
    options=[("— pick —", ""), ("Yes", "yes"), ("No", "no")],
    description="Q2: Will the same fact row ever need to be UPDATED later?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_idem_q3 = widgets.Dropdown(
    options=[("— pick —", ""), ("Yes", "yes"), ("No", "no")],
    description="Q3: Small enough that a full rebuild every run is OK?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_idem_q4 = widgets.Dropdown(
    options=[("— pick —", ""), ("Yes", "yes"), ("No", "no")],
    description="Q4: Need to keep full history of every version of every row?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_idem_q5 = widgets.Dropdown(
    options=[("— pick —", ""), ("Yes", "yes"), ("No", "no")],
    description="Q5: Source has a reliable change signal (event_ts/updated_at/CDC)?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_idem_btn = widgets.Button(
    description="Apply recommendation",
    button_style="info",
    layout=widgets.Layout(width="240px"),
)
sd2_dt_idem_out = widgets.Output()

def _on_idem_recommend(b):
    q1 = sd2_dt_idem_q1.value
    q2 = sd2_dt_idem_q2.value
    q3 = sd2_dt_idem_q3.value
    q4 = sd2_dt_idem_q4.value
    q5 = sd2_dt_idem_q5.value
    if not q1:
        with sd2_dt_idem_out:
            clear_output(wait=True)
            print("Answer Q1 before applying.")
        return
    if q1 == "no":
        rec, label, rationale = (
            "na",
            "N/A — one-shot ad-hoc query",
            "N/A means: re-run safety only matters for models that run on a schedule. A one-shot query you write once doesn't have a second run to compare against."
        )
    else:
        if not q2:
            with sd2_dt_idem_out:
                clear_output(wait=True)
                print("Answer Q2 before applying.")
            return
        if q2 == "no":
            rec, label, rationale = (
                "append_view",
                "Append-only fact + view that nets out corrections",
                "Append-only means: each fact row is born complete and never updated after insert. New events on later days create NEW rows, never touch existing ones. Picked because rows in this fact don't get updated — no MERGE logic needed."
            )
        else:
            if not q3:
                with sd2_dt_idem_out:
                    clear_output(wait=True)
                    print("Answer Q3 before applying.")
                return
            if q3 == "yes":
                rec, label, rationale = (
                    "full_rebuild",
                    "Full table rebuild every run",
                    "Full rebuild means: every run, drop the entire fact and rebuild from source. Re-run safety is guaranteed by construction (no duplicates possible). Picked because the fact is small enough that this is fast."
                )
            else:
                if not q4:
                    with sd2_dt_idem_out:
                        clear_output(wait=True)
                        print("Answer Q4 before applying.")
                    return
                if q4 == "yes":
                    rec, label, rationale = (
                        "snapshot",
                        "dbt snapshot — SCD-2 on the fact itself",
                        "Snapshot means: keep every version of every fact row over time with valid_from/valid_to/is_current. Heavyweight but required when audit/forensic needs reconstruction of any past state."
                    )
                else:
                    if not q5:
                        with sd2_dt_idem_out:
                            clear_output(wait=True)
                            print("Answer Q5 before applying.")
                        return
                    if q5 == "yes":
                        rec, label, rationale = (
                            "merge",
                            "MERGE / UPSERT on grain key",
                            "MERGE means: each run, look at source rows changed since last high-water mark and either UPDATE the existing fact row (if grain key exists) or INSERT new ones. Picked because the source has a reliable change signal and the fact is too big for full rebuild."
                        )
                    else:
                        rec, label, rationale = (
                            "window",
                            "Window function rebuild",
                            "Window function rebuild means: every run, read ALL source events and use LAST_VALUE/ROW_NUMBER to recompute the latest state per grain key. Defensive full rebuild driven by the event log. Picked because no reliable change signal from source — can't be selective."
                        )
    sd2_idem_dd.value = rec
    sd2_idem_rationale_ta.value = rationale
    with sd2_dt_idem_out:
        clear_output(wait=True)
        print(f"Recommended: {label}\\n\\n{rationale}\\n\\n(dropdown and rationale below have been pre-filled)")

sd2_dt_idem_btn.on_click(_on_idem_recommend)

sd2_dt_idem_box = widgets.VBox([
    widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:8px 12px; margin-bottom:6px; font-size:12.5px; line-height:1.5; border-radius:3px;'>"
        "<strong>Decision walkthrough.</strong> Answer the questions in order. Q1 = No skips the rest (N/A); otherwise continue. The form picks the right strategy and pre-fills the dropdown + rationale."
        "</div>"
    ),
    sd2_dt_idem_q1,
    sd2_dt_idem_q2,
    sd2_dt_idem_q3,
    sd2_dt_idem_q4,
    sd2_dt_idem_q5,
    sd2_dt_idem_btn,
    sd2_dt_idem_out,
])


# ----- Metrics classifier (Grain step) -----
# Dynamic table built from the loaded problem's stakeholder_asks. For each ask,
# the user picks: natural unit, aggregation pattern, group-by column, required
# raw ingredients. After filling, the natural unit column should show the same
# value for all rows — that value IS the grain.
sd2_metrics_box = widgets.VBox([
    widgets.HTML("<i>Generate a schema_design problem to see the metrics classifier.</i>")
])

def _sd2_rebuild_metrics_box():
    """Rebuild the per-ask metrics classifier. Each ask gets:
    - Natural unit dropdown (per claim, per patient, per message, ...)
    - Aggregation dropdown (count, sum, ratio, median, time-delta median, ...)
    - Filter dim dropdown (populated from the problem's candidate_dimensions)
    - Drill-down attribute dropdown (per-attribute on candidate dims)
    - Ingredients SelectMultiple (populated from the source schema columns)

    All widget references stored in _sd2_state['metrics_widgets'] so grade time
    can serialize the user's picks into the response payload."""
    p = STATE.get("problem") or {}
    asks = p.get("stakeholder_asks", []) or []
    candidates = p.get("candidate_dimensions", []) or []
    schema_ddl = p.get("schema_ddl", "") or ""
    _sd2_state["metrics_widgets"] = {}
    if not asks:
        sd2_metrics_box.children = [widgets.HTML(
            "<i>No stakeholder_asks in this problem.</i>"
        )]
        return

    # Build dim & attribute option lists once
    dim_options = [("— pick —", "")]
    attr_options = [("— pick —", ""), ("(no drill-down attribute needed)", "_none_")]
    for d in candidates:
        if not isinstance(d, dict):
            continue
        dn = d.get("name", "?")
        dim_options.append((dn, dn))
        # Parse attributes from desc if no explicit attributes list
        attrs = d.get("attributes", []) or []
        if not attrs and d.get("description"):
            attrs = [a.strip() for a in d.get("description", "").split(",") if a.strip()]
        for a in attrs[:8]:
            label = a if len(a) < 60 else a[:57] + "..."
            attr_options.append((f"{dn}.{label}", f"{dn}.{a}"))

    # Parse source columns from schema_ddl for the ingredients picker
    source_cols = []
    try:
        parsed = dru.spu.parse_create_tables(dru._strip_sql_comments(schema_ddl))
        for tname, cols in parsed:
            for cname, ctype in cols:
                source_cols.append(f"{cname} ({ctype})")
    except Exception:
        pass

    rows = [widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:8px 12px; margin-bottom:8px; font-size:12.5px; line-height:1.5; border-radius:3px;'>"
        "<strong>Metrics classifier.</strong> For each stakeholder ask, pick the natural unit, the aggregation pattern, "
        "the filter dim (becomes an FK on the fact), the drill-down attribute (lives on the joined dim), and the source "
        "column ingredients you'd need on the fact. The natural unit column should show the SAME value across all rows — "
        "that value IS your grain."
        "</div>"
    )]
    # Inline schema reference so the user sees the source columns + candidate dims
    if schema_ddl.strip():
        rows.append(widgets.HTML(
            "<details style='margin:6px 0; border-left:2px solid #57606a; padding-left:10px;'>"
            "<summary style='cursor:pointer; font-weight:600; font-size:12.5px; color:#0c447c;'>"
            "📋 Source schema + candidate dims (click to expand)</summary>"
            "<div style='font-size:11.5px; line-height:1.45; margin:6px 0;'>"
            f"<div style='font-weight:600; margin-top:4px;'>Source DDL:</div>"
            f"<pre style='background:#f6f8fa; padding:6px; margin:4px 0; font-size:11px; "
            f"overflow-x:auto;'>{schema_ddl[:1500]}</pre>"
            "<div style='font-weight:600; margin-top:8px;'>Candidate dimensions:</div>"
            "<ul style='margin:4px 0 4px 18px;'>"
            + "".join(
                f"<li><code>{(d.get('name','?'))}</code> (key: <code>{(d.get('key','?'))}</code>) — "
                f"{(d.get('description','') or '')}</li>"
                for d in candidates if isinstance(d, dict)
            )
            + "</ul></div></details>"
        ))

    common_nouns = ["claim", "message", "kit", "prescription", "patient", "visit",
                    "test", "order", "event", "shipment", "appointment", "day", "PA"]
    agg_options = [
        ("— pick —", ""),
        ("count", "count"),
        ("sum", "sum"),
        ("average", "avg"),
        ("median", "median"),
        ("count distinct", "count_distinct"),
        ("ratio (numerator / denominator)", "ratio"),
        ("duration: median of (ts2 minus ts1)", "duration_median"),
        ("duration: average of (ts2 minus ts1)", "duration_avg"),
        ("first / earliest (MIN of timestamp)", "first_min"),
        ("last / latest (MAX of timestamp)", "last_max"),
        ("rate: count(condition) / count(base)", "conditional_rate"),
    ]
    ingredient_options = source_cols if source_cols else ["(no source columns parsed)"]

    for idx, ask in enumerate(asks):
        # Header label using HTML so it wraps freely
        rows.append(widgets.HTML(
            f"<div style='font-size:13px; margin-top:14px; line-height:1.5; padding:6px 10px; "
            f"background:#f6f8fa; border-left:3px solid #0969da; border-radius:3px;'>"
            f"<strong>Ask {idx + 1}:</strong> {ask}</div>"
        ))
        unit_dd = widgets.Dropdown(
            options=[("— pick —", "")] + [(f"per {n}", f"per_{n}") for n in common_nouns],
            description="Natural unit:",
            style={"description_width": "150px"},
            layout=widgets.Layout(width="540px"),
        )
        agg_dd = widgets.Dropdown(
            options=agg_options,
            description="Aggregation:",
            style={"description_width": "150px"},
            layout=widgets.Layout(width="540px"),
        )
        filter_dd = widgets.Dropdown(
            options=dim_options,
            description="Filter dim (FK):",
            style={"description_width": "150px"},
            layout=widgets.Layout(width="540px"),
        )
        drilldown_dd = widgets.Dropdown(
            options=attr_options,
            description="Drill-down attr:",
            style={"description_width": "150px"},
            layout=widgets.Layout(width="700px"),
        )
        ingredients_sel = widgets.SelectMultiple(
            options=ingredient_options,
            rows=min(len(ingredient_options), 6),
            description="Ingredients:",
            style={"description_width": "150px"},
            layout=widgets.Layout(width="700px"),
        )
        _sd2_state["metrics_widgets"][idx] = {
            "unit": unit_dd, "agg": agg_dd,
            "filter_dim": filter_dd, "drilldown": drilldown_dd,
            "ingredients": ingredients_sel,
        }
        rows.append(unit_dd)
        rows.append(agg_dd)
        rows.append(filter_dd)
        rows.append(drilldown_dd)
        rows.append(ingredients_sel)
        rows.append(widgets.HTML(
            "<div style='font-size:11.5px; color:#57606a; margin:2px 0 0 12px;'>"
            "<em>Filter dim becomes an FK column on the fact. Drill-down attribute lives on the joined dim "
            "(NOT on the fact). Ingredients are the raw source columns you derive your fact columns from.</em>"
            "</div>"
        ))
    sd2_metrics_box.children = rows


# ----- Time-axis decision tree (Grain step) -----
# Helps the user decide whether the grain needs a time axis (per day/week/month)
# or stays at entity level. Two questions guide the recommendation; output shows
# the suggested grain template the user copies into the grain textarea.
# Long-question dropdowns: render the question as a separate full-width HTML
# label above the dropdown so it wraps naturally instead of getting clipped by
# ipywidgets' fixed description column.
sd2_dt_grain_time_q1_label = widgets.HTML(
    "<div style='font-size:12.5px; font-weight:600; margin:8px 0 2px 0; line-height:1.5;'>"
    "Q1: For the same entity, does each metric give ONE lifetime answer, or a FRESH answer per period?"
    "</div>"
)
sd2_dt_grain_time_q1 = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("One answer per entity (lifecycle outcome — yes/no, one duration, one final state)", "one_shot"),
        ("Fresh answer per time period (a new value every day/week/month for the same entity)", "periodic"),
    ],
    description="",
    layout=widgets.Layout(width="100%"),
)
sd2_dt_grain_time_q2_label = widgets.HTML(
    "<div style='font-size:12.5px; font-weight:600; margin:8px 0 2px 0; line-height:1.5;'>"
    "Q2: What time bucket is the metric naturally measured at? (only matters if Q1=periodic)"
    "</div>"
)
sd2_dt_grain_time_q2 = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("per day", "day"),
        ("per week", "week"),
        ("per month", "month"),
        ("per quarter", "quarter"),
    ],
    description="",
    layout=widgets.Layout(width="100%"),
)
sd2_dt_grain_time_q3_label = widgets.HTML(
    "<div style='font-size:12.5px; font-weight:600; margin:8px 0 2px 0; line-height:1.5;'>"
    "Q3: Should period values be STORED in the fact, or computed on the fly via dim_date FK? "
    "(only matters if Q1=periodic)"
    "</div>"
)
sd2_dt_grain_time_q3 = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Stored as data (snapshot/rollup fact — adds time axis to grain)", "stored"),
        ("Computed on the fly (entity grain only — slice via dim_date FK)", "computed"),
    ],
    description="",
    layout=widgets.Layout(width="100%"),
)
sd2_dt_grain_time_btn = widgets.Button(
    description="Apply time-axis recommendation",
    button_style="info",
    layout=widgets.Layout(width="280px"),
)
sd2_dt_grain_time_out = widgets.Output()

def _on_grain_time_recommend(b):
    q1 = sd2_dt_grain_time_q1.value
    q2 = sd2_dt_grain_time_q2.value
    q3 = sd2_dt_grain_time_q3.value
    with sd2_dt_grain_time_out:
        clear_output(wait=True)
        if not q1:
            print("Pick Q1 first.")
            return
        if q1 == "one_shot":
            template = "one row per [entity_id]"
            rec = (
                "No time axis in grain. Each metric has ONE answer over each entity's lifetime, "
                "so the fact stores ONE row per entity with all lifecycle outcomes flattened into "
                "columns (was_approved, was_reversed, cycle_time_hours, etc). The dashboard slices "
                "by date by joining fact.[some_timestamp] -> dim_date."
            )
            print(f"Recommended grain template:\\n  {template}\\n\\n{rec}")
            return
        if q1 == "periodic":
            if not q2 or not q3:
                print("Pick Q2 and Q3 to finalize the recommendation.")
                return
            if q3 == "computed":
                template = "one row per [entity_id]"
                rec = (
                    "No time axis in grain even though metrics are periodic. The dashboard can "
                    "compute period-specific values on the fly by joining the fact to dim_date "
                    "on the relevant timestamp column. Keep the fact at entity grain to avoid "
                    "row blowup, and put a date FK on the timestamp."
                )
                print(f"Recommended grain template:\\n  {template}\\n\\n{rec}")
                return
            # periodic + stored
            time_label = {
                "day": "per event_date",
                "week": "per week_start_date",
                "month": "per year_month",
                "quarter": "per quarter",
            }[q2]
            template = f"one row per [entity_id] {time_label}"
            rec = (
                "Add time axis to grain. The same entity has a fresh metric answer each "
                f"{q2}, and the dashboard wants those values stored (not recomputed). This is "
                "a snapshot/rollup fact — the fact's primary key is the composite of entity + "
                "time bucket. Common pattern for adherence metrics, retention metrics, "
                "running KPI snapshots."
            )
            print(f"Recommended grain template:\\n  {template}\\n\\n{rec}")
            return

sd2_dt_grain_time_btn.on_click(_on_grain_time_recommend)

sd2_dt_grain_time_box = widgets.VBox([
    widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:8px 12px; "
        "margin-bottom:6px; font-size:12.5px; line-height:1.5; border-radius:3px;'>"
        "<strong>Time-axis decision tree.</strong> Walks you through whether the grain needs "
        "a time axis (per day/week/month) or stays at entity level. The shortcut: ask if the "
        "same entity gets a fresh metric answer every period."
        "</div>"
    ),
    sd2_dt_grain_time_q1_label,
    sd2_dt_grain_time_q1,
    sd2_dt_grain_time_q2_label,
    sd2_dt_grain_time_q2,
    sd2_dt_grain_time_q3_label,
    sd2_dt_grain_time_q3,
    sd2_dt_grain_time_btn,
    sd2_dt_grain_time_out,
])


# ----- Other-axes decision tree (Grain step) -----
# Beyond the time axis, three other axes can modify the grain: channel/method,
# sub-entity/line-item, and snapshot/as-of-date. Three yes/no questions; output
# lists which axes should be added to the grain (if any).
sd2_dt_grain_other_q1_label = widgets.HTML(
    "<div style='font-size:12.5px; font-weight:600; margin:8px 0 2px 0; line-height:1.5;'>"
    "Q1: Channel/method/source — does the same entity have multiple channels, and does the dashboard "
    "need each channel as a separate ROW?"
    "</div>"
)
sd2_dt_grain_other_q1 = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Yes — dashboard wants per-channel rows preserved", "yes"),
        ("No — channel is a single column on the fact (FK to dim_channel) or not relevant", "no"),
    ],
    description="",
    layout=widgets.Layout(width="100%"),
)
sd2_dt_grain_other_q2_label = widgets.HTML(
    "<div style='font-size:12.5px; font-weight:600; margin:8px 0 2px 0; line-height:1.5;'>"
    "Q2: Sub-entity / line item — does the entity break into measurable parts that the metrics target?"
    "</div>"
)
sd2_dt_grain_other_q2 = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Yes — entity decomposes into measurable parts (claim->claim_line, order->order_line)", "yes"),
        ("No — the entity is the smallest measurable unit", "no"),
    ],
    description="",
    layout=widgets.Layout(width="100%"),
)
sd2_dt_grain_other_q3_label = widgets.HTML(
    "<div style='font-size:12.5px; font-weight:600; margin:8px 0 2px 0; line-height:1.5;'>"
    "Q3: Snapshot / as-of — does the same entity's measurement re-state over time and the dashboard "
    "needs to reproduce historical reports?"
    "</div>"
)
sd2_dt_grain_other_q3 = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Yes — same entity's value re-states over time and dashboards must reproduce historical reports", "yes"),
        ("No — historical re-statement is not a requirement", "no"),
    ],
    description="",
    layout=widgets.Layout(width="100%"),
)
sd2_dt_grain_other_btn = widgets.Button(
    description="Apply other-axes recommendation",
    button_style="info",
    layout=widgets.Layout(width="280px"),
)
sd2_dt_grain_other_out = widgets.Output()

def _on_grain_other_recommend(b):
    q1 = sd2_dt_grain_other_q1.value
    q2 = sd2_dt_grain_other_q2.value
    q3 = sd2_dt_grain_other_q3.value
    with sd2_dt_grain_other_out:
        clear_output(wait=True)
        if not all([q1, q2, q3]):
            print("Answer all three questions before applying.")
            return
        added = []
        notes = []
        if q1 == "yes":
            added.append("per channel")
            notes.append(
                "Channel becomes part of the grain when the dashboard wants per-channel "
                "ROWS (not just a per-channel filter). Common in messaging fact tables where "
                "sms/email/phone counts are tracked separately per entity per day."
            )
        if q2 == "yes":
            added.append("at line-item level instead of entity level")
            notes.append(
                "Drop down to the sub-entity grain. The fact is one row per claim_line_id "
                "(not per claim_id) when claim-line measures (paid_amount per line, denied "
                "per line) drive the metrics. The parent entity becomes a column/FK on each line."
            )
        if q3 == "yes":
            added.append("per as_of_date")
            notes.append(
                "Add as_of_date to the grain when the dashboard must reproduce historical "
                "reports. Each entity has one row per snapshot version. Common in financial "
                "reporting where claim amounts re-state at month-end."
            )
        if not added:
            print(
                "No additional axes. Grain stays at entity level only.\\n\\n"
                "None of the three modifying axes apply: channel is a single FK column (not "
                "a row multiplier), the entity is atomic (no line items), and historical "
                "re-statements are not required. Final grain is just one row per [entity_id] "
                "(plus any time axis you decided in the time-axis tree above)."
            )
            return
        print(
            "Add the following axes to the grain:\\n  - " + "\\n  - ".join(added) +
            "\\n\\nRationale per axis:\\n" + "\\n\\n".join(notes)
        )

sd2_dt_grain_other_btn.on_click(_on_grain_other_recommend)

sd2_dt_grain_other_box = widgets.VBox([
    widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:8px 12px; "
        "margin-bottom:6px; font-size:12.5px; line-height:1.5; border-radius:3px;'>"
        "<strong>Other-axes decision tree.</strong> Beyond time, three other axes can modify "
        "the grain: channel, sub-entity (line item), and snapshot/as-of-date. Run this AFTER "
        "the time-axis tree to layer on any additional axes the grain needs."
        "</div>"
    ),
    sd2_dt_grain_other_q1_label,
    sd2_dt_grain_other_q1,
    sd2_dt_grain_other_q2_label,
    sd2_dt_grain_other_q2,
    sd2_dt_grain_other_q3_label,
    sd2_dt_grain_other_q3,
    sd2_dt_grain_other_btn,
    sd2_dt_grain_other_out,
])


# ----- Source column classifier (Fact columns step) -----
# Table built from the source schema_ddl. For each source column, dropdowns:
# - how many values per grain (one / many / drop)
# - what happens on the fact (PK / FK / pivoted / measure / dropped)
# - include in fact? (yes / no)
sd2_srccols_box = widgets.VBox([
    widgets.HTML("<i>Generate a schema_design problem to see the source column classifier.</i>")
])

def _sd2_extract_event_types(problem):
    """Pull the list of event_type values from the problem prompt (used to
    populate the pivot follow-up SelectMultiple)."""
    import re
    text = (problem.get("prompt") or "") + " " + (problem.get("schema_ddl") or "")
    # Look for patterns like 'event_type values: a, b, c, d' or 'event_types: ...'
    m = re.search(r"event[_ ]types?\s*(?:values\s*)?:\s*([a-zA-Z0-9_,\s\-]+?)(?:\.|\\n|$)", text, re.I)
    if not m:
        return []
    raw = m.group(1)
    # Split on commas / and / or whitespace; strip and dedupe
    parts = re.split(r"[,/]|\s+and\s+|\s+or\s+", raw)
    out = []
    seen = set()
    for p in parts:
        v = p.strip().strip(".").strip()
        if v and v.lower() not in seen and len(v) <= 50:
            seen.add(v.lower())
            out.append(v)
    return out[:12]

def _sd2_rebuild_srccols_box():
    """Rebuild the source column classifier. Per source column, the user picks:
    - per_grain: ONE / MANY / DROP at the chosen grain
    - role: PK / FK / Measure / Pivoted / Timestamp / Dropped
    - include: Yes / No
    - pivoted_into: SelectMultiple of resulting fact columns (only when role=pivoted)
    - measure_purpose: Dropdown of metric purpose (only when role=measure)

    Widget references stored in _sd2_state['srccols_widgets'] keyed by
    (table_name, col_name) so grade time can serialize the picks."""
    p = STATE.get("problem") or {}
    schema_ddl = p.get("schema_ddl", "") or ""
    _sd2_state["srccols_widgets"] = {}
    if not schema_ddl.strip():
        sd2_srccols_box.children = [widgets.HTML(
            "<i>No schema_ddl in this problem.</i>"
        )]
        return
    try:
        parsed = dru.spu.parse_create_tables(dru._strip_sql_comments(schema_ddl))
    except Exception:
        parsed = []
    if not parsed:
        sd2_srccols_box.children = [widgets.HTML(
            "<i>Could not parse columns from schema_ddl.</i>"
        )]
        return

    # Parse event_type values from the prompt (drives pivot follow-up).
    event_types = _sd2_extract_event_types(p)
    pivot_options = []
    if event_types:
        # Build typical naming: <event>_ts and <event>_flag
        for et in event_types:
            slug = et.strip().replace(" ", "_").replace("-", "_").lower()
            pivot_options.append((f"{slug}_ts (timestamp of first/last {et} event)", f"{slug}_ts"))
            pivot_options.append((f"was_{slug} (1/0 indicator that {et} occurred)", f"was_{slug}"))
        pivot_options.append(("first_event_ts (MIN over all events)", "first_event_ts"))
        pivot_options.append(("last_event_ts (MAX over all events)", "last_event_ts"))
        pivot_options.append(("final_status (terminal event_type)", "final_status"))
    rows = [widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:8px 12px; margin-bottom:8px; font-size:12.5px; line-height:1.5; border-radius:3px;'>"
        "<strong>Source column classifier.</strong> For each source column, decide what role it plays at YOUR grain. "
        "The result tells you which columns go on the fact and how. "
        "<strong>Your picks here are passed to the grader as your fact column proposal — you don&#39;t need to re-type them in the textbox below.</strong>"
        "</div>"
    )]
    for table_name, cols in parsed:
        rows.append(widgets.HTML(
            f"<div style='font-weight:600; font-size:13px; color:#0c447c; margin-top:8px;'>"
            f"Source table: <code>{table_name}</code></div>"
        ))
        for col_name, col_type in cols:
            rows.append(widgets.HTML(
                f"<div style='font-size:12.5px; margin-top:6px;'>"
                f"<code>{col_name}</code> ({col_type})</div>"
            ))
            values_dd = widgets.Dropdown(
                options=[
                    ("— pick —", ""),
                    ("ONE value per grain", "one"),
                    ("MANY values per grain", "many"),
                    ("Drop — only meaningful at source grain", "drop"),
                ],
                description="Per grain:",
                style={"description_width": "100px"},
                layout=widgets.Layout(width="500px"),
            )
            role_dd = widgets.Dropdown(
                options=[
                    ("— pick —", ""),
                    ("PK (the grain key)", "pk"),
                    ("FK to a dim", "fk"),
                    ("Measure / count / sum", "measure"),
                    ("Pivoted into multiple columns (event_type → timestamps)", "pivoted"),
                    ("Supporting timestamp", "timestamp"),
                    ("Dropped", "dropped"),
                ],
                description="Role on fact:",
                style={"description_width": "100px"},
                layout=widgets.Layout(width="700px"),
            )
            include_dd = widgets.Dropdown(
                options=[
                    ("— pick —", ""),
                    ("Yes — include on fact", "yes"),
                    ("No — drop", "no"),
                ],
                description="Include?",
                style={"description_width": "100px"},
                layout=widgets.Layout(width="400px"),
            )
            # Pivot follow-up — visible/relevant when role=pivoted. Always rendered
            # so the user can plan ahead, but the grader only honors picks when
            # the role is actually 'pivoted'.
            if pivot_options:
                pivot_sel = widgets.SelectMultiple(
                    options=pivot_options,
                    rows=min(len(pivot_options), 6),
                    description="Pivots into:",
                    style={"description_width": "100px"},
                    layout=widgets.Layout(width="700px"),
                )
            else:
                pivot_sel = widgets.SelectMultiple(
                    options=["(no event_type values detected — use the supplemental textbox)"],
                    rows=1,
                    description="Pivots into:",
                    style={"description_width": "100px"},
                    layout=widgets.Layout(width="700px"),
                )
            # Measure purpose — visible/relevant when role=measure. Helps the grader
            # see whether this measure feeds a rate/count/sum and what its denominator is.
            measure_purpose_dd = widgets.Dropdown(
                options=[
                    ("— pick (only matters if role=measure) —", ""),
                    ("Raw count contributor (count of rows is the metric)", "count"),
                    ("Raw sum contributor (SUM is the metric)", "sum"),
                    ("Numerator of a rate (paired with a denominator measure)", "numerator"),
                    ("Denominator of a rate (the base count)", "denominator"),
                    ("Compared against a constant or dim value (adherence-style)", "compare_against"),
                    ("Aggregated as MIN/MAX (timestamps for cycle time)", "min_max"),
                ],
                description="Measure purpose:",
                style={"description_width": "150px"},
                layout=widgets.Layout(width="700px"),
            )
            _sd2_state["srccols_widgets"][(table_name, col_name)] = {
                "type": col_type,
                "per_grain": values_dd,
                "role": role_dd,
                "include": include_dd,
                "pivoted_into": pivot_sel,
                "measure_purpose": measure_purpose_dd,
            }
            rows.append(values_dd)
            rows.append(role_dd)
            rows.append(include_dd)
            rows.append(pivot_sel)
            rows.append(measure_purpose_dd)
    sd2_srccols_box.children = rows


# ----- Conformed dims gate question -----
sd2_dt_conformed_q = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Yes — problem mentions multiple facts", "yes"),
        ("No — single-fact drill", "no"),
    ],
    description="Does the problem mention more than one fact table (existing or to-be-built)?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_conformed_btn = widgets.Button(
    description="Apply recommendation",
    button_style="info",
    layout=widgets.Layout(width="240px"),
)
sd2_dt_conformed_out = widgets.Output()

def _on_conformed_recommend(b):
    q = sd2_dt_conformed_q.value
    if not q:
        with sd2_dt_conformed_out:
            clear_output(wait=True)
            print("Pick yes or no first.")
        return
    if q == "no":
        sd2_conformed_rationale_ta.value = (
            "N/A — single-fact drill. Conformed dims is about reusing the SAME dim across "
            "multiple fact tables; with only one fact in scope, there's nothing to conform with."
        )
        # Uncheck any conformed checkboxes
        for cb in _sd2_state.get("conformed_checkboxes", {}).values():
            cb.value = False
        with sd2_dt_conformed_out:
            clear_output(wait=True)
            print("Recommended: N/A — single-fact drill.\\n\\nRationale auto-filled. Conformed checkboxes cleared.")
    else:
        sd2_conformed_rationale_ta.value = (
            "Multi-fact problem — pick the dims that should be SHARED across the facts so the "
            "warehouse uses one source of truth. Common conformed dims: dim_patient, dim_date. "
            "Specific to outreach domain (dim_channel, dim_care_team_user) usually NOT conformed."
        )
        with sd2_dt_conformed_out:
            clear_output(wait=True)
            print("Multi-fact problem detected. Now pick the conformed dims from the checkboxes below.")

sd2_dt_conformed_btn.on_click(_on_conformed_recommend)

sd2_dt_conformed_box = widgets.VBox([
    widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:8px 12px; margin-bottom:6px; font-size:12.5px; line-height:1.5; border-radius:3px;'>"
        "<strong>Decision walkthrough.</strong> Most problems describe a single fact table — answer No to mark this step N/A."
        "</div>"
    ),
    sd2_dt_conformed_q,
    sd2_dt_conformed_btn,
    sd2_dt_conformed_out,
])


# ----- Late-arriving walkthrough -----
sd2_dt_late_q1 = widgets.Dropdown(
    options=[("— pick —", ""), ("Yes", "yes"), ("No", "no")],
    description="Q1: Can events arrive AFTER the period they belong to has closed?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_late_q2 = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Accuracy — dashboard always shows latest true state", "accuracy"),
        ("Reproducibility — past period numbers stay unchanged", "reproducibility"),
    ],
    description="Q2: What matters more — accuracy or reproducibility?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_late_q3 = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Small (a few percent of events arrive late)", "small"),
        ("Large (many percent arrive late)", "large"),
    ],
    description="Q3 (accuracy path): How much late data is typical?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_late_q4 = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Record as adjustments — original stays, inverse row added", "adjustments"),
        ("Ignore them — closed periods frozen forever", "ignore"),
    ],
    description="Q4 (reproducibility path): Record adjustments or ignore?",
    style={"description_width": "440px"},
    layout=widgets.Layout(width="100%"),
)
sd2_dt_late_btn = widgets.Button(
    description="Apply recommendation",
    button_style="info",
    layout=widgets.Layout(width="240px"),
)
sd2_dt_late_out = widgets.Output()

def _on_late_recommend(b):
    q1 = sd2_dt_late_q1.value
    q2 = sd2_dt_late_q2.value
    q3 = sd2_dt_late_q3.value
    q4 = sd2_dt_late_q4.value
    if not q1:
        with sd2_dt_late_out:
            clear_output(wait=True)
            print("Answer Q1 before applying.")
        return
    if q1 == "no":
        rec, label, rationale = (
            "na",
            "N/A — static data, no late arrivals possible",
            "N/A means: late-arriving event handling is irrelevant when the source data is static or always arrives within its period."
        )
    else:
        if not q2:
            with sd2_dt_late_out:
                clear_output(wait=True)
                print("Answer Q2 before applying.")
            return
        if q2 == "accuracy":
            if not q3:
                with sd2_dt_late_out:
                    clear_output(wait=True)
                    print("Answer Q3 before applying.")
                return
            if q3 == "small":
                rec, label, rationale = (
                    "merge_predicate",
                    "dbt incremental with merge predicate (grain_key, event_ts)",
                    "Merge predicate means: dbt incremental with a wider lookback window catches late events naturally. Cheap and effective when only a few percent arrive late."
                )
            else:
                rec, label, rationale = (
                    "restate",
                    "Re-state closed periods (rebuild affected partitions)",
                    "Re-state means: every run, rebuild affected past partitions using the latest source events. Past period numbers shift slightly with each rebuild as late events arrive. Picked because accuracy matters more than report stability and late data volume is non-trivial."
                )
        else:
            if not q4:
                with sd2_dt_late_out:
                    clear_output(wait=True)
                    print("Answer Q4 before applying.")
                return
            if q4 == "adjustments":
                rec, label, rationale = (
                    "correction_row",
                    "Append correction row",
                    "Correction row means: original fact row stays unchanged; an inverse/correction row is appended. The view layer nets them out at query time. Past period totals stay reproducible."
                )
            else:
                rec, label, rationale = (
                    "snapshot_lock",
                    "Snapshot lock-in",
                    "Snapshot lock-in means: once a period closes, never update it. Late events are dropped or held outside the closed period. Reports stay perfectly reproducible but become inaccurate over time."
                )
    sd2_late_dd.value = rec
    sd2_late_rationale_ta.value = rationale
    with sd2_dt_late_out:
        clear_output(wait=True)
        print(f"Recommended: {label}\\n\\n{rationale}\\n\\n(dropdown and rationale below have been pre-filled)")

sd2_dt_late_btn.on_click(_on_late_recommend)

sd2_dt_late_box = widgets.VBox([
    widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:8px 12px; margin-bottom:6px; font-size:12.5px; line-height:1.5; border-radius:3px;'>"
        "<strong>Decision walkthrough.</strong> Q1 = No skips the rest (N/A). Q2 picks the path: accuracy uses Q3, reproducibility uses Q4."
        "</div>"
    ),
    sd2_dt_late_q1,
    sd2_dt_late_q2,
    sd2_dt_late_q3,
    sd2_dt_late_q4,
    sd2_dt_late_btn,
    sd2_dt_late_out,
])


sd2_panels = [
    widgets.VBox([sd2_hint_business_process, sd2_example_business_process, sd2_bp_finder_box, sd2_business_process_activity_ta, sd2_business_process_outcome_ta]),
    widgets.VBox([sd2_hint_grain, sd2_example_grain, sd2_metrics_box, sd2_dt_grain_time_box, sd2_dt_grain_other_box, sd2_input_grain_ta, sd2_grain_ta]),
    widgets.VBox([sd2_hint_dim_joins, sd2_example_dim_joins, sd2_dim_box]),
    widgets.VBox([sd2_hint_scd, sd2_pitfall_scd, sd2_example_scd, sd2_scd_box, sd2_scd_rationale_ta]),
    widgets.VBox([sd2_hint_conformed, sd2_example_conformed, sd2_dt_conformed_box, sd2_conformed_box, sd2_conformed_rationale_ta]),
    widgets.VBox([sd2_hint_fact_columns, sd2_pitfall_fact_columns, sd2_field2_template, sd2_srccols_box, sd2_example_fact_columns, sd2_fact_cols_ta]),
    widgets.VBox([sd2_hint_key, sd2_pitfall_key, sd2_example_key, sd2_dt_surr_box, sd2_key_dd, sd2_key_rationale_ta]),
    widgets.VBox([
        sd2_hint_models,
        sd2_example_models,
        sd2_models_box,
        sd2_add_model_btn,
    ]),
    widgets.VBox([sd2_hint_tests, sd2_example_tests, sd2_tests_box]),
    widgets.VBox([sd2_hint_idempotency, sd2_example_idempotency, sd2_dt_idem_box, sd2_idem_dd, sd2_idem_rationale_ta]),
    widgets.VBox([sd2_hint_late_arriving, sd2_example_late_arriving, sd2_dt_late_box, sd2_late_dd, sd2_late_rationale_ta]),
    widgets.VBox([sd2_hint_edge, sd2_example_edge, sd2_edge_panel_box]),
]

sd2_accordion = widgets.Accordion(children=sd2_panels)
sd2_accordion.set_title(0, "(1) Business process — what activity is this fact measuring?")
sd2_accordion.set_title(1, "(2) Grain — one row per ___")
sd2_accordion.set_title(2, "(3) Dim joins — which dims do we need?")
sd2_accordion.set_title(3, "(4) How does this dim handle changes over time?")
sd2_accordion.set_title(4, "(5) Dims shared across multiple fact tables")
sd2_accordion.set_title(5, "(6) Fact columns — what the fact stores")
sd2_accordion.set_title(6, "(7) Generate a new ID, or reuse the source's ID?")
sd2_accordion.set_title(7, "(8) Models — name, purpose, layer, materialization")
sd2_accordion.set_title(8, "(9) dbt tests per model")
sd2_accordion.set_title(9, "(10) Re-run safety — what happens if the model runs twice?")
sd2_accordion.set_title(10, "(11) What happens when an event arrives after its period closed?")
sd2_accordion.set_title(11, "(12) Tricky scenarios you'd test for")
sd2_accordion.selected_index = None  # all collapsed


# ============================================================
# Grade button handler
# ============================================================

def on_schema_design_grade(b):
    with sd2_grade_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p:
            print("Generate a problem first."); return
        if p.get("_meta", {}).get("subtopic") != "schema_design":
            print("This form is for schema_design problems only."); return

        _sd2_sync_models()
        dim_picks = [n for n, cb in _sd2_state["dim_checkboxes"].items() if cb.value]
        scd_per_dim = {n: v for n, v in _sd2_state["scd_picks"].items() if n in dim_picks}
        conformed_picks = [n for n, cb in _sd2_state.get("conformed_checkboxes", {}).items() if cb.value]

        # Filter test_selections / test_custom to only include CURRENT model names.
        # Defends against stale keys from intermediate model name keystrokes.
        current_model_names = {m.get("name", "").strip() for m in _sd2_state.get("models", []) if m.get("name", "").strip()}
        clean_test_selections = {
            mname: sels
            for mname, sels in (_sd2_state.get("test_selections", {}) or {}).items()
            if mname in current_model_names
        }
        clean_test_custom = {
            mname: txt
            for mname, txt in (_sd2_state.get("test_custom", {}) or {}).items()
            if mname in current_model_names
        }

        # Serialize the metrics classifier picks (per ask) for the grader.
        metrics_classifier = {}
        for ask_idx, ws in (_sd2_state.get("metrics_widgets") or {}).items():
            picks = {
                "unit": ws["unit"].value,
                "agg": ws["agg"].value,
                "filter_dim": ws["filter_dim"].value,
                "drilldown": ws["drilldown"].value,
                "ingredients": list(ws["ingredients"].value or ()),
            }
            if any(picks.values()):
                metrics_classifier[str(ask_idx)] = picks

        # Serialize the source column classifier picks for the grader.
        srccols_classifier = {}
        for (tname, cname), ws in (_sd2_state.get("srccols_widgets") or {}).items():
            picks = {
                "type": ws.get("type", ""),
                "per_grain": ws["per_grain"].value,
                "role": ws["role"].value,
                "include": ws["include"].value,
            }
            # Include pivot follow-up only when role=pivoted (otherwise irrelevant).
            if picks["role"] == "pivoted" and ws.get("pivoted_into"):
                picks["pivoted_into"] = list(ws["pivoted_into"].value or ())
            # Include measure purpose only when role=measure.
            if picks["role"] == "measure" and ws.get("measure_purpose"):
                mp = ws["measure_purpose"].value
                if mp:
                    picks["measure_purpose"] = mp
            if any(picks.get(k) for k in ("per_grain", "role", "include")):
                srccols_classifier[f"{tname}.{cname}"] = picks

        # Per-dim attribute usage selections (Step 3 — Approach 2).
        dim_attribute_usage = {}
        for dn, attrs_map in (_sd2_state.get("dim_attr_widgets") or {}).items():
            picks = {}
            for attr, (cb, usage_dd) in attrs_map.items():
                if cb.value:
                    picks[attr] = usage_dd.value or ""
            if picks:
                dim_attribute_usage[dn] = picks

        responses = {
            "business_process": sd2_business_process_ta.value,
            "grain": sd2_grain_ta.value,
            "input_grain": (sd2_input_grain_ta.value if 'sd2_input_grain_ta' in globals() else ""),
            "fact_columns": sd2_fact_cols_ta.value,
            "fact_columns_classifier": srccols_classifier,
            "metrics_classifier": metrics_classifier,
            "dim_attribute_usage": dim_attribute_usage,
            "key_strategy": sd2_key_dd.value,
            "key_rationale": sd2_key_rationale_ta.value,
            "dim_joins": dim_picks,
            "scd_per_dim": scd_per_dim,
            "scd_rationale": sd2_scd_rationale_ta.value,
            "conformed_dims": conformed_picks,
            "conformed_rationale": sd2_conformed_rationale_ta.value,
            "models": _sd2_state["models"],
            "tests_per_model": clean_test_selections,
            "tests_custom_per_model": clean_test_custom,
            "translate_picks": dict(_sd2_state.get("translate_picks", {}) or {}),
            "translate_decomp": {
                str(k): {fk: (v or "") for fk, v in (sub or {}).items() if (v or "").strip()}
                for k, sub in (_sd2_state.get("translate_decomp", {}) or {}).items()
                if any((v or "").strip() for v in (sub or {}).values())
            },
            "mode": _sd2_state.get("mode", "solve"),
            # Edge cases — picked from canned scenarios (no text input).
            # edge_cases_per_category: {cat_id: list of selected option strings}
            # edge_cases_applies: {cat_id: bool} — was the 'applies' checkbox ticked
            "edge_cases_per_category": {
                cat_id: list(w.value or ())
                for cat_id, w in _sd2_edge_cat_widgets.items()
                if (w.value or ())
            },
            "edge_cases_applies": {
                cat_id: bool(cb.value)
                for cat_id, cb in _sd2_edge_applies_widgets.items()
            },
            "idempotency_strategy": sd2_idem_dd.value,
            "idempotency_rationale": sd2_idem_rationale_ta.value,
            "late_arriving_strategy": sd2_late_dd.value,
            "late_arriving_rationale": sd2_late_rationale_ta.value,
            # Build the legacy 'edge_cases' string from picks so the grader still
            # gets a readable summary even though the user never typed.
            "edge_cases": "\\n".join(
                f"[{cat_id}] " + "; ".join(list(w.value or ()))
                for cat_id, w in _sd2_edge_cat_widgets.items()
                if (w.value or ())
            ),
        }
        # Require at least something
        any_filled = (
            (sd2_grain_ta.value or "").strip()
            or (sd2_fact_cols_ta.value or "").strip()
            or sd2_key_dd.value
            or dim_picks
            or _sd2_state["models"]
        )
        if not any_filled:
            print("Fill in at least a few fields before grading.")
            return
        print("Asking Claude to grade your schema design ...")
        result = dru.grade_schema_design_form(p, responses)
        clear_output(wait=True)
        if not result:
            print("Grading failed."); return
        # Auto-save the attempt so reload restores the form
        try:
            saved_path = dru.save_schema_design_attempt(p, responses, grade=result, solved_dir=SOLVED_DIR)
            if saved_path:
                print(f"(attempt saved to {os.path.basename(saved_path)})")
        except Exception as save_err:
            print(f"(warning: could not save attempt: {save_err})")
        display(HTML(dru.schema_design_form_grade_to_html(result)))
sd2_grade_btn.on_click(on_schema_design_grade)


# ============================================================
# Compose form box (hidden by default)
# ============================================================

# Manual "Reload form from current problem" button — fallback if the auto-refresh
# on Generate didn't fire (e.g. cell ordering issue, swallowed exception).
sd2_reload_btn = widgets.Button(
    description="🔄 Reload form from current problem",
    button_style="warning",
    layout=widgets.Layout(width="320px"),
    tooltip="Click if dim checkboxes / SCD dropdowns / source column table are blank",
)
sd2_reload_out = widgets.Output()
def _on_sd2_reload(b):
    with sd2_reload_out:
        clear_output(wait=True)
        try:
            refresh_subtopic_form()
            p = STATE.get("problem") or {}
            sub = (p or {}).get("_meta", {}).get("subtopic", "")
            cdims = len(p.get("candidate_dimensions", []) or [])
            asks = len(p.get("stakeholder_asks", []) or [])
            print(f"Form reloaded. subtopic={sub}, candidate_dimensions={cdims}, stakeholder_asks={asks}")
        except Exception as e:
            import traceback
            print(f"Reload error: {type(e).__name__}: {e}")
            traceback.print_exc()
sd2_reload_btn.on_click(_on_sd2_reload)

_schema_design_form_box = widgets.VBox(
    [
        widgets.HBox([sd2_reload_btn, sd2_reload_out]),
        widgets.HTML(
            "<ul style='font-size:13px; line-height:1.6; margin:6px 0 10px 18px; padding-left:0;'>"
            "<li>11 fields, one accordion panel each. Open one at a time.</li>"
            "<li>Dynamic fields adapt to the problem: dim checkboxes from the candidate "
            "dim list; SCD dropdowns from your checked dims; per-model tests from your model rows.</li>"
            "<li>Mark fields N/A when not relevant to the current drill — the grader honors that.</li>"
            "<li>Click <strong>Get Schema Design Feedback</strong> when ready.</li>"
            "</ul>"
        ),
        _sd2_concept_primer,
        widgets.HTML(
            "<div style='font-weight:600; font-size:14px; color:#0c447c; margin-top:10px;'>"
            "MODE — How do you want to learn?</div>"
            "<div style='font-size:12.5px; color:#57606a; margin:4px 0 4px 0; line-height:1.55;'>"
            "<strong>Solve mode</strong> = try blind, get graded against the rubric. Best for "
            "self-testing once you understand the framework. <strong>Walkthrough mode</strong> = "
            "the worked answer + lay-language rationale appears IN the hint area for each field. "
            "You read it, then paraphrase in your own words below to lock it in. Best for "
            "learning the patterns when you're stuck. Switch any time."
            "</div>"
        ),
        sd2_mode_toggle,
        # Step 1 (translate-the-asks text decomposition) was hidden because it was
        # redundant with the Step 2 metrics classifier dropdowns. The legacy widget
        # `sd2_translate_box` still exists and saves/loads with the form, but is
        # not rendered to the user.
        widgets.HTML(
            "<div style='font-weight:600; font-size:14px; color:#0c447c; margin-top:14px;'>"
            "Fill the response form</div>"
            "<div style='font-size:12.5px; color:#57606a; margin:4px 0 6px 0; line-height:1.55;'>"
            "Open one accordion panel at a time. Step 2 (Grain) has the metrics classifier — "
            "use those dropdowns to think through each ask before you write anything."
            "</div>"
        ),
        sd2_accordion,
        sd2_grade_btn,
        sd2_grade_out,
    ],
)
# =============================================================
# Version Control Response Form — 5th panel
# =============================================================

# Per-subtopic section maps. Each section becomes a textarea inside the form's
# nested accordion. The user fills each section to satisfy the prompt's
# requirements. New subtopics inherit the GENERIC_VC_SECTIONS fallback.
_VC_SECTION_MAPS = {
    "branching_strategy": [
        ("branch_naming", "Branch naming convention",
         "Define the naming pattern: type/short-description (e.g., feat/fpar-fact, fix/dim-payer-typo). State who owns each branch and the typical lifespan."),
        ("merge_rules", "What gets merged to main and when",
         "What MUST be true before a branch merges to main? What's blocked? When does merge happen (after CI green, after PR approval, scheduled)?"),
        ("env_mapping", "Environment-to-branch mapping",
         "Which branch deploys to dev / staging / prod? How do branches promote between environments? Especially for daily-deploy-to-prod-at-6am."),
        ("pr_review", "PR review process",
         "Required reviewers, approval count, branch protection rules, what reviewers check. Cite CODEOWNERS if relevant."),
        ("ci_integration", "CI integration",
         "What runs on each PR / merge / nightly? dbt tests, slim CI (state:modified+), lint, compile. What blocks merge vs warns."),
    ],
    "merge_conflict_resolution": [
        ("detection", "How conflicts are detected",
         "When does a conflict surface (PR merge button, local rebase, CI)? Who finds it first?"),
        ("resolution_steps", "Resolution steps in order",
         "Step-by-step: pull latest, identify conflicting hunks, decide intent (yours/theirs/both/neither), test."),
        ("re_test", "Re-test plan after resolution",
         "What tests run after the conflict is resolved? dbt build for affected models? Full or slim CI?"),
        ("communication", "Team communication",
         "When/how to ping the other branch's author. PR comment vs Slack vs sync chat."),
    ],
    "rebase_vs_merge": [
        ("when_rebase", "When to rebase",
         "Use cases for git rebase: pulling main into a feature branch, cleaning history before PR, squashing fixup commits."),
        ("when_merge", "When to merge",
         "Use cases for merge commit: integrating long-lived feature branch into main, preserving the integration point."),
        ("forbidden", "Forbidden cases (NEVER rebase here)",
         "Shared branches (main, develop), branches others have already pulled, public history. Why force-push to shared branches breaks teammates."),
        ("history_policy", "History/audit policy",
         "Linear history vs merge bubbles. Squash merge vs rebase merge vs merge commit at the org level."),
    ],
    "pr_review_critique": [
        ("blocking_issues", "Blocking issues to call out",
         "Bugs, missing tests, breaking schema changes, security issues. Anything that would make you request changes."),
        ("nits_vs_blockers", "Nits vs blockers",
         "What's a 'nit' (style, naming) vs a 'blocker' (correctness, tests). When to leave nits as suggestions and approve."),
        ("approval_criteria", "Approval criteria",
         "What MUST be true to approve. Tests pass, code matches the PR description, no unresolved review threads."),
        ("communication_tone", "Communication tone",
         "Constructive vs nitpicky. Asking questions vs demanding changes. Linking to docs/conventions instead of personal preference."),
    ],
    "commit_message_critique": [
        ("title_quality", "Title quality assessment",
         "<= 72 chars, imperative mood, scope prefix per Conventional Commits (feat/fix/chore/docs/refactor/test). Subject answers WHY at a glance."),
        ("body_quality", "Body quality assessment",
         "What changed, why, links to ticket. Wrap at 72. Body explains the WHY the title alone can't carry."),
        ("conventional_format", "Conventional Commits compliance",
         "type(scope): subject. Footer with BREAKING CHANGE: or Closes #123. Used by semantic-release for version bumps."),
        ("rewrite_proposal", "Proposed rewrite",
         "Show the before/after. Title + body + footer. Justify each change."),
    ],
    "revert_strategy": [
        ("blast_radius", "Blast radius assessment",
         "What's affected: which models, dashboards, downstream consumers, customer impact. How urgent."),
        ("revert_method", "git revert vs reset vs hotfix",
         "git revert (creates inverse commit, preserves history) vs git reset (rewrites history, only on private branches) vs forward-fix in a hotfix branch."),
        ("validation", "Validation after revert",
         "How to confirm the revert restored prior behavior. Re-run dashboards, dbt build, smoke test."),
        ("communication", "Stakeholder communication",
         "Who to notify and when. Status page, Slack channel, on-call rotation. Post-incident write-up."),
    ],
    "git_state_diagnose": [
        ("symptom_diagnosis", "What does the git state tell you",
         "Read the output of git status / log / reflog. Identify the symptom: detached HEAD, unmerged paths, divergent branches, dirty working tree, etc."),
        ("recovery_steps", "Recovery steps in order",
         "Step-by-step recovery commands. git stash / git reflog / git checkout / git reset / git rebase --abort. Order matters — avoid making it worse."),
        ("data_loss_risk", "Data loss risk assessment",
         "What could be permanently lost (uncommitted work, deleted branches, force-pushed history). Use git reflog to recover when possible."),
        ("post_recovery", "Post-recovery hygiene",
         "Run tests, push to remote, update PR. Document what happened so the team avoids it next time."),
    ],
}

_VC_GENERIC_SECTIONS = [
    ("approach", "Your approach",
     "Describe the approach in 2-3 sentences. State the recommendation up front."),
    ("specifics", "Specifics",
     "The concrete details that make the approach actionable: commands, branch names, tools, file paths."),
    ("tradeoffs", "Trade-offs",
     "What you gave up. What alternative you rejected and why."),
    ("example", "Concrete example walkthrough",
     "One realistic scenario narrated step by step. Forces the approach to be tested against a real flow."),
]

# Per-subtopic edge case categories — same checkbox + SelectMultiple pattern
# as schema_design but with git-flavored scenarios.
_VC_EDGE_CATEGORIES = [
    ("hotfix_to_prod",
     "Hotfix to prod",
     "An urgent fix needs to ship before normal merge cadence allows.",
     [
         "Branch off main, fast-forward back to main with a single PR",
         "Branch off prod tag/commit, cherry-pick into main after deploy",
         "Skip CI gates with documented incident-channel approval",
         "Trigger out-of-band deploy outside the 6am UTC schedule",
     ]),
    ("broken_ci_on_main",
     "Broken CI on main",
     "Main branch CI is red and blocking everyone's PRs.",
     [
         "Revert the offending commit immediately, fix forward later",
         "Pin / disable the failing test temporarily with a tracking ticket",
         "Lock main branch protection until fix lands",
         "Page the on-call analytics engineer",
     ]),
    ("force_push_aftermath",
     "Force push aftermath",
     "Someone force-pushed to a shared branch and other teammates' branches are now stale.",
     [
         "Rebuild local branches from reflog (git reset --hard ORIG_HEAD)",
         "Pull --rebase to get the new history, replay local commits on top",
         "Restore lost commits from git reflog",
         "Add branch protection to prevent force push to shared branches",
     ]),
    ("conflicting_feature_branches",
     "Conflicting feature branches",
     "Two long-lived branches both modified the same model and now conflict.",
     [
         "Sync more often — pull main into both branches daily",
         "Pair-resolve with both authors in a sync chat",
         "Split the conflicting model into smaller files",
         "Land one branch first, rebase the other on top",
     ]),
    ("abandoned_pr",
     "Abandoned PR",
     "An open PR has gone stale (no activity for weeks).",
     [
         "Close with a comment explaining why; cherry-pick salvageable commits",
         "Reassign to another team member to finish",
         "Auto-close after N days via stale-bot",
         "Convert to draft until ready to revisit",
     ]),
    ("large_refactor",
     "Large refactor PR",
     "A massive refactor touches 50+ files; reviewers are paralyzed.",
     [
         "Split into a stack of small PRs (one per logical change)",
         "Pre-merge sync meeting to walk reviewers through the diff",
         "Land behind a feature flag / dbt variable for gradual rollout",
         "Use git bisect-friendly atomic commits inside the PR",
     ]),
]

# Reference / known-pattern multi-select. Picking known patterns demonstrates
# the candidate knows the canon.
_VC_REFERENCE_PATTERNS = [
    "GitHub Flow",
    "GitLab Flow",
    "Trunk-based development",
    "Git Flow (Driessen, 2010)",
    "Conventional Commits",
    "Semantic Versioning",
    "semantic-release",
    "dbt slim CI (state:modified+)",
    "dbt full CI (run all models)",
    "Continuous Deployment",
    "Squash merge",
    "Rebase merge",
    "Merge commit (no fast-forward)",
    "Cherry-pick",
    "git bisect",
    "git reflog",
    "Pre-commit hooks",
    "Branch protection rules",
    "Required reviewers",
    "CODEOWNERS",
    "Stacked PRs",
    "Feature flags / dbt variables",
    "Linear history policy",
    "Monorepo vs polyrepo",
]

# Widget state for the VC form.
_vc_state = {
    "section_widgets": {},   # field_id -> Textarea
    "edge_widgets": {},      # cat_id -> SelectMultiple
    "edge_applies": {},      # cat_id -> Checkbox
}

# ----- Top-level VC form widgets -----
vc_goal_ta = widgets.Textarea(
    placeholder=(
        "ONE-LINE recommendation. Pick a position and stick with it.\\n"
        "Example: 'Trunk-based development with short-lived feature branches, "
        "squash-merge to main, prod deploys daily at 6am UTC from main.'"
    ),
    layout=widgets.Layout(width="100%", min_height="60px"),
    description="Goal / recommendation:",
    style={"description_width": "180px"},
)
vc_goal_ta.add_class("diagnose-textarea")

vc_section_box = widgets.VBox([
    widgets.HTML("<i>Generate a version_control problem to see subtopic-specific sections.</i>")
])

vc_tradeoffs_ta = widgets.Textarea(
    placeholder=(
        "What did you give up by picking this approach? What alternative did you reject and why?\\n"
        "Example: 'Trunk-based gives up release branches, so we can't sit on a feature for a "
        "week to coordinate with other teams; mitigated by feature flags. Rejected GitFlow because "
        "the develop branch + release branch overhead doesn't fit a 5-person team with daily prod deploy.'"
    ),
    layout=widgets.Layout(width="100%", min_height="80px"),
    description="Trade-offs:",
    style={"description_width": "180px"},
)
vc_tradeoffs_ta.add_class("diagnose-textarea")

vc_example_ta = widgets.Textarea(
    placeholder=(
        "Walk through ONE realistic scenario step by step.\\n"
        "Example: 'Analyst John is adding a delivery_time_to_dose model. He branches off main as "
        "feat/delivery-time-fact, commits work daily, opens a PR Tuesday. Slim CI runs in 4 min "
        "showing the new model + downstream models. Reviewer approves Wednesday. Squash-merge "
        "lands on main; the 6am Thursday prod deploy includes the new model.'"
    ),
    layout=widgets.Layout(width="100%", min_height="100px"),
    description="Example walkthrough:",
    style={"description_width": "180px"},
)
vc_example_ta.add_class("diagnose-textarea")

# Edge case panel — checkbox per category + SelectMultiple of canned scenarios
_vc_edge_panel_children = [
    widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:10px 14px; "
        "margin-bottom:10px; font-size:12.5px; line-height:1.55; border-radius:3px;'>"
        "<strong>Address at least 2 categories</strong> with canned scenario picks. "
        "These are the failure modes that would test your strategy in practice."
        "</div>"
    ),
]
for cat_id, cat_label, cat_prompt, options in _VC_EDGE_CATEGORIES:
    applies_cb = widgets.Checkbox(
        value=False,
        description=f"Yes, '{cat_label}' applies to this answer",
        indent=False,
        layout=widgets.Layout(width="100%"),
    )
    sel = widgets.SelectMultiple(
        options=options,
        rows=min(len(options), 4),
        description="Tick all that apply:",
        style={"description_width": "150px"},
        layout=widgets.Layout(width="100%"),
    )
    _vc_state["edge_widgets"][cat_id] = sel
    _vc_state["edge_applies"][cat_id] = applies_cb
    _vc_edge_panel_children.append(widgets.HTML(
        f"<div style='font-weight:600; font-size:13px; color:#0c447c; margin-top:14px;'>"
        f"{cat_label}</div>"
        f"<div style='font-size:12.5px; color:#444; margin-bottom:6px;'>{cat_prompt}</div>"
    ))
    _vc_edge_panel_children.append(applies_cb)
    _vc_edge_panel_children.append(sel)
vc_edge_panel_box = widgets.VBox(_vc_edge_panel_children)

# Reference patterns multi-select
vc_references_sel = widgets.SelectMultiple(
    options=_VC_REFERENCE_PATTERNS,
    rows=10,
    description="Reference patterns:",
    style={"description_width": "180px"},
    layout=widgets.Layout(width="100%"),
)

# Grade button + output
vc_grade_btn = widgets.Button(
    description="Get Version Control Feedback",
    button_style="success",
    layout=widgets.Layout(width="280px"),
)
vc_grade_out = widgets.Output()


# ============================================================
# branching_strategy — INTERACTIVE form (replaces text accordion)
# ============================================================
# Each section has: educational primer + structured picker widgets +
# canonical walkthrough answers. Mode toggle (solve / walkthrough) controls
# whether widgets start blank or pre-filled with explanations.

_VC_BRANCHING_INTERACTIVE = [
    {
        "section_id": "workflow_pattern",
        "title": "(1) Workflow pattern",
        "primer": (
            "<strong>What this means.</strong> A workflow pattern is the BIG decision that "
            "constrains everything else: how branches are organized, how features integrate, "
            "and how releases happen. Pick one canonical pattern and explain why it fits THIS team. "
            "<br><br><strong>Why for this team:</strong> 5 analysts, weekly feature deploys, daily prod. "
            "Small team + frequent deploys → favor lightweight patterns (GitHub Flow, Trunk-based). "
            "Heavy patterns (Git Flow with release/develop branches) are over-engineered here."
        ),
        "picks": [
            {
                "id": "pattern",
                "kind": "Dropdown",
                "label": "Workflow pattern",
                "options": [
                    ("— pick —", ""),
                    ("GitHub Flow — main + short-lived feature branches, deploy from main", "github_flow"),
                    ("Trunk-based development — main + tiny short-lived branches (<1 day), deploy multiple times daily", "trunk"),
                    ("Git Flow (Driessen 2010) — main + develop + feature/release/hotfix branches", "git_flow"),
                    ("GitLab Flow — main + production + per-environment branches", "gitlab_flow"),
                ],
                "walkthrough_value": "github_flow",
                "walkthrough_explain": (
                    "GitHub Flow fits a 5-person team with weekly deploys. main is always deployable; "
                    "feature branches live for 1-3 days; PRs gate every merge. Git Flow's develop + release "
                    "branches add ceremony that pays off only at 30+ engineer scale. Trunk-based is also "
                    "defensible if your team can deploy multiple times per day, but weekly cadence makes "
                    "GitHub Flow the cleaner pick."
                ),
            },
        ],
    },
    {
        "section_id": "branch_naming",
        "title": "(2) Branch naming convention",
        "primer": (
            "<strong>What this means.</strong> Naming conventions let teammates scan a list of branches "
            "and instantly know what each one is for. Three common patterns: type-prefix (feat/, fix/, chore/), "
            "ticket-based (DATA-123-pa-cycle), or author-prefix (trinidad/pa-cycle). "
            "<br><br><strong>Why it matters:</strong> on a small team you'll have 5-15 active branches. "
            "Without a convention, you waste time asking 'what branch was that PR on?' Branch names also drive "
            "automation — CI rules can match feat/* differently from hotfix/*."
        ),
        "picks": [
            {
                "id": "pattern",
                "kind": "Dropdown",
                "label": "Naming pattern",
                "options": [
                    ("— pick —", ""),
                    ("type-prefix (feat/pa-cycle, fix/dim-payer-typo, chore/bump-deps)", "type_prefix"),
                    ("ticket-based (DATA-123-pa-cycle)", "ticket_based"),
                    ("author-prefix (trinidad/pa-cycle)", "author_prefix"),
                    ("free-form (no convention enforced)", "free_form"),
                ],
                "walkthrough_value": "type_prefix",
                "walkthrough_explain": (
                    "Type-prefix is the standard for teams without strict ticket-tracking integration. "
                    "Examples: feat/pa-cycle-fact, fix/dim-payer-null, chore/bump-dbt-version. "
                    "Pairs well with Conventional Commits for the commit messages and lets CI rules "
                    "match patterns (e.g., hotfix/* triggers expedited deploy)."
                ),
            },
            {
                "id": "type_prefixes",
                "kind": "SelectMultiple",
                "label": "Allowed type prefixes",
                "options": [
                    "feat (new model, new metric, new test pack)",
                    "fix (bug fix in an existing model)",
                    "chore (deps, infra, non-functional changes)",
                    "refactor (restructuring without behavior change)",
                    "hotfix (urgent prod fix branched from main)",
                    "docs (documentation only)",
                    "test (test additions only)",
                    "exp (exploratory / spike, never merged)",
                ],
                "walkthrough_value": (
                    "feat (new model, new metric, new test pack)",
                    "fix (bug fix in an existing model)",
                    "chore (deps, infra, non-functional changes)",
                    "refactor (restructuring without behavior change)",
                    "hotfix (urgent prod fix branched from main)",
                ),
                "walkthrough_explain": (
                    "These five cover 95% of analytics work. feat for new fact tables, fix for "
                    "bugs in existing models, chore for dbt version bumps, refactor for renaming "
                    "columns or restructuring CTEs, hotfix for urgent prod patches."
                ),
            },
            {
                "id": "lifespan",
                "kind": "Dropdown",
                "label": "Branch lifespan target",
                "options": [
                    ("— pick —", ""),
                    ("Short-lived (1-3 days, merge quickly)", "short"),
                    ("Medium (1 week, sync with main daily)", "medium"),
                    ("Long-lived (weeks/months for big refactors)", "long"),
                ],
                "walkthrough_value": "short",
                "walkthrough_explain": (
                    "Short-lived branches are the safest — less drift from main, fewer conflicts, "
                    "easier reviews. The prompt mentions one analyst on a multi-day refactor — that's "
                    "a medium branch (sync with main daily to avoid drift). Long-lived branches "
                    "(weeks) are an anti-pattern in trunk-based / GitHub Flow; if a refactor is that "
                    "big, split it into a stack of short PRs."
                ),
            },
        ],
    },
    {
        "section_id": "merge_rules",
        "title": "(3) Merge rules — what gets into main",
        "primer": (
            "<strong>What this means.</strong> Merge rules define when changes can move into main "
            "and what shape they take. Branch protection enforces them server-side. Merge strategy "
            "(squash vs merge commit vs rebase) affects what main's git log looks like. "
            "<br><br><strong>Why it matters:</strong> main is what production deploys from. Anything "
            "that lands in main runs in front of executives at 6am. Strict gates (PR + CI + approval) "
            "catch bugs BEFORE they affect the dashboard. Merge strategy affects how easy bisect / "
            "revert are when something breaks."
        ),
        "picks": [
            {
                "id": "pr_required",
                "kind": "Dropdown",
                "label": "PR required to merge to main?",
                "options": [
                    ("— pick —", ""),
                    ("Yes — every change goes through a PR", "yes"),
                    ("No — direct push to main allowed", "no"),
                ],
                "walkthrough_value": "yes",
                "walkthrough_explain": (
                    "Always yes for analytics teams. Direct push to main bypasses review and CI, "
                    "which means a typo or broken model can reach prod silently. PR gate is the "
                    "single highest-leverage safety net."
                ),
            },
            {
                "id": "approvals",
                "kind": "Dropdown",
                "label": "Required approvals before merge",
                "options": [
                    ("— pick —", ""),
                    ("0 (peer review optional)", "0"),
                    ("1 (any teammate approves)", "1"),
                    ("2 (two-person review for safety)", "2"),
                    ("CODEOWNERS-driven (specific reviewer per file)", "codeowners"),
                ],
                "walkthrough_value": "1",
                "walkthrough_explain": (
                    "1 approval is the right balance for a 5-person team. 2 approvals slows everyone "
                    "and reviewer pool is too small. CODEOWNERS works when you have domain experts "
                    "(e.g., one analyst owns dim_payer); add it later if needed. The reviewer should "
                    "actually run dbt build locally if the change is non-trivial — the approval is a "
                    "real check, not a rubber stamp."
                ),
            },
            {
                "id": "ci_required",
                "kind": "Dropdown",
                "label": "CI must pass before merge?",
                "options": [
                    ("— pick —", ""),
                    ("Yes — green CI is a hard gate (branch protection)", "yes"),
                    ("No — CI is informational, can override", "no"),
                ],
                "walkthrough_value": "yes",
                "walkthrough_explain": (
                    "Hard gate. Use GitHub branch protection on main: 'require status checks to pass'. "
                    "Pick which checks are required (dbt build, dbt test, lint). Without this, someone "
                    "can merge a red CI 'just this once' and break prod."
                ),
            },
            {
                "id": "merge_strategy",
                "kind": "Dropdown",
                "label": "Merge strategy",
                "options": [
                    ("— pick —", ""),
                    ("Squash merge (1 commit per PR — clean history)", "squash"),
                    ("Merge commit (preserves all PR commits + a merge node)", "merge"),
                    ("Rebase merge (linear history, replays PR commits)", "rebase"),
                ],
                "walkthrough_value": "squash",
                "walkthrough_explain": (
                    "Squash merge = each PR becomes ONE commit on main. Pros: clean history, easy "
                    "bisect, easy revert (one commit to revert). Cons: loses individual commit messages "
                    "from the PR. For analytics dbt repos this is the standard pick. Rebase merge is "
                    "fine if you keep PR commits clean. Avoid plain merge commits — they clutter main."
                ),
            },
            {
                "id": "branch_protection",
                "kind": "Dropdown",
                "label": "Branch protection on main?",
                "options": [
                    ("— pick —", ""),
                    ("Yes — server-enforced (no force-push, PR required, CI required)", "yes"),
                    ("No — relies on team discipline", "no"),
                ],
                "walkthrough_value": "yes",
                "walkthrough_explain": (
                    "GitHub branch protection rules on main: (a) require PR before merge, (b) require "
                    "approving reviews, (c) require status checks (CI), (d) require conversation resolution, "
                    "(e) restrict who can push, (f) include administrators. Server-enforced is the only "
                    "reliable way — discipline alone fails when someone is in a hurry."
                ),
            },
        ],
    },
    {
        "section_id": "env_mapping",
        "title": "(4) Environment mapping + dbt schema isolation",
        "primer": (
            "<strong>What this means.</strong> Three environments — dev (analyst experimentation), "
            "staging (full prod-like build for validation), prod (executive dashboards). Each maps "
            "to a branch + a deploy trigger. dbt schema isolation prevents 5 analysts from clobbering "
            "each other's dev tables. "
            "<br><br><strong>Why it matters:</strong> the prompt says 'one analyst on a multi-day refactor "
            "while others ship smaller changes.' Without per-analyst dev schemas, when Trinidad runs "
            "<code>dbt run</code> she'd overwrite Maria's in-progress fct_pa_cycle. dbt's solution: each "
            "analyst writes to their own schema (e.g., <code>dbt_trinidad</code>, <code>dbt_maria</code>) "
            "via the dbt profile target."
        ),
        "picks": [
            {
                "id": "prod_branch",
                "kind": "Dropdown",
                "label": "Prod environment deploys from",
                "options": [
                    ("— pick —", ""),
                    ("main", "main"),
                    ("develop", "develop"),
                    ("production tag (semver release)", "tag"),
                ],
                "walkthrough_value": "main",
                "walkthrough_explain": (
                    "main is always-deployable in GitHub Flow. Prod runs from main on a 6am UTC "
                    "schedule (per the prompt). Tagged releases work for software libs but are overkill "
                    "for an analytics dbt repo with daily dashboards."
                ),
            },
            {
                "id": "prod_trigger",
                "kind": "Dropdown",
                "label": "Prod deploy trigger",
                "options": [
                    ("— pick —", ""),
                    ("Scheduled (cron / GitHub Actions schedule, e.g., daily 6am UTC)", "scheduled"),
                    ("On merge to main (every PR triggers prod build)", "on_merge"),
                    ("On tagged release (manual)", "on_tag"),
                    ("Manual button only", "manual"),
                ],
                "walkthrough_value": "scheduled",
                "walkthrough_explain": (
                    "Scheduled daily at 6am UTC matches the prompt. Lets the team batch a day's worth "
                    "of merges into one deploy. On-merge triggers run prod multiple times per day, "
                    "which can race with stakeholders looking at the dashboard. Most analytics teams "
                    "use scheduled."
                ),
            },
            {
                "id": "staging_trigger",
                "kind": "Dropdown",
                "label": "Staging environment trigger",
                "options": [
                    ("— pick —", ""),
                    ("On every PR (CI builds the changed models in staging schema)", "on_pr"),
                    ("On merge to main (post-merge validation before scheduled prod)", "on_merge"),
                    ("No staging — PR CI is enough", "none"),
                ],
                "walkthrough_value": "on_pr",
                "walkthrough_explain": (
                    "On every PR, run dbt slim CI (state:modified+) into a staging schema. The reviewer "
                    "can then query the staging tables to validate before approving. This is the "
                    "highest-leverage automated check — most bugs surface here."
                ),
            },
            {
                "id": "dev_isolation",
                "kind": "Dropdown",
                "label": "How analysts isolate dev work",
                "options": [
                    ("— pick —", ""),
                    ("Per-analyst dev schemas via dbt CLI target (e.g., dbt run --target trinidad_dev)", "cli_target"),
                    ("dbt Cloud personal dev credentials (each analyst has their own schema auto-prefixed)", "cloud_creds"),
                    ("Shared dev schema with prefixes (e.g., trinidad_fct_pa)", "shared_prefix"),
                    ("No isolation — everyone writes to dbt_dev", "none"),
                ],
                "walkthrough_value": "cli_target",
                "walkthrough_explain": (
                    "Per-analyst dev schemas via dbt profile target. In ~/.dbt/profiles.yml, each analyst "
                    "has their own target (trinidad_dev, maria_dev, etc) that writes to their personal "
                    "schema. Then dbt run --target trinidad_dev sends Trinidad's models to dbt_trinidad. "
                    "No collisions. dbt Cloud handles this automatically with personal dev creds. "
                    "Shared dev with prefixes is brittle (forgot the prefix? clobbered)."
                ),
            },
        ],
    },
    {
        "section_id": "pr_review",
        "title": "(5) PR review process",
        "primer": (
            "<strong>What this means.</strong> A PR review is the team's quality gate. The reviewer "
            "is checking: SQL correctness, test coverage, downstream impact (does this break a dashboard?), "
            "naming, documentation. "
            "<br><br><strong>Why it matters:</strong> reviews catch bugs cheaper than prod incidents. "
            "They're also how the team levels up — junior analysts learn dim modeling by reviewing "
            "senior analysts' PRs. A good review takes 10-30 min for a typical dbt PR; longer for "
            "schema changes."
        ),
        "picks": [
            {
                "id": "reviewers_required",
                "kind": "Dropdown",
                "label": "Required reviewers",
                "options": [
                    ("— pick —", ""),
                    ("1 reviewer (any teammate)", "1"),
                    ("2 reviewers (parallel review)", "2"),
                    ("CODEOWNERS — specific reviewer per file/folder", "codeowners"),
                    ("1 + senior approval for breaking changes", "1_plus_senior"),
                ],
                "walkthrough_value": "1",
                "walkthrough_explain": (
                    "1 reviewer for a 5-person team. Two-person review depletes reviewer capacity. "
                    "CODEOWNERS becomes useful once you have domain owners (e.g., dim_payer owner)."
                ),
            },
            {
                "id": "checks",
                "kind": "SelectMultiple",
                "label": "What reviewers MUST check",
                "options": [
                    "SQL logic correctness (does the model produce the right rows?)",
                    "dbt test coverage (unique, not_null, relationships, accepted_values)",
                    "Downstream model impact (run dbt ls --models +<model> to see consumers)",
                    "Materialization choice (table vs view vs incremental)",
                    "Naming conventions (stg_, int_, fct_, dim_ prefixes)",
                    "Model documentation (description in YAML, column-level docs)",
                    "Performance impact on prod build time",
                    "PII / data privacy for new columns",
                ],
                "walkthrough_value": (
                    "SQL logic correctness (does the model produce the right rows?)",
                    "dbt test coverage (unique, not_null, relationships, accepted_values)",
                    "Downstream model impact (run dbt ls --models +<model> to see consumers)",
                    "Naming conventions (stg_, int_, fct_, dim_ prefixes)",
                    "Model documentation (description in YAML, column-level docs)",
                ),
                "walkthrough_explain": (
                    "These five are the dbt PR-review canon. The big two are SQL logic (run the staging "
                    "build, check the rows) and downstream impact (a column rename can break 12 downstream "
                    "models). Materialization + perf are bonus for big PRs. PII checks become required "
                    "if you're touching patient data."
                ),
            },
            {
                "id": "self_merge",
                "kind": "Dropdown",
                "label": "Allow self-merge after approval?",
                "options": [
                    ("— pick —", ""),
                    ("Yes — author merges their own PR after approval lands", "yes"),
                    ("No — reviewer merges (extra checkpoint)", "no"),
                ],
                "walkthrough_value": "yes",
                "walkthrough_explain": (
                    "Self-merge is fine on a small team. Author knows when their tests are stable and "
                    "they're ready to ship. Reviewer-merges adds friction without much safety upside "
                    "since CI is already gating the merge."
                ),
            },
            {
                "id": "stale_reapproval",
                "kind": "Dropdown",
                "label": "Stale review re-approval after new commits?",
                "options": [
                    ("— pick —", ""),
                    ("Yes — new commits invalidate prior approval", "yes"),
                    ("No — once approved, stays approved", "no"),
                ],
                "walkthrough_value": "yes",
                "walkthrough_explain": (
                    "GitHub branch protection setting: 'dismiss stale pull request approvals when new "
                    "commits are pushed.' Yes is the safe default — otherwise an author can sneak in a "
                    "post-approval change. The reviewer just re-clicks approve in 30 seconds."
                ),
            },
        ],
    },
    {
        "section_id": "ci_integration",
        "title": "(6) CI integration",
        "primer": (
            "<strong>What this means.</strong> CI runs automated checks on every PR and merge. For a "
            "dbt repo, that's dbt parse, dbt build (only changed models, via slim CI), dbt test, and "
            "lint. Slim CI uses <code>--select state:modified+</code> to only build models that changed "
            "or depend on changed models — fast (3-5 min) instead of slow (30+ min full build). "
            "<br><br><strong>Why it matters:</strong> CI is the safety net. It catches: missing tests, "
            "broken refs, syntax errors, breaking schema changes, downstream model failures. Fast PR "
            "CI keeps reviewers unblocked. Slim CI is the canonical dbt pattern — every analytics team "
            "should use it."
        ),
        "picks": [
            {
                "id": "ci_tool",
                "kind": "Dropdown",
                "label": "CI tool",
                "options": [
                    ("— pick —", ""),
                    ("GitHub Actions", "github_actions"),
                    ("dbt Cloud (CI jobs)", "dbt_cloud"),
                    ("Both — GitHub Actions for lint/dbt parse, dbt Cloud for slim CI builds", "both"),
                ],
                "walkthrough_value": "github_actions",
                "walkthrough_explain": (
                    "GitHub Actions is the standard for dbt-core CLI users. dbt Cloud has a built-in "
                    "CI jobs feature if you're on Cloud. The prompt allows either; pick GitHub Actions "
                    "as the default unless the team is dbt Cloud-first."
                ),
            },
            {
                "id": "on_pr",
                "kind": "SelectMultiple",
                "label": "What runs on every PR",
                "options": [
                    "dbt parse (catches syntax errors fast, ~5 sec)",
                    "dbt build with state:modified+ (slim CI — only changed models + downstream)",
                    "dbt test (run all tests on the slim-CI build)",
                    "sqlfluff lint (style consistency)",
                    "regression check (compare row counts vs prod for changed models)",
                    "Full dbt build (slow — only do this on merge, not PR)",
                ],
                "walkthrough_value": (
                    "dbt parse (catches syntax errors fast, ~5 sec)",
                    "dbt build with state:modified+ (slim CI — only changed models + downstream)",
                    "dbt test (run all tests on the slim-CI build)",
                    "sqlfluff lint (style consistency)",
                ),
                "walkthrough_explain": (
                    "Slim CI on every PR. dbt parse for fast feedback, slim build + test for the real "
                    "check, sqlfluff for style. Full dbt build on PR is too slow (30+ min) — save it "
                    "for merge or scheduled runs. Regression check is a bonus for high-stakes models."
                ),
            },
            {
                "id": "on_merge",
                "kind": "SelectMultiple",
                "label": "What runs on merge to main",
                "options": [
                    "Full dbt build to staging (validation)",
                    "dbt test (full)",
                    "Deploy to staging schema",
                    "Trigger scheduled prod build (or wait for cron)",
                    "Generate / publish dbt docs",
                    "Cut a release tag (semver)",
                ],
                "walkthrough_value": (
                    "Full dbt build to staging (validation)",
                    "dbt test (full)",
                    "Deploy to staging schema",
                    "Generate / publish dbt docs",
                ),
                "walkthrough_explain": (
                    "Post-merge: full build to staging (validates the merged change in a clean prod-like "
                    "environment), full test, refresh docs. Prod runs at 6am UTC on schedule, so we "
                    "don't trigger prod from merge — the cron picks it up."
                ),
            },
            {
                "id": "use_slim_ci",
                "kind": "Dropdown",
                "label": "Use dbt slim CI (state:modified+) for PR builds?",
                "options": [
                    ("— pick —", ""),
                    ("Yes — store prod manifest.json artifact, defer to it on PR builds", "yes"),
                    ("No — full build every PR", "no"),
                ],
                "walkthrough_value": "yes",
                "walkthrough_explain": (
                    "Slim CI is the canonical pattern. Store manifest.json from the latest prod build "
                    "as a CI artifact, then use <code>--defer --state path/to/prod/manifest.json --select "
                    "state:modified+</code> on PRs. Build time drops from 30 min to 3-5 min for typical "
                    "PRs. dbt Cloud handles this automatically; for GitHub Actions, store the manifest "
                    "as a workflow artifact."
                ),
            },
        ],
    },
]


# Mode toggle for the VC form (solve / walkthrough). Mirrors schema_design.
vc_mode_toggle = widgets.ToggleButtons(
    options=[("🧠 Solve mode (try blind)", "solve"),
             ("📖 Walkthrough mode (read answer + paraphrase)", "walkthrough")],
    value="solve",
    style={"button_width": "auto"},
)

# State for branching_strategy interactive form widgets.
_vc_branching_widgets = {}  # section_id -> {pick_id: widget}


def _vc_apply_branching_walkthrough():
    """Pre-fill all branching_strategy picks with their canonical walkthrough values."""
    for section in _VC_BRANCHING_INTERACTIVE:
        sid = section["section_id"]
        for pick in section["picks"]:
            pid = pick["id"]
            w = _vc_branching_widgets.get(sid, {}).get(pid)
            wval = pick.get("walkthrough_value")
            if w is None or wval is None:
                continue
            try:
                if isinstance(wval, tuple):
                    valid = tuple(v for v in wval if v in (w.options or ()))
                    w.value = valid
                else:
                    w.value = wval
            except Exception:
                pass


def _vc_clear_branching_picks():
    for section in _VC_BRANCHING_INTERACTIVE:
        sid = section["section_id"]
        for pick in section["picks"]:
            pid = pick["id"]
            w = _vc_branching_widgets.get(sid, {}).get(pid)
            if w is None:
                continue
            try:
                if pick["kind"] == "SelectMultiple":
                    w.value = ()
                else:
                    w.value = ""
            except Exception:
                pass


def _on_vc_mode_change(change):
    if change["new"] == "walkthrough":
        _vc_apply_branching_walkthrough()
    # In solve mode, leave existing picks alone (don't blow away user work)
vc_mode_toggle.observe(_on_vc_mode_change, names="value")


def _vc_rebuild_branching_interactive():
    """Render the structured interactive form for branching_strategy. Each section
    is a nested Accordion item containing primer HTML + structured pickers.
    Mode toggle at top controls solve / walkthrough fill behavior."""
    _vc_branching_widgets.clear()
    section_panels = []
    section_titles = []
    for section in _VC_BRANCHING_INTERACTIVE:
        sid = section["section_id"]
        _vc_branching_widgets[sid] = {}
        children = []
        # Primer
        children.append(widgets.HTML(
            f"<div style='background:#f6f8fa; border-left:3px solid #57606a; "
            f"padding:10px 14px; margin-bottom:10px; font-size:12.5px; "
            f"line-height:1.6; border-radius:3px;'>"
            f"{section['primer']}</div>"
        ))
        # Picks
        for pick in section["picks"]:
            pid = pick["id"]
            kind = pick["kind"]
            label = pick["label"]
            opts = pick["options"]
            if kind == "Dropdown":
                w = widgets.Dropdown(
                    options=opts,
                    description=label,
                    style={"description_width": "200px"},
                    layout=widgets.Layout(width="100%"),
                )
            elif kind == "SelectMultiple":
                w = widgets.SelectMultiple(
                    options=opts,
                    rows=min(len(opts), 6),
                    description=label,
                    style={"description_width": "200px"},
                    layout=widgets.Layout(width="100%"),
                )
            else:
                continue
            _vc_branching_widgets[sid][pid] = w
            children.append(w)
            # Walkthrough explanation panel (collapsible)
            wexp = pick.get("walkthrough_explain")
            if wexp:
                children.append(widgets.HTML(
                    f"<details style='margin:4px 0 10px 0; border-left:2px solid #1a7f37; "
                    f"padding-left:10px;'>"
                    f"<summary style='cursor:pointer; color:#1a7f37; font-weight:600; "
                    f"font-size:12px;'>💡 Show canonical answer + why (peek when stuck)</summary>"
                    f"<div style='margin-top:6px; font-size:12px; line-height:1.55; "
                    f"background:#f0f8f0; padding:8px 10px; border-radius:3px;'>"
                    f"{wexp}</div></details>"
                ))
        # Per-section walkthrough fill button
        section_btn = widgets.Button(
            description=f"Fill walkthrough for this section",
            button_style="info",
            layout=widgets.Layout(width="280px"),
        )
        def _fill_section(b, secid=sid):
            for pick in next(s for s in _VC_BRANCHING_INTERACTIVE if s["section_id"] == secid)["picks"]:
                pid = pick["id"]
                w = _vc_branching_widgets[secid].get(pid)
                wval = pick.get("walkthrough_value")
                if w is None or wval is None:
                    continue
                try:
                    if isinstance(wval, tuple):
                        valid = tuple(v for v in wval if v in (w.options or ()))
                        w.value = valid
                    else:
                        w.value = wval
                except Exception:
                    pass
        section_btn.on_click(_fill_section)
        children.append(section_btn)
        section_panels.append(widgets.VBox(children))
        section_titles.append(section["title"])

    inner_accordion = widgets.Accordion(children=section_panels)
    for i, t in enumerate(section_titles):
        inner_accordion.set_title(i, t)
    inner_accordion.selected_index = None  # all collapsed by default

    # Top-level fill-all walkthrough button
    fill_all_btn = widgets.Button(
        description="📖 Pre-fill ALL with walkthrough answers",
        button_style="warning",
        layout=widgets.Layout(width="380px"),
    )
    def _fill_all(b):
        _vc_apply_branching_walkthrough()
    fill_all_btn.on_click(_fill_all)

    clear_btn = widgets.Button(
        description="🧠 Clear all (start blind)",
        button_style="",
        layout=widgets.Layout(width="240px"),
    )
    def _clear_all(b):
        _vc_clear_branching_picks()
    clear_btn.on_click(_clear_all)

    vc_section_box.children = [
        widgets.HTML(
            "<div style='background:#fff8e6; border-left:3px solid #d1a72a; padding:10px 14px; "
            "margin:6px 0 10px 0; font-size:12.5px; line-height:1.55; border-radius:3px;'>"
            "<strong>👉 New to Git admin topics?</strong> Each section below has a primer explaining "
            "what it means and why it matters. Pick from dropdowns / multi-selects (no typing). "
            "<br><br>"
            "<strong>Two modes:</strong> "
            "<strong>Solve mode</strong> = pick blind, get graded. "
            "<strong>Walkthrough mode</strong> = pre-fill canonical answers and read the explanations "
            "to learn the patterns. Switch any time using the toggle below."
            "</div>"
        ),
        widgets.HTML(
            "<div style='font-weight:600; font-size:13px; color:#0c447c; margin:6px 0 4px 0;'>"
            "MODE</div>"
        ),
        vc_mode_toggle,
        widgets.HBox([fill_all_btn, clear_btn]),
        widgets.HTML(
            "<div style='font-weight:600; font-size:14px; color:#0c447c; margin:14px 0 6px 0;'>"
            "Step through each section below</div>"
            "<div style='font-size:12px; color:#57606a; margin:0 0 8px 0;'>"
            "Click any section to expand. The 💡 button under each pick shows the canonical answer + "
            "why if you get stuck."
            "</div>"
        ),
        inner_accordion,
    ]


def _vc_get_section_map(problem):
    sub = (problem or {}).get("_meta", {}).get("subtopic", "")
    return _VC_SECTION_MAPS.get(sub, _VC_GENERIC_SECTIONS)


def _vc_rebuild_section_box():
    """Rebuild the per-subtopic section accordion. Each section gets a textarea
    + a problem-aware hint."""
    p = STATE.get("problem") or {}
    sections = _vc_get_section_map(p)
    _vc_state["section_widgets"] = {}
    rows = [widgets.HTML(
        "<div style='background:#eef5fc; border-left:3px solid #0969da; padding:8px 12px; "
        "margin-bottom:8px; font-size:12.5px; line-height:1.5; border-radius:3px;'>"
        "<strong>Section breakdown.</strong> Each prompt has a structured set of sections — fill them all. "
        "Hints below each are the canon for that subtopic."
        "</div>"
    )]
    for field_id, label, hint in sections:
        rows.append(widgets.HTML(
            f"<div style='font-weight:600; font-size:13px; color:#0c447c; margin-top:10px;'>"
            f"{label}</div>"
            f"<div style='font-size:12px; color:#57606a; margin:4px 0 4px 0; line-height:1.55;'>"
            f"{hint}</div>"
        ))
        ta = widgets.Textarea(
            placeholder=f"Your answer for {label.lower()} ...",
            layout=widgets.Layout(width="100%", min_height="80px"),
        )
        ta.add_class("diagnose-textarea")
        _vc_state["section_widgets"][field_id] = ta
        rows.append(ta)
    vc_section_box.children = rows


def on_vc_grade(b):
    with vc_grade_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p:
            print("Generate a problem first."); return
        if p.get("_meta", {}).get("subtopic", "") not in _VC_SECTION_MAPS \
                and p.get("_meta", {}).get("category", "") != "version_control":
            print("This form is for version_control problems only."); return

        sections_payload = {
            fid: (w.value or "").strip()
            for fid, w in (_vc_state.get("section_widgets") or {}).items()
            if (w.value or "").strip()
        }
        # Serialize the branching_strategy structured picks (interactive form).
        # Only filled when the subtopic is branching_strategy and the interactive
        # rebuild populated _vc_branching_widgets.
        branching_picks = {}
        for sid, picks_map in (_vc_branching_widgets or {}).items():
            section_payload = {}
            for pid, w in picks_map.items():
                v = w.value
                if isinstance(v, tuple):
                    if v:
                        section_payload[pid] = list(v)
                else:
                    if v:
                        section_payload[pid] = v
            if section_payload:
                branching_picks[sid] = section_payload
        edge_picks = {
            cid: list(w.value or ())
            for cid, w in (_vc_state.get("edge_widgets") or {}).items()
            if (w.value or ())
        }
        edge_applies = {
            cid: bool(cb.value)
            for cid, cb in (_vc_state.get("edge_applies") or {}).items()
        }

        responses = {
            "goal": vc_goal_ta.value,
            "sections": sections_payload,
            "branching_picks": branching_picks,
            "mode": vc_mode_toggle.value,
            "tradeoffs": vc_tradeoffs_ta.value,
            "example": vc_example_ta.value,
            "edge_cases_per_category": edge_picks,
            "edge_cases_applies": edge_applies,
            "reference_patterns": list(vc_references_sel.value or ()),
        }
        any_filled = (
            (vc_goal_ta.value or "").strip()
            or sections_payload
            or branching_picks
            or (vc_tradeoffs_ta.value or "").strip()
            or (vc_example_ta.value or "").strip()
        )
        if not any_filled:
            print("Fill in at least a few fields before grading.")
            return
        print("Asking Claude to grade your version control response ...")
        try:
            result = dru.grade_vc_form(p, responses)
        except AttributeError:
            print("dru.grade_vc_form not yet defined — update notebooks/nb02_drill_utils.py first.")
            return
        clear_output(wait=True)
        if not result:
            print("Grading failed."); return
        try:
            saved_path = dru.save_vc_attempt(p, responses, grade=result, solved_dir=SOLVED_DIR)
            if saved_path:
                print(f"(attempt saved to {os.path.basename(saved_path)})")
        except Exception as save_err:
            print(f"(warning: could not save attempt: {save_err})")
        try:
            display(HTML(dru.vc_form_grade_to_html(result)))
        except Exception:
            print(result if isinstance(result, str) else str(result))
vc_grade_btn.on_click(on_vc_grade)


# Compose the VC form box
_vc_form_box = widgets.VBox([
    widgets.HTML(
        "<ul style='font-size:13px; line-height:1.6; margin:6px 0 10px 18px; padding-left:0;'>"
        "<li>6 fields. Open the section accordion to fill subtopic-specific sub-fields.</li>"
        "<li>Goal / recommendation comes first — pick a position before unpacking.</li>"
        "<li>Edge cases are picked from canned scenarios (no typing).</li>"
        "<li>Reference patterns multi-select rewards naming the canon.</li>"
        "</ul>"
    ),
    widgets.HTML(
        "<div style='font-weight:600; font-size:14px; color:#0c447c; margin-top:8px;'>"
        "(1) Goal / recommendation</div>"
    ),
    vc_goal_ta,
    widgets.HTML(
        "<div style='font-weight:600; font-size:14px; color:#0c447c; margin-top:14px;'>"
        "(2) Section breakdown — subtopic-specific</div>"
    ),
    vc_section_box,
    widgets.HTML(
        "<div style='font-weight:600; font-size:14px; color:#0c447c; margin-top:14px;'>"
        "(3) Trade-offs</div>"
    ),
    vc_tradeoffs_ta,
    widgets.HTML(
        "<div style='font-weight:600; font-size:14px; color:#0c447c; margin-top:14px;'>"
        "(4) Edge cases / failure modes</div>"
    ),
    vc_edge_panel_box,
    widgets.HTML(
        "<div style='font-weight:600; font-size:14px; color:#0c447c; margin-top:14px;'>"
        "(5) Concrete example walkthrough</div>"
    ),
    vc_example_ta,
    widgets.HTML(
        "<div style='font-weight:600; font-size:14px; color:#0c447c; margin-top:14px;'>"
        "(6) Reference patterns named</div>"
        "<div style='font-size:12px; color:#57606a; margin:4px 0 6px 0;'>"
        "Pick the standard names that apply. Showing you know the canon prevents reinventing terminology."
        "</div>"
    ),
    vc_references_sel,
    vc_grade_btn,
    vc_grade_out,
])


# Wire the actual form widgets into their placeholders so they render
# inside the new category accordion panels via _populate_category_panels.
# (Phase 2: the accordion is now category-organized with 4 children, and
# the placeholders live inside the relevant category panel.)
_schema_design_panel_placeholder.children = (_schema_design_form_box,)
_vc_panel_placeholder.children = (_vc_form_box,)


def refresh_subtopic_form():
    """When a schema_design problem loads, reset the form fields and auto-expand
    the 4th accordion panel so the user knows where to go. For other subtopics,
    leave the accordion alone (all panels collapsed by default)."""
    # Phase 1: repopulate the 4 category panels based on active subtopic.
    try:
        _populate_category_panels()
    except NameError:
        pass  # _populate_category_panels defined later in this cell
    except Exception as _e:
        print(f"[populate_category_panels warning] {type(_e).__name__}: {_e}")
    p = STATE.get("problem")
    sub = (p or {}).get("_meta", {}).get("subtopic", "")
    if sub == "schema_design":
        # Reset state and widgets
        _sd2_state["scd_picks"] = {}
        _sd2_state["conformed_picks"] = {}
        _sd2_state["models"] = []
        _sd2_state["test_selections"] = {}
        _sd2_state["test_custom"] = {}
        _sd2_state["translate_picks"] = {}
        _sd2_state["translate_decomp"] = {}
        sd2_business_process_ta.value = ""
        sd2_grain_ta.value = ""
        sd2_fact_cols_ta.value = ""
        sd2_key_dd.value = ""
        sd2_key_rationale_ta.value = ""
        sd2_scd_rationale_ta.value = ""
        sd2_conformed_rationale_ta.value = ""
        sd2_idem_dd.value = ""
        sd2_idem_rationale_ta.value = ""
        sd2_late_dd.value = ""
        sd2_late_rationale_ta.value = ""
        sd2_edge_ta.value = ""
        # Reset edge case picks (SelectMultiple needs an empty tuple, not "")
        for _w in _sd2_edge_cat_widgets.values():
            try:
                _w.value = ()
            except Exception:
                pass
        for _cb in _sd2_edge_applies_widgets.values():
            _cb.value = False
        sd2_models_box.children = []
        # Rebuild dynamic widgets from problem state
        _sd2_rebuild_dim_box()
        _sd2_rebuild_scd_box()
        _sd2_rebuild_conformed_box()
        _sd2_rebuild_tests_box()
        _sd2_rebuild_translate_box()
        try: _sd2_rebuild_metrics_box()
        except Exception: pass
        try: _sd2_rebuild_srccols_box()
        except Exception: pass
        try: _sd2_refresh_edge_suggestions()
        except Exception: pass
        _sd2_update_field_hints()
        _sd2_update_worked_examples()
        # Try to load and apply a previously saved attempt for this problem
        try:
            pid = (p or {}).get("_meta", {}).get("problem_id")
            saved = dru.load_schema_design_attempt(pid, SOLVED_DIR)
            if saved and saved.get("responses"):
                _sd2_apply_saved_responses(saved["responses"])
                # Re-apply mode after restoring (mode toggle's observe may have re-rendered hints)
                _sd2_apply_mode()
                with sd2_grade_out:
                    clear_output(wait=True)
                    saved_at = saved.get("saved_at", "")
                    grade = saved.get("grade") or {}
                    score = grade.get("total_score") if grade else None
                    score_msg = f" Last score: {score}/100." if score is not None else ""
                    print(f"Restored your prior attempt for this problem (saved {saved_at}).{score_msg}")
        except Exception as load_err:
            print(f"(warning: could not load saved attempt: {load_err})")
        # Phase 2: _populate_category_panels already opened the right
        # accordion entry (the slim view has only one child). No-op.
    elif (p or {}).get("_meta", {}).get("category", "") == "version_control":
        # Reset and rebuild the version control form for this subtopic.
        try:
            vc_goal_ta.value = ""
            vc_tradeoffs_ta.value = ""
            vc_example_ta.value = ""
            vc_references_sel.value = ()
            for _w in (_vc_state.get("edge_widgets") or {}).values():
                try:
                    _w.value = ()
                except Exception:
                    pass
            for _cb in (_vc_state.get("edge_applies") or {}).values():
                _cb.value = False
            sub = (p or {}).get("_meta", {}).get("subtopic", "")
            if sub == "branching_strategy":
                _vc_rebuild_branching_interactive()
            else:
                _vc_rebuild_section_box()
            # Try to restore a prior saved attempt for this problem
            try:
                pid = (p or {}).get("_meta", {}).get("problem_id")
                saved = dru.load_vc_attempt(pid, SOLVED_DIR) if hasattr(dru, "load_vc_attempt") else None
                if saved and saved.get("responses"):
                    r = saved["responses"]
                    vc_goal_ta.value = str(r.get("goal", "") or "")
                    vc_tradeoffs_ta.value = str(r.get("tradeoffs", "") or "")
                    vc_example_ta.value = str(r.get("example", "") or "")
                    refs = r.get("reference_patterns") or []
                    valid_refs = tuple(x for x in refs if x in (vc_references_sel.options or ()))
                    try:
                        vc_references_sel.value = valid_refs
                    except Exception:
                        pass
                    sec_payload = r.get("sections", {}) or {}
                    for fid, w in (_vc_state.get("section_widgets") or {}).items():
                        w.value = str(sec_payload.get(fid, "") or "")
                    edge_payload = r.get("edge_cases_per_category", {}) or {}
                    for cid, w in (_vc_state.get("edge_widgets") or {}).items():
                        sel = edge_payload.get(cid, [])
                        if isinstance(sel, list):
                            valid = tuple(s for s in sel if s in (w.options or ()))
                            try: w.value = valid
                            except Exception: pass
                    applies = r.get("edge_cases_applies", {}) or {}
                    for cid, cb in (_vc_state.get("edge_applies") or {}).items():
                        cb.value = bool(applies.get(cid, False))
                    with vc_grade_out:
                        clear_output(wait=True)
                        saved_at = saved.get("saved_at", "")
                        grade = saved.get("grade") or {}
                        score = grade.get("total_score") if grade else None
                        score_msg = f" Last score: {score}/100." if score is not None else ""
                        print(f"Restored your prior attempt for this problem (saved {saved_at}).{score_msg}")
            except Exception as load_err:
                print(f"(warning: could not load saved VC attempt: {load_err})")
        except Exception as e:
            print(f"[vc form rebuild error] {type(e).__name__}: {e}")
        # Phase 2: _populate_category_panels already opened the right
        # accordion entry (the slim view has only one child). No-op.
    else:
        # Phase 2: the accordion is rebuilt per problem in
        # _populate_category_panels, no manual collapse needed here.
        pass

# Diagnostic textarea theme + tab handling
display(HTML("""
<style>
.diagnose-textarea { width: 100% !important; }
.diagnose-textarea textarea {
  font: 14px/1.5 ui-monospace, Consolas, Menlo, monospace !important;
  tab-size: 4; -moz-tab-size: 4;
  border: 1px solid #44475a !important; border-radius: 6px !important;
  outline: none !important; padding: 8px 10px !important;
  background: #282a36 !important; color: #f8f8f2 !important;
  caret-color: #f8f8f2 !important; resize: vertical;
  min-height: 90px; width: 100% !important; box-sizing: border-box;
}
.diagnose-textarea textarea::placeholder { color: #6272a4 !important; }
.diagnose-textarea textarea::selection { background: #44475a !important; }
.diagnose-textarea textarea:focus { border-color: #bd93f9 !important; }
</style>
"""))

display(Javascript(r"""
(function () {
  function setupOne(ta) {
    if (ta.dataset.diagEnhanced) return;
    ta.dataset.diagEnhanced = "1";
    ta.addEventListener("keydown", function (e) {
      // Block Shift+Enter from re-running the cell (which would wipe the textarea)
      if (e.shiftKey && e.key === "Enter") {
        e.preventDefault(); e.stopPropagation();
        var s = ta.selectionStart, en = ta.selectionEnd, v = ta.value;
        ta.value = v.slice(0, s) + "\\n" + v.slice(en);
        ta.selectionStart = ta.selectionEnd = s + 1;
        ta.dispatchEvent(new Event("input", { bubbles: true }));
        return;
      }
      if (e.key !== "Tab") return;
      e.preventDefault(); e.stopPropagation();
      var s = ta.selectionStart, en = ta.selectionEnd, v = ta.value, indent = "    ";
      if (s === en && !e.shiftKey) {
        ta.value = v.slice(0, s) + indent + v.slice(en);
        ta.selectionStart = ta.selectionEnd = s + indent.length;
      } else {
        var before = v.slice(0, s);
        var lineStart = before.lastIndexOf("\\n") + 1;
        var block = v.slice(lineStart, en);
        var lines = block.split("\\n");
        var newLines = e.shiftKey
          ? lines.map(function (l) { return l.startsWith(indent) ? l.slice(indent.length) : (l.startsWith("\\t") ? l.slice(1) : l); })
          : lines.map(function (l) { return indent + l; });
        var indented = newLines.join("\\n");
        ta.value = v.slice(0, lineStart) + indented + v.slice(en);
        ta.selectionStart = lineStart;
        ta.selectionEnd = lineStart + indented.length;
      }
      ta.dispatchEvent(new Event("input", { bubbles: true }));
    });
  }
  function poll() { document.querySelectorAll(".diagnose-textarea textarea").forEach(setupOne); }
  poll(); setInterval(poll, 1000);
})();
"""))


# ============================================================
# Multiple choice quiz UI builder (Phase 1 rebuild)
# ============================================================

_mc_state = {
    "problem": None,
    "answer_widgets": {},
    "result_out": None,
}


def _build_mc_quiz_ui(problem):
    """Return a VBox with quiz widgets for the given multiple_choice problem."""
    _mc_state["problem"] = problem
    _mc_state["answer_widgets"] = {}

    qs = problem.get("questions", [])
    blocks = []
    blocks.append(widgets.HTML(
        f"<div style='padding:10px 14px; background:#ddf4ff; border-left:4px solid "
        f"#0969da; border-radius:4px; margin-bottom:12px;'>"
        f"<b>{problem.get('title','Quiz')}</b><br>"
        f"<span style='color:#57606a;'>{problem.get('introduction','')}</span></div>"
    ))

    for i, q in enumerate(qs):
        qid = q.get("id", f"q{i+1}")
        qt = q.get("type", "mcq")
        stem = q.get("question", "")
        opts = q.get("options", [])

        block_children = [widgets.HTML(
            f"<div style='margin-top:12px;'><b>Q{i+1} ({qt}):</b> {stem}</div>"
        )]

        if qt in ("mcq", "true_false"):
            opts_pairs = [(f"{chr(65+j)}. {o}", j) for j, o in enumerate(opts)]
            rb = widgets.RadioButtons(
                options=opts_pairs,
                value=None,
                description="",
                layout=widgets.Layout(margin="4px 0 4px 12px"),
            )
            block_children.append(rb)
            _mc_state["answer_widgets"][qid] = rb

        elif qt == "order":
            block_children.append(widgets.HTML(
                "<div style='font-size:12px; color:#57606a; margin-left:12px;'>"
                "For each position, pick which step belongs there. Each step is "
                "labeled A, B, C, ... and shown out of order below.</div>"
            ))
            labels_html = "<ol style='margin:4px 0 4px 24px;'>" + "".join(
                f"<li><b>{chr(65+j)}.</b> {o}</li>" for j, o in enumerate(opts)
            ) + "</ol>"
            block_children.append(widgets.HTML(labels_html))
            dd_list = []
            opts_pairs = [("— pick —", None)] + [(f"{chr(65+j)}", j) for j in range(len(opts))]
            for pos in range(len(opts)):
                dd = widgets.Dropdown(
                    options=opts_pairs,
                    value=None,
                    description=f"Pos {pos+1}:",
                    style={"description_width": "60px"},
                    layout=widgets.Layout(width="200px", margin="2px 12px"),
                )
                dd_list.append(dd)
            block_children.append(widgets.HBox(dd_list))
            _mc_state["answer_widgets"][qid] = dd_list

        blocks.append(widgets.VBox(block_children))

    submit_btn = widgets.Button(
        description="Grade Quiz",
        button_style="success",
        layout=widgets.Layout(width="180px", height="34px", margin="14px 0 6px 0"),
    )
    result_out = widgets.Output()
    _mc_state["result_out"] = result_out

    def on_submit(_):
        p = _mc_state.get("problem")
        if not p:
            return
        user_answers = {}
        for qid, w in _mc_state["answer_widgets"].items():
            if isinstance(w, list):
                picks = [d.value for d in w]
                if any(v is None for v in picks):
                    user_answers[qid] = None
                else:
                    user_answers[qid] = picks
            else:
                user_answers[qid] = w.value
        grade = dru.grade_multiple_choice_answers(p, user_answers)
        with result_out:
            clear_output(wait=True)
            score = grade["score"]; total = grade["total"]
            pct = round(100 * score / total) if total else 0
            color = "#1a7f37" if pct >= 75 else ("#d4a72c" if pct >= 50 else "#cf222e")
            display(HTML(
                f"<div style='padding:12px 16px; background:#fafbfc; border:1px solid "
                f"#d0d7de; border-radius:6px; margin-top:8px;'>"
                f"<h4 style='margin:0 0 8px; color:{color};'>Score: {score} / {total} "
                f"({pct}%)</h4>"
            ))
            for r in grade["results"]:
                tick = ("<span style='color:#1a7f37;'>&#10003; correct</span>"
                        if r["is_correct"] else
                        "<span style='color:#cf222e;'>&#10007; incorrect</span>")
                ua = r["user_answer"]
                ca = r["correct_answer"]
                opts = r["options"]
                def _label(ans, opts=opts):
                    if ans is None:
                        return "<i>(no answer)</i>"
                    if isinstance(ans, list):
                        return ", ".join(chr(65+i) for i in ans)
                    return f"{chr(65+ans)}. {opts[ans]}" if isinstance(ans, int) and 0 <= ans < len(opts) else str(ans)
                display(HTML(
                    f"<div style='margin:10px 0; padding:8px 12px; background:#fff; "
                    f"border:1px solid #d0d7de; border-radius:4px;'>"
                    f"<div><b>{r['id']}</b> &middot; {tick}</div>"
                    f"<div style='font-size:13px; color:#57606a; margin-top:4px;'>"
                    f"Your answer: {_label(ua)}</div>"
                    f"<div style='font-size:13px; color:#57606a;'>"
                    f"Correct answer: {_label(ca)}</div>"
                    f"<div style='margin-top:6px;'><b>Why:</b> {r['explanation']}</div>"
                    f"</div>"
                ))
            display(HTML("</div>"))

    submit_btn.on_click(on_submit)
    blocks.append(submit_btn)
    blocks.append(result_out)
    return widgets.VBox(blocks)


_sql_handoff_banner_html = (
    "<div style='padding:10px 14px; background:#fff8c5; border-left:4px solid "
    "#d4a72c; border-radius:4px; margin-top:10px;'>"
    "<b>SQL subtopic.</b> Use this accordion for the diagnostic form, then "
    "scroll to <b>Section 3 — Write your SQL</b> below to run, test, and submit."
    "</div>"
)


def _populate_category_panels():
    """Repopulate the active category panel based on the active subtopic, fold
    the SQL/KPI editor inside the panel where applicable, and rebuild the
    accordion to show only the active category (others are hidden so the page
    stays focused on the current problem)."""
    p = STATE.get("problem")
    if not p:
        return
    meta = p.get("_meta", {})
    cat = meta.get("category", "")
    sub = meta.get("subtopic", "")
    kind = meta.get("kind", "")

    # Prime the editor for the active problem so it shows the right pane
    # (SQL editor for kind=sql, KPI markdown answer area for kind=kpi).
    try:
        switch_editor_for_kind(kind)
    except NameError:
        pass
    except Exception as _e:
        print(f"[switch_editor_for_kind warning] {type(_e).__name__}: {_e}")
    try:
        apply_subtopic_editor_override(sub)
    except NameError:
        pass
    except Exception as _e:
        print(f"[apply_subtopic_editor_override warning] {type(_e).__name__}: {_e}")

    # Pick the children list for the active category panel.
    fallback = widgets.HTML("<i style='color:#57606a;'>No matching form for this subtopic.</i>")

    def _editor_block():
        """Reminder + editor_box, in a VBox so the editor sits below the form."""
        try:
            return widgets.VBox([reminder_box, editor_box])
        except NameError:
            return widgets.HTML(
                "<i style='color:#57606a;'>Editor widgets defined in the next "
                "cell — run that cell first.</i>"
            )

    if cat == "transformation_modeling":
        if sub == "schema_design":
            children = [_schema_design_panel_placeholder, _editor_block()]
        elif sub == "multiple_choice":
            children = [_build_mc_quiz_ui(p)]
        elif sub in ("dimensional_modeling", "scd_type_2"):
            children = [_modeling_panel, _editor_block()]
        else:
            children = [_modeling_panel, _editor_block()]
        active_panel = _panel_tm
    elif cat == "critical_reasoning":
        children = [_structural_panel, _editor_block()]
        active_panel = _panel_cr
    elif cat == "product_kpis":
        if sub == "multiple_choice":
            children = [_build_mc_quiz_ui(p)]
        elif sub == "metric_critique":
            try:
                _refresh_metric_critique_form()
            except NameError:
                pass  # form defined later in this cell
            children = [metric_critique_form_box]
        elif sub == "metric_design":
            try:
                _refresh_metric_design_form()
            except NameError:
                pass
            children = [metric_design_form_box]
        else:
            children = [_business_panel, _editor_block()]
        active_panel = _panel_pk
    elif cat == "version_control":
        if sub == "multiple_choice":
            children = [_build_mc_quiz_ui(p)]
        else:
            children = [_vc_panel_placeholder, _editor_block()]
        active_panel = _panel_vc
    else:
        children = [fallback]
        active_panel = _panel_tm

    active_panel.children = children

    # Rebuild the accordion to contain only the active category panel.
    # Other categories are hidden until the user generates a problem in them.
    _category_labels = {
        "transformation_modeling": "1. Data Transformation Modeling",
        "critical_reasoning":      "2. Critical Reasoning SQL",
        "product_kpis":            "3. Understanding Product Metrics & KPIs",
        "version_control":         "4. Version Control (Git workflows)",
    }
    label = _category_labels.get(cat, "Response Builder")
    _generic_diagnostics_accordion.children = (active_panel,)
    _generic_diagnostics_accordion.set_title(0, label)
    _generic_diagnostics_accordion.selected_index = 0

''', hidden=True)




# ============================================================
# Cell 7 — Combined editor with kind switcher
# ============================================================
code('''# ── Editor (SQL + KPI, switched on category kind) ──

def _render_problem_reminder():
    """Show the full problem detail in the editor area too, so the user does not have
    to scroll back to the picker. Schema/data/output sections are collapsed by default
    (compact=True) to save vertical space; click to expand."""
    p = STATE.get("problem")
    if not p:
        return widgets.HTML('<div style="color:#57606a; padding:10px;"><i>Generate a problem first.</i></div>')
    kind = p.get("_meta", {}).get("kind", "sql")
    if kind == "sql":
        return widgets.HTML(dru.render_sql_problem(p, compact=True))
    else:
        return widgets.HTML(dru.render_kpi_problem(p, compact=True))

reminder_box = widgets.VBox([_render_problem_reminder()])

def refresh_reminder():
    reminder_box.children = [_render_problem_reminder()]

# ---- SQL editor ----
code_ta = widgets.Textarea(
    value="/* notes */\\n\\n",
    placeholder="/* notes */\\n\\nSELECT ...",
    layout=widgets.Layout(width="100%", min_height="240px"),
)
code_ta.add_class("sql-code-editor")

test_btn = widgets.Button(description="Test", button_style="", layout=widgets.Layout(width="110px"))
run_btn = widgets.Button(description="Run", button_style="info", layout=widgets.Layout(width="110px"))
submit_btn = widgets.Button(description="Submit", button_style="success", layout=widgets.Layout(width="110px"))
hint_btn = widgets.Button(description="Hint", button_style="warning", layout=widgets.Layout(width="110px"))
format_btn = widgets.Button(description="Format", button_style="", layout=widgets.Layout(width="110px"),
                            tooltip="Re-indent SQL")
result_out = widgets.Output()
hint_out = widgets.Output()

# ---- KPI editor ----
markdown_ta = widgets.Textarea(
    placeholder="Write your answer in markdown ...",
    layout=widgets.Layout(width="100%", min_height="280px"),
)
markdown_ta.add_class("kpi-md-editor")

grade_btn = widgets.Button(description="Get Grade", button_style="success", layout=widgets.Layout(width="150px"))
kpi_hint_btn = widgets.Button(description="Hint", button_style="warning", layout=widgets.Layout(width="110px"))
kpi_save_btn = widgets.Button(description="Save Attempt", button_style="", layout=widgets.Layout(width="150px"))
reveal_btn = widgets.Button(description="Reveal Reference", button_style="", layout=widgets.Layout(width="180px"))
kpi_result_out = widgets.Output()
kpi_hint_out = widgets.Output()

sql_container = widgets.VBox([
    code_ta,
    widgets.HBox([test_btn, run_btn, submit_btn, hint_btn, format_btn]),
    hint_out, result_out,
])
kpi_container = widgets.VBox([
    markdown_ta,
    widgets.HBox([grade_btn, kpi_hint_btn, kpi_save_btn, reveal_btn]),
    kpi_hint_out, kpi_result_out,
])
editor_box = widgets.VBox([sql_container])

_section3_form_replaces_editor_subtopics = {"schema_design"}
_section3_replaced_notice = widgets.HTML(
    "<div style='background:#fff8e1; border-left:4px solid #f9a825; "
    "padding:10px 14px; border-radius:4px; font-size:13px;'>"
    "<strong>Form-graded subtopic.</strong> Your answer goes in the schema design form "
    "in section 2 (Diagnose). Click <em>Get Schema Design Feedback</em> there. This SQL "
    "editor is unused for this subtopic.</div>"
)


def switch_editor_for_kind(kind):
    if kind == "kpi":
        editor_box.children = [kpi_container]
    else:
        editor_box.children = [sql_container]


def apply_subtopic_editor_override(subtopic):
    """Some subtopics are graded entirely by a section 2 form (schema_design today).
    For those, replace the editor with a notice pointing back to section 2."""
    if subtopic in _section3_form_replaces_editor_subtopics:
        editor_box.children = [_section3_replaced_notice]

# ---- Hint ----
def on_hint(b):
    with hint_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p: print("Generate a problem first."); return
        idx = STATE.get("hint_index", 0)
        text = dru.get_hint(p, idx)
        STATE["hint_index"] = idx + 1
        total = len(p.get("hints", []))
        display(HTML(f'<div style="background:#fff8c5; border-left:4px solid #d4a72c; padding:10px 14px; border-radius:4px;"><strong>Hint {min(idx+1,total)}/{total}:</strong> {text}</div>'))

def on_kpi_hint(b):
    with kpi_hint_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p: print("Generate a problem first."); return
        idx = STATE.get("hint_index", 0)
        text = dru.get_hint(p, idx)
        STATE["hint_index"] = idx + 1
        total = len(p.get("hints", []))
        display(HTML(f'<div style="background:#fff8c5; border-left:4px solid #d4a72c; padding:10px 14px; border-radius:4px;"><strong>Hint {min(idx+1,total)}/{total}:</strong> {text}</div>'))

hint_btn.on_click(on_hint)
kpi_hint_btn.on_click(on_kpi_hint)

# ---- SQL Format ----
def on_format(b):
    try:
        import sqlparse
    except ImportError:
        with hint_out:
            clear_output(); print("Format requires sqlparse. pip install sqlparse")
        return
    raw = code_ta.value or ""
    parts = [p for p in sqlparse.split(raw) if p.strip()]
    formatted = [
        sqlparse.format(p, reindent_aligned=True, keyword_case="upper",
                        identifier_case=None, strip_comments=False).strip()
        for p in parts
    ]
    code_ta.value = "\\n\\n".join(formatted)
format_btn.on_click(on_format)

# ---- SQL Test/Run/Submit ----
def _current_dialect():
    return STATE.get("problem", {}).get("_meta", {}).get("dialect", "postgresql")

def _load_example_into_sandbox():
    p = STATE.get("problem"); d = _current_dialect()
    sbx.reset(d); sbx.execute_script(d, p.get("schema_ddl", ""))
    sbx.execute_script(d, p.get("example_input_data", ""))

def _load_test_into_sandbox():
    p = STATE.get("problem"); d = _current_dialect()
    sbx.reset(d); sbx.execute_script(d, p.get("schema_ddl", ""))
    sbx.execute_script(d, p.get("test_data", ""))

def _show_df(df, label="Output"):
    if df is None: return
    if df.empty:
        display(HTML(f'<div style="color:#57606a;"><b>{label}:</b> empty result set.</div>'))
    else:
        display(HTML(f'<h4>{label}</h4>' + df.to_html(index=False)))

def on_test(b):
    refresh_reminder()
    with result_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p or p.get("_meta", {}).get("kind") != "sql":
            print("No SQL problem loaded."); return
        try: _load_example_into_sandbox()
        except Exception as e: print(f"Sandbox load error: {e}"); return
        df, err = sbx.run_query(_current_dialect(), code_ta.value)
        if err:
            display(HTML(f'<div style="background:#ffebe9; border-left:4px solid #cf222e; padding:10px;"><b>Error:</b><pre style="white-space:pre-wrap; margin:6px 0 0;">{err}</pre></div>'))
            return
        _show_df(df, "Test output (example data)")

def on_run(b):
    refresh_reminder()
    with result_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p or p.get("_meta", {}).get("kind") != "sql":
            print("No SQL problem loaded."); return
        try: _load_example_into_sandbox()
        except Exception as e: print(f"Sandbox load error: {e}"); return
        df, err = sbx.run_query(_current_dialect(), code_ta.value)
        if err:
            display(HTML(f'<div style="background:#ffebe9; border-left:4px solid #cf222e; padding:10px;"><b>Error:</b><pre style="white-space:pre-wrap; margin:6px 0 0;">{err}</pre></div>'))
            return
        expected = dru.expected_to_dataframe(p, "example")
        ok, msg = sbx.compare_results(df, expected)
        color = "#dcfce7" if ok else "#ffebe9"
        bar = "#1a7f37" if ok else "#cf222e"
        verdict = "CORRECT on example data" if ok else "MISMATCH on example data"
        display(HTML(f'<div style="background:{color}; border-left:4px solid {bar}; padding:10px; margin-bottom:10px;"><b>{verdict}</b><pre style="white-space:pre-wrap; margin:6px 0 0;">{msg}</pre></div>'))
        _show_df(df, "Your output")
        _show_df(expected, "Expected output")

def on_submit(b):
    refresh_reminder()
    with result_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p or p.get("_meta", {}).get("kind") != "sql":
            print("No SQL problem loaded."); return
        try: _load_test_into_sandbox()
        except Exception as e: print(f"Sandbox load error: {e}"); return
        df, err = sbx.run_query(_current_dialect(), code_ta.value)
        if err:
            display(HTML(f'<div style="background:#ffebe9; border-left:4px solid #cf222e; padding:10px;"><b>Error on hidden test data:</b><pre style="white-space:pre-wrap; margin:6px 0 0;">{err}</pre></div>'))
            return
        expected = dru.expected_to_dataframe(p, "test")
        ok, msg = sbx.compare_results(df, expected)
        color = "#dcfce7" if ok else "#ffebe9"
        bar = "#1a7f37" if ok else "#cf222e"
        verdict = "PASS — saved to solved bank" if ok else "FAIL on hidden test data"
        if ok:
            try: dru.save_solved(p, code_ta.value, SOLVED_DIR)
            except Exception as e: msg += f"\\n(could not save solved record: {e})"
        display(HTML(f'<div style="background:{color}; border-left:4px solid {bar}; padding:10px; margin-bottom:10px;"><b>{verdict}</b><pre style="white-space:pre-wrap; margin:6px 0 0;">{msg}</pre></div>'))
        if not ok:
            _show_df(df, "Your output (hidden test data)")
            _show_df(expected, "Expected output (hidden test data)")

test_btn.on_click(on_test)
run_btn.on_click(on_run)
submit_btn.on_click(on_submit)

# ---- KPI Grade / Save / Reveal ----
def on_grade(b):
    refresh_reminder()
    with kpi_result_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p or p.get("_meta", {}).get("kind") != "kpi":
            print("No KPI problem loaded."); return
        if not (markdown_ta.value or "").strip():
            print("Write an answer first, then click Get Grade."); return
        print("Asking Claude to grade ...")
        result = dru.grade_kpi_answer(p, markdown_ta.value)
        clear_output(wait=True)
        if not result:
            print("Grading failed."); return
        display(HTML(dru.grade_to_html(result)))
        total = result.get("total_score", 0)
        if total >= 70:
            try:
                path = dru.save_solved(p, markdown_ta.value, SOLVED_DIR, grade_result=result)
                display(HTML(f'<div style="margin-top:8px; color:#1a7f37; font-size:13px;">Saved to solved bank ({os.path.basename(path)}). Score {total}/100.</div>'))
            except Exception as e:
                display(HTML(f'<div style="color:#cf222e;">Could not save solved record: {e}</div>'))

def on_kpi_save(b):
    with kpi_result_out:
        p = STATE.get("problem")
        if not p or p.get("_meta", {}).get("kind") != "kpi":
            print("No KPI problem loaded."); return
        try:
            path = dru.save_solved(p, markdown_ta.value or "", SOLVED_DIR, grade_result=None)
            print(f"Attempt saved: {os.path.basename(path)}")
        except Exception as e:
            print(f"Save error: {e}")

def on_reveal(b):
    with kpi_result_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p or p.get("_meta", {}).get("kind") != "kpi":
            print("No KPI problem loaded."); return
        ref = p.get("reference_answer", "")
        common = p.get("common_mistakes", [])
        common_html = ""
        if common:
            common_html = "<h4 style='margin-top:14px;'>Common mistakes</h4><ul>" + "".join(f"<li>{c}</li>" for c in common) + "</ul>"
        display(HTML(
            '<div style="border:1px solid #d0d7de; border-radius:6px; padding:14px; background:#f6f8fa;">'
            '<h4 style="margin:0 0 10px;">Reference answer</h4>'
            f'<div style="white-space:pre-wrap; font-family:ui-monospace, Menlo, monospace; font-size:13px; line-height:1.5;">{ref}</div>'
            f'{common_html}'
            '</div>'
        ))

grade_btn.on_click(on_grade)
kpi_save_btn.on_click(on_kpi_save)
reveal_btn.on_click(on_reveal)

# Phase 2: editor widgets are folded inside the response builder accordion;
# display call suppressed so this cell no longer renders Section 3 inline.
# (sql_container, kpi_container, editor_box, reminder_box remain defined globals.)

# Editor styles
display(HTML("""
<style>
.sql-editor-container {
  display: flex; border: 1px solid #44475a; border-radius: 6px;
  overflow: hidden; background: #282a36; margin-top: 6px;
  width: 100% !important; box-sizing: border-box;
}
.sql-editor-container .line-gutter {
  background: #21222c; color: #6272a4; padding: 8px 10px; text-align: right;
  font: 13px/1.5 ui-monospace, Consolas, Menlo, monospace;
  user-select: none; white-space: pre; min-width: 36px;
  border-right: 1px solid #44475a; overflow: hidden;
}
.sql-editor-container .line-gutter-inner { will-change: transform; }
.sql-code-editor { width: 100% !important; }
.sql-code-editor textarea {
  font: 14px/1.5 ui-monospace, Consolas, Menlo, monospace !important;
  tab-size: 4; -moz-tab-size: 4;
  border: none !important; outline: none !important;
  padding: 8px 10px !important; margin: 0 !important;
  background: #282a36 !important; color: #f8f8f2 !important;
  caret-color: #f8f8f2 !important;
  flex: 1 1 auto; resize: vertical; min-height: 280px; width: 100% !important;
}
.sql-code-editor textarea::placeholder { color: #6272a4 !important; }
.sql-code-editor textarea::selection { background: #44475a !important; }

.kpi-md-editor textarea {
  font: 14px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
  border: 1px solid #d0d7de !important; border-radius: 6px !important;
  outline: none !important; padding: 12px !important;
  background: #ffffff !important; color: #1f2328 !important;
  resize: vertical; min-height: 280px; width: 100% !important; box-sizing: border-box;
}
.kpi-md-editor textarea:focus { border-color: #0969da !important; }
.kpi-md-editor textarea::placeholder { color: #6e7781 !important; }

.kpi-rubric-table { font-size: 13px; border-collapse: collapse; width: 100%; margin-top: 6px; }
.kpi-rubric-table th, .kpi-rubric-table td { border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; vertical-align: top; }
.kpi-rubric-table th { background: #f6f8fa; }
</style>
"""))

display(Javascript(r"""
(function () {
  function setupOne(ta) {
    if (ta.dataset.sqlEnhanced) return;
    ta.dataset.sqlEnhanced = "1";
    var parent = ta.parentNode;
    var wrap = document.createElement("div");
    wrap.className = "sql-editor-container";
    var gutter = document.createElement("div");
    gutter.className = "line-gutter";
    var gutterInner = document.createElement("div");
    gutterInner.className = "line-gutter-inner";
    gutter.appendChild(gutterInner);
    parent.insertBefore(wrap, ta);
    wrap.appendChild(gutter); wrap.appendChild(ta);
    function refresh() {
      var n = (ta.value.match(/\\n/g) || []).length + 1;
      var s = "";
      for (var i = 1; i <= n; i++) s += i + "\\n";
      gutterInner.textContent = s;
    }
    refresh();
    ta.addEventListener("input", refresh);
    ta.addEventListener("scroll", function () {
      gutterInner.style.transform = "translateY(" + (-ta.scrollTop) + "px)";
    });
    ta.addEventListener("keydown", function (e) {
      // Block Shift+Enter from re-running the cell (which would wipe the textarea)
      if (e.shiftKey && e.key === "Enter") {
        e.preventDefault(); e.stopPropagation();
        // Insert a literal newline at cursor instead — feels natural for SQL editing
        var s = ta.selectionStart, en = ta.selectionEnd, v = ta.value;
        ta.value = v.slice(0, s) + "\\n" + v.slice(en);
        ta.selectionStart = ta.selectionEnd = s + 1;
        ta.dispatchEvent(new Event("input", { bubbles: true }));
        refresh();
        return;
      }
      if (e.key !== "Tab") return;
      e.preventDefault(); e.stopPropagation();
      var s = ta.selectionStart, en = ta.selectionEnd, v = ta.value, indent = "    ";
      if (s === en && !e.shiftKey) {
        ta.value = v.slice(0, s) + indent + v.slice(en);
        ta.selectionStart = ta.selectionEnd = s + indent.length;
      } else {
        var before = v.slice(0, s);
        var lineStart = before.lastIndexOf("\\n") + 1;
        var block = v.slice(lineStart, en);
        var lines = block.split("\\n");
        var newLines = e.shiftKey
          ? lines.map(function (l) { return l.startsWith(indent) ? l.slice(indent.length) : (l.startsWith("\\t") ? l.slice(1) : l); })
          : lines.map(function (l) { return indent + l; });
        var indented = newLines.join("\\n");
        ta.value = v.slice(0, lineStart) + indented + v.slice(en);
        ta.selectionStart = lineStart;
        ta.selectionEnd = lineStart + indented.length;
      }
      ta.dispatchEvent(new Event("input", { bubbles: true }));
      refresh();
    });
  }
  function poll() { document.querySelectorAll(".sql-code-editor textarea").forEach(setupOne); }
  poll(); setInterval(poll, 1000);
})();
"""))
''', hidden=True)


# ============================================================
# Cell 8 — Next problem header
# ============================================================
md('''## 3. Next problem

Clear all fields and start over.
''')


# ============================================================
# Cell 9 — Next button
# ============================================================
code('''# ── Next Question ──
next_btn = widgets.Button(description="Next Question (clear all)", button_style="danger",
                          layout=widgets.Layout(width="240px", height="34px"))
next_out = widgets.Output()

def on_next(b):
    STATE["problem"] = None
    STATE["hint_index"] = 0
    # Reset SQL editor to the notes scaffold so the user always starts from the same baseline
    code_ta.value = "/* notes */\\n\\n"
    markdown_ta.value = ""
    paraphrase_ta.value = ""
    moves_ta.value = ""
    input_dd.value = ""
    output_dd.value = ""
    recipe_dd.value = ""
    interpretation_ta.value = ""
    recommendation_ta.value = ""
    materialization_dd.value = ""
    materialization_rationale_ta.value = ""
    grain_ta.value = ""
    join_strategy_ta.value = ""
    dbt_layer_dd.value = ""
    for _cb in _dbt_cb_widgets.values():
        _cb.value = False
    test_coverage_details_ta.value = ""
    design_notes_ta.value = ""
    # Schema design form (sd2_*) is reset inside refresh_subtopic_form() since
    # most of its widgets are dynamic (built per-problem).
    try: refresh_reminder()
    except NameError: pass
    try: refresh_subtopic_form()
    except NameError: pass
    for area in [problem_out, feedback_out, modeling_feedback_out, business_feedback_out, result_out, hint_out, kpi_result_out, kpi_hint_out, status_out, next_out, sd2_grade_out]:
        try:
            with area: clear_output(wait=True)
        except Exception: pass
    with next_out:
        print("Cleared. Pick a category and generate a new problem above.")

next_btn.on_click(on_next)
display(widgets.VBox([next_btn, next_out]))
''')


# ============================================================
# Cell 10 — Footer
# ============================================================
md('''---

**Files written each run:**

- `data/outputs/generated_problems/` — every generated problem (loadable via Source: Saved)
- `data/outputs/solved/` — your passing SQL solves and KPI grade attempts
- `data/outputs/sessions/` — reserved for session logs

**Key files:**

- `nb02_drill_utils.py` — category catalog, prompt templates, generators, KPI grader
- `sql_practice_utils.py` — shared with nb01 (validation harness, hints, helpers)
- `sandbox.py` — Postgres + MySQL connection (Postgres only used here)
''')


# ============================================================
# Write the notebook
# ============================================================
nb = {
    "cells": CELLS,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out_path = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "notebooks", "nb02_fuze_interview_drills.ipynb")
)
with open(out_path, "w") as f:
    json.dump(nb, f, indent=1)

print(f"Wrote {out_path}")
print(f"Cells: {len(CELLS)} ({sum(1 for c in CELLS if c['cell_type']=='code')} code, {sum(1 for c in CELLS if c['cell_type']=='markdown')} markdown)")



# ============================================================
# metric_critique response form (Phase 3)
# ============================================================
# Two field structured response with Solve / Walkthrough toggle. When the
# active subtopic is metric_critique, _populate_category_panels swaps this
# form into Accordion 3 (Product Metrics & KPIs) instead of the generic
# Business Analysis panel.

mc_mode_toggle = widgets.ToggleButtons(
    options=[
        ("🎯 Guided (decision flow)", "guided"),
        ("🧠 Try blind (fill in the blank)", "solve"),
        ("📖 Walkthrough (read the answer, paraphrase)", "walkthrough"),
    ],
    value="guided",
    description="Mode:",
    style={"description_width": "60px", "button_width": "260px"},
    layout=widgets.Layout(margin="6px 0 10px 0"),
)


# Framework reference shown at the top of the Step 1 block. GSM expanded
# to Goal, Signal, Metric per the user's request, and the 5 Pressure Test
# checks are now a bullet list.
_mc_framework_ref = widgets.HTML(
    "<div style='background:#ddf4ff; border-left:4px solid #0969da; "
    "padding:10px 14px; border-radius:4px; margin:10px 0;'>"
    "<b>Framework: Product Analytics Academy — Goal, Signal, Metric (GSM) "
    "+ Pressure Test</b><br>"
    "<span style='font-size:12px;'>For &quot;what is wrong with this metric&quot; "
    "questions, the prescribed approach is to <b>skip GSM</b> and walk the "
    "metric through the 5 Pressure Test checks:</span>"
    "<ul style='font-size:12px; margin:6px 0 6px 18px;'>"
    "<li>Ambiguity</li>"
    "<li>Normalization</li>"
    "<li>Time window</li>"
    "<li>Survivorship</li>"
    "<li>Understandability</li>"
    "</ul>"
    "<span style='font-size:12px;'>The dropdowns below cover all 5 checks. "
    "Pick &quot;Not sure&quot; for any check that doesn't apply to the current metric "
    "— the Compose button will only assemble a sentence from the checks that "
    "failed.</span></div>"
)


# Helper that renders a <details> collapsible explaining a Pressure Test
# check and giving a sentence template for translating picks into prose.
def _mc_info_block(title, what_it_checks, how_to_read, sentence_template):
    return widgets.HTML(
        f"<details style='margin:2px 0 8px 0;'>"
        f"<summary style='cursor:pointer; color:#0969da; font-size:12px;'>"
        f"ℹ How to read {title}</summary>"
        f"<div style='background:#f6f8fa; border:1px solid #d0d7de; "
        f"border-radius:4px; padding:8px 12px; margin-top:4px; font-size:12px;'>"
        f"<div><b>What this check is asking:</b> {what_it_checks}</div>"
        f"<div style='margin-top:6px;'><b>How to read the options:</b> {how_to_read}</div>"
        f"<div style='margin-top:6px;'><b>Sentence template:</b> {sentence_template}</div>"
        f"</div></details>"
    )


# --- Q1 Ambiguity ------------------------------------------------------
_mc_q1_label = widgets.HTML(
    "<div style='margin-top:10px;'>"
    "<b>Q1 — Pressure Test: Ambiguity</b><br>"
    "<span style='font-size:12px; color:#57606a;'>Can this metric move up for "
    "<i>opposite</i> reasons? If yes, the metric is ambiguous — a rise could "
    "mean improvement OR degradation, and you can't tell which without "
    "decomposing the metric further.</span></div>"
)
mc_g_q1_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Yes — it is ambiguous (moves up whether behavior improves or degrades)", "ambiguous"),
        ("No — it cleanly tracks one direction (better behavior moves it up only)", "clean"),
        ("Not sure", "unsure"),
    ],
    value="",
    description="Q1:",
    style={"description_width": "30px"},
    layout=widgets.Layout(width="700px", margin="3px 0"),
)
_mc_q1_info = _mc_info_block(
    title="Q1 (Ambiguity)",
    what_it_checks=(
        "Whether the metric can rise for two different reasons. Example: "
        "&quot;total matches per week&quot; rises if quality improved OR if you simply "
        "added more users (without per user quality changing)."
    ),
    how_to_read=(
        "Pick <b>Yes</b> if the metric mixes two signals (volume + quality, "
        "engagement + sign ups, etc.). Pick <b>No</b> if only one mechanism can "
        "move it. Pick <b>Not sure</b> if the prompt doesn't give you enough "
        "to tell."
    ),
    sentence_template=(
        "&quot;This metric is ambiguous because it can rise both when "
        "[improvement scenario] and when [degradation scenario].&quot;"
    ),
)
_mc_q1_walk = widgets.HTML("")

# --- Q2 Normalization --------------------------------------------------
_mc_q2_label = widgets.HTML(
    "<div style='margin-top:10px;'>"
    "<b>Q2 — Pressure Test: Normalization</b><br>"
    "<span style='font-size:12px; color:#57606a;'>Is the metric a raw count "
    "or a rate? Raw counts scale with the user base. Rates normalize per user, "
    "per session, per interaction. <b>Time window (&quot;per week&quot;) is a separate "
    "check — see Q3.</b> Normalization here means &quot;divided by users / sessions / "
    "interactions.&quot;</span></div>"
)
mc_g_q2_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Raw count or total — has no per-user, per-session, or per-interaction divisor", "raw_count"),
        ("Rate or percentage — already divided by users / sessions / interactions", "rate"),
        ("Duration or statistic — median, p95, mean (e.g., median time to first match)", "duration"),
        ("Not sure", "unsure"),
    ],
    value="",
    description="Q2:",
    style={"description_width": "30px"},
    layout=widgets.Layout(width="700px", margin="3px 0"),
)
_mc_q2_info = _mc_info_block(
    title="Q2 (Normalization)",
    what_it_checks=(
        "Whether the metric divides by a population (users, sessions, "
        "interactions). &quot;Per week&quot; is NOT normalization — that's the time "
        "window check (Q3). &quot;Per user&quot; or &quot;per session&quot; IS normalization."
    ),
    how_to_read=(
        "Pick <b>Raw count</b> for any metric that has no per user / per "
        "session / per interaction divisor — even if it has a time window. "
        "&quot;Total matches this week&quot; is a raw count because it doesn't divide "
        "by users. Pick <b>Rate</b> for &quot;matches per active user&quot; or &quot;match "
        "rate per interaction.&quot; Pick <b>Duration</b> for &quot;median time to first "
        "match&quot; or &quot;p95 latency.&quot;"
    ),
    sentence_template=(
        "&quot;This metric is a raw count not normalized per [users / sessions / "
        "interactions], so a larger cohort always appears better even when "
        "per user behavior is worse.&quot;"
    ),
)
_mc_q2_walk = widgets.HTML("")

# --- Q3 Time window ----------------------------------------------------
_mc_q3_label = widgets.HTML(
    "<div style='margin-top:10px;'>"
    "<b>Q3 — Pressure Test: Time window</b><br>"
    "<span style='font-size:12px; color:#57606a;'>Does the metric specify "
    "a window (per day, per week, rolling 28 days)? Without a window the "
    "metric drifts — &quot;total matches&quot; means different things depending on "
    "whether you mean today or all time.</span></div>"
)
mc_g_q3_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Yes — has an explicit time window (per day / week / rolling 28 days, etc.)", "windowed"),
        ("No window specified — the metric drifts in scope", "no_window"),
        ("Not sure", "unsure"),
    ],
    value="",
    description="Q3:",
    style={"description_width": "30px"},
    layout=widgets.Layout(width="700px", margin="3px 0"),
)
_mc_q3_info = _mc_info_block(
    title="Q3 (Time window)",
    what_it_checks=(
        "Whether the metric tells you WHEN it is measured. &quot;Total matches "
        "per week&quot; passes — the window is &quot;per week.&quot; &quot;Total matches&quot; with no "
        "window fails — you don't know if that's today, last 30 days, or all "
        "time."
    ),
    how_to_read=(
        "Pick <b>Yes</b> if the metric name or definition includes phrases "
        "like &quot;per day,&quot; &quot;per week,&quot; &quot;rolling 28 days,&quot; or &quot;during the "
        "experiment window.&quot; Pick <b>No window</b> if the metric is stated as "
        "a flat number with no temporal scope."
    ),
    sentence_template=(
        "&quot;This metric has no explicit time window, so it is not operable — "
        "you can't tell whether it's measured daily, weekly, or all time.&quot;"
    ),
)
_mc_q3_walk = widgets.HTML("")

# --- Q4 Survivorship ---------------------------------------------------
_mc_q4d_label = widgets.HTML(
    "<div style='margin-top:10px;'>"
    "<b>Q4 — Pressure Test: Survivorship</b><br>"
    "<span style='font-size:12px; color:#57606a;'>Does the metric's "
    "denominator only include users who already succeeded at some prior "
    "step? If yes, the metric is biased: users who would have failed are "
    "excluded from the population entirely.</span></div>"
)
mc_g_q4d_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Yes — denominator only counts users who already passed an earlier step (survivorship bias)", "survivorship"),
        ("No — denominator includes everyone who could have done the action", "clean_denom"),
        ("N/A — the metric has no denominator (it is a raw count)", "no_denom"),
        ("Not sure", "unsure"),
    ],
    value="",
    description="Q4:",
    style={"description_width": "30px"},
    layout=widgets.Layout(width="700px", margin="3px 0"),
)
_mc_q4d_info = _mc_info_block(
    title="Q4 (Survivorship)",
    what_it_checks=(
        "Whether the population in the denominator was already filtered. "
        "Example: &quot;match rate per user who completed verification&quot; — the "
        "denominator excludes users who quit during verification, so the rate "
        "looks better than the true funnel."
    ),
    how_to_read=(
        "Pick <b>Yes</b> if the denominator implicitly excludes users who "
        "would have failed (verified users only, paying users only, users who "
        "completed profile only). Pick <b>No</b> if everyone who could have "
        "done the action is counted. Pick <b>N/A</b> if there is no denominator."
    ),
    sentence_template=(
        "&quot;The denominator only includes [survivor population], which "
        "excludes [users who failed earlier], so the rate looks better than "
        "the true end to end funnel.&quot;"
    ),
)
_mc_q4d_walk = widgets.HTML("")

# --- Q5 Understandability ----------------------------------------------
_mc_q5d_label = widgets.HTML(
    "<div style='margin-top:10px;'>"
    "<b>Q5 — Pressure Test: Understandability</b><br>"
    "<span style='font-size:12px; color:#57606a;'>Could a PM or exec hold "
    "this metric in their head and explain it to someone else without "
    "looking it up? If not, the metric won't drive action because the team "
    "can't reason about it day to day.</span></div>"
)
mc_g_q5d_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Yes — easy to remember and explain in one sentence", "understandable"),
        ("No — the formula is too complex for a PM to hold in their head", "not_understandable"),
        ("No — simple, but doesn't address the scenario's purpose", "doesnt_address_purpose"),
        ("Not sure", "unsure"),
    ],
    value="",
    description="Q5:",
    style={"description_width": "30px"},
    layout=widgets.Layout(width="700px", margin="3px 0"),
)
_mc_q5d_info = _mc_info_block(
    title="Q5 (Understandability)",
    what_it_checks=(
        "Whether the metric is operable in day to day product conversations. "
        "Highly complex metrics (multi step composite scores, ML model "
        "outputs) often fail this check even when they are technically valid."
    ),
    how_to_read=(
        "Pick <b>Yes</b> if you can summarize the metric in one sentence (e.g., "
        "&quot;mutual matches per active user, weekly&quot;). Pick <b>No</b> if it "
        "takes a paragraph to explain or if the formula has 3+ nested conditions."
    ),
    sentence_template=(
        "&quot;This metric is too complex for a PM to hold in their head; a "
        "simpler proxy like [simpler metric] would be more operable.&quot;"
    ),
)
_mc_q5d_walk = widgets.HTML("")


# --- Step 2 Fix dropdowns (renumbered Q6 / Q7 / Q8) --------------------
_mc_fix_source_note = widgets.HTML(
    "<div style='background:#fff8c5; border-left:4px solid #d4a72c; "
    "padding:8px 12px; border-radius:4px; margin:10px 0; font-size:12px;'>"
    "<b>About these options:</b> the Q6 / Q7 / Q8 dropdowns are curated "
    "lists drawn from the BooedUp app context (mutual matches, interactions, "
    "active users, Type Score). They are <i>not</i> generated per problem by "
    "Claude — they are static options chosen to fit dating app metrics in "
    "general. For a problem that doesn't fit any option, pick the closest "
    "match and edit the composed draft in the Step 2 textarea.</div>"
)

_mc_q6_label = widgets.HTML(
    "<div style='margin-top:10px;'>"
    "<b>Q6 — Fix: numerator of the corrected metric</b><br>"
    "<span style='font-size:12px; color:#57606a;'>What event or count goes "
    "on top? Pick the user behavior that actually reflects success of the "
    "feature.</span></div>"
)
mc_g_num_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Mutual matches in the period", "mutual_matches"),
        ("Interactions initiated (likes, winks, superlikes)", "interactions"),
        ("Messages sent in the period", "messages_sent"),
        ("First messages sent after a Match or Wingman connection", "first_messages"),
        ("Reply messages (responses to an existing thread)", "reply_messages"),
        ("Profile views received", "profile_views"),
        ("Paid (Premium) upgrades in the period", "premium_upgrades"),
        ("Activated users (verified + profile complete + first interaction)", "activated"),
        ("Sessions", "sessions"),
    ],
    value="",
    description="Q6:",
    style={"description_width": "30px"},
    layout=widgets.Layout(width="700px", margin="3px 0"),
)
_mc_q6_info = _mc_info_block(
    title="Q6 (numerator)",
    what_it_checks="What event you count on the top of the fraction.",
    how_to_read=(
        "Pick the behavior that, if it increases, means the feature succeeded. "
        "Mutual matches measures pair formation; interactions measures attempted "
        "outreach; activated users measures funnel completion."
    ),
    sentence_template=(
        "&quot;Replace with [numerator] divided by [denominator from Q7], paired "
        "with [guardrail from Q8].&quot;"
    ),
)
_mc_q6_walk = widgets.HTML("")

_mc_q7_label = widgets.HTML(
    "<div style='margin-top:10px;'>"
    "<b>Q7 — Fix: denominator</b><br>"
    "<span style='font-size:12px; color:#57606a;'>What does the numerator "
    "get divided by? Pick the population at risk of doing the numerator "
    "behavior.</span></div>"
)
mc_g_denom_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Active users in the period (DAU or MAU)", "active_users"),
        ("Interactions initiated", "interactions"),
        ("Match connections in the period", "match_connections"),
        ("Wingman connections in the period", "wingman_connections"),
        ("Total connections (Match + Wingman) in the period", "total_connections"),
        ("Conversations started (at least one message exchanged)", "conversations_started"),
        ("Verified users in cohort", "verified_users"),
        ("Sessions", "sessions"),
        ("No denominator — keep as raw count", "no_denom"),
    ],
    value="",
    description="Q7:",
    style={"description_width": "30px"},
    layout=widgets.Layout(width="700px", margin="3px 0"),
)
_mc_q7_info = _mc_info_block(
    title="Q7 (denominator)",
    what_it_checks="What population the numerator is divided by.",
    how_to_read=(
        "Pick &quot;active users&quot; for engagement rates. Pick &quot;interactions&quot; if "
        "you want the success rate per attempt (matches / attempts). Pick "
        "&quot;sessions&quot; if you want per visit. Avoid &quot;verified users&quot; if you "
        "are NOT trying to measure post verification behavior — that's "
        "survivorship bias."
    ),
    sentence_template=(
        "&quot;The denominator [users / sessions / interactions] is the population "
        "at risk of doing the numerator behavior.&quot;"
    ),
)
_mc_q7_walk = widgets.HTML("")

_mc_q8_label = widgets.HTML(
    "<div style='margin-top:10px;'>"
    "<b>Q8 — Fix: guardrail / counter metric</b><br>"
    "<span style='font-size:12px; color:#57606a;'>The counter metric is the "
    "opposite hypothesis — what would move if the feature is hurting users "
    "in a way the primary metric can't see. If this moves the wrong way, "
    "you would stop the rollout.</span></div>"
)
mc_g_guardrail_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Type Score acceptance rate (match quality not just volume)", "type_score_quality"),
        ("Report rate / safety incidents per active user", "safety"),
        ("Time to first match (engagement depth, not just throughput)", "time_to_first_match"),
        ("Premium churn rate", "churn"),
        ("Message response rate after match (matches converting to conversation)", "response_rate"),
        ("Conversation depth — median messages per connection", "conversation_depth"),
        ("Match-to-message conversion rate (Match formed → first message sent within 48h)", "match_to_message"),
        ("Connection longevity — % of Match connections still active at 30 days", "connection_longevity"),
        ("None / not needed for this metric", "none"),
    ],
    value="",
    description="Q8:",
    style={"description_width": "30px"},
    layout=widgets.Layout(width="700px", margin="3px 0"),
)
_mc_q8_info = _mc_info_block(
    title="Q8 (guardrail / counter metric)",
    what_it_checks=(
        "A second metric that would catch harm the primary metric misses. "
        "Required for every A/B test in the academy framework."
    ),
    how_to_read=(
        "Pick a metric that measures quality (Type Score acceptance), safety "
        "(report rate), or downstream value (message response rate) — not "
        "another volume metric."
    ),
    sentence_template=(
        "&quot;Pair this with [guardrail metric] so the model is not optimizing "
        "for [the harmful behavior the guardrail catches].&quot;"
    ),
)
_mc_q8_walk = widgets.HTML("")


mc_compose_btn = widgets.Button(
    description="Compose draft from picks",
    button_style="info",
    layout=widgets.Layout(width="240px", height="32px", margin="10px 0"),
)


# --- Container groups for visibility toggling --------------------------
mc_guided_step1_box = widgets.VBox([
    widgets.HTML("<b>Step 1 — diagnose the flaw (pick each row):</b>"),
    _mc_framework_ref,
    _mc_q1_label, mc_g_q1_dd, _mc_q1_walk, _mc_q1_info,
    _mc_q2_label, mc_g_q2_dd, _mc_q2_walk, _mc_q2_info,
    _mc_q3_label, mc_g_q3_dd, _mc_q3_walk, _mc_q3_info,
    _mc_q4d_label, mc_g_q4d_dd, _mc_q4d_walk, _mc_q4d_info,
    _mc_q5d_label, mc_g_q5d_dd, _mc_q5d_walk, _mc_q5d_info,
])
mc_guided_step2_box = widgets.VBox([
    widgets.HTML("<b>Step 2 — frame the fix (pick each row):</b>"),
    _mc_fix_source_note,
    _mc_q6_label, mc_g_num_dd, _mc_q6_walk, _mc_q6_info,
    _mc_q7_label, mc_g_denom_dd, _mc_q7_walk, _mc_q7_info,
    _mc_q8_label, mc_g_guardrail_dd, _mc_q8_walk, _mc_q8_info,
])
mc_guided_compose_box = widgets.VBox([mc_compose_btn])

# --- Textarea labels (clarify example vs answer) -----------------------
mc_flaw_label = widgets.HTML(
    "<h4 style='margin:10px 0 4px;'>Step 1 — What is wrong with this metric?</h4>"
    "<div style='font-size:12px; color:#57606a; margin-bottom:6px;'>"
    "Name the specific flaw in one or two short sentences. "
    "<b>The dark text below is just an EXAMPLE</b> — your real answer should be "
    "based on this problem's metric. In Guided mode the dropdowns above "
    "shape the draft via the Compose button; in Try blind mode you write "
    "from scratch.</div>"
)
mc_flaw_ta = widgets.Textarea(
    placeholder="Example answer (do not copy verbatim — write your own): 'Total matches per week is a raw count not normalized by active users, so a larger cohort always appears better even when match quality is worse per user.'",
    layout=widgets.Layout(width="100%", min_height="80px"),
)
mc_flaw_ta.add_class("diagnose-textarea")
mc_flaw_hint = widgets.HTML("")

mc_fix_label = widgets.HTML(
    "<h4 style='margin:14px 0 4px;'>Step 2 — How would you fix it?</h4>"
    "<div style='font-size:12px; color:#57606a; margin-bottom:6px;'>"
    "Propose a specific replacement metric with formula plus a guardrail. "
    "<b>The dark text below is an EXAMPLE</b> — write your own.</div>"
)
mc_fix_ta = widgets.Textarea(
    placeholder="Example answer (do not copy verbatim): 'Mutual Match Rate = (mutual matches) / (interactions initiated), measured per active user. Guardrail: Type Score acceptance rate so the model is not optimizing for promiscuous matching.'",
    layout=widgets.Layout(width="100%", min_height="80px"),
)
mc_fix_ta.add_class("diagnose-textarea")
mc_fix_hint = widgets.HTML("")

mc_grade_btn = widgets.Button(
    description="Get Grade",
    button_style="success",
    layout=widgets.Layout(width="180px", height="34px", margin="12px 0 6px 0"),
)
mc_grade_out = widgets.Output()

# Case context widgets — defined before the form box so the box can hold
# references to them. Both widgets share the same HTML content (set by
# _mc_render_case_context). One is shown at the top of Step 1, the other
# above Step 2 so the learner does not have to scroll back up.
_mc_case_context = widgets.HTML("")
_mc_case_context_step2 = widgets.HTML("")
_mc_case_context_box = widgets.Accordion(
    children=[widgets.VBox([_mc_case_context])],
)
_mc_case_context_box.set_title(0, "📋 Case context — scenario, proposed metric, stakeholder rationale")
_mc_case_context_box.selected_index = 0  # open by default

_mc_case_context_step2_box = widgets.Accordion(
    children=[widgets.VBox([_mc_case_context_step2])],
)
_mc_case_context_step2_box.set_title(0, "📋 Case context — repeated here so you don't have to scroll")
_mc_case_context_step2_box.selected_index = None  # collapsed by default at Step 2

metric_critique_form_box = widgets.VBox([
    mc_mode_toggle,
    _mc_case_context_box,        # case context Accordion (open) above Step 1
    mc_guided_step1_box,
    mc_flaw_label, mc_flaw_ta, mc_flaw_hint,
    _mc_case_context_step2_box,  # case context Accordion (collapsed) above Step 2
    mc_guided_step2_box,
    mc_fix_label, mc_fix_ta, mc_fix_hint,
    mc_guided_compose_box,
    mc_grade_btn, mc_grade_out,
])


# --- Walkthrough mode heuristics: infer recommended dropdown picks -----
# Reads the problem's expected_themes / rubric and suggests a pick per
# dropdown by keyword matching. Non destructive: the suggestion appears
# in a small green note under the dropdown, the dropdown's actual value
# is left alone.
def _mc_walk_suggest(problem):
    """Return dict mapping dropdown name -> suggested option label."""
    p = problem or {}
    text = " ".join(p.get("expected_themes", []) or []).lower()
    rubric = p.get("rubric", []) or []
    text += " " + " ".join(
        (r.get("description", "") + " " + r.get("criterion", "")).lower()
        for r in rubric
    )
    suggestions = {}
    if any(k in text for k in ("ambigu", "opposite reason", "both directions")):
        suggestions["q1"] = "Yes — ambiguous"
    if any(k in text for k in ("normaliz", "raw count", "per user", "per active user", "rate")):
        suggestions["q2"] = "Raw count or total"
    if any(k in text for k in ("time window", "no window", "rolling", "weekly", "per week")):
        if "no window" in text or "without window" in text or "missing window" in text:
            suggestions["q3"] = "No window specified"
    if "survivorship" in text or "survivor" in text:
        suggestions["q4d"] = "Yes — survivorship"
    if "complex" in text or "understandab" in text or "hold in their head" in text:
        suggestions["q5d"] = "No — too complex"
    # Fix
    # Q6 numerator
    if "first message" in text:
        suggestions["q6"] = "First messages sent after a Match or Wingman connection"
    elif "reply" in text and "message" in text:
        suggestions["q6"] = "Reply messages"
    elif "message" in text:
        suggestions["q6"] = "Messages sent in the period"
    elif "mutual match" in text:
        suggestions["q6"] = "Mutual matches in the period"
    elif "activat" in text:
        suggestions["q6"] = "Activated users"
    elif "profile view" in text:
        suggestions["q6"] = "Profile views received"
    elif "premium" in text and "upgrade" in text:
        suggestions["q6"] = "Premium upgrades in the period"
    elif "interaction" in text:
        suggestions["q6"] = "Interactions initiated"
    # Q7 denominator
    if "per match" in text or "per connection" in text or "per relationship" in text:
        if "wingman" in text and "match" not in text.replace("wingman", "", 1):
            suggestions["q7"] = "Wingman connections in the period"
        elif "match" in text and "wingman" not in text:
            suggestions["q7"] = "Match connections in the period"
        else:
            suggestions["q7"] = "Total connections (Match + Wingman) in the period"
    elif "active user" in text or "per active" in text or "per user" in text:
        suggestions["q7"] = "Active users in the period (DAU or MAU)"
    elif "conversation" in text:
        suggestions["q7"] = "Conversations started"
    elif "interaction" in text:
        suggestions["q7"] = "Interactions initiated"
    # Q8 guardrail
    if "type score" in text:
        suggestions["q8"] = "Type Score acceptance rate"
    elif "safety" in text or "report" in text:
        suggestions["q8"] = "Report rate / safety incidents"
    elif "conversation depth" in text or "messages per connection" in text:
        suggestions["q8"] = "Conversation depth"
    elif "longevity" in text or "still active" in text:
        suggestions["q8"] = "Connection longevity"
    elif "response" in text or "message" in text:
        suggestions["q8"] = "Message response rate"
    return suggestions


def _mc_walk_note(label):
    """Render a small green walkthrough suggestion note."""
    if not label:
        return ""
    return (
        f"<div style='font-size:12px; color:#1a7f37; margin:-4px 0 6px 36px;'>"
        f"💡 Walkthrough suggests: <b>{label}</b></div>"
    )


# --- Dropdown -> sentence helpers --------------------------------------
def _mc_label_for(dd):
    for label, value in dd.options:
        if value == dd.value:
            return label if value else ""
    return ""


def _mc_compose_flaw_sentence():
    """Build a sentence enumerating each Pressure Test that failed."""
    fails = []
    if mc_g_q1_dd.value == "ambiguous":
        fails.append("ambiguity — the metric can move up for opposite reasons (improvement OR cohort growth that masks per user decline)")
    if mc_g_q2_dd.value == "raw_count":
        fails.append("normalization — it is a raw count not a rate, so it scales with the user base instead of measuring per user behavior")
    if mc_g_q3_dd.value == "no_window":
        fails.append("time window — no explicit window, so the metric is not operable from a fixed point in time")
    if mc_g_q4d_dd.value == "survivorship":
        fails.append("survivorship — the denominator only counts users who already passed an earlier step, so the rate looks better than the true end to end funnel")
    if mc_g_q5d_dd.value == "not_understandable":
        fails.append("understandability — the metric is too complex for a PM or exec to hold in their head, so it can't drive day to day decisions")
    if mc_g_q5d_dd.value == "doesnt_address_purpose":
        fails.append("understandability — the metric is simple to read but does not connect to the scenario's stated purpose; looking at the number doesn't tell anyone whether the underlying goal was achieved")
    if not fails:
        return ""
    if len(fails) == 1:
        return f"This metric fails the Pressure Test on {fails[0]}."
    return "This metric fails the Pressure Test on multiple checks: " + "; ".join(fails) + "."


def _mc_compose_fix_sentence():
    num = _mc_label_for(mc_g_num_dd)
    denom = _mc_label_for(mc_g_denom_dd)
    guard = _mc_label_for(mc_g_guardrail_dd)
    if not (num and denom):
        return ""
    if mc_g_denom_dd.value == "no_denom":
        formula = f"Keep the numerator as is — {num} — but report it per user segment so a larger cohort cannot mask a worse per user rate."
    else:
        formula = f"Replace with ({num}) divided by ({denom})."
    parts = [formula]
    if guard and mc_g_guardrail_dd.value not in ("", "none"):
        parts.append(f"Pair it with this guardrail metric: {guard}.")
    return " ".join(parts)


def _on_mc_compose(_b):
    flaw = _mc_compose_flaw_sentence()
    fix = _mc_compose_fix_sentence()
    if flaw:
        mc_flaw_ta.value = flaw
    if fix:
        mc_fix_ta.value = fix


mc_compose_btn.on_click(_on_mc_compose)


def _set_visible(box, visible):
    box.layout.display = "" if visible else "none"


def _mc_apply_mode():
    mode = mc_mode_toggle.value
    # Guided controls
    _set_visible(mc_guided_step1_box, mode == "guided")
    _set_visible(mc_guided_step2_box, mode == "guided")
    _set_visible(mc_guided_compose_box, mode == "guided")
    # Walkthrough hints on the textareas
    p = STATE.get("problem") or {}
    themes = p.get("expected_themes", []) or []
    if mode == "walkthrough":
        if themes:
            half = max(1, len(themes) // 2)
            flaw_themes = themes[:half]
            fix_themes = themes[half:]
        else:
            flaw_themes = ["raw count vs rate", "missing normalization", "missing counter metric"]
            fix_themes = ["named replacement metric with formula", "one line on why it's better", "a guardrail metric"]
        mc_flaw_hint.value = (
            "<div style='background:#fff8c5; border-left:4px solid #d4a72c; "
            "padding:10px; border-radius:4px; margin:4px 0 10px;'>"
            "<b>Walkthrough — points to hit in Step 1:</b>"
            "<ul style='margin:6px 0 0 18px;'>"
            + "".join(f"<li>{t}</li>" for t in flaw_themes)
            + "</ul></div>"
        )
        mc_fix_hint.value = (
            "<div style='background:#fff8c5; border-left:4px solid #d4a72c; "
            "padding:10px; border-radius:4px; margin:4px 0 10px;'>"
            "<b>Walkthrough — points to hit in Step 2:</b>"
            "<ul style='margin:6px 0 0 18px;'>"
            + "".join(f"<li>{t}</li>" for t in fix_themes)
            + "</ul></div>"
        )
    else:
        mc_flaw_hint.value = ""
        mc_fix_hint.value = ""
    # Walkthrough mode also surfaces a recommended dropdown pick under each
    # dropdown (both Step 1 and Step 2). Non destructive: just a green note.
    if mode == "walkthrough":
        s = _mc_walk_suggest(p)
        _mc_q1_walk.value = _mc_walk_note(s.get("q1", ""))
        _mc_q2_walk.value = _mc_walk_note(s.get("q2", ""))
        _mc_q3_walk.value = _mc_walk_note(s.get("q3", ""))
        _mc_q4d_walk.value = _mc_walk_note(s.get("q4d", ""))
        _mc_q5d_walk.value = _mc_walk_note(s.get("q5d", ""))
        _mc_q6_walk.value = _mc_walk_note(s.get("q6", ""))
        _mc_q7_walk.value = _mc_walk_note(s.get("q7", ""))
        _mc_q8_walk.value = _mc_walk_note(s.get("q8", ""))
        # In Walkthrough mode also show the guided dropdowns so the user can
        # see WHICH options the walkthrough recommends.
        _set_visible(mc_guided_step1_box, True)
        _set_visible(mc_guided_step2_box, True)
    else:
        for w in (_mc_q1_walk, _mc_q2_walk, _mc_q3_walk, _mc_q4d_walk,
                  _mc_q5d_walk, _mc_q6_walk, _mc_q7_walk, _mc_q8_walk):
            w.value = ""


# Static fallback options used when the problem JSON does not carry
# metric_critique_picks. These match the curated catalog from before.
_MC_STATIC_NUM_OPTS = [
    ("— pick —", ""),
    ("Mutual matches in the period", "mutual_matches"),
    ("Interactions initiated (likes, winks, superlikes)", "interactions"),
    ("Messages sent in the period", "messages_sent"),
    ("First messages sent after a Match or Wingman connection", "first_messages"),
    ("Reply messages (responses to an existing thread)", "reply_messages"),
    ("Profile views received", "profile_views"),
    ("Paid (Premium) upgrades in the period", "premium_upgrades"),
    ("Activated users (verified + profile complete + first interaction)", "activated"),
    ("Sessions", "sessions"),
]
_MC_STATIC_DENOM_OPTS = [
    ("— pick —", ""),
    ("Active users in the period (DAU or MAU)", "active_users"),
    ("Interactions initiated", "interactions"),
    ("Match connections in the period", "match_connections"),
    ("Wingman connections in the period", "wingman_connections"),
    ("Total connections (Match + Wingman) in the period", "total_connections"),
    ("Conversations started (at least one message exchanged)", "conversations_started"),
    ("Verified users in cohort", "verified_users"),
    ("Sessions", "sessions"),
    ("No denominator — keep as raw count", "no_denom"),
]
_MC_STATIC_GUARD_OPTS = [
    ("— pick —", ""),
    ("Type Score acceptance rate (match quality not just volume)", "type_score_quality"),
    ("Report rate / safety incidents per active user", "safety"),
    ("Time to first match (engagement depth, not just throughput)", "time_to_first_match"),
    ("Premium churn rate", "churn"),
    ("Message response rate after match (matches converting to conversation)", "response_rate"),
    ("Conversation depth — median messages per connection", "conversation_depth"),
    ("Match-to-message conversion rate (Match formed → first message sent within 48h)", "match_to_message"),
    ("Connection longevity — % of Match connections still active at 30 days", "connection_longevity"),
    ("None / not needed for this metric", "none"),
]


def _mc_dynamic_opts(static_opts, picks_list):
    """Merge dynamic picks from the problem JSON in front of the static
    catalog. Picks come as a list of {"label": ..., "value": ...} dicts."""
    if not picks_list:
        return static_opts
    dyn = [("— pick —", "")]
    seen_values = set()
    for it in picks_list:
        if not isinstance(it, dict):
            continue
        lbl = it.get("label", "").strip()
        val = it.get("value", "").strip()
        if not lbl or not val or val in seen_values:
            continue
        # Tag dynamic picks so the learner sees they were tailored to this problem.
        dyn.append((f"⭐ {lbl}", val))
        seen_values.add(val)
    # Append the static catalog below the dynamic picks as a fallback.
    for lbl, val in static_opts[1:]:
        if val not in seen_values:
            dyn.append((lbl, val))
    return dyn


def _mc_render_case_context(p):
    if not p:
        _mc_case_context.value = ""
        return
    scenario = p.get("scenario", "") or ""
    rationale = p.get("stakeholder_rationale", "") or ""
    title = p.get("title", "") or ""
    prompt_text = p.get("prompt", "") or ""
    # Prefer the explicit proposed_metric field (added in this rebuild).
    # Older problems may not have it; fall back to extracting a single
    # or double quoted metric name out of the prompt text. Last resort:
    # use the title (which is the problem TITLE, not the metric, but
    # better than blank).
    proposed_metric = (p.get("proposed_metric", "") or "").strip()
    if not proposed_metric and prompt_text:
        import re as _re
        m = _re.search(r"[\u2018\u2019\'\"]([^\u2018\u2019\'\"]{4,80})[\u2018\u2019\'\"]", prompt_text)
        if m:
            proposed_metric = m.group(1).strip()
    if not proposed_metric:
        proposed_metric = title
    parts = [
        "<div style='background:#fafbfc; border:1px solid #d0d7de; "
        "border-radius:6px; padding:12px 14px; margin:8px 0;'>",
        "<div style='font-size:11px; color:#57606a; "
        "text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;'>"
        "Case context (kept here so you don't have to scroll)</div>",
    ]
    if scenario:
        parts.append(
            f"<div style='margin:4px 0;'><b>Scenario (purpose):</b> "
            f"{scenario}</div>"
        )
    if proposed_metric:
        parts.append(
            f"<div style='margin:4px 0;'><b>Proposed metric (under review):"
            f"</b> {proposed_metric}</div>"
        )
    if rationale:
        parts.append(
            f"<div style='margin:4px 0;'><b>Stakeholder rationale "
            f"(why they think this metric works):</b> {rationale}</div>"
        )
    parts.append("</div>")
    html = "".join(parts)
    _mc_case_context.value = html
    try:
        _mc_case_context_step2.value = html
    except NameError:
        pass


def _refresh_metric_critique_form():
    p = STATE.get("problem")
    # Rebuild Q6/Q7/Q8 options from dynamic picks if present
    picks = (p or {}).get("metric_critique_picks", {}) or {}
    mc_g_num_dd.options = _mc_dynamic_opts(_MC_STATIC_NUM_OPTS, picks.get("numerator"))
    mc_g_denom_dd.options = _mc_dynamic_opts(_MC_STATIC_DENOM_OPTS, picks.get("denominator"))
    mc_g_guardrail_dd.options = _mc_dynamic_opts(_MC_STATIC_GUARD_OPTS, picks.get("guardrail"))
    # Reset state
    for dd in (mc_g_q1_dd, mc_g_q2_dd, mc_g_q3_dd, mc_g_q4d_dd, mc_g_q5d_dd,
               mc_g_num_dd, mc_g_denom_dd, mc_g_guardrail_dd):
        dd.value = ""
    mc_flaw_ta.value = ""
    mc_fix_ta.value = ""
    with mc_grade_out:
        clear_output()
    # Render case context at the top of the panel
    _mc_render_case_context(p)
    _mc_apply_mode()
    # Build the metric movers checklist for the active problem. Guarded
    # so callers don't crash if the helper hasn't been defined yet (it
    # lives in the appendix below in this cell).
    try:
        _mc_build_movers_ui(STATE.get("problem"))
    except NameError:
        pass
    except Exception as _movers_err:
        print(f"[_mc_build_movers_ui warning] {type(_movers_err).__name__}: {_movers_err}")


mc_mode_toggle.observe(lambda _change: _mc_apply_mode(), names="value")


def _mc_learning_mode_html(result):
    """Build a small banner showing a Learning mode score that drops the
    Conciseness criterion (if present) and rescales the remaining weights
    so the learner is not penalized for over thorough answers when they
    are practicing rather than interviewing."""
    if not result:
        return ""
    scores = result.get("scores", []) or []
    drops = [s for s in scores if "conciseness" in str(s.get("criterion", "")).lower()]
    kept = [s for s in scores if "conciseness" not in str(s.get("criterion", "")).lower()]
    if not drops or not kept:
        return ""  # nothing to drop, no banner
    kept_weight = sum(s.get("weight", 0) for s in kept) or 1
    kept_earned = sum(s.get("earned", 0) for s in kept)
    # Rescale earned weight to 100 so the score is comparable across drills.
    learning_score = round(100 * kept_earned / kept_weight)
    color = "#1a7f37" if learning_score >= 80 else ("#9a6700" if learning_score >= 60 else "#cf222e")
    dropped_names = ", ".join(s.get("criterion", "") for s in drops)
    return (
        f"<div style='margin:8px 0; padding:10px 14px; background:#ddf4ff; "
        f"border-left:4px solid #0969da; border-radius:4px;'>"
        f"<b>Learning mode score:</b> "
        f"<span style='color:{color}; font-weight:700;'>{learning_score}/100</span> "
        f"<span style='font-size:12px; color:#57606a;'>"
        f"(dropped: {dropped_names} — only matters when you're cosplaying the actual interview)"
        f"</span></div>"
    )


def _on_mc_grade(_b):
    with mc_grade_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p:
            print("Generate a problem first.")
            return
        if not mc_flaw_ta.value.strip() and not mc_fix_ta.value.strip():
            print("Fill in at least one field before grading (or click Compose draft from picks).")
            return
        combined = (
            "What is wrong with this metric:\n"
            + mc_flaw_ta.value.strip()
            + "\n\nHow I would fix it:\n"
            + mc_fix_ta.value.strip()
        )
        print("Grading ...")
        result = dru.grade_kpi_answer(p, combined)
        clear_output(wait=True)
        if not result:
            print("Grading failed.")
            return
        # Show the interview-style grade first, then a Learning mode banner.
        display(HTML(dru.grade_to_html(result)))
        learning_html = _mc_learning_mode_html(result)
        if learning_html:
            display(HTML(learning_html))


mc_grade_btn.on_click(_on_mc_grade)


# Phase 3: if a problem already lives in STATE (the user generated before
# this cell ran), populate the slim view now so they don't have to click
# Generate again.
try:
    refresh_subtopic_form()
except Exception as _e:
    print(f"[initial refresh_subtopic_form] {type(_e).__name__}: {_e}")



# ============================================================
# metric_design Guided form — GSM + Pressure Test walk (5 steps)
# ============================================================
# metric_design problems ask the learner to invent metrics for a feature.
# The academy framework prescribes walking all 5 steps:
#   1. Goal
#   2. Signal
#   3. Metric (numerator + denominator + statistic + window)
#   4. Layer three types (primary + guardrail + counter)
#   5. Pressure Test (5 checks against the proposed metric)

md_mode_toggle = widgets.ToggleButtons(
    options=[
        ("🎯 Guided (walk the framework)", "guided"),
        ("🧠 Try blind", "solve"),
        ("📖 Walkthrough", "walkthrough"),
    ],
    value="guided",
    description="Mode:",
    style={"description_width": "60px", "button_width": "260px"},
    layout=widgets.Layout(margin="6px 0 10px 0"),
)

_md_framework_ref = widgets.HTML(
    "<div style='background:#ddf4ff; border-left:4px solid #0969da; "
    "padding:10px 14px; border-radius:4px; margin:10px 0;'>"
    "<b>Framework: Product Analytics Academy — Goal, Signal, Metric "
    "(GSM) + Pressure Test</b><br>"
    "<span style='font-size:12px;'>For &quot;propose metrics for this feature&quot; "
    "questions, walk all 5 steps:</span>"
    "<ol style='font-size:12px; margin:6px 0 6px 18px;'>"
    "<li><b>Goal</b> — one sentence from the user's perspective.</li>"
    "<li><b>Signal</b> — observable behavior for success AND failure.</li>"
    "<li><b>Metric</b> — numerator + denominator + statistic + time window.</li>"
    "<li><b>Layer three types</b> — primary + guardrail + counter.</li>"
    "<li><b>Pressure Test</b> — Ambiguity, Normalization, Time window, "
    "Survivorship, Understandability.</li>"
    "</ol></div>"
)

_md_case_context = widgets.HTML("")


def _md_render_case_context(p):
    if not p:
        _md_case_context.value = ""
        return
    scenario = p.get("scenario", "") or ""
    prompt_text = p.get("prompt", "") or ""
    rationale = p.get("stakeholder_rationale", "") or ""
    title = p.get("title", "") or ""
    parts = [
        "<div style='background:#fafbfc; border:1px solid #d0d7de; "
        "border-radius:6px; padding:12px 14px; margin:8px 0;'>",
        "<div style='font-size:11px; color:#57606a; "
        "text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;'>"
        "Case context (kept here so you don't have to scroll)</div>",
    ]
    if title:
        parts.append(f"<div style='margin:4px 0;'><b>Feature:</b> {title}</div>")
    if scenario:
        parts.append(
            f"<div style='margin:4px 0;'><b>Scenario:</b> {scenario}</div>"
        )
    if rationale:
        parts.append(
            f"<div style='margin:4px 0;'><b>What the team wants to learn:</b> "
            f"{rationale}</div>"
        )
    parts.append("</div>")
    _md_case_context.value = "".join(parts)


# Step 1 — Goal
md_goal_label = widgets.HTML(
    "<h4 style='margin:10px 0 4px;'>Step 1 — Goal (one sentence)</h4>"
    "<div style='font-size:12px; color:#57606a;'>State what the feature is "
    "trying to accomplish from the <b>user's</b> perspective in one sentence. "
    "Avoid commercial language (revenue, conversion). Behavioral verbs only "
    "(&quot;find,&quot; &quot;decide,&quot; &quot;reach,&quot; &quot;avoid&quot;).</div>"
)
md_goal_ta = widgets.Textarea(
    placeholder="Example: 'Help users identify and start conversations with people they would likely form a Match with, without scrolling through dozens of low fit profiles.'",
    layout=widgets.Layout(width="100%", min_height="60px"),
)
md_goal_ta.add_class("diagnose-textarea")

# Step 2 — Signal
md_signal_label = widgets.HTML(
    "<h4 style='margin:14px 0 4px;'>Step 2 — Signal (success and failure)</h4>"
    "<div style='font-size:12px; color:#57606a;'>What would a user who "
    "succeeded actually <i>do</i>? What would a user who failed do? "
    "Observable behavior only — not feelings.</div>"
)
md_signal_success_ta = widgets.Textarea(
    placeholder="Success signal example: 'User initiates a Match within 5 minutes of opening the map view, the Match is accepted, and a first message is sent within 24 hours.'",
    description="Success:",
    style={"description_width": "70px"},
    layout=widgets.Layout(width="100%", min_height="60px"),
)
md_signal_success_ta.add_class("diagnose-textarea")
md_signal_failure_ta = widgets.Textarea(
    placeholder="Failure signal example: 'User opens the app, scrolls the map for 60+ seconds, closes without initiating any interaction.'",
    description="Failure:",
    style={"description_width": "70px"},
    layout=widgets.Layout(width="100%", min_height="60px"),
)
md_signal_failure_ta.add_class("diagnose-textarea")

# Step 3 — Metric build
md_metric_label = widgets.HTML(
    "<h4 style='margin:14px 0 4px;'>Step 3 — Metric (numerator + denominator + statistic + window)</h4>"
    "<div style='font-size:12px; color:#57606a;'>Turn the success signal into "
    "a countable metric. Every metric needs four pieces.</div>"
)
md_num_ta = widgets.Text(
    placeholder="Numerator (event counted on top): e.g., Matches initiated within 5 min of map open",
    description="Numerator:",
    style={"description_width": "100px"},
    layout=widgets.Layout(width="100%", margin="3px 0"),
)
md_denom_ta = widgets.Text(
    placeholder="Denominator (population): e.g., Active users in the period",
    description="Denominator:",
    style={"description_width": "100px"},
    layout=widgets.Layout(width="100%", margin="3px 0"),
)
md_stat_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Rate (numerator / denominator)", "rate"),
        ("Median (use when outliers skew the mean)", "median"),
        ("Mean", "mean"),
        ("Percentile (P75, P90, P95)", "percentile"),
        ("Count", "count"),
    ],
    value="",
    description="Statistic:",
    style={"description_width": "100px"},
    layout=widgets.Layout(width="100%", margin="3px 0"),
)
md_window_dd = widgets.Dropdown(
    options=[
        ("— pick —", ""),
        ("Daily", "daily"),
        ("Weekly", "weekly"),
        ("Rolling 28 days", "rolling_28d"),
        ("Per session", "per_session"),
        ("During the experiment window", "experiment_window"),
    ],
    value="",
    description="Window:",
    style={"description_width": "100px"},
    layout=widgets.Layout(width="100%", margin="3px 0"),
)

# Step 4 — Layer three types
md_layer_label = widgets.HTML(
    "<h4 style='margin:14px 0 4px;'>Step 4 — Layer three metric types</h4>"
    "<div style='font-size:12px; color:#57606a;'>Every rollout needs a "
    "<b>Primary</b> (moves if the feature works), a <b>Guardrail</b> (must "
    "not break), and a <b>Counter metric</b> (the opposite hypothesis — "
    "what would move if the feature is hurting users in a way the primary "
    "metric can't see).</div>"
)
md_primary_ta = widgets.Text(
    placeholder="Primary metric (your Step 3 result): e.g., Match initiation rate within 5 min of map open",
    description="Primary:",
    style={"description_width": "100px"},
    layout=widgets.Layout(width="100%", margin="3px 0"),
)
md_guardrail_ta = widgets.Text(
    placeholder="Guardrail (must not break): e.g., Report rate / safety incidents per active user",
    description="Guardrail:",
    style={"description_width": "100px"},
    layout=widgets.Layout(width="100%", margin="3px 0"),
)
md_counter_ta = widgets.Text(
    placeholder="Counter metric (opposite hypothesis): e.g., Match-to-message conversion rate (catches superficial matches)",
    description="Counter:",
    style={"description_width": "100px"},
    layout=widgets.Layout(width="100%", margin="3px 0"),
)

# Step 5 — Pressure Test (free form note: one sentence per check)
md_pressure_label = widgets.HTML(
    "<h4 style='margin:14px 0 4px;'>Step 5 — Pressure Test your primary metric</h4>"
    "<div style='font-size:12px; color:#57606a;'>For each of the 5 checks, "
    "state in one sentence why your primary metric passes (or what you "
    "would change to make it pass).</div>"
)
md_pressure_ta = widgets.Textarea(
    placeholder=(
        "Example:\n"
        "Ambiguity — passes; only one mechanism (more Match initiations) moves the rate.\n"
        "Normalization — passes; rate is per active user, not raw count.\n"
        "Time window — passes; measured rolling 28 days.\n"
        "Survivorship — passes; denominator is all active users, not just users who already matched.\n"
        "Understandability — passes; PM can hold &quot;Match initiation rate per active user, rolling 28d.&quot;"
    ),
    layout=widgets.Layout(width="100%", min_height="120px"),
)
md_pressure_ta.add_class("diagnose-textarea")

# Compose + grade
md_compose_btn = widgets.Button(
    description="Compose final metric design draft",
    button_style="info",
    layout=widgets.Layout(width="280px", height="32px", margin="10px 0"),
)
md_draft_label = widgets.HTML(
    "<h4 style='margin:14px 0 4px;'>Final design draft</h4>"
    "<div style='font-size:12px; color:#57606a;'>Compose stitches your "
    "Step 1 to Step 5 entries into a clean response. Edit before grading."
    "</div>"
)
md_draft_ta = widgets.Textarea(
    placeholder="Click Compose above to build the draft from your picks, then edit.",
    layout=widgets.Layout(width="100%", min_height="160px"),
)
md_draft_ta.add_class("diagnose-textarea")

md_grade_btn = widgets.Button(
    description="Get Grade",
    button_style="success",
    layout=widgets.Layout(width="180px", height="34px", margin="12px 0 6px 0"),
)
md_grade_out = widgets.Output()

md_guided_box = widgets.VBox([
    md_mode_toggle,
    _md_case_context,
    _md_framework_ref,
    md_goal_label, md_goal_ta,
    md_signal_label, md_signal_success_ta, md_signal_failure_ta,
    md_metric_label, md_num_ta, md_denom_ta, md_stat_dd, md_window_dd,
    md_layer_label, md_primary_ta, md_guardrail_ta, md_counter_ta,
    md_pressure_label, md_pressure_ta,
    md_compose_btn,
    md_draft_label, md_draft_ta,
    md_grade_btn, md_grade_out,
])


def _md_label_for(dd):
    for label, value in dd.options:
        if value == dd.value:
            return label if value else ""
    return ""


def _on_md_compose(_b):
    goal = md_goal_ta.value.strip()
    success = md_signal_success_ta.value.strip()
    failure = md_signal_failure_ta.value.strip()
    num = md_num_ta.value.strip()
    denom = md_denom_ta.value.strip()
    stat = _md_label_for(md_stat_dd)
    window = _md_label_for(md_window_dd)
    primary = md_primary_ta.value.strip()
    guardrail = md_guardrail_ta.value.strip()
    counter = md_counter_ta.value.strip()
    pressure = md_pressure_ta.value.strip()

    parts = []
    if goal:
        parts.append(f"**Goal**\n{goal}")
    sigs = []
    if success: sigs.append(f"- Success: {success}")
    if failure: sigs.append(f"- Failure: {failure}")
    if sigs:
        parts.append("**Signal**\n" + "\n".join(sigs))
    metric_pieces = []
    if num: metric_pieces.append(f"- Numerator: {num}")
    if denom: metric_pieces.append(f"- Denominator: {denom}")
    if stat: metric_pieces.append(f"- Statistic: {stat}")
    if window: metric_pieces.append(f"- Time window: {window}")
    if metric_pieces:
        parts.append("**Metric**\n" + "\n".join(metric_pieces))
    layered = []
    if primary: layered.append(f"- Primary: {primary}")
    if guardrail: layered.append(f"- Guardrail: {guardrail}")
    if counter: layered.append(f"- Counter: {counter}")
    if layered:
        parts.append("**Layer three types**\n" + "\n".join(layered))
    if pressure:
        parts.append(f"**Pressure Test**\n{pressure}")
    md_draft_ta.value = "\n\n".join(parts)


md_compose_btn.on_click(_on_md_compose)


def _refresh_metric_design_form():
    md_goal_ta.value = ""
    md_signal_success_ta.value = ""
    md_signal_failure_ta.value = ""
    md_num_ta.value = ""
    md_denom_ta.value = ""
    md_stat_dd.value = ""
    md_window_dd.value = ""
    md_primary_ta.value = ""
    md_guardrail_ta.value = ""
    md_counter_ta.value = ""
    md_pressure_ta.value = ""
    md_draft_ta.value = ""
    with md_grade_out:
        clear_output()
    _md_render_case_context(STATE.get("problem"))
    _md_apply_mode()


def _md_apply_mode():
    """For now Guided is the only mode that does anything special; Try blind
    just hides the framework banner and reveals an empty draft area; Walkthrough
    fills the draft with the reference answer (if present) so the learner can
    paraphrase."""
    mode = md_mode_toggle.value
    # Framework + step widgets are visible in Guided and Walkthrough; hidden
    # in Try blind (where the learner just gets the empty draft textarea).
    for w in (_md_framework_ref, md_goal_label, md_goal_ta,
              md_signal_label, md_signal_success_ta, md_signal_failure_ta,
              md_metric_label, md_num_ta, md_denom_ta, md_stat_dd, md_window_dd,
              md_layer_label, md_primary_ta, md_guardrail_ta, md_counter_ta,
              md_pressure_label, md_pressure_ta, md_compose_btn):
        w.layout.display = "" if mode in ("guided", "walkthrough") else "none"
    if mode == "walkthrough":
        p = STATE.get("problem") or {}
        ref = p.get("reference_answer", "") or ""
        if ref:
            md_draft_ta.value = ref


md_mode_toggle.observe(lambda _c: _md_apply_mode(), names="value")


def _on_md_grade(_b):
    with md_grade_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p:
            print("Generate a problem first.")
            return
        body = md_draft_ta.value.strip()
        if not body:
            print("Fill in the steps and click Compose first, then Get Grade.")
            return
        print("Grading ...")
        result = dru.grade_kpi_answer(p, body)
        clear_output(wait=True)
        if not result:
            print("Grading failed.")
            return
        display(HTML(dru.grade_to_html(result)))


md_grade_btn.on_click(_on_md_grade)

metric_design_form_box = md_guided_box



# ============================================================
# Q1 learning aid: "Why might this metric move?" checklist
# ============================================================
_MC_STATIC_MOVERS = [
    {
        "reason": "More users joined the cohort during the period",
        "tag": "Population",
        "applies": True,
        "explanation": "A raw count rises proportionally with cohort size, even when per user behavior is identical.",
    },
    {
        "reason": "A marketing push attracted users who tend to be heavy users",
        "tag": "Mix",
        "applies": True,
        "explanation": "Composition shift toward heavier users raises the average per user count without changing any individual's behavior.",
    },
    {
        "reason": "Tracking code was updated and now double counts events",
        "tag": "Measurement",
        "applies": True,
        "explanation": "Measurement artifacts can fake any direction of metric movement; always rule this out first.",
    },
    {
        "reason": "A holiday weekend reduced overall app activity",
        "tag": "External",
        "applies": True,
        "explanation": "Seasonality moves volume metrics independent of any product change.",
    },
    {
        "reason": "The team improved the matching algorithm quality",
        "tag": "Quality",
        "applies": True,
        "explanation": "Per user behavior shifts when matches are better — same cohort, more engagement per pair.",
    },
    {
        "reason": "The app icon was changed in the App Store",
        "tag": "—",
        "applies": False,
        "explanation": "Icon changes may affect downloads, but rarely move behavior of users already in the app.",
    },
    {
        "reason": "Premium subscription price increased by $1",
        "tag": "—",
        "applies": False,
        "explanation": "Price changes affect conversion to Premium, not the messaging behavior of users who are already there.",
    },
]


def _mc_tag_chip(tag):
    colors = {
        "Population":  "#0969da",
        "Quality":     "#1a7f37",
        "Mix":         "#8250df",
        "Measurement": "#cf222e",
        "External":    "#9a6700",
    }
    color = colors.get(tag, "#57606a")
    return (
        f"<span style='display:inline-block; padding:2px 8px; "
        f"background:#f6f8fa; color:{color}; border:1px solid {color}; "
        f"border-radius:10px; font-size:11px; font-weight:600; "
        f"margin-right:8px;'>{tag}</span>"
    )


mc_movers_box = widgets.VBox([])
mc_movers_check_btn = widgets.Button(
    description="Check my picks",
    button_style="info",
    layout=widgets.Layout(width="180px", height="32px", margin="8px 0"),
)
mc_movers_out = widgets.Output()

_mc_movers_header = widgets.HTML(
    "<details open style='margin-top:10px;'>"
    "<summary style='cursor:pointer; color:#0969da; font-weight:600; "
    "font-size:13px;'>🧩 Why might this metric move? — practice identifying "
    "the levers</summary>"
    "<div style='font-size:12px; color:#57606a; padding:6px 0;'>"
    "Check the reasons that actually could move <b>THIS metric</b>. "
    "Distractors are mixed in — pick carefully. Tags show the pattern "
    "category so you can build a mental map of metric movement causes."
    "</div></details>"
)

_mc_movers_inner_vbox = widgets.VBox([
    _mc_movers_header,
    mc_movers_box,
    mc_movers_check_btn,
    mc_movers_out,
])
mc_movers_section = widgets.Accordion(children=[_mc_movers_inner_vbox])
mc_movers_section.set_title(0, "🧩 Why might this metric move? — practice identifying the levers (click to expand)")
mc_movers_section.selected_index = None  # collapsed by default to save vertical space

_mc_movers_rows = []


def _mc_build_movers_ui(problem):
    global _mc_movers_rows
    movers = (problem or {}).get("metric_movers")
    if not movers:
        movers = _MC_STATIC_MOVERS
    _mc_movers_rows = []
    rows_widgets = []
    for m in movers:
        if not isinstance(m, dict):
            continue
        reason = m.get("reason", "")
        tag = m.get("tag", "—")
        applies = bool(m.get("applies", False))
        explanation = m.get("explanation", "")
        cb = widgets.Checkbox(
            value=False,
            indent=False,
            layout=widgets.Layout(width="28px"),
        )
        label = widgets.HTML(
            f"<div style='padding-top:2px;'>{_mc_tag_chip(tag)}{reason}</div>"
        )
        row = widgets.HBox(
            [cb, label],
            layout=widgets.Layout(align_items="flex-start", margin="3px 0"),
        )
        rows_widgets.append(row)
        _mc_movers_rows.append({
            "checkbox": cb,
            "applies": applies,
            "tag": tag,
            "reason": reason,
            "explanation": explanation,
        })
    mc_movers_box.children = rows_widgets
    with mc_movers_out:
        clear_output()


def _on_mc_movers_check(_b):
    correct = 0
    rendered = []
    for r in _mc_movers_rows:
        picked = r["checkbox"].value
        is_right = picked == r["applies"]
        if is_right:
            correct += 1
        if r["applies"] and picked:
            verdict = "<span style='color:#1a7f37; font-weight:600;'>&#10003; correct apply</span>"
        elif r["applies"] and not picked:
            verdict = "<span style='color:#cf222e; font-weight:600;'>&#10007; missed</span> — this DOES apply"
        elif (not r["applies"]) and picked:
            verdict = "<span style='color:#cf222e; font-weight:600;'>&#10007; false positive</span> — this does NOT apply"
        else:
            verdict = "<span style='color:#1a7f37; font-weight:600;'>&#10003; correctly ignored</span>"
        rendered.append(
            f"<div style='margin:6px 0; padding:8px 12px; background:#fafbfc; "
            f"border:1px solid #d0d7de; border-radius:4px;'>"
            f"<div>{_mc_tag_chip(r['tag'])}{r['reason']}</div>"
            f"<div style='font-size:12px; margin-top:4px;'>{verdict}</div>"
            f"<div style='font-size:12px; color:#57606a; margin-top:4px;'>"
            f"<b>Why:</b> {r['explanation']}</div>"
            f"</div>"
        )
    total = len(_mc_movers_rows)
    pct = round(100 * correct / total) if total else 0
    color = "#1a7f37" if pct >= 75 else ("#d4a72c" if pct >= 50 else "#cf222e")
    with mc_movers_out:
        clear_output(wait=True)
        display(HTML(
            f"<div style='padding:10px 14px; background:#fff; border:1px solid "
            f"#d0d7de; border-radius:6px;'>"
            f"<h4 style='margin:0 0 8px; color:{color};'>Score: {correct} / "
            f"{total} ({pct}%)</h4>"
            + "".join(rendered)
            + "</div>"
        ))


mc_movers_check_btn.on_click(_on_mc_movers_check)


_step1_children = list(mc_guided_step1_box.children)
try:
    _q1_info_idx = _step1_children.index(_mc_q1_info)
    _step1_children.insert(_q1_info_idx + 1, mc_movers_section)
    mc_guided_step1_box.children = tuple(_step1_children)
except ValueError:
    mc_guided_step1_box.children = tuple(_step1_children) + (mc_movers_section,)


# Phase: the movers call now lives INSIDE the original
# _refresh_metric_critique_form (above) so there's no wrapper
# indirection. Older versions used a wrapper here; removed for
# robustness.

# One shot populate: trigger the movers UI build now that everything
# is wired. If a problem was loaded before cell 5 ran (or the user
# generates after this cell finishes) the rows will refresh either
# way thanks to the call baked into _refresh_metric_critique_form.
try:
    _mc_build_movers_ui(STATE.get("problem"))
except Exception as _initial_movers_err:
    print(f"[initial _mc_build_movers_ui warning] "
          f"{type(_initial_movers_err).__name__}: {_initial_movers_err}")


# One shot populate so the movers list shows up even when the initial
# refresh_subtopic_form auto call (at end of cell 5) ran BEFORE this
# wrapper was bound. Safe to call multiple times.
try:
    _mc_build_movers_ui(STATE.get("problem"))
except Exception as _e:
    print(f"[initial _mc_build_movers_ui warning] {type(_e).__name__}: {_e}")



# ============================================================
# Metric explorer UI — comparison cards for bad / picked / alternatives
# ============================================================

mc_explain_btn = widgets.Button(
    description="🔍 Explain how the metrics would actually look",
    button_style="info",
    layout=widgets.Layout(width="380px", height="34px", margin="6px 0"),
    tooltip="Generate worked examples on synthetic data for the bad metric, your pick, and every starred alternative.",
)
mc_explain_out = widgets.Output()


def _mc_explorer_card(card, color_border, color_label, label):
    """Render one comparison card (bad / picked / alternative) as HTML."""
    if not isinstance(card, dict):
        return ""
    name = card.get("name", "")
    measures = card.get("what_it_measures", "")
    calc = card.get("calculation", "")
    value = card.get("value", "")
    interp = card.get("interpretation", "")
    why_fail = card.get("why_it_fails_the_purpose", "")
    why_address = card.get("why_it_addresses_the_purpose", "")
    tradeoff = card.get("trade_off_vs_picked", "")

    # Render example data as a small HTML table.
    data = card.get("example_data", []) or []
    data_html = ""
    if data and isinstance(data, list):
        cols = []
        for row in data:
            if isinstance(row, dict):
                for k in row.keys():
                    if k not in cols:
                        cols.append(k)
        if cols:
            head = "".join(f"<th style='padding:4px 8px; text-align:left; background:#eaeef2;'>{c}</th>" for c in cols)
            body_rows = []
            for row in data:
                cells = "".join(f"<td style='padding:4px 8px; border-top:1px solid #d0d7de;'>{row.get(c, '')}</td>" for c in cols)
                body_rows.append(f"<tr>{cells}</tr>")
            data_html = (
                "<table style='border-collapse:collapse; margin:6px 0; font-size:12px;'>"
                f"<thead><tr>{head}</tr></thead>"
                f"<tbody>{''.join(body_rows)}</tbody>"
                "</table>"
            )

    purpose_line = ""
    if why_fail:
        purpose_line = f"<div style='font-size:12px; color:#cf222e; margin-top:6px;'><b>Why it fails the purpose:</b> {why_fail}</div>"
    elif why_address:
        purpose_line = f"<div style='font-size:12px; color:#1a7f37; margin-top:6px;'><b>Why it addresses the purpose:</b> {why_address}</div>"
    elif tradeoff:
        purpose_line = f"<div style='font-size:12px; color:#57606a; margin-top:6px;'><b>Trade off vs your pick:</b> {tradeoff}</div>"

    return (
        f"<div style='border:2px solid {color_border}; border-radius:6px; "
        f"padding:12px 14px; margin:10px 0; background:#fff;'>"
        f"<div style='display:inline-block; padding:2px 8px; background:{color_border}; "
        f"color:#fff; border-radius:4px; font-size:11px; font-weight:600; "
        f"text-transform:uppercase; letter-spacing:0.5px;'>{label}</div>"
        f"<div style='font-weight:700; font-size:14px; margin-top:6px;'>{name}</div>"
        f"<div style='font-size:12px; color:#57606a; margin:4px 0;'>{measures}</div>"
        f"{data_html}"
        f"<div style='font-size:12px; margin-top:6px;'><b>Calculation:</b> {calc}</div>"
        f"<div style='font-size:12px; margin-top:4px;'><b>Result:</b> {value}</div>"
        f"<div style='font-size:12px; margin-top:4px;'><b>Interpretation:</b> {interp}</div>"
        f"{purpose_line}"
        f"</div>"
    )


def _mc_collect_dynamic_picks(p):
    """Pull the dynamic numerator/denominator/guardrail picks from the problem's
    metric_critique_picks field. Returns three lists of LABEL strings."""
    picks = (p or {}).get("metric_critique_picks", {}) or {}
    def labels(key):
        out = []
        for it in picks.get(key, []) or []:
            if isinstance(it, dict):
                lbl = it.get("label", "").strip()
                if lbl:
                    out.append(lbl)
        return out
    return labels("numerator"), labels("denominator"), labels("guardrail")


def _mc_current_user_picks():
    """Read the learner's currently selected Q6/Q7/Q8 LABELS (not values)."""
    return {
        "numerator":   _mc_label_for(mc_g_num_dd).lstrip("⭐ ").strip(),
        "denominator": _mc_label_for(mc_g_denom_dd).lstrip("⭐ ").strip(),
        "guardrail":   _mc_label_for(mc_g_guardrail_dd).lstrip("⭐ ").strip(),
    }


def _mc_alternative_picks(p, user_picks):
    """All starred alternatives the user did NOT pick — by dropdown."""
    nums, denoms, guards = _mc_collect_dynamic_picks(p)
    return {
        "numerator":   [n for n in nums   if n != user_picks.get("numerator")],
        "denominator": [d for d in denoms if d != user_picks.get("denominator")],
        "guardrail":   [g for g in guards if g != user_picks.get("guardrail")],
    }


def _mc_render_explainer(report):
    """Top level renderer for the explorer JSON."""
    if not report:
        return "<div style='color:#cf222e;'>Could not generate explanation. Try clicking the button again.</div>"
    parts = []
    parts.append(
        "<div style='margin:8px 0 14px 0; padding:10px 14px; background:#fafbfc; "
        "border:1px solid #d0d7de; border-radius:6px;'>"
        "<b>📊 Metric explorer:</b> same synthetic population, different aggregations. "
        "Compare what each candidate metric tells the team about the scenario's "
        "stated purpose.</div>"
    )
    parts.append(_mc_explorer_card(report.get("bad_metric"), "#cf222e", "#cf222e", "❌ Bad metric (the one being critiqued)"))
    parts.append(_mc_explorer_card(report.get("user_picked_metric"), "#1a7f37", "#1a7f37", "✅ Your pick"))
    for alt in report.get("alternatives", []) or []:
        parts.append(_mc_explorer_card(alt, "#9a6700", "#9a6700", "⚙️ Alternative (starred but not picked)"))
    return "".join(parts)


def _on_mc_explain(_b=None, _silent=False):
    with mc_explain_out:
        clear_output(wait=True)
        p = STATE.get("problem")
        if not p:
            print("Generate a problem first.")
            return
        user_picks = _mc_current_user_picks()
        if not (user_picks["numerator"] and user_picks["denominator"]):
            print("Pick at least a numerator (Q6) and denominator (Q7) before clicking Explain.")
            return
        alt = _mc_alternative_picks(p, user_picks)
        if not _silent:
            print("Generating worked examples for each candidate metric ...")
        report = dru.explain_metrics(p, user_picks, alt)
        clear_output(wait=True)
        if not report:
            print("Could not generate the explanation. The API may be overloaded; try again.")
            return
        display(HTML(_mc_render_explainer(report)))


mc_explain_btn.on_click(_on_mc_explain)


# Splice the explain widgets into metric_critique_form_box AFTER the grade
# button + grade output.
_metric_critique_children = list(metric_critique_form_box.children)
try:
    _grade_idx = _metric_critique_children.index(mc_grade_out)
    _metric_critique_children.insert(_grade_idx + 1, mc_explain_btn)
    _metric_critique_children.insert(_grade_idx + 2, mc_explain_out)
    metric_critique_form_box.children = tuple(_metric_critique_children)
except ValueError:
    metric_critique_form_box.children = tuple(_metric_critique_children) + (mc_explain_btn, mc_explain_out)


# Wrap _on_mc_grade so the explorer auto fires after grading.
_mc_original_grade_handler = _on_mc_grade

def _on_mc_grade_with_explorer(_b):
    _mc_original_grade_handler(_b)
    # Auto fire the explorer if the user has filled in Q6 + Q7.
    try:
        if mc_g_num_dd.value and mc_g_denom_dd.value:
            _on_mc_explain(None, _silent=False)
    except Exception as _e:
        print(f"[explorer auto fire warning] {type(_e).__name__}: {_e}")


# Re-bind the click handler from the wrapper.
mc_grade_btn._click_handlers.callbacks = []
mc_grade_btn.on_click(_on_mc_grade_with_explorer)
