# Data Analyst Interview Prep — context.md

Living changelog and decision log for the multi-notebook interview-drill framework (formerly `sql_practice_generator`). Track what changed, what worked, and what to avoid next time. The historical changelog below the "What this project is" heading is older SQL-era history and is kept for reference.

---

## CURRENT STATE — read this first (updated 2026-06-16)

**What this project is now.** A reusable **data-analyst interview-drill framework**: one shared engine pattern (catalog → generate → diagnose → grade) behind several focused notebooks. Renamed from `sql_practice_generator` → `data_analyst_interview_prep` on 2026-06-16.

**Notebooks (in `notebooks/`), renumbered 2026-06-25 to free nb02 for Python practice:**
- `nb01_sql_practice.ipynb` — SQL drills (Postgres/MySQL sandbox). Engine: `sql_practice_utils.py` + `sandbox.py`.
- `nb02_python_practice.ipynb`: **NEW (2026-06-25)** Python practice covering pandas, numpy, and Python basics (array and string operations). Built separately. Slots between the SQL notebook and the analyst drills.

**NEXT BUILD (do in a fresh cowork):** create `folders/sql/python_problem_patterns.html` mirroring the layout of `folders/sql/sql_problem_patterns.html`, for the pandas/numpy/python patterns in nb02. The repo root `bitterscientist.com` is now connectable (request_cowork_directory), which is required to reach `folders/sql/`. The nb02 engine generates problems on its own; Trinidad may optionally supply 5 to 10 real sample problems to calibrate format and difficulty.

- `nb03_data_cleaning_modeling_drills.ipynb`: was nb02. Data cleaning and modeling drills (clean messy raw data, build the target model with CREATE TABLE AS SELECT). Engine: `nb03_modeling_drill_utils.py`.
- `nb04_analyst_interview_drills.ipynb`: was nb03. Analyst drills in 4 categories: Data Transformation Modeling, Critical Reasoning SQL, Product Metrics & KPIs, Version Control. Engine: `nb04_drill_utils.py`.
- `nb05_statistical_methods_drills.ipynb`: was nb04. Statistical methods: A/B testing, power and sample size, hypothesis tests, regression, claims metrics (PDC/PMPM). Engine: `stats_drill_utils.py`.
- `nb06_sql_error_review.ipynb`: was nb05. Reviews every failed Submit logged from nb01, ranked by error type. Engine: `sql_practice_utils.py`.

**nb03 design (the current template for new notebooks):** 3-step UX matching nb01/nb02 — **(1) Pick a problem** (dropdowns: Topic, Scenario [same industry list as nb01/nb02], Difficulty Easy/Moderate/Hard, Source New/Solved-replay; renders a scenario-grounded problem card), **(2) Diagnose before coding** (Walkthrough mode = guided dropdowns that lead to the right test and assemble the strategy; Solve mode = free-text diagnosis graded), **(3) Implement** (scenario shown above a runnable Python editor; Test / Submit [auto-run numeric check + Claude rubric] / Reveal reference). Collapsible code cells throughout (reuses nb02's ▼/▲ toggle). Generated problems saved to `data/outputs/stats_problems/` and replayable. Auto-run numeric check works offline; **Claude rubric + diagnosis feedback turn on when `ANTHROPIC_API_KEY` is in the project `.env`** (model via `DRILL_MODEL`, default `claude-sonnet-4-6`).

**Subfolder:** `interview_practice_tool/` — a Claude-powered mock case-study coaching tool (5-phase product-analytics lifecycle, voice-to-text via Web Speech API, rubric scoring, hints/example answers). Moved in 2026-06-16, **parked / under evaluation** — Trinidad hasn't run it yet but likes the voice-to-text + rubric-scoring pieces, which could be borrowed into the drill framework. Logic in `interview_practice_tool/notebooks/interview_practice_utils.py` and `ui_components.py`.

**Trinidad's situation (2026-06-16).** Active healthcare data-analyst job search (separate `job_posting_resume_optimizer` project). This week's interviews: **MDCalc** Senior Data Analyst (phone screen pending) and **Judi Health / Capital Rx** recruiter call Thu 6/18 9am PT. Drilling A/B testing + statistical methods (nb03) and SQL (nb01) for these. She is **moving this project into a folder dedicated to her coding projects** — keep paths relative to the project root where possible.

**Roadmap / open work.** Flesh out the new `nb02_python_practice.ipynb` (pandas, numpy, basic Python array and string operations) on the shared engine pattern. Continue splitting the analyst notebook's four categories into their own thin per-domain notebooks (target lineup: SQL, Python, statistical methods, product metrics, dbt and data modeling, version control). The statistical methods notebook (now nb05) is the pattern to copy.

**SQL track — 2026-06-16 cowork (canonical detail in `folders/sql/HANDOFF.md`).** Two artifacts changed this day:
- `notebooks/sql_practice_utils.py` (nb01 engine): 31 → 32 qtypes. NEW `window_benchmark_compare` (whole-group `AVG/MIN/MAX OVER (PARTITION BY)` with no ORDER BY, compare each row in an outer query). `left_join_on_filter` now rotates 6 shapes including a left-filter-in-WHERE + right-filter-in-ON combo. `window_running_total` rotates SUM/AVG/COUNT. After the edit, reload nb01 from disk before running.
- `folders/sql/sql_problem_patterns.html` (the SQL recipe playbook — NOTE this is a different file from `pharmacy_problem_patterns.html`): the whole Single-Table tab was regrouped into technique/method leaves (Filter, Aggregate, Scalar, Dedup) each with a decision tree, a mirrored reference table, and a Template card; Window/Pair/Rank templates were distributed into their leaves; the Sessionization section was rebuilt so you pick a template by reading the expected output columns ("One row per session" vs "One row per person"), with all "engine"/"Strategy N" jargon removed and self-documenting CTE names.

**Reinforced tone (from the 2026-06-16 SQL session).** Pick drills by the expected output, then match a template. No jargon, no invented metaphors ("engine" and "Strategy N" numbering were both banned mid-session), no walls of text. Self-documenting CTE names.

### Planned features — practice timers (requested 2026-07-06)

Three timer features for the practice notebooks, in plain terms:

1. A solve-time tracker that quietly times each problem from when it opens until a passing submit, so the learner can see how fast they solve.
2. A per-problem countdown the learner can set, where the code editor freezes when time is up and they can then ask for feedback on whatever they had written.
3. A whole-session timer over a set of problems (for example, five in a chosen number of minutes) that locks the editor when time runs out and gives a wrap-up of how many were correct, what worked and what did not, and links to the matching sections of `sql_problem_patterns.html` to study, even for problems left unfinished.

**How to be useful in chat.**
- DEFAULT TO ONE SENTENCE. Answer questions in a single simple, non-technical, lay-language sentence. Do NOT give multi-paragraph explanations, full tree walkthroughs, or restate the problem. If she wants more, she will ask a follow-up. Long answers make her furious. This overrides any urge to be thorough in chat.
- NEVER STRIP THE GROUP STRUCTURE WHEN EXPLAINING SQL. A GROUP BY (and ROW_NUMBER) always involves a SET of columns whose shared values DEFINE the group, PLUS one or more OTHER columns you aggregate (min, max, sum, avg, count) or rank. Do NOT describe it as if there is a single column or "a summary rolled up from the group" - that is conceptually wrong and makes her furious. Always name both parts: the grouping columns and the separate aggregated/ranked columns. Stay close to her exact wording.
- CORE COMMUNICATION PRINCIPLE (the thing that keeps her from getting angry): SHOW, do not just describe. Whenever a concept is at all complex, lead with the actual SQL using real column and table names so she can SEE the idea in code, rather than decoding an abstract sentence. Concrete code with real names is always easier for her to understand than an abstract description; reach for the runnable example first, then explain it. An explanation she has to decode is a failure even if it is technically correct.
- WHEN EXPLAINING A CHOICE BETWEEN TWO METHODS, ALWAYS SHOW A CONCRETE EXAMPLE with real column and table names; never leave an abstract phrase standing on its own. Banned-without-an-example phrases include: "conditional aggregate", "restrict every aggregate", "row level / group level", "the result needs more than one X". She does not know what these mean in the abstract. Instead show it: e.g. "two output columns in the same query, one is COUNT of rows where fee < 7 and the other is COUNT of rows where fee >= 7, each needing its own CASE WHEN" versus "one output column, COUNT of rows where fee < 7, a single condition". Make the abstract idea visible as actual SQL/columns every single time.
- Be concise. Don't show code unless explicitly asked — she reads diffs herself.
- Don't append a summary of what was just done. Lead with the result and a `computer://` link.
- No hyphens unless they're compound nouns ("five-step" OK, gratuitous hyphenation NOT OK).
- After editing any notebook, validate it executes headlessly (nbclient) or that all code cells parse with `ast.parse` before handing back.
- For big/structural changes, work in an isolated copy first; only adopt into the live files once she approves.

---

## What this project is

Two Jupyter notebooks plus a companion blog post, all centered on pharmacy / digital-health analytics interview prep:

- **`notebooks/nb01_sql_practice.ipynb`** — original SQL practice notebook (general purpose).
- **`notebooks/nb02_fuze_interview_drills.ipynb`** — interview-focused drill notebook with **5 categories**: Pharmacy Claims SQL, Data Transformation Modeling, Critical Reasoning SQL, Product Metrics & KPIs, Version Control (Git). (Filename keeps the original code path; all company references inside have been scrubbed.)
- **`folders/sql/pharmacy_problem_patterns.html`** — companion blog with worked recipe cards. Each card has signal words, glossary, real-world context, recipe template, worked example, common gotchas.

Both notebooks share `nb02_drill_utils.py` (problem generator, validators, graders) and use a Postgres Docker sandbox to validate `answer_key` SQL.

The build script for nb02 is committed at `build/build_nb02.py` (inside the project folder, survives Cowork session boundaries). Edit it, run it, and it writes the notebook into `notebooks/`.

### Categories and subtopics (current)

| Tab | Category | Subtopics |
|---|---|---|
| 1 | Pharmacy Claims Analytical SQL | adjudication_funnel, cohort_retention, window_event_log, reject_pareto, segment_performance, time_to_fill, net_acceptance_rate, reversal_rate, adherence_pdc |
| 2 | Data Transformation Modeling | **schema_design** (KPI form), dimensional_modeling (SQL), scd_type_2 (SQL), dbt_tests_macros (markdown) |
| 3 | Critical Reasoning SQL | ambiguous_metric, missing_data, edge_cases, clarify_then_query, outlier_handling, broken_query_critique |
| 4 | Product Metrics & KPIs | metric_critique, metric_design, metric_diagnosis, counter_metric_design, experiment_critique, event_vs_user_property, event_properties_design, user_properties_design, tracking_plan_design, prd_impact_measurement |
| 5 | Version Control (Git for analytics) | branching_strategy, merge_conflict_resolution, rebase_vs_merge, pr_review_critique, commit_message_critique, revert_strategy, git_state_diagnose |

**Tab 2 dropped on 2026-05-05:** cte_chain (covered by nb01 SQL practice), staging_vs_marts (conceptually covered by schema_design field 7), materialization_choice (conceptually covered by schema_design field 7). Tab 2 is now modeling-focused with 4 essential subtopics.

---

## Major systems / what each piece does

| Piece | Role |
|---|---|
| `notebooks/nb02_drill_utils.py` | CATEGORIES catalog, prompt templates, LLM problem generation, validators, graders (`grade_diagnostic`, `grade_modeling_diagnostic`, `grade_kpi_answer`, `grade_interpretation_recommendation`, `grade_schema_design_form`), render helpers, save/load attempts |
| `notebooks/sandbox.py` | Postgres + MySQL Docker sandbox helpers — runs `answer_key` SQL to confirm it executes. The Postgres splitter is paren/quote/comment aware (handles `--` comments, `/* */` blocks, `'...'` string literals) |
| `notebooks/sql_practice_utils.py` | Older nb01 helpers (Claude init, problem persistence). `_extract_json` is shared by both notebooks |
| `build/build_nb02.py` | Cell-by-cell builder that emits the nb02 .ipynb JSON (committed to project) |
| `data/outputs/generated_problems/` | Saved generated problems, loadable via the picker's "Saved (replay)" radio |
| `data/outputs/solved/` | Saved solution attempts (SQL submissions, KPI markdown answers, AND schema_design form responses with grades) |
| `folders/sql/pharmacy_problem_patterns.html` | Tabbed reference blog with worked recipe cards |

### Schema design form (the centerpiece of Tab 2)

`schema_design` is a structured 11-field KPI-graded drill, NOT a SQL execution drill. Section 2 of nb02 has a 4-panel accordion: Structural Diagnostic / Modeling Diagnostic / Business Analysis / **Schema Design Response Form**. The 4th panel auto-expands when a schema_design problem is loaded.

The form's 11 fields, each in its own collapsible accordion sub-panel:
1. Grain (textarea)
2. Fact columns (textarea + collapsible markdown table template)
3. Surrogate vs natural key (dropdown + rationale textarea)
4. Dim joins (multi-select checkboxes built dynamically from `problem.candidate_dimensions`)
5. SCD type per dim (dropdowns rendered dynamically from checked dims in field 4 — Type 0/1/2 with definitions inline)
6. Conformed dims (multi-select from checked dims in field 4)
7. Models (multi-row builder: model_name + layer dropdown + materialization dropdown, with Add/Remove buttons)
8. dbt tests per model (rebuilds dynamically per model in field 7)
9. Idempotency / re-run safety (dropdown + rationale)
10. Late-arriving / out-of-order events (dropdown + rationale)
11. Edge cases acknowledged (textarea)

Plus pre-form helpers stacked above the accordion:
- **Concept primer** — collapsible "🧭 How to construct a fact table" walkthrough + "Concepts reference" with 13 entries (grain, fact-vs-dim, raw-measure-vs-derived-metric, star schema, SCD types, surrogate vs natural key, conformed dim, idempotency, late-arriving, materialization, dbt layers, join types, dbt tests). Each entry has a definition + a concrete EXAMPLE block (blue-bordered) showing how it applies in real pharmacy schemas.
- **Mode toggle** — Solve mode (try blind, get graded against rubric) vs Walkthrough mode (worked answer + lay-language rationale REPLACES the hint area, user paraphrases to lock in the concept). Switches any time.
- **Translate-the-asks pre-form exercise** — for each `stakeholder_asks` entry, a dropdown asking the user to map it to: measure / FK / drill-down attribute / supporting timestamp / combination. Primes the brain before the main form.

Per-accordion-field add-ons:
- **Hint widget** at the top of each panel. In Solve mode: shows generic guidance OR `field_hints[fid]` from the problem (yellow border for problem-specific). In Walkthrough mode: REPLACED with `worked_example_per_field[fid]` formatted as Answer + Why (green border).
- **Pitfall callout** (red border) on Field 2 (don't pivot dim into columns), Field 3 (fact-key vs dim-SCD distinction), Field 5 (SCD applies to dims, not facts).
- **Field 2 fact column template** — collapsible green-bordered block with both an HTML table (visual reference) AND a copyable markdown source block.
- **Worked-example reveal** in Solve mode — collapsible "💡 Show example answer" per field (collapsed by default; peek when stuck). Hidden in Walkthrough mode (redundant).

Persistence: every Get Schema Design Feedback / Check Understanding click auto-saves the full form state to `data/outputs/solved/<problem_id>_schema_design_attempt.json`. On problem reload (via the saved-problems dropdown), `refresh_subtopic_form()` repopulates every field from the saved file — text values, dropdowns, dim checkboxes, SCD picks, model rows, tests per model, translate picks, mode. The grade output area shows "Restored your prior attempt (saved <ts>). Last score: N/100."

### nb02 cell layout (current)

Cell sequence in the .ipynb:
- 0: intro markdown (5 categories listed)
- 1: setup code (imports, GEN_DIR/SOLVED_DIR setup) — code-toggle button at top
- 2: `## 1. Pick a problem` markdown
- 3: picker code (category/subtopic/dialect/source dropdowns + Generate button) — code-toggle
- 4: `## 2. Diagnose before coding` markdown
- 5: diagnostic form code — DEFINES generic 3-panel diagnostic + 11-field schema_design form + accordion wiring + refresh_subtopic_form. Code-toggle button at top, input collapses on render
- 6: `## 3. Write your SQL` markdown — labeled SQL only; non-SQL answers go in section 2
- 7: editor code (SQL editor + KPI markdown editor; KPI markdown editor is hidden for schema_design via `apply_subtopic_editor_override`)
- 8: `## 4. Next problem` markdown
- 9: Next Question handler — clears state + reset widgets + calls refresh_subtopic_form
- 10: trailing markdown

Every code cell starts with a JS-injected blue toggle button (`▲ Hide code` / `▼ Show code`) that auto-collapses the cell input on render and lets the user toggle it manually.

---

## What's worked (keep doing)

- **Walkthrough mode for learning new concepts.** When Trinidad hits a topic she doesn't yet have the framework for (e.g., schema design fact-vs-dim split), Walkthrough mode shows the worked answer + lay-language Why directly in the hint area. She paraphrases it back; grader checks understanding (not correctness from scratch). Major learning lift over blind solving when the framework isn't internalized yet. Switch to Solve mode for self-testing once she's drilled a few.
- **Pre-form translate-the-asks exercise on schema_design.** Forces the user to map each stakeholder ask to its design element (measure / FK / drill-down / timestamp) BEFORE filling the main form. Catches the "didn't read the asks carefully" failure mode that drove early low scores.
- **Concept reference with concrete examples.** Each concept entry has a definition AND an example block (blue border) showing the concept applied to a real pharmacy fact/dim. Examples beat abstract definitions for retention.
- **Auto-save + auto-load schema_design form responses.** Every grade click saves the full form state to disk keyed by problem_id. Reloading the same problem repopulates every field. Lets Trinidad iterate without losing work, switch between problems, study yesterday's responses.
- **Pinning unstable subtopics to one explicit shape with a hand-traced math example.** Subtopics that previously failed validation (cohort_retention, segment_performance, time_to_fill) became reliable once the prompt forced one specific row layout and gave the LLM the expected math for it.
- **Validator self-consistency check.** Comparing the LLM's stated `example_output_rows` against what the `answer_key` actually returns catches the most common "LLM made up the answer" failure mode.
- **Validator hard rules for schema_design.** Reject any KPI problem that looks like schema_design unless it includes `candidate_dimensions`, `stakeholder_asks`, `field_hints` (with all 11 keys non-empty), `worked_example_per_field` (with all 11 keys non-empty), and `schema_ddl`. Prevents incomplete generations from breaking walkthrough mode.
- **Stakeholder-driven prompt format for schema_design.** Four labeled sections: STAKEHOLDER CONTEXT (3-5 asks, each with a formula in plain language), VOLUME AND UPDATE FREQUENCY (drives materialization decision), WHAT YOU HAVE IN SOURCE (dim list with attributes, no "yes" affirmations), YOUR TASK (explicit fact-table-only focus). Forces the LLM to give the user real interview-grade context.
- **Industry-vocabulary mandate in prompts.** Hard rules against inventing metric names, NCPDP codes, drug classes, and benchmarks dramatically cut hallucinated content.
- **Per-subtopic `kind` override.** Lets `dbt_tests_macros` and `schema_design` live inside the modeling category but get markdown / form grading.
- **Promoting Trinidad's actual solutions into recipe cards.** Every gotcha entry in the blog comes from a real mistake she made while drilling — these resonate when she re-reads them.
- **Splitting visual reference from input widget for the dbt tests table** (current approach using a single GridBox: 1 checkbox + 4 HTML cells per row, all flat-listed). One scrollbar, columns aligned across rows.
- **Auto-resize textareas** (the `.diagnose-textarea`, `.sql-code-editor`, `.kpi-md-editor` JS poller). Saves a lot of friction when answers grow long.
- **Shift+Enter blocker on textareas.** Trinidad lost work multiple times before this; now a global keydown handler `preventDefault`s on textarea/input targets.
- **Code-toggle button on every cell.** A blue HTML+JS button auto-hides the cell's input area on render. The user can click to show source if they want to inspect. Keeps the long form-builder cells visually clean.

---

## What to avoid (gotchas we've already paid for)

### Build script syntax — string quoting
- `build_nb02.py` wraps each cell source in `code('''...''')` (triple-single-quotes). **Inside that, escape sequences in strings are interpreted by Python when reading the file.** `\"` collapses to `"` before it reaches the notebook, breaking f-strings whose own delimiters are `"..."`.
- **Rule:** when you need a double quote inside an f-string inside a `code('''...''')` cell, use single quotes for HTML attributes (`style='...'`). Don't try to escape with `\"`.
- For the same reason, **don't use `f'''...'''` inside `code('''...''')`** — the inner triple-single-quotes terminate the outer string. Use string concatenation across multiple `'...'` lines instead.

### ipywidgets layout — the dbt tests table saga
- **VBox of HBox per row produces one scrollbar PER ROW** and breaks column alignment because each row's flex/grid layout computes widths independently. Avoid for tabular data.
- **HBox containing many HTML cells (5+) per row** rendered as gray loading bars in past attempts.
- **Working pattern:** flat list of children in one `widgets.GridBox` with `grid_template_columns="..."`. The grid wraps automatically based on column count. ONE scrollbar (set on the GridBox), ALL rows share column widths.
- Set `box-sizing:border-box` and `overflow-wrap:anywhere; word-break:break-word;` on cell content `<div>`s to prevent overflow.

### Prompt engineering — what the LLM keeps trying to do wrong
- **Inventing metric names, drug classes, NCPDP codes, benchmarks.** Always specify the exact vocabulary list in the prompt and reject responses that introduce new terms.
- **Returning column-less INSERTs.** Generator must include `INSERT INTO t (col1, col2, ...) VALUES ...` explicitly. We added `_parse_column_less_inserts()` as a fallback parser when the LLM forgets, but the prompt should still demand columns.
- **Inconsistent row tuple lengths in INSERT statements.** Validator now checks all tuples in a multi-row INSERT have the same number of values.
- **Calculation explanation rendered as one paragraph** when the LLM emits all numbered steps inline. Renderer detects inline `\d+\. ` patterns and splits.
- **`_canonical_value` false positive** on `'0.5000'` (string) vs `Decimal('0.5000')`. Fixed by numericizing string-typed numbers in the comparator.
- **UNDEFINED ACRONYMS / INVENTED SHORTHAND — banned (2026-07-06).** A `returns_table` problem used "non-OP reply" ("OP" = original poster, forum slang) without ever defining it; Trinidad could not decode it. RULE (added to the generation prompt Hard rules in `sql_practice_utils.py`): no acronym, abbreviation, or invented domain shorthand in ANY learner-facing field (`prompt`, `context`, `task`, `field_logic`, `edge_cases`, `answer_shape`, `output_field_notes`, `hints`) — including OP/non-OP, DAU, MAU, CTR, AOV, MRR, ARPU, KPI, FK, PK. Write the full plain phrase every time ("a reply from someone other than the thread's creator"). Prefer NO acronyms at all; if a standard technical term is unavoidable, spell it out and define it in plain words on first use. Only SQL keywords/type names inside code (schema_ddl, function_signature, test_call) are exempt.
- **WALLS OF TEXT in `display.answer_shape` ("What to write") — banned (2026-07-06).** The LLM kept writing the whole procedural shape as one dense paragraph ("Write a DO block that declares a RECORD variable ... Use FOR rec IN ... LOOP ... Inside the loop, SELECT ... then use IF / ELSIF ... After END LOOP, end with ..."). Trinidad cannot scan that. FIX (nb01 `sql_practice_utils.py`): the `answer_shape` schema instruction now REQUIRES a scannable bullet outline (optional one-line intro, then top-level `- ` steps grouped by phase — declare / loop / inside / after — with two-space-indented `- ` sub-items, one action per bullet, exact table/column names); a global "NO WALLS OF TEXT" hard rule was added; and `render_problem_card` renders `answer_shape` through the new `_answer_shape_html` helper (nested `<ul>`; degrades gracefully for old prose). Same principle applies to every `display` field — `field_logic` (one rule per line), `edge_cases` (one 'If ... then ...' per item) — never a paragraph.

### Build script string escaping (THE recurring bite)
- **`\n` inside `code('''...''')` gets converted to a real newline by Python when reading the build script's triple-single-quoted string.** This breaks string literals in the emitted cell source. ALWAYS escape as `\\n` when you want a literal `\n` in a cell's Python source. Same for `\t`, `\\`, etc. This burned us multiple times on Field 2 template, worked-example renderer, and inline JS strings.
- **Python comments in the build script are ALSO inside the triple-quoted string.** A comment containing `\n` will also break the cell. Avoid `\n` references in comments — say "newline character" or "backslash-n" instead.
- **`\\` in regex strings doubles up the same way.** ASCII diagrams using backslashes in concept primer entries need `\\\\` in build script source to land as `\\` in the cell, which displays as `\` in HTML.

### Schema_design generation gotchas
- **`max_tokens` must be 6000 for schema_design** (other KPI subtopics stay at 3000). The full JSON has multi-section prompt + candidate_dimensions + stakeholder_asks + field_hints (11 entries) + worked_example_per_field (11 entries) — easily exceeds 3000 tokens, gets truncated mid-JSON.
- **Validator must enforce all 11 keys for `field_hints` AND `worked_example_per_field`.** Without this, the LLM skips fields and walkthrough mode falls back to the "older format" warning. The validator's heuristic: if a problem has any of `candidate_dimensions`, `schema_ddl`, `stakeholder_asks`, `field_hints`, or `worked_example_per_field`, enforce ALL required schema_design fields.
- **`worked_example_per_field` entries must follow "Answer: X. Why: Y" structure.** Walkthrough mode displays this as the hint. The KPI guidance demands it explicitly with examples; the LLM follows when shown.

### Postgres script splitter (sandbox.py)
- **`_split_pg_statements` must be paren/quote/comment aware.** Original version naively split on `;`, which broke when answer_keys had `;` inside SQL `--` comments (e.g., `-- Source: claim_events; dim_patient`) — the splitter yielded a comment-only chunk and psycopg2 errored "can't execute an empty query." Fixed: skip over `--` line comments, `/* */` block comments, and `'...'` string literals (with `''` escape) when scanning for `;`. Drop chunks that contain nothing but whitespace and comments.

### Schema rendering (`schema_to_html`)
- **DDL with inline `--` comments leaks comment text as a garbage row** (named `--`) when parsed. Fix: nb02_drill_utils overrides `schema_to_html` with a wrapper that calls `_strip_sql_comments(ddl)` first to remove `--` and `/* */` before delegating to `spu.schema_to_html`.

### Prompt rendering (`prompt_to_bullets_nested`)
- **The renderer must handle structured prompts** (uppercase section headers, newline-prefixed bullets, paragraph blocks) for schema_design's STAKEHOLDER CONTEXT / VOLUME / WHAT YOU HAVE IN SOURCE / YOUR TASK format. Otherwise bullets get crammed into one inline-dash sentence.
- **Detection rules:**
  - All-caps line of 2-6 words at start of paragraph → `<h5>` section header
  - Lines starting with `-`, `*`, or `•` → `<ul><li>` block
  - Lettered enumeration `(a) X (b) Y` after a colon → nested `<ul>` with letter strong tags
  - Plain-text fallback for paragraphs without explicit structure

### Schema_design form widget gotchas
- **`continuous_update=False` on model name TextInput.** Otherwise every keystroke fires `_sd2_sync_models()` + `_sd2_rebuild_tests_box()`, polluting `test_selections` dict with every intermediate name (`m`, `ma`, `mar`, ...). At grade time, 30+ stale partial-name keys get serialized.
- **Filter stale keys at grade time** as defense in depth: only include `tests_per_model` entries for model names currently in `_sd2_state["models"]`.
- **Mode toggle re-renders hint widgets, not text-area values.** Switching solve↔walkthrough preserves the user's typed text in every textarea. Only `.value` of the HTML hint widget changes.
- **Defensive re-cache in `_sd2_apply_mode`.** Always call `_sd2_cache_problem_content()` at the top of apply_mode so toggling mode after problem load works even if `refresh_subtopic_form()` somehow didn't fire.

### Tone / editorial
- **Task-done = ONE sentence + a one-line next step (2026-06-18).** When a task completes, summarize in a single sentence and note any next steps in one short line. No blocks of text, no multi-paragraph recaps.
- **No hyphens unless compound nouns.** Per the global editorial rule.
- **Be concise. Don't show code unless asked.** Especially in chat replies — Trinidad reads diffs herself.
- **Don't summarize what was just done at the end of every reply.** Lead with the result.
- **Don't auto-build when she asks to discuss / propose / review.** Stop, propose framework, ask for sign-off, then build. She's been frustrated multiple times by over-eager building.

---

## Recent change history (most recent first)

| Date | Area | Change |
|---|---|---|
| 2026-06-18 | sql playbook + engine | Procedures tab cut to 4 topics (Procedural Blocks folded into Updates/Deletes/Inserts); Series Generation got 6 engine subtypes matching its playbook leaves; new `scalar_extract` qtype (LIMIT/OFFSET); Period Overlap recipe got Trinidad's CROSS-JOIN-in-CTE variant + plain-language LEFT JOIN walkthrough; 32 playbook backups purged. Full detail in `folders/sql/HANDOFF.md` (canonical for `sql_problem_patterns.html` + `sql_practice_utils.py`). |
| 2026-05-06 | nb02 schema_design form | Granular translate-the-asks decomposition. Replaced the single "Maps to:" dropdown per ask with five sub-fields per ask: Numerator, Denominator, Filter dim (FK), Drill-down attribute, Supporting timestamp. Forces decomposition before the main form. State persists via `translate_decomp` and is fed to the grader prompt as a labeled per-ask block. Legacy `translate_picks` still loaded for back-compat with prior saved attempts. |
| 2026-05-06 | nb02 schema_design form | Kimball 4-step banner added at top of concept primer. Gold-bordered table mapping the 4 Kimball steps (business process → grain → dims → facts) to the form fields that ground each one. Sets the design framework before the user opens the accordion. |
| 2026-05-06 | nb02 schema_design form | Closed out the 25 logged interactive widget changes: per-dim attribute checkboxes (Approach 2) with usage dropdowns (group-by / filter / drill-down / display / not used), business process noun-finder, metrics classifier table, source column classifier table, edge case category cards, models purpose dropdown with auto-suggest layer, dbt tests pack reminder callout, conformed dims yes/no gate, SCD per-dim 2-question walkthrough, surrogate vs natural key 4-question walkthrough, re-run safety 5-question gated walkthrough, late-arriving 4-question branching walkthrough. All recommendations include lay-language definitions. |
| 2026-05-05 (later) | nb02 schema_design form | Added Walkthrough mode toggle. In Walkthrough, the worked answer + lay-language Why REPLACES the hint area for each field. User paraphrases to lock in the concept; grader scores understanding (not correctness from scratch). Solve mode preserved as default for self-testing. |
| 2026-05-05 (later) | nb02 schema_design form | Auto-save + auto-load form responses. Every grade click writes `data/outputs/solved/<problem_id>_schema_design_attempt.json` with full form state (texts, dropdowns, dim picks, SCD picks, models, tests, translate picks, mode). Reload via saved-problems dropdown repopulates every field. |
| 2026-05-05 (later) | nb02 schema_design form | Concept primer entries now include concrete EXAMPLES (blue-bordered) alongside definitions. New entry: "Raw measure vs derived metric — what belongs on the fact" addresses Trinidad's most common mistake (designing rates as columns instead of raw counts). |
| 2026-05-05 (later) | nb02 schema_design form | Field 2 fact column template now renders as a proper HTML table (visual reference) PLUS a copyable markdown source block. Was a confusing `<pre>` block of raw markdown text. |
| 2026-05-05 (later) | nb02 schema_design form | Worked example reveal per field — collapsible "💡 Show example answer" populated from `worked_example_per_field` for solve mode peeking. Hidden in walkthrough mode (redundant). |
| 2026-05-05 (later) | nb02 generator | schema_design KPI guidance restructured: 4-section prompt format (STAKEHOLDER CONTEXT / VOLUME AND UPDATE FREQUENCY / WHAT YOU HAVE IN SOURCE / YOUR TASK), each ask must have a formula, dim list with attributes (no "yes" affirmations), explicit fact-table-only focus, newline bullets required (no inline " - " separators). |
| 2026-05-05 (later) | nb02 validator | `_validate_kpi_problem` now enforces schema_design extras: candidate_dimensions (3+ entries), stakeholder_asks (3+), field_hints (all 11 keys non-empty), worked_example_per_field (all 11 keys non-empty), schema_ddl. Rejects incomplete generations so walkthrough mode always has data. |
| 2026-05-05 (later) | nb02 prompt renderer | `prompt_to_bullets_nested` rewritten to handle structured prompts: uppercase section headers → `<h5>`, newline-prefixed bullets → `<ul>`, paragraph blocks separated by blank lines. Falls back to legacy comma-list / lettered-enumeration logic for plain text. |
| 2026-05-05 (later) | nb02 schema rendering | `schema_to_html` strips SQL `--` line comments and `/* */` block comments before parsing DDL. Fixes the garbage `--` row that appeared when LLM emitted inline column comments. |
| 2026-05-05 (later) | nb02 catalog | Tab 2 reduced from 7 to 4 subtopics. Dropped: cte_chain (covered by nb01 SQL practice), staging_vs_marts (schema_design field 7 covers conceptually), materialization_choice (schema_design field 7 covers). Kept: schema_design (KPI form), dimensional_modeling (SQL), scd_type_2 (SQL), dbt_tests_macros (KPI markdown). |
| 2026-05-05 (later) | nb02 catalog | Added Tab 5: Version Control (Git for analytics). 7 markdown-graded subtopics: branching_strategy, merge_conflict_resolution, rebase_vs_merge, pr_review_critique, commit_message_critique, revert_strategy, git_state_diagnose. |
| 2026-05-05 (later) | sandbox.py | Fixed `_split_pg_statements` to skip `--` line comments, `/* */` block comments, and `'...'` string literals when scanning for `;`. Was breaking on answer_keys with semicolons inside SQL comments (psycopg2 "can't execute an empty query"). |
| 2026-05-05 (later) | nb02 layout | Section 2 has one accordion with 4 panels: Structural / Modeling / Business / Schema Design Response Form. Schema Design panel auto-expands when subtopic loads. Section 3 is SQL only — for non-SQL subtopics, section 3 shows a notice pointing back to section 2. |
| 2026-05-05 (later) | nb02 setup | Code-toggle button (HTML+JS) auto-prepended to every code cell. Auto-hides input on render; click to show source. Works in JupyterLab and classic Notebook 7+. |
| 2026-05-05 (later) | nb02 form bug | `continuous_update=False` on schema_design model name TextInput. Was firing observe on every keystroke, polluting test_selections with stale partial-name keys (`m`, `ma`, `mar`, ...). Plus defense-in-depth filter at grade time. |
| 2026-05-05 | nb02 schema_design (initial Path B) | Converted schema_design from SQL execution to KPI markdown-graded form. 11-field structured response: grain, fact columns, surrogate vs natural key, dim joins, SCD per dim, conformed dims, models, dbt tests, idempotency, late-arriving, edge cases. Per-field hints, pitfall callouts, dynamic widgets driven by candidate_dimensions list. |
| 2026-05-05 | project layout | Moved `build_nb02.py` into the project at `build/build_nb02.py` so it survives Cowork session boundaries (was previously session-only in outputs dir) |
| 2026-05-05 | context.md | Added next-session orientation block, recipe-card template, open-work tracker — making the file self-sufficient as a handoff |
| 2026-05-03 | nb02 dbt tests table | Added `expect_column_values_to_be_of_type` (dbt_expectations) — schema enforcement for INT/DATE column types |
| 2026-05-03 | blog Tab 2 | Promoted `materialization_choice` card from placeholder; based on Trinidad's kit-event drill. Includes new "Modeling diagnostic — appropriate response" section with bullet-pointed rationale across all 5 axes (materialization, grain, joins, dbt layer, tests) |
| 2026-05-03 | nb01 | Added auto-resize JS to cell 1 — `.diagnose-textarea` and `.sql-code-editor` textareas now grow with content (parity with nb02) |
| 2026-05-03 | nb02 dbt tests table | Final form: single `widgets.GridBox` with checkbox + 4 HTML cells per row, all flat-listed. Replaces the broken VBox-of-HBox attempt. One shared scrollbar, aligned columns |
| 2026-05-03 | nb02 dbt tests table | Intermediate (rejected) attempt: pure HTML reference table on top + SelectMultiple picker below — Trinidad wanted checkboxes inline |
| 2026-05-02 | nb02 dbt tests table | First attempt at 5-column checkbox table broke (gray loading bars) — too many nested HTML widgets per HBox |
| 2026-05-02 | nb02 modeling diagnostic | Added input+output grain prompt, single-table join leniency, dbt layer dropdown definitions |
| 2026-05-02 | nb02 modeling grader | Added `grade_modeling_diagnostic` with rubrics for materialization, grain (BOTH input+output), join strategy, dbt layer, test coverage; knows dbt-core, dbt_utils, dbt_expectations, dbt_project_evaluator |
| 2026-05-01 | both notebooks | Disabled Shift+Enter on textareas (was wiping in-progress work) |
| 2026-05-01 | blog | Promoted staging_vs_marts card; cleaned up CTE naming |
| 2026-05-01 | nb02 | Added `dbt_tests_macros` subtopic to transformation_modeling (markdown-graded via per-subtopic kind override) |
| 2026-04-30 | blog | Promoted scd_type_2, dimensional_modeling, cte_chain cards from placeholders |
| 2026-04-30 | nb02 | Scrubbed all company names from problem generator and notebook intro |
| 2026-04-29 | nb02 | Added Interpretation + Recommendation practice fields to diagnostic section |
| 2026-04-29 | blog | Promoted reject_pareto, window_event_log, segment_performance, time_to_fill, adherence_pdc, reversal_rate, cohort_retention cards |
| 2026-04-28 | nb02 | Pinned segment_performance, time_to_fill, cohort_retention to one explicit shape each with hand-traced math |
| 2026-04-28 | nb02 | Implemented validator self-consistency, industry vocab enforcement, KPI rubric floor, benchmark grounding |
| 2026-04-27 | nb02 | Added new subtopics: net_acceptance_rate, reversal_rate, adherence_pdc |
| 2026-04-27 | nb02 | Fixed INSERT data rendering (parser fallback + generator constraint), `_canonical_value` numeric-string false positive |
| 2026-04-26 | nb02 | Initial build: 11 cells, 4 categories, replay support |

---

## Current state of the blog (`pharmacy_problem_patterns.html`)

| Tab | Cards populated | Cards still as placeholders |
|---|---|---|
| Tab 1 — Pharmacy Claims SQL | All 9 (cohort_retention, window_event_log, reject_pareto, segment_performance, time_to_fill, adjudication_funnel, net_acceptance_rate, reversal_rate, adherence_pdc) | — |
| Tab 2 — Transformation Modeling | 5 cards exist for the OLD 7-subtopic catalog (cte_chain, dimensional_modeling, scd_type_2, staging_vs_marts, materialization_choice). Catalog dropped 3 of these on 2026-05-05; cards remain in the blog as reference. | schema_design, dbt_tests_macros (new placeholders for the new catalog) |
| Tab 3 — Critical Reasoning SQL | — | All |
| Tab 4 — Product Metrics & KPIs | — | All |
| Tab 5 — Version Control | — | All (new tab as of 2026-05-05) |

Note: the 3 cards for dropped subtopics (cte_chain, staging_vs_marts, materialization_choice) stay in the blog as reference material — they were good content, just not in the active drill catalog anymore. Don't delete them unless Trinidad asks.

Trinidad mentioned a future quiz tab — she'll provide the framework when she's ready.

---

## Open work / known TODOs

| Tab | Cards still placeholder | Notes |
|---|---|---|
| Tab 2 — Transformation Modeling | `schema_design`, `dbt_tests_macros` | Will get filled in as Trinidad drills them. schema_design is the centerpiece — its recipe card should reflect the 11-field framework (grain, fact columns, dim joins + SCD, models, tests, idempotency, late-arriving, edge cases) with one of her actual worked answers from a Walkthrough or Solve attempt. The dbt_tests_macros card should pull from her notebook drills + the dbt tests reference table |
| Tab 3 — Critical Reasoning SQL | `ambiguous_metric`, `missing_data`, `edge_cases`, `clarify_then_query`, `outlier_handling`, `critique_broken_sql` | All still placeholders |
| Tab 4 — Product Metrics & KPIs | All cards | Still placeholders. Maps to Product Analytics Academy framework: critical / counter / sanity / guardrail metrics |
| Tab 5 — Version Control (new) | All 7 cards | Pure placeholders. 7 subtopics available in nb02. Cards would benefit from real PR diff snippets / merge conflict examples |
| Future | Quiz tab | Trinidad mentioned wanting one — she'll provide the framework |

Don't start filling these proactively — wait until Trinidad drills the corresponding subtopic in nb02 and asks for the card to be promoted. Each card should reflect HER worked solution + the gotchas SHE actually hit.

---

## Recipe card template (for new cards in `pharmacy_problem_patterns.html`)

Every populated card has these 8 sections in this order, all collapsed by default. Use the `materialization_choice` card (lines ~3518 in the HTML) as the most up-to-date reference — it's the only one with the "Modeling diagnostic — appropriate response" section.

```html
<div class="recipe-card" id="<subtopic_id>">
  <div class="recipe-header" onclick="toggleCard(this)">
    <h3 class="recipe-title"><span class="recipe-id">RECIPE</span><Card title></h3>
    <span class="recipe-toggle"></span>
  </div>
  <div class="recipe-body">
    <div class="section-controls">
      <button onclick="expandAllSections(this)">Expand all</button>
      <button onclick="collapseAllSections(this)">Collapse all</button>
    </div>

    <!-- 1. Signal words in the prompt -->
    <!-- 2. Glossary (lay-language definitions, <dl><dt><dd>) -->
    <!-- 3. Real-world business context (<glossary-block> with multiple <strong>+<ul> blocks) -->
    <!-- 4. How the calculation works (<calc-block> with <ol>) -->
    <!-- 5. Recipe template (<pre class="sql-block">) -->
    <!-- 6. Modeling diagnostic — appropriate response  (NEW since 2026-05-03; only on modeling cards in Tab 2) -->
    <!-- 7. Worked example (problem-statement + schema-table + data-table + per-X trace + output-table + Trinidad's pre.example-block + optional rationale callout) -->
    <!-- 8. Common gotchas (<ul class="gotcha-list">) -->
  </div>
</div>
```

Conventions:
- Always attribute Trinidad's solution: `<div class="table-label">Working solution (Trinidad, YYYY-MM-DD):</div>`
- Gotchas should be SPECIFIC mistakes Trinidad made on this problem (or that an interviewer would penalize), not generic advice.
- The "Modeling diagnostic — appropriate response" section is ONLY for Tab 2 modeling cards. Skip it on Tab 1 (analytical SQL) and Tab 3 (critical reasoning) cards.

---

## How to extend things safely

- **Adding a new subtopic** → edit `CATEGORIES` in `nb02_drill_utils.py`, add a generator template (SQL → `SUBTOPIC_GUIDANCE`, KPI → `KPI_SUBTOPIC_GUIDANCE`), add to PHARMACY_SCENARIOS if needed. If grading should be markdown, set `kind: "kpi"` on the catalog entry.
- **Adding a new category** → add to `CATEGORIES` dict. The picker dropdown auto-populates from `category_keys()`. No build script changes needed.
- **Adding a new dbt test to the dbt tests table** → edit `_dbt_test_specs` list in build_nb02.py cell 5. Rebuild.
- **Adding a new field to the modeling diagnostic** → add the widget in cell 5's modeling diagnostic block, add it to the `answers` dict in `on_modeling_feedback`, add a rubric to `MODELING_GRADER_SYSTEM` in nb02_drill_utils.py, add a renderer block to `modeling_grade_to_html`. Reset it in the Next Question handler.
- **Adding a new field to the schema_design form (sd2_*)** → cleaner workflow:
  1. Add the widget in cell 5's schema_design block (text/dropdown/multiselect as appropriate)
  2. Add a hint widget via `_make_hint_widget("...")` and a generic-defaults entry in `_SD2_GENERIC_HINTS`
  3. (Optional) Add a worked-example widget via `_make_worked_example_widget()`
  4. Add to `_SD2_HINT_WIDGETS` and `_SD2_EXAMPLE_WIDGETS` maps in `_sd2_init_widget_maps()`
  5. Add the panel to `sd2_panels` list with title via `sd2_accordion.set_title(N, "...")`
  6. Update `on_schema_design_grade` to include the field in the responses dict
  7. Update `_sd2_apply_saved_responses` to populate the widget on reload
  8. Update `grade_schema_design_form` user_prompt to format the field for the grader
  9. Update `SCHEMA_DESIGN_FORM_GRADER_SYSTEM` rubric to include the new axis
  10. Update `_sd2_state` reset in `refresh_subtopic_form` if the field has dynamic state
  11. Update `KPI_SUBTOPIC_GUIDANCE["schema_design"]` to demand the new key in `field_hints` and `worked_example_per_field`
  12. Update `_validate_kpi_problem` `REQUIRED_FIELD_IDS` tuple
- **Adding a new concept to the schema_design concept primer** → add a `_sd2_concept_block(title, definition_html, example_html)` entry inside `_sd2_concept_primer`. Both definition and example required for clarity.
- **Adding a new recipe card to the blog** → mirror the nested collapsible structure used by existing cards (signal words, glossary, real-world context, recipe template, worked example, common gotchas). All sections start collapsed by default.
- **After any nb02 change** → always rebuild via `python3 build/build_nb02.py` and verify with the smoke test pattern (`json.load` + `ast.parse` each code cell). Then have Trinidad RESTART the kernel (not just re-run cells — old code stays in memory until restart).
- **When generation fails JSON parsing** → bump `max_tokens` in `_call_claude` for that subtopic (schema_design uses 6000). Check `_build_kpi_user_prompt` retry guidance — it tells the LLM to be terser on retry.

---

## Reference paths

- Project root: `folders/ds_blogs/projects/data_analyst_interview_prep/`
- Build script: `folders/ds_blogs/projects/data_analyst_interview_prep/build/build_nb02.py`
- Drill utils (prompts, validators, graders): `folders/ds_blogs/projects/data_analyst_interview_prep/notebooks/nb02_drill_utils.py`
- Notebook: `folders/ds_blogs/projects/data_analyst_interview_prep/notebooks/nb02_fuze_interview_drills.ipynb`
- Companion blog: `folders/sql/pharmacy_problem_patterns.html`
- Postgres sandbox: `docker compose up -d` from project root
