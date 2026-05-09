# Handoff: Trinidad's SQL Practice & Playbook

Updated 2026-05-08. Pick up here for the next cowork session.

## Two active artifacts

1. **Playbook** — `/Users/trinidadcisneros/Documents/Development/Coding/bitterscientist.com/bitterscientist.com/folders/sql/sql_problem_patterns.html`
2. **Practice notebook** — `/Users/trinidadcisneros/Documents/Development/Coding/bitterscientist.com/bitterscientist.com/folders/ds_blogs/projects/sql_practice_generator/notebooks/nb01_sql_practice.ipynb` (and its util module `sql_practice_utils.py` next to it)

Trinidad is prepping for SQL interviews (Solace Health DA assessment, SmarterDx senior product analyst). Day-to-day is Redshift/Snowflake/Databricks, comfortable with PostgreSQL.

## RESPONSE RULES — non-negotiable

- Default to HINTS, not solutions. Never paste full SQL unless explicitly asked ("show me the code").
- Single-sentence lay language. No paragraphs. One concept per bullet, each one short sentence.
- No metaphors that introduce new jargon. Use concrete words (slot, position, label).
- "Walking through a query" = TABLES showing rows at each step, NOT prose.
- "Is X correct?" → yes/no first, then ONE sentence.
- Slip and over-explain → Trinidad will say so loudly. Apologize once, fix it.
- Keep audit columns visible in CTE staircases — don't collapse raw join columns into derived flags.
- When editing pasted drafts (emails, code), preserve line breaks and untouched sentences exactly.
- **Tables must use ATOMIC cells.** One fact per cell. Never cram "predicate + result + outcome" into one cell. If a row would need many columns, split into multiple smaller tables stacked vertically. Avoid jargon ("predicate", "three-valued logic", "tuple comparison"); say "check", "expression", "SQL has three answers — TRUE, FALSE, NULL".

## EDITORIAL — content rules for the playbook

- No hyphens unless compound nouns ("five-step" OK).
- No emojis unless Trinidad uses them first.
- DO NOT mention CodeSignal, LeetCode, StrataScratch, DataLemur, or any brand names anywhere in the playbook (HTML comments included). Use generic phrasing ("the test harness", "practice platforms").

## PLAYBOOK STATE (`sql_problem_patterns.html`)

Tabs: Diagnostic Process | Decision Tree | Single-Table Recipes | Multi-Table Recipes | Procedures

### Procedures tab — top-level Quick Scaffolds card

A "Quick Code Scaffolds" reference card sits at the very top of the Procedures tab (collapsed by default) with paste-ready starters for: DML (single UPDATE / DELETE / INSERT), DO sequential, DO row-by-row, RETURNS scalar, RETURNS TABLE — plus a decision-guide table mapping prompt signals to scaffolds.

### Procedures topics (5 containers)

1. **Procedural Blocks** — Reference + 2 recipes:
   - Simple Sequential UPDATEs (set-based) — anchors: tiered discounts, driver shifts, loyalty points, shipment delays
   - Row-by-Row State Mutation (FOR LOOP) — anchors: airline seats, refund queue, cohort enrollment, readmission severity, content watch session, **Sequential Medication Dose Adjustments**, **Apply Sequential No-Show Penalties (compounding 2x+1)**

2. **Functions** — Reference (Method Scaffolds & Pitfalls — now includes type-cast pitfall row covering TO_CHAR→TEXT, COUNT→BIGINT, AVG→unconstrained NUMERIC, bare VARCHAR vs VARCHAR(N)) + 2 recipes:
   - RETURNS scalar — anchors: SLA breach rate, reviewer denial rate, avg engagement score, sleep adherence, **30-Day Readmission Rate (LAG previous discharge)**, **Trial Conversion Rate by Cohort (CTE staircase + denominator gotcha)**
   - RETURNS TABLE — anchors: #177 NthHighestSalary, #2230 Eligible for Discount, Patient Medication Adherence, Filter Claims by Denial Category, Therapy Engagement Score, **Loan Stage Duration (EXTRACT EPOCH)**, **Trial Conversion Report by Plan Tier (multi-table JOIN + time-window filter + inclusive day count)**

3. **Recursive Queries** — Reference + Hierarchies, Paths, Chains recipe (Trace Transaction Approval Chain)

4. **Updates, Deletes, Inserts** — Reference + 3 recipes (UPDATE → DELETE → INSERT order):
   - Single-Statement UPDATE — anchors: tiered subscription discount, fraud flag risk score, sleep logs goal achievement, **Apply Tiered Review Status Updates (multi-column CASE in one SET)**
   - Single-Statement DELETE — has Common DELETE cases reference table (7 cases: conditional, duplicates, orphans, cross-table, time-based pruning, two-condition, NULL-safe positive WHERE) + Common pitfalls table. Anchors: article views dedup, milestone purge after delivered, **Remove Incomplete Sleep Sessions (positive WHERE vs NOT IN + NULL handling)**
   - Single-Statement INSERT — anchor: archive approved loans

5. **Window Function Edges** — Reference only

### Procedures tab intro

Now lists all 5 topics explicitly (was "two families" — fixed). Functions topic excerpt now distinguishes `RETURN ( ... );` (scalar) from `RETURN QUERY ( ... );` (table) and notes they are NOT interchangeable.

### Single-Table Recipes — Gaps-and-Islands & percentile clusters

- **Gaps-and-Islands summary callout** (purple-bordered) sits before #601 Human Traffic of Stadium with three tables: pick approach by data shape (4 forms), GROUP BY + key pitfall per approach, trace examples per approach. Critical correction: form A (`PARTITION BY entity` outer) is NOT a superset of form B; if there's no entity column, you MUST use form B. Substituting status as the entity collapses every same-status row into one giant island.
- **#1225 Report Contiguous Dates** — has TWO ranked solutions: Rank 1 `rn_overall - rn_per_state` (dialect-agnostic), Rank 2 `date - (rn_per_state)::INT` (Postgres-friendly, no missing days)
- Yellow callout under #1225 explaining the calendar-vs-data-sequence distinction with the leap-year example
- **Anchor: Member Workout vs Skip Streaks** — leap-year trap (Feb 28 / Mar 1 / Mar 2 with Feb 29 missing) with per-row trace table
- **Anchor: Collapse Order Status Periods (UNION + per-entity partition)** — multi-entity timelines requiring `PARTITION BY order_id` on BOTH windows; GROUP BY three keys
- **Percentile & Distribution Metrics summary callout** (teal-bordered) sits between Top 10% Trial Sites anchor and #2377. Covers PERCENTILE_CONT/DISC, NTILE, PERCENT_RANK with method comparison + quick decision table. Also notes ROW_NUMBER fallback for "top N" without percentage.
- **Anchor: Top 10% Trial Sites by Enrollment Rate** — PERCENT_RANK + ratio output, DESC direction trick (order so the "best" rows sit at pr=0; filter pr <= X/100). Two-CTE staircase (base → ranked → final). Watch-outs cover integer division flattening, NULLIF zero guard, ratio vs percent rank confusion in output, and ROUND on DOUBLE PRECISION.
- **Anchor: Quartile Bucketing of Monthly Box Revenue** — `NTILE(4) OVER (ORDER BY metric DESC)` for "highest in bucket 1". Watch-outs cover uneven splits going to lower buckets, ties not sharing buckets, NTILE only accepting literal integer.

### Reshape Recipes (Reshape Recipes tab) — pivot/unpivot/cross-join cluster

The four technique cards now have ID anchors (`reshape-union`, `reshape-pivot`, `reshape-unpivot`, `reshape-cross-join`) so the Decision Tree's blue Reshape cards (UNION, UNION ALL, Pivot, Unpivot, Calendar / skeleton CTE, CROSS JOIN for combos) navigate directly to the matching technique section.

- **Conditional Pivot (Long to Wide)** — 6 example problems including: #618, #1179, #1479, #1777, **Pivot Trial Adverse Events by Severity (SUM + COALESCE 0)**, **Pivot Appointment Types by Provider (LEFT JOIN + SUM pivot)**. Mnemonic established: "row, column, cell" — row key → GROUP BY, column key → CASE WHEN inside aggregate, cell value → THEN clause inside CASE.
- **Unpivot via UNION ALL (Wide to Long)** — 4 example problems including: Reverse of #618, #1783, #1795, **Unpivot Approval Metrics by Channel (keep NULLs)**. Includes the CROSS JOIN LATERAL VALUES Postgres alternative.
- **CROSS JOIN / Calendar Skeleton (Complete Combinations)** — 5 example problems including: #1127, #1280, #1633, **Weekly Session Attendance with Zero-Fill (calendar skeleton derived from data, month-padded)**, **Daily Ward Admission Gaps Report (date_range CTE + CROSS JOIN + LEFT JOIN)**. Both anchors emphasize: build skeleton FIRST (CROSS JOIN), THEN LEFT JOIN actuals. Don't add `FROM <table>` to a `generate_series` CTE.

### Common mnemonics (already in playbook, don't re-explain unless asked)

- PARTITION BY: "winner per something" = partition; "one winner overall" = no partition
- Scalar-extract is always overall (no PARTITION)
- Tiebreaker ORDER BY: ASC/DESC applies per column
- Self-joins live in enrich-join, not row-compare
- Window functions evaluate at SELECT step; can't reference in WHERE/HAVING
- ROW_NUMBER for "exactly one winner per group"; DENSE_RANK for "Nth distinct"
- LEFT JOIN: right-side filter in WHERE drops unmatched rows → put in ON
- DECIMAL(10,2) rounding flips strict > comparisons in DO blocks
- `INTERVAL 'p_lookback_days days'` does NOT interpolate; use `(p_lookback_days || ' days')::INTERVAL` or `CURRENT_DATE - p_lookback_days` (DATE − INT works, TIMESTAMP − INT doesn't)
- For "latest per group": `DISTINCT ON (group) ORDER BY group, ts DESC`
- RETURNS TABLE column shadowing — alias source table and qualify every column
- RETURN scalar uses `RETURN ( ... );` not RETURN QUERY
- `DO $$ ... END $$;` (semicolon required)
- CREATE FUNCTION alone produces no rows; trailing `SELECT * FROM fn(args);` required
- `SELECT * FROM fn()` for RETURNS TABLE; `SELECT fn() AS alias` for RETURNS scalar
- 0 in expected output → LEFT JOIN + filter inside SUM/COUNT, never WHERE
- Scalar aggregate (no GROUP BY) always returns one row, even when WHERE matches nothing — COALESCE the NULL
- For "% of nights in fixed N-day window," generate the date skeleton with `generate_series(start, start + (N-1), INTERVAL '1 day')::date` and LEFT JOIN source to it. Otherwise denominator drops below N when rows are missing
- VARCHAR(N) length-match in RETURNS TABLE — bare VARCHAR vs VARCHAR(100) raises "structure of query does not match function result type"
- `LEAST(value + delta, cap)` to cap at cap; `GREATEST(value, floor)` to floor
- Don't name PL/pgSQL variables after reserved keywords (`current_date`, `current_user`, etc.) — Postgres uses the keyword instead. Use `v_` or `p_` prefix
- `NOT IN` with NULLs evaluates to UNKNOWN for every row; use `NOT EXISTS` if the subquery can return NULL
- DELETE dedup: `WHERE pk NOT IN (SELECT MIN(pk) FROM t GROUP BY group_cols)`. Two-condition DELETE (group eligibility AND row exemption) is a different shape
- `EXTRACT(EPOCH FROM interval)` returns total seconds; divide by 60 for minutes, 3600 for hours
- "Ago" = older = smaller date = `<`; "more than 90 days ago" is `date < CURRENT_DATE - 90`
- Inclusive day count adds `+ 1` to the gap (Jan 10 minus Jan 1 is 9, but the trial lasted 10 days)
- DATE_TRUNC('month', date) returns first-of-month with year intact; cohort match via `DATE_TRUNC('month', x) = DATE_TRUNC('month', y)` includes year
- WHERE only fires on TRUE; both FALSE and NULL are ignored. Any comparison with NULL is NULL
- Express WHERE for the rows you want to ACT on, not the inverse — NULL handling breaks NOT IN inversions
- Write the DELETE positively (`WHERE duration < 180 OR quality IS NULL`) instead of `NOT IN (keep set)` — the inverse breaks on NULL comparisons
- For percentage rules in DML, ALWAYS confirm "X% of which column" — the prompt should name the multiplicand
- For multi-rule UPDATE sequences with status changes, ensure each rule's status filter can be true given the rows the prior rules left behind
- The two gaps-and-islands forms differ when data has missing days: `date - rn_per_state` requires calendar consecutiveness; `rn_overall - rn_per_state` only requires data-sequence consecutiveness. Default to the second form when "continuous" isn't explicitly defined as "every calendar day"

## NOTEBOOK STATE (`nb01_sql_practice.ipynb`)

11 cells: Setup → Pick Problem → Diagnose → Write SQL (cell 7) → Next Problem (cell 9) → notes.

### Question types in `QUESTION_TYPES` (sql_practice_utils.py)

- `select_analytical` (postgresql, mysql)
- `do_block` (postgresql) — strict set-based, NO loop, NO compounding (recently strengthened)
- `do_block_queue` (postgresql) — FOR LOOP with per-iteration state read
- `returns_table` (postgresql)
- `returns_scalar` (postgresql)
- `recursive_cte` (postgresql, mysql)
- `dml` (postgresql, mysql) — picks UPDATE/DELETE/INSERT at 33/33/33
- `window_edge` (postgresql, mysql)
- **`union_islands`** (postgresql, mysql) — picks one of 4 flavors at 25/25/25/25: `date_calendar` (date - rn), `date_sequence` (rn - rn), `integer_seq` (single-table id - rn, no UNION), `partitioned_status_periods` (per-entity timelines, both windows partitioned by entity key)
- **`percentile_metrics`** (postgresql, mysql) — picks one of 3 flavors per dialect: `percentile_aggregate` (Postgres only, PERCENTILE_CONT/DISC), `ntile_buckets` (NTILE for quartile/decile), `top_n_percent` (PERCENT_RANK for top X%)
- **`pivot`** (postgresql) — long format to wide format using `aggfn(CASE WHEN cat = 'X' THEN val END) AS x_col`. Prompt names the closed category set, target columns, and aggregation function explicitly. Test data must have one entity missing rows for one category (NULL vs COALESCE'd 0) and one entity with multiple rows in the same category.
- **`unpivot`** (postgresql) — wide format to long format using UNION ALL of one SELECT per source column with literal labels. Alternative form: `CROSS JOIN LATERAL (VALUES ...)`. Prompt names exact label strings and explicit NULL handling rule.
- **`cross_join`** (postgresql) — motivated CROSS JOIN usage. Generator rotates across three shapes per generation: SHAPE A (calendar/date skeleton via `generate_series` CROSS JOINed with entity table, LEFT JOIN actuals, COALESCE 0), SHAPE B (categorical skeleton fan-out like #1907), SHAPE C (all-pairs self-cross-join with `a.id < b.id` dedupe filter). Prompt must explicitly motivate WHY cross join is needed (forbidden: gratuitous Cartesian products).
- **`date_operations`** (postgresql) — date and timestamp methods are the centerpiece. Covers DATE_TRUNC for cohort buckets, EXTRACT for components (YEAR, DOW, HOUR), DATE ± INT arithmetic, 'X days ago' filtering, inclusive vs exclusive day counts (+ 1 trap), EXTRACT(EPOCH FROM interval) for durations, generate_series for date skeletons. Pitfall guard: column-driven intervals must use `(col || ' days')::INTERVAL` or `CURRENT_DATE - col`, NOT `INTERVAL 'col days'` (no string interpolation).

### Generator guardrails added in this session

- **Returns_table generator** no longer puts placeholder bodies in schema_ddl (fixed the syntax-error-on-load bug)
- **Do_block guidance** now explicitly forbids FOR LOOP, SELECT INTO, RECORD variables, IF/ELSIF on row state, and any compounding formula on the column being updated. Includes a list of forbidden prompt language (the exact phrasing that produced the no-show problem)
- **Trailing-call explicitness** rule: any function with parameters must include "Test your function by calling: `SELECT ...`" with the exact arguments that produce example_output_rows, and the answer_key must end with the same call verbatim
- **Explicit-formula rule**: any rule computing a derived value must name the source column, target column, and exact formula in code formatting. Forbidden: "apply a 15% fee" without naming the multiplicand
- **Column-label discipline**: if rule 1 sets a status to a value and a later rule references that label, the prompt must clarify whether it means the literal status value or the underlying criterion. Forbids reusing a status label across rules whose status filters can't both be true at once
- **`gaps-and-islands`** added to RECIPE_VOCAB

### Cell 7 (SQL editor) state

- Plain ipywidgets Textarea (no CodeMirror — CodeMirror integration with ipywidgets in JupyterLab kept breaking)
- `add_class('sql-code-editor')` + dracula CSS (`#282a36` background, `#f8f8f2` text, `#21222c` gutter, `#6272a4` line numbers)
- Line-numbers gutter built via JS-injected sibling div
- Tab inserts 4 spaces; Shift+Tab outdents; multi-line selection indents/outdents as a block
- Tab handler now calls both `preventDefault()` AND `stopPropagation()` so JupyterLab doesn't grab the keystroke
- Buttons: Test, Run, Submit, Hint, Format, **Code Reference**
- Format uses `sqlparse.split(raw) → format each with reindent_aligned=True, keyword_case='upper' → join with '\n\n'`. `pip install sqlparse` once
- **`code_ta` defaults to `/* notes */\n\n`** so the user can immediately type notes; `on_next` (cell 9) resets to the same default
- **Reminder block now includes Expected output** as an open `<details>` panel (alongside Schema and Example input data)
- **Code Reference button** calls `spu.get_code_reference(qtype, islands_flavor, percentile_flavor)` and renders a generic SQL framework skeleton in the Hint output area. Templates live in `CODE_REFERENCE` dict in `sql_practice_utils.py` (19 entries: 12 question types + 4 union_islands flavors + 3 percentile_metrics flavors)

### Cell 5 (Diagnostic form)

- `paraphrase_ta` and `moves_ta` now have `add_class('diagnose-textarea')`
- Same dracula theme + Tab/Shift+Tab indent handling as cell 7
- Native textarea undo (Cmd+Z) works for typed-character edits

### Cell 1 (Setup) global keyboard guard

- Capture-phase listener at document level
- Stops propagation on Shift+Enter inside textareas (so cell run doesn't wipe widget state)
- Stops propagation on Cmd/Ctrl+Z and Cmd/Ctrl+Shift+Z inside textareas (so JupyterLab's "undo cell" doesn't fight native textarea undo)
- Does NOT stop Tab — cell-level handlers consume that

### Cell 9 (Next Question) on_next

- Clears `paraphrase_ta.value`, `moves_ta.value` directly
- Resets `code_ta.value` to `'/* notes */\n\n'` (NOT empty string) so user can keep typing notes immediately

### Cell 3 (`render_problem`) and Cell 7 (`_render_problem_reminder`)

- Prompt rendered as bullets, schema as Column/Type table, INSERT data as actual table
- Helpers in `sql_practice_utils.py`: `prompt_to_bullets`, `schema_to_html`, `insert_data_to_html`

## JUPYTERLAB AUTOSAVE GOTCHA

If Trinidad has the notebook tab open in JupyterLab while you edit the .ipynb on disk, JupyterLab's autosave will overwrite your edits with its in-memory copy. ALWAYS tell Trinidad: **File → Reload Notebook from Disk first (don't save), then Kernel → Restart Kernel and Run All Cells.**

## PERSISTENT STRUGGLES (be patient)

- Frequency-based median (#571) — prefers expand-then-rank
- Tiebreaking ASC/DESC on each column
- NULL behavior with IN vs NOT IN, comparisons with NULL evaluating to NULL
- ROWS vs RANGE for missing-value gaps
- Date math: INTERVAL parameter interpolation, CAST timestamps vs dates for boundary checks
- RETURNS TABLE column shadowing trap (forgetting to qualify columns)
- RETURNS TABLE strict type matching (TO_CHAR returns TEXT, COUNT returns BIGINT, AVG returns unconstrained NUMERIC — must cast)
- The denominator gotcha (averaging over the whole table when the cohort is a subset)
- Linear vs compounding math in DO blocks (the no-show problem)
- The two gaps-and-islands formulations and when each one breaks
- Trailing-call argument values must match the prompt's expected output

## WORKING STYLE

- Trinidad pastes their CTE/code and asks "is this right?" or "why am I getting X?" — debug from the actual output table they paste
- Prefers CTE staircase (each step verifiable) over minimal solutions. Don't refactor unless asked
- "It's messy" = invitation to suggest cleanup hints, not rewrite
- "Is this in the playbook?" → grep -c '#NNN' the file. Offer to add if no
- When showing tables for query walkthroughs, show row state at each step explicitly
- Trinidad goes granular: original data → first CTE step → next CTE step, with questions between each
- Generator-bug pattern: every column matches except `archived_at` or similar `CURRENT_TIMESTAMP` field — that's the test harness comparing two CURRENT_TIMESTAMP captures from different moments. NOT user's bug.

## MEMORY FILES

`/Users/trinidadcisneros/Library/Application Support/Claude/local-agent-mode-sessions/35d42d8a-1c02-467e-b7ce-a9419e6e036b/e22d76de-c0b1-4917-ae48-8319db7db0c3/spaces/29d32b05-e26e-4dad-9078-df3d29546460/memory/`

- `feedback_preserve_drafts.md`
- `feedback_keep_audit_columns.md`
- `feedback_table_atomic_cells.md`
- `feedback_islands_form_choice.md` — newest. Form A (PARTITION BY entity) is NOT a superset of form B; substituting status as the entity collapses every same-status row into one giant island. Use form A only when there's a real entity column.

## OPENING LINE FOR NEW COWORK

"Picking up your SQL prep — playbook + practice notebook with 14 question types (incl. union_islands 4 flavors, percentile_metrics, pivot, unpivot, cross_join, date_operations). Hints not solutions, single sentences, lay language, atomic table cells. What problem are you on?"

## RECENT MNEMONICS WORTH REMEMBERING

- **Pivot mental model:** "row, column, cell" — row key → GROUP BY; column key → CASE WHEN inside aggregate; cell value → THEN clause. SUM for additive, MAX for one value per cell.
- **Top X% direction trick:** order so the BEST rows sit at pr=0; filter `pr <= X/100`. DESC for "top X% highest", ASC for "top X% lowest". Same threshold both directions.
- **NTILE direction:** `ORDER BY metric DESC` for "highest in bucket 1"; ASC for "lowest in bucket 1". NTILE(n) only takes a literal integer.
- **Cross join build order:** skeleton FIRST (CROSS JOIN), actuals LAST (LEFT JOIN with ON). Reversing produces a syntax error or mis-attached actuals. Don't add `FROM <table>` to a `generate_series` CTE — multiplies the date count.
- **Calendar skeleton from data:** for "every week of the month X covers", use MIN(date)'s month bounds (DATE_TRUNC('month', MIN) + INTERVAL '1 month' - INTERVAL '1 day'). Plain MIN/MAX of dates misses trailing/leading empty weeks.
- **Multi-column tiered UPDATE:** two CASE expressions in one SET clause, same branch order in both, ELSE col_name on each. Sequential UPDATEs work for disjoint conditions but the prompt's "single UPDATE" constraint forces the CASE form.
- **DELETE NULL-safe positive WHERE:** write the WHERE for the rows you want to ACT on, not the inverse. `NOT IN` with NULLs evaluates to UNKNOWN for every row.
