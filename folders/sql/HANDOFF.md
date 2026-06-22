# Handoff: Trinidad's SQL Practice & Playbook

Updated 2026-06-21. Pick up here for the next cowork session. This file is canonical for the playbook `sql_problem_patterns.html` and the nb01 engine `sql_practice_utils.py`.

> **READ FIRST — current architecture (2026-06-21).** All "How to pick" decision trees are now **interactive click-through itrees** — they replaced the SVG flowcharts and the old `dt-flow` markup described in earlier sessions. Each container has `<div id="{id}-itree" class="itree"></div>`; one `<script>` near `</body>` defines `itreeTable()` + `renderITree()` + a `COWORK_ITREES` map registered on `DOMContentLoaded`. 25 trees total; only 2 non-tree `<svg>` remain. Every leaf endpoint shows a generic SQL template + a worked input→output example + a recipe link; question branches show a result-preview mini-table. **The generators are persisted in `folders/sql/build_scripts/`** (the Cowork scratchpad is wiped each session): `itree_specs.py` (tree SPECS), `itree_content.py` (CODE templates + EX worked examples per leaf anchor), `build_itree_examples.py` (rebuilds all trees), `eabuild.py` (worked-card builder + DuckDB verify), plus recent one-off card builders and a `README.md`. To change a tree: edit SPECS (+ CODE/EX for new leaf anchors) → run `build_itree_examples.py`. Invariant after any edit: div opens==closes, depth 0, `<svg>`==`</svg>`, `function renderITree` appears once. Current balance **div 6535/6535**.

## SESSION 2026-06-21 (later 5) — Single-Table Filter › Qualify-on-thresholds card + missing engine pointer

Added a 3rd worked card to `rf-leaf-having` ("Qualify on thresholds across distinct rows (GROUP BY + HAVING)", badge 2 → **3**): "Loyalty Members Meeting Multi-Month Spending Thresholds" (Easy) — member qualifies only if points >= 500 in BOTH January AND February; two conditional SUMs ANDed in HAVING, the slice column kept OUT of GROUP BY. Trinidad's verbatim SQL preserved; explanation in the `/* */` block. DuckDB-verified (101, 103). Also fixed an engine gap: `filter_strategies` subtype `group_threshold` existed in SUBTYPES + guidance but had NO `playbook_pointer` entry; added `("filter_strategies","group_threshold") -> ("rf-leaf-having", …)` so nb04 Study links land. Balance **div 6547/6547**, depth 0, svg 2/2, details 76/76.

## SESSION 2026-06-21 (later 4) — itree "← Back one step" button

Added a "← Back one step" button to `renderITree` (in `build_itree_examples.py`) that pops the last path entry, shown left of "Start over" whenever `path.length`. Reuses the `.itree-reset` class (no new CSS) with a 16px right margin. Applies to ALL 25 trees since the renderer is shared. Rebuilt; balance **div 6535/6535**, renderITree once.

## SESSION 2026-06-21 (later 3) — ej-decide questions reworded to be OUTPUT-driven (Trinidad navigates by expected output)

Trinidad navigates the tree by reading the expected output, and found the prior phrasings too abstract. Reworded all four `ej-decide` questions to lead with a concrete output EXAMPLE, with a plain `sub` line giving the output-shape rule (her chosen blend of two proposed styles). Final `q` text: self-join "Output like (employee, their manager) or (player, who they beat) — two rows from the SAME table paired up?"; cross join "Output like every (store, month) pair with 0 where nothing sold — one row per combination, empties included?"; per-group "Output like each sale with its store's average beside it — same rows as the detail, plus a group number column?"; compound "Output like the few customers who bought ALL categories — one row per entity that cleared multiple conditions?" (sub keeps the anti-join note). Routing and leaf anchors unchanged. Rebuilt; balance **div 6535/6535**. NOTE for future tree edits: keep this output-example-first voice.

## SESSION 2026-06-21 (later 2) — Look Up Columns leaves got their per-method template cards

Each `enrich-join` leaf was missing the top-of-leaf "Copy-paste skeleton" template card that every `enrich-aggregate` leaf has (`ea-tmpl-*`). Added one to all five: `ej-tmpl-lookup`, `ej-tmpl-selfjoin`, `ej-tmpl-cross`, `ej-tmpl-pergroup`, `ej-tmpl-compound` — same format (collapsed `problem-card`, "(back to tree)" link to `#ej-decide`, "What this template does, step by step" `<ol>`, dark code skeleton). Skeletons mirror the itree CODE for each leaf; the compound one is the threshold + LEFT-JOIN-count + WHERE NOT EXISTS anti-join shape. Inserted as the first child of each leaf's `problem-card-content`. Balance **div 6535/6535**, depth 0, svg 2/2, renderITree once, details 76/76.

## SESSION 2026-06-21 (later) — Look Up Columns › Compound eligibility: anti-join recency card + new engine subtype

**Playbook (`enrich-join` › `ej-leaf-compound`).** Added a 3rd worked card "High-Value Members Without Recent Activity" (Medium, badge 2 → **3**): balance >= 500 AND never redeemed on/after a cutoff, with a count of ALL redemptions. Teaches the trap Trinidad hit — the recency rule EXCLUDES the whole member so it is a `NOT EXISTS` anti-join in WHERE, NOT a date in the counting join's ON; the count join is a plain LEFT JOIN on the key only. Card notes the equivalent `HAVING COUNT(CASE WHEN date >= cutoff THEN 1 END) = 0` single-join form. DuckDB-verified (Bob excluded, Eva kept at 0). Refreshed the `ej-leaf-compound` itree CODE+EX to the anti-join shape and added a `sub` clarifier on the `ej-decide` compound branch naming the "AND never did B / not active in a recent window" case. Rebuilt trees; balance **div 6515/6515**.

**Engine (`sql_practice_utils.py`).** New `enrich_join` subtype **`threshold_no_recent`** ("Threshold AND not active in a recent window (anti-join)") added to SUBTYPES + `_ej_opts` rotation + an `_EJ` PIN that forbids putting the recency date in the join ON, pins LEFT-JOIN-count + WHERE NOT EXISTS (HAVING-conditional-count accepted), and requires the four discriminating test rows (recent-active excluded, zero-child count 0, old-only kept, below-threshold excluded). `playbook_pointer("enrich_join","threshold_no_recent")` → `ej-leaf-compound`. Verified: engine imports (38 qtypes), PIN fires, random rotation reaches it ~14%. Reload nb01 / restart kernel to pick it up.

## SESSION 2026-06-21 — Gated Lookup CASE leaf split by CASE position + gate type; new conditional-count card; gl itree deepened

**Playbook (`gated-lookup` › `gl-leaf-case`).** Renamed the leaf "CASE and the aggregate" (badge 14 → **15**) and split it into nested sub-containers: **`gl-case-around`** "CASE around the aggregate" (14) holding the moved `gl-tmpl-case` template + two gate sub-leaves — **`gl-case-around-threshold`** "Numeric threshold gate" (10) and **`gl-case-around-flag`** "Boolean / status flag gate" (4) — plus **`gl-case-inside`** "CASE inside the aggregate" (1) with a new `gl-tmpl-case-inside` template. All 14 existing cards moved VERBATIM (depth-aware extract); classification by gate operator (`>=`/number vs flag/`= 'status'`). Outer `gl-leaf-case` id preserved (deep links + `playbook_pointer` still land).

**New worked card** in `gl-case-inside`: "Count High-Value Results by Kit Type" (Easy) — Trinidad's solve, `SUM(CASE WHEN r.price_paid > 75 THEN 1 ELSE 0 END)` over a LEFT JOIN so empty kit types land on 0 with no COALESCE. DuckDB-verified against the 4 expected rows. Card + inside template note: same result as filtering in the JOIN ON then `COUNT` (`gl-leaf-onclause`); engine-wise it is a `left_join_on_filter` / `numeric_threshold` shape, grouped here as a CASE-and-aggregate contrast at Trinidad's request.

**gl itree (hand-authored inline in `build_itree_examples.py`).** Replaced the old "only which users qualify vs also filters which rows" question with: Q "Where does the gate live — entity or fact rows?" → entity → Q "number comparison vs yes/no flag" → `gl-case-around-threshold` / `gl-case-around-flag`; fact-rows → Q "filter in JOIN ON + COUNT vs SUM(CASE) inside" → `gl-leaf-onclause` / `gl-case-inside`. Added CODE + EX for the 3 new anchors in `itree_content.py`. Rebuilt via `build_itree_examples.py` (25 trees, 114 leaves). Balance after: **div 6503/6503, depth 0, svg 2/2, renderITree once, details 76/76**.

The project was renamed `sql_practice_generator` → `data_analyst_interview_prep`; the engine now lives at `folders/ds_blogs/projects/data_analyst_interview_prep/notebooks/sql_practice_utils.py`. The playbook stays at `folders/sql/sql_problem_patterns.html` (backups purged 2026-06-18 — only the live file remains in `folders/sql/`). Note: `context.md` calls `pharmacy_problem_patterns.html` the companion blog, but the file actively reorganized below is the separate `sql_problem_patterns.html`.

## SESSION 2026-06-19 — Multi-Table Join-Then-Aggregate recipe finished; anti-join + pattern-matching leaves nested by method; frame-clause leaf built out; nb01 window subtypes added

**Procedures › Functions rebuilt to new standard + many engine subtypes added (latest 2026-06-19).**
- **Playbook:** Procedures › Functions (`topic-functions`) now opens with a `fn-decide` flowchart (RETURNS scalar vs RETURNS TABLE) over the two leaves. ALL 17 worked cards converted to two-container Problem+Solution format: `function-wrapped-scalar` (9) + `function-wrapped` (8). Because `CREATE FUNCTION` can't run in DuckDB, each card's INNER query was DuckDB-verified against fabricated data (literal params; CURRENT_DATE cards use a fixed cutoff in the example) and the verified result IS the expected output; the Solution card shows the full CREATE FUNCTION + trailing call. Build scripts: `build_fn_scalar.py`, `build_fn_table.py` (read `scalar_cards.json`/`table_cards.json` for the original SQL). Also converted: 3 Reshape Cross-Join worked cards (`build_crossjoin.py`) and added 3 Pivot leaves `pv-leaf-signed/membership/threshold` (`build_pivot_leaves.py`) so the playbook Pivot recipe mirrors the generator's 4 flavors. Global div balance 6150/6150.
- **Engine (`sql_practice_utils.py`) NEW qtypes/subtypes this session:** `point_in_time` (asof_single/default_no_history/fill_forward), `delete_duplicates` (keep_min_id/self_join/row_number, DELETE-path), `enrich_join` (straight_lookup/self_join/cross_join/per_group/compound), `unpivot` subtypes (drop/keep/aggregate), `pivot` SUBTYPES wired to in-pivot leaves, `window_top_n_per_group` subtypes, `window_lag_lead` re-cut to the 4 row-compare strategies. `_meta` now also records `pivot_flavor` (was missing → nb01 showed "no subtypes" for pivot). `playbook_pointer` maps every qtype+subtype to its leaf anchor; the generic Random pre-pick records the chosen subtype. **nb01 Format button now uses `sqlglot`** (dialect-aware) instead of sqlparse — run `pip install sqlglot`. Reminder: reload nb01 / restart kernel after engine edits.

**ALL decision trees converted to SVG flowcharts (later 2026-06-19).** Trinidad wanted every "How to pick" decision tree to be a scannable diagram, not a text/`dt-flow` wall. Reusable generator in the outputs scratchpad: `flowchart.py` (`flowchart_flat(qlines, branches, note)` → one question node on the left, fan of clickable green result boxes [title + ≤6-word criterion] on the right, optional amber cross-link note; `replace_decide(text, id, svg, new_excerpt)` swaps a decide card's content). Drivers: `gi_diagram.py` (the first, gi-decide, a true cascade with edge labels), `build_flowcharts.py` (17 flat trees: rf/ag/sc/tx/nb/dd/ej/ea/fj/gl/ml/rp-multi/un/pv/up/sg/pit), `build_flowcharts2.py` (rp/tw/gbc, which used non-dt-flow formats). 21 `*-decide` cards now hold an SVG (22 `<svg>` total incl. gi); every excerpt set to "Follow the arrows — tap a green box to jump to that method." Result boxes link to leaf/template anchors via `#id` (the deep-link handler added earlier expands the target). Audited: all 21 have an SVG, zero leftover `dt-flow`/`<ol>`/`Q1.` text, every `href="#…"` resolves; global div 6013/6013. New leaf id added: `gi-leaf-adjacency` (so the gaps-and-islands adjacency shortcut is linkable). To re-edit a chart, change the spec in the driver and re-run (it re-reads and re-splices by id).

**Dedup container cleanup + new `delete_duplicates` qtype (later 2026-06-19).**
- **Playbook `delete-duplicates`:** removed the orange "Filter Rows vs Remove Duplicates" callout; folded its message into `dd-decide` as a leading "First: is this really a DELETE?" note (purple). Leaves unchanged (`dd-leaf-minid` / `dd-leaf-selfjoin` / `dd-leaf-rownumber`). Balance div 6072/6072.
- **Engine new qtype `delete_duplicates`** (label "Dedup (delete duplicate rows)", pg+mysql) with method SUBTYPES `keep_min_id` / `self_join` / `row_number`. It is a DELETE-family qtype: `generate_problem` sets `dml_op="DELETE"` but routes to its OWN guidance branch (`qtype_for_guidance="delete_duplicates"`), so the prompt pins the method while the answer_key stays a DELETE + trailing SELECT (validation is generic — it just runs the answer and compares the trailing SELECT, so no extra validation wiring was needed; `dml_op` only feeds the prompt + `_meta`). Auto-appears in the nb01 Type dropdown and random_any pool. `playbook_pointer` maps it to `delete-duplicates` and each subtype to its `dd-leaf-*` anchor. NOTE: this overlaps with `dml_delete` → `duplicate_rows` (the generic DML delete still exists); `delete_duplicates` is the focused single-table Dedup recipe matching the playbook. Reminder: reload nb01 / restart kernel.

**Point in Time recipe built out (Single-Table) + new `point_in_time` qtype (later 2026-06-19).**
- **Playbook `point-in-time`:** was a placeholder (intro + Pattern card + an orange "where to find / future pass" callout + one template). Removed the orange callout; kept the intro + "As-of lookup with fill forward" Pattern card; added a `pit-decide` decision tree + 3 leaves, each a Template + ONE DuckDB-verified worked problem: `pit-leaf-asof` (As of a single cutoff — reuses the existing `tw-tmpl-pit` template + "Product Price as of a Cutoff Date"), `pit-leaf-default` (Default when no history — `pit-tmpl-default` + "Subscription Plan as of a Cutoff, Default When New"), `pit-leaf-fill` (Fill forward over a date spine — `pit-tmpl-fill` + "Daily Effective Price"). Badge "cross-linked" → "3 problems". Built via `build_pit.py` (scratchpad) using `eabuild`. Global balance div 6073/6073, details 96/96, depth 0; recipe has 3 Problem + 3 Solution badges.
- **Engine new qtype `point_in_time`** (postgres + mysql) with SUBTYPES `asof_single` / `default_no_history` / `fill_forward`, a guidance base + per-subtype PIN (asof/default recipe `rank-partition`, fill_forward recipe `time-window`; fill_forward note: generate_series in Postgres, recursive CTE spine in MySQL). Auto-appears in the nb01 Type dropdown (populated from QUESTION_TYPES) and the random_any pool. `playbook_pointer` maps the qtype to `point-in-time` and each subtype to its `pit-leaf-*` anchor. All 3 worked solutions DuckDB-verified before insertion. Reminder: reload nb01 / restart kernel.

**Compare container restructure (Single-Table) + window_lag_lead subtypes re-cut (later 2026-06-19).**
- **Playbook `row-compare`:** removed the orange "Not the same as a self-join lookup" callout. In the "Compare to the previous or next row" leaf, deleted the 3 standalone reference tables (`rc-table-1/2/3`); kept ONLY the decision tree. Each Table's per-method content (core snippet + edge/NULL handling + key pitfall + trace) is now folded into a per-pattern **Template** card placed at the top of each of the 4 strategy containers, which gained ids: `rc-leaf-neighbor-value`, `rc-leaf-gap-delta`, `rc-leaf-fixed-run`, `rc-leaf-pair-role`. Built via `build_compare_restructure.py` (scratchpad); div 6032/6032, depth 0. Templates verified positioned id < template < worked-card in every leaf.
- **Engine `window_lag_lead` re-cut to mirror that leaf 1:1 (user chose "replace subtypes").** SUBTYPES are now `neighbour_value` / `gap_delta` / `fixed_run` / `pair_by_role` (was lag/lead/both). Guidance base rewritten to "compare to previous/next row" (recipe `row-compare`) with a strong PIN per subtype (pair_by_role pins self-join / MAX(CASE), NOT LAG/LEAD). Label/description updated to "Compare to previous / next row". `playbook_pointer` for `window_lag_lead` now points to `row-compare` and each subtype to its `rc-leaf-*` anchor. Random rotates through all 4 (verified) and the chosen subtype is recorded in `_meta` via the generic pre-pick. Reminder: reload nb01 / restart kernel.
- **Deep-link handler** was added to the playbook earlier this session so external `#rc-leaf-*` links open the Single-Table tab and expand the leaf.
- **Gaps-and-Islands restructure DONE (same pattern).** Kept `gi-decide` only; deleted `gi-table-1/2/3` and the `gi-templates` wrapper. Each `gi-tmpl-*` card was MOVED into its matching strategy container (ids preserved: `gi-tmpl-int/date-nogap/date-gap/entity` still resolve) and AUGMENTED with that shape's GROUP BY + key pitfall (from Table 2) and trace (from Table 3). Strategy containers gained ids: `gi-leaf-int`, `gi-leaf-date-nogap`, `gi-leaf-date-gap`, `gi-leaf-entity` (the "Adjacency & gap checks" leaf has no template, left as is). Built via `build_gi_restructure.py`. Both decision-tree "Every leaf maps to the same three tables …" sentences (Compare + Gaps-and-Islands) were rewritten to point at the per-leaf Template cards — zero dangling `#rc-table-*` / `#gi-table-*` / `#gi-templates` links remain. Global balance div 6016/6016, details 96/96, depth 0. Generation already works via the `union_islands` qtype (subtypes date_calendar / date_sequence / integer_seq / partitioned_status_periods / consecutive_day_streak_per_entity); those subtypes are now ALSO mapped in `playbook_pointer` to the new `gi-leaf-*` anchors so the nb04 "Study" links land on the exact shape leaf.

**NEW anti-join recipe card + Random-subtype display + error tracking (later 2026-06-19).**
- **Playbook:** added a 6th card to Single-Table › Filter › Anti-join › `rf-antijoin-notexists`: "Find Episodes Never Completed by Any User" (badge 5→6). Teaches the gated NOT EXISTS — "never completed" = no `completed = true` row exists, one correlated NOT EXISTS covers partial-only / NULL-flag / no-sessions at once, and it is NULL-safe where `NOT IN` would break. Built with the shared `eabuild.py` (DuckDB-verified, div 6029/6029, details 96/96). The learner's working two-branch `OR` version is correct but the single NOT EXISTS is the canonical answer.
- **Engine display fix:** `generate_problem` now, when `subtype is None` and the qtype has a `SUBTYPES` menu (excluding the flavor qtypes union_islands/percentile_metrics/pivot, which already record their own flavor), does `subtype = random.choice(...)` BEFORE the guidance call, so the actual subtype is pinned AND recorded in `_meta["subtype"]`. Scenario was already recorded in `_meta["scenario"]`. `effective_subtype(meta)` helper reads subtype-or-flavor.
- **nb01:** the generate step now prints **Type / Subtype / Scenario** (cell 3, after `STATE['problem']=problem`), flagging "🎲 Random picked this" when the learner left Subtype/Scenario on Random. Resolved meta-qtypes show `original → resolved`.
- **Error tracking (item 3):** on a failed Submit (BOTH a thrown SQL error AND a wrong answer on the hidden test), nb01 cell 7 calls `spu.log_error(...)`, which writes one JSON per failure to `data/outputs/errors/` (new `ERRORS_DIR`, added to cell 1's dir loop). Each record captures the full problem context INCLUDING `answer_key` (the correct solution), the submitted SQL, and either the error message or your-columns/your-rows vs `test_expected_*`. Filenames carry microseconds + a uuid suffix so rapid re-submits never collide (this was a real bug found in testing). Engine helpers: `log_error`, `load_errors(qtype/subtype/failure_kind filters)`, `summarize_errors` (by_type / by_pattern / by_kind DataFrames), `recommend_practice` (ranks type+subtype by failure count). **New notebook `nb04_sql_error_review.ipynb`:** filter dropdowns (type / subtype / kind) + "Show overview" button → most-failed patterns, recommended practice order, and per-error cards (your SQL, your-vs-expected or the error, and the correct answer_key side by side); plus an optional "Analyze with Claude" button that summarizes the recurring KINDS of mistakes (NULL handling, grain, join, filter, ordering) via `spu._call_claude`. Build/edit scripts in the outputs scratchpad: `build_gl_episodes.py`, `fix_episodes_placement.py`, `edit_nb01_display.py`, `edit_nb01_logging.py`, `build_nb04.py`. Suggested learning loop: drill the top-ranked failing type+subtype, re-generate that exact subtype in nb01, and watch the failure count fall.
- **Playbook pointers (later 2026-06-19).** Engine gained `playbook_pointer(qtype, subtype)` → `{tab, anchor, label}` mapping every qtype/subtype to its home in `sql_problem_patterns.html` (maps `_PB_QTYPE` + `_PB_SUBTYPE`, mirroring the engine↔playbook 1:1 design). `recommend_practice` now annotates each row with its `playbook` pointer. nb04 renders a breadcrumb (Tab › Recipe › Leaf) + a clickable `file://…#anchor` deep link in the recommendations AND on every error card ("Study: …"), and feeds each failure's `playbook_location` into the Claude prompt so its plan names where to study. nb04 finds the playbook by walking up from PROJECT_ROOT looking for `sql/sql_problem_patterns.html` (falls back to breadcrumb-only text if not found). **Playbook got a deep-link handler:** a `DOMContentLoaded` listener reads `location.hash`, activates the target's tab, un-collapses the target AND all collapsed ancestors, and scrolls — so external `#leaf-id` links actually reveal deep leaves (plain `jumpToRecipe` only un-collapsed the target itself). Honest note recorded in nb04: with a personal error log, frequency counts + Claude's qualitative read are the right tools; a trained ML model would need far more data and would not beat counting which patterns are missed most.

**RECIPE-CARD REFACTOR — Multi-Table → Gated Lookup (`gated-lookup`) COMPLETE (16/16).** Converted all worked cards in the three leaves to the two-container Problem+Solution format, all DuckDB-verified against fabricated compact datasets (4–8 rows each): `gl-leaf-case` (14, CASE-around-aggregate), `gl-leaf-onclause` (1, gate-on-A + B-row-filter both in JOIN ON), `gl-leaf-rownumber` (1, ROW_NUMBER + rn=1). The recipe now has 16 Problem + 16 Solution badges, 16 Copy buttons, and zero `solution-container` markers. Rich cards (Match Eligibility, Squad Invite, Reimbursement Cap, Gig Worker Earliest Bid) kept their teaching content folded into the leading `/* */` comment (multi-solution / why-CASE-fails / MIN-vs-earliest distinctions). Templates and the decision tree (`gl-decide`, `gl-tmpl-*`) were left alone. Build scripts in the outputs scratchpad: `build_gl_case.py` (14) + `build_gl_misc.py` (2), using the recreated shared `eabuild.py`. DuckDB note: pass decimals/money as numeric STRINGS in the card dict so the displayed table keeps trailing zeros (e.g. `'32.50'`) while `_norm` still compares them numerically; `players.rank` works unquoted as a column in DuckDB. Balance after: div 6017/6017, details 96/96, final depth 0. **Two pre-existing `LeetCode` references remain OUTSIDE Gated Lookup** (a "View on LeetCode" link in the Matchup/Leaderboard tournament card, and a grader note in another recipe) — left untouched as out-of-scope; rename when those sections are converted.

**RECIPE-CARD REFACTOR — Multi-Table → Join Tables Then Aggregate (`enrich-aggregate`) COMPLETE (48/48).** Converted the final 37 worked cards to the two-container Problem+Solution format, all DuckDB-verified against fabricated compact datasets, across the leaves: SUM/AVG (13), Rate/ratio/percentage (5), Aggregate+filter HAVING/CASE (13), Date-window/cohort (3), set-membership (1), LEFT-JOIN-filter-in-ON (2). The recipe now has exactly 48 Problem + 48 Solution badges and zero old-format markers. Two practice-platform brand names removed: "Leetcodify Friends Recommendations" → "Friend Recommendations by Shared Listens", "Leetcodify Similar Friends" → "Similar Friends by Shared Listens". Build scripts live in the outputs scratchpad (`build_ea_*.py`) using the shared `eabuild.py` (`build_card`, `verify` with `check_sql` for DELETE, `find_block`, `run`). DuckDB gotcha logged: `generate_series(a,b)` in a SELECT returns a LIST; use it as a table function `FROM generate_series(1,12) AS m(m)` for scalar rows. `~` regex operator is Postgres-only — verify regex cards with `regexp_matches()` in DuckDB while displaying the `~` form.

**SINGLE-TABLE → Filter → Anti-join leaf (`rf-leaf-antijoin`) restructured into method sub-containers.** Now: a root "Which anti-join method?" decision tree + three nested qtype-groups — `rf-antijoin-notexists` (NOT EXISTS, 5 cards), `rf-antijoin-leftnull` (LEFT JOIN … IS NULL, 3), `rf-antijoin-notin` (NOT IN, 3). Each holds its own method template; the decision-tree branches link to the containers. Cards were filed by their PRIMARY EXECUTED statement (comment-only mentions of other methods ignored). Two cards recoded so the container holds only real anti-join code: "Drop Type 1 Orders for Customers With Type 0 Orders" (flag+branch → `OR NOT EXISTS`), "Employees Whose Manager Left the Company" (`NOT IN` → correlated `NOT EXISTS`). New card added: "Students Who Never Improved Their Grades" (positive EXISTS + negative NOT EXISTS; the user's `ON`-inside-subquery error → correlation goes in WHERE). Outer leaf count left at 11 (= 5+3+3) at the user's request.

**SINGLE-TABLE → Filter → Pattern-matching leaf (`rf-leaf-pattern`) restructured.** Root "LIKE or regex?" decision tree (replaced the old root template) + two containers: `rf-pattern-like` (LIKE/ILIKE, 1 card, template covers `%` `_` ILIKE ESCAPE) and `rf-pattern-regex` (3 cards) which itself nests a "Which regex job?" decision tree + `rf-pattern-regex-validate` (anchored `^…$` format match: Valid E-Mails + new "Find SKUs with Size Variant Codes", regex `_[A-Z]{2}$`) and `rf-pattern-regex-extract` (word-boundary/count: Count Occurrences). All three existing cards were already two-container; only refiled. Outer badge updated 3→4.

**SINGLE-TABLE → Window → Frame-clauses leaf (`window_frames`) built out from an empty placeholder.** Now a "ROWS or RANGE?" decision tree + `tw-leaf-frame-rows` (ROWS BETWEEN, template `tw-tmpl-frame-rows`) + `tw-leaf-frame-range` (RANGE BETWEEN, template `tw-tmpl-frame-range`). Templates only for now (sample code + step list); worked recipes to be added later. Decision branches link to the two sub-containers.

**NEW DELETE card.** "Delete High-Churn Client Trade Alerts" added to the `dml-single-delete` → Conditional-delete leaf (badge "template only" → "1 problem"), two-container format, DuckDB-verified (DELETE + trailing SELECT leaves 5 rows). Two conditions: plain `status='pending'` AND a `client_id IN (… GROUP BY … HAVING COUNT(*)>=5)` volume subquery; comment notes the subquery sees the pre-delete table state.

**ENGINE (`sql_practice_utils.py`) — three window qtypes gained subtypes (no notebook edit needed; cell-3 dropdown auto-populates from `SUBTYPES` and already prepends 🎲 Random=None).**
- `window_lag_lead`: `lag` / `lead` / `both` — pins the answer to LAG-only, LEAD-only, or both-neighbors (with the matching NULL-edge note).
- `window_sessionization`: `one_per_session` / `one_per_person` / `one_per_event` — mirrors the playbook's three sessionization output-shape containers (roll up per session; second GROUP BY per person; label each event, no final GROUP BY).
- `window_frames`: `rows_between` / `range_between` — pins the frame family.
- `window_top_n_per_group` (added later 2026-06-19): `top1_by_value` / `top1_by_date` / `topn` / `nth` / `special` — mirrors the playbook's Multi-Table › Rank Within Groups to Select Top-N leaves 1:1 (`rp-multi-top1-by-value` / `-by-date` / `-topn` / `-nth` / `-special`). Before this, `window_top_n_per_group` was the one rank/top-n qtype with NO `SUBTYPES` entry, so it could not be pinned to a leaf. `special` is kept HERE on purpose (median / threshold-from-rank / rank deltas / asc-desc exclusion all use rank-within-group); blank/Random now rotates through all five, verified, so the special shape DOES get generated. Note `percentile_metrics` also maps `recipe = rank-partition` and separately covers median / extreme-exclusion via its own subtypes — overlap is intentional.
- Pattern: each block appends a `subtype if subtype in (...) else random.choice([...])` PIN after the base guidance, so blank/Random rotates among the subtype options. Plumbing confirmed: `generate_problem(subtype=…)` → `_topic_specific_guidance(subtype=…)` (line ~4128); for window qtypes `subtype` passes straight through (no remap, unlike union_islands/percentile_metrics/pivot). Reload notebook / restart kernel to reimport.

**STATUS — recipe-card refactor.** Single-Table tab FULLY converted; Multi-Table `enrich-aggregate` and `gated-lookup` converted. Remaining old-format worked cards = **85** (proxy: `class="solution-container"` count): Multi-Table 18 (rank-partition multi 17, Matchup&Leaderboard 1), Reshape 27 (Series Generation `sg-leaf-*` 11, Unpivot `up-leaf-*` 7, Pivot `pv-leaf-*` 6, Union `un-leaf-*` 3), Procedures 40 (Functions `topic-functions` 17, INSERT 14, UPDATE 4, DELETE 4, Recursive 1). 259 cards already converted; div/details balance clean (6017/6017 div, 96/96 details). **NEXT: Multi-Table rank-partition multi (`rp-multi-*`, 17) or Reshape leaves — user's call.**

## SESSION 2026-06-18 — Procedures tab consolidated (Procedural Blocks removed), Series Generation subtypes wired, scalar_extract qtype, Period Overlap recipe variant, backups purged

**PLAYBOOK (`sql_problem_patterns.html`).**
- **Procedures tab streamlined to 4 topics** (was 5). Deleted the intro paragraph and the two standalone top-level reference cards (Quick Code Scaffolds + Procedural Problem Types index). Dropped the "Select Analytical" qtype card and the cross-technique "Quick decision guide" table (Trinidad's call). Scaffolds + qtype shape cards were nested INTO each technique container as a single steel-blue "Reference" card so no reference info sits outside it. `.qtype-card` styles lifted to the top of the tab.
- **Procedural Blocks container deleted entirely**, folded into **Updates, Deletes, and Inserts** (`topic-dml`): the DO sequential + DO row-by-row scaffolds, the DO Block shape card, and the FOR LOOP vs set-based decision callout now live INSIDE the DML Reference card; the 3 recipes (Simple Sequential UPDATEs, Row-by-Row State Mutation, Process Story View Events) are now DML recipes. Decision Tree "Procedures" source dropped to 4 shapes; DO-block tech cards merged into the Updates/Deletes/Inserts shape; source count 5→4. No dangling `topic-procedural-blocks` refs remain.
- **Series Generation → `sg-leaf-overlap` (Period overlap) recipe** gained a 2nd solution: Trinidad's working variant that folds the CROSS JOIN into the `month_spine` CTE and uses the prompt's real columns (`created_date` / `closed_date`). Added a plain-language "what each LEFT JOIN line does and how it moves COUNT" section. Logic-verified against the 12 expected rows. NOTE: canonical solution 1 still uses `stage_created_date` / `stage_won_date`; the variant uses `created_date` / `closed_date`.

**ENGINE (`sql_practice_utils.py`) — 32 → 33 qtypes + series_generation subtypes.**
- NEW qtype `scalar_extract` (fills the LIMIT/OFFSET gap): 4 subtypes (`single_aggregate`, `top1`, `nth`, `ratio`) mirroring the Single-Table Scalar leaves. Centers the LIMIT/OFFSET shape and the WHERE-returns-0-rows-not-NULL trap (Nth via subquery-in-SELECT). 3-edit recipe + SUBTYPES entry; classification.recipe = `scalar-extract`.
- `series_generation` now has **6 SUBTYPES matching the playbook leaves exactly**: `full_date_spine` (SHAPE A), `bounds_from_data` (SHAPE D), `filtered_entities` (SHAPE A filtered-DISTINCT variant), `categorical_label_spine` (SHAPE E), `lateral_range_expansion` (SHAPE C), `period_overlap` (SHAPE F). Picking a subtype PINS the generation to that shape (override appended after the difficulty-based `shape_hint` rotation, just before `base +=`). Scenario (industry) + difficulty still apply on top — difficulty scales complexity, not shape. No subtype → rotates as before. The nb01 cell-3 Subtype dropdown auto-populates from `SUBTYPES`, so no notebook edit was needed.
- Same-day earlier: gated_lookup subtypes confirmed 1:1 with its 5 method leaves.

**HOUSEKEEPING.** Deleted 32 `sql_problem_patterns_backup*.html` snapshots (~77 MB) from `folders/sql/`; only the live file remains. The save-before-edit auto-backup produced them — consider disabling/redirecting it. Deleting in the mounted folder needs `mcp__cowork__allow_cowork_file_delete` first (sandbox blocks `rm`).

**NEW RECIPE-CARD FORMAT (2026-06-18) — Trinidad approved; rolling out to ALL recipes.** Each worked recipe card becomes a collapsed `problem-card` (difficulty badge + title) containing EXACTLY TWO nested collapsed cards:
1. **Problem** card — steel-blue `#2c5f8a` "Problem" badge, title "Case study &amp; test data". Holds the full case study like the nb01 notebook view: **Prompt** (bullets), **Schema** (one table per input, Column/Type rows), **Example input** (data table per input), **Expected output** (data table). Plain tables: `border-collapse:collapse; font-size:1.2rem`, header row `border-bottom:2px solid #cbd5e1`, zebra `background:#f7f9fb` on alt rows. This REPLACES the old top-level Tables line / Decision Tree Path / Real-World Example / trace tables.
2. **Solution** card — green `#2e7d32` "Solution" badge, title "Annotated SQL", with a `.tpl-copy` Copy button in the header. Holds ONE `<pre><code>` block: a leading `/* ... */` comment that explains the key lines + a "Verified against the example data" line, THEN the SQL with inline `--` comments on the working lines. (No separate bulleted "Key lines" section — it lives inside the `/* */`.)

Approach decided by Trinidad: **fabricate compact DuckDB-verified test data** for every card that lacks it; roll out **tab by tab** (Single-Table → Multi-Table → Reshape → Procedures). Reusable card builder pattern: a Python `card(diff,color,title,excerpt,prompt_lis,schema_name,schema_cols,in_name,in_head,in_rows,exp_head,exp_rows,sol_code)` helper emits the two-container HTML; tables use the plain style above; `esc()` HTML-escapes the code. Build data → verify in DuckDB → replace the old card block (balanced-div extract) → check div/details balance.

**PROGRESS (2026-06-18):** In the Single-Table → Window (time-window) container, 3 leaves FULLY converted (all cards DuckDB-verified):
- "Running total / cumulative aggregate" (5/5): Cumulative Completed Visits by Provider, Running Total for Different Genders, Account Balance, Last Person to Fit in the Bus, Cumulative Minutes Listened Per User.
- "Group benchmark compare" (2/2): both "Couriers Faster Than Zone Average" cards (no-ORDER-BY form + explicit-frame form).
- "LAG / LEAD comparison" (3/3): Month-over-Month Revenue Growth by Region, Days Between Consecutive Logins per User, Detect Subscription Status Changes.
REMAINING in Window container: "Sliding window aggregate (rolling N days)" (7 cards), "FIRST_VALUE / LAST_VALUE" (2), "Sessionization (gap based grouping)" (~5, nested by output-shape — careful). Then the rest of Single-Table (Filter, Aggregate, Scalar, Rank&Percentile, Transform, Compare, Pair, Dedup), then Multi-Table, Reshape, Procedures. ~190 cards remain — multi-session. Builder + DuckDB-verify recipe is proven; templates and "How to pick" cards are NOT converted (only worked cards with difficulty badges). Data sourcing for cards that lack example input/expected output: fabricate compact DuckDB-verified datasets (preferred — the Problem card needs real tables to be useful) vs carry over only what the card already has. Work leaf-by-leaf, verify each (`<div>`/`<details>` balance + DuckDB-check the solution against the fabricated data). This is a multi-batch / multi-session effort given ~224 cards.

**Decision Tree — Reshape source rebuilt to the Procedures row-wise pattern + jump links fixed (2026-06-18).** The Reshape source (`dt-union`) was a single "Reshape" shape with a flat 7-card grid and a broken custom "Open Reshape Recipes tab" button (raw inline JS, not `jumpToRecipe`). Replaced with THREE expandable subtopic rows like Procedures: **Stacking tables** (UNION, UNION ALL → `reshape-union`), **Pivot / Unpivot** (Pivot → `reshape-pivot`, Unpivot → `reshape-unpivot`), **Generate rows (spine, skeleton, combos)** (Calendar/skeleton CTE + CROSS JOIN combos → `reshape-cross-join`, Series Generation spine → `reshape-series-generation`). Each row's CTA + tech cards use `jumpToRecipe(id)` (the proven path: switches tab via `[data-tab]`, un-collapses the target card, scrolls). Audited ALL decision-tree `jumpToRecipe` targets across every source — all resolve to existing ids. `jumpToRecipe` is the canonical cross-tab jump; do NOT hand-roll tab-switch JS in buttons.

**Diagnostic Process tab streamlined (7 → 4 top-level containers).** Merged the two six-step walkthroughs (brief "The Six Steps" + detailed "Step-by-Step Reference") into ONE **"The Six Steps"** Process card — kept the detailed version's content + the #1193 Monthly Transactions I worked example + the PROBLEM-rewrite pre-step + the 14 category IDs + elimination sentences + failure-mode table, and folded in the brief version's unique bits (Step 2 self-join shapes → enrich-join; Step 4 Decision-Tree-tab two-tap navigation; Step 5 recipe-card contents). Nested the three Step 3–4 lookups (Single Table Shape Comparison, Multi Table Shape Comparison, Signal Words → Shape) under one **"Identify the Shape"** Reference card (their individual badges removed). Kept the **Copy-Paste Diagnostic Starter** (Template badge) and **SQL Execution Order** (Reference). Standardized: all Reference badges → steel-blue `#2c5f8a` (was a mix of purple `#6a1b9a` / blue `#1565c0`); stripped the inner step cards' colored left-borders for a calm white-card look; Process badge stays gray `#455a64`, Template badge unchanged. Final order: Six Steps → Identify the Shape → Copy-Paste Starter → SQL Execution Order.

## SESSION 2026-06-16 — Single-Table tab reorganized into technique leaves + templates everywhere + sessionization rebuilt by output shape

**TONE / FEEDBACK (hardened this session — honor it).** Trinidad wants drills picked by reading the **expected output columns**, then matching a template. Hard rules: distilled, lay language, NO jargon, NO walls of text, NO invented metaphors. Two terms she explicitly banned mid-session: "engine" (for the LAG → flag → running-total setup) and "Strategy 1 + 4" style numbering — both removed from the sessionization section. CTE names must be self-documenting (`add_previous_time`, `flag_new_session`, `assign_session_id`, `totals_per_session`), not `ordered`/`flagged`/`sessions`. Show the solution only when asked.

**ENGINE (`sql_practice_utils.py`) — 31 → 32 qtypes.**
- `left_join_on_filter` now ROTATES 6 shapes: A right-side date window, B status/category equality, C numeric threshold, **D left-filter-in-WHERE + right-filter-in-ON combo** (a LEFT-table filter goes in WHERE, a RIGHT-table filter goes in ON; biased ~30% on medium/hard via `force_shape_d`), E SUM/AVG with COALESCE, F boolean existence flag. `CODE_REFERENCE["left_join_on_filter"]` gained the both-sides (hire_date in WHERE) example.
- NEW qtype `window_benchmark_compare` — `AVG/MIN/MAX OVER (PARTITION BY group)` with **no ORDER BY** (whole-group benchmark on every row), then compare each row in the OUTER query; teaching points = the missing ORDER BY (else it's a cumulative running average, a different qtype) and the CTE-wrapper requirement (a window function can't sit in WHERE). Added to `_WINDOW_VARIANTS`; `window_random` label now "8 variants"; own `CODE_REFERENCE` skeleton ends with a 3-way contrast (whole-group vs cumulative vs rolling).
- `window_running_total` widened to rotate SUM / AVG / COUNT (was SUM-only). AVG here = cumulative/expanding average to date (NOT the rolling window, NOT the benchmark).
- Reminder: after any `.ipynb` OR engine edit, JupyterLab **File → Reload Notebook from Disk** before running.

**PLAYBOOK (`sql_problem_patterns.html`) — Single-Table tab fully reorganized.** Every recipe now: loose problems grouped into **technique/method leaves**, a **How-to-pick decision tree** card, a **reference table whose rows mirror the leaves** (each Pattern cell links to its leaf), and a **Template card at the top of every leaf**. Method for the regroups (reuse it): a depth-aware Python script extracts each top-level `problem-card` block by its `#NNN`, classifies via a fixed map, and rebuilds into leaf wrappers — cards moved VERBATIM. After every edit verify `<div>` open==close, `<details>` open==close, and min stack depth >= 0.
- **Filter** (`row-filter`) → 5 leaves: `rf-leaf-compare` (7), `rf-leaf-null` (1), `rf-leaf-pattern` (3), `rf-leaf-membership` (IN/EXISTS, 6), `rf-leaf-antijoin` (NOT IN/NOT EXISTS/never, 10) + `rf-decide` + reference. 27 problems.
- **Aggregate** (`group-aggregate`) → 6 leaves: `ag-leaf-count` (5), `ag-leaf-countdistinct` (6), `ag-leaf-sumavg` (6), `ag-leaf-having` (9), `ag-leaf-conditional` (7), `ag-leaf-ratio` (3) + `ag-decide` + reference. Badge corrected 35 → 36 (`#1612` and `#1205` are both titled "Monthly Transactions II" — likely a near-duplicate worth a look).
- **Scalar** (`scalar-extract`) → 4 leaves: `sc-leaf-aggregate` (3), `sc-leaf-nth` (2), `sc-leaf-top1` (2), `sc-leaf-ratio` (5) + `sc-decide` + reference. Kept the orange "WHERE returns 0 rows instead of NULL" callout. 12 problems.
- **Dedup** (`delete-duplicates`) → 3 method leaves: `dd-leaf-minid` (keep lowest id, NOT IN MIN; #196), `dd-leaf-selfjoin` (Remove Duplicate Pending Transactions), `dd-leaf-rownumber` (template only) + `dd-decide` + reference; kept the "is it really a DELETE" callout.
- **Templates distributed everywhere.** Filter/Aggregate/Scalar/Dedup leaves each got an authored Template card. **Window** method leaves received the skeletons moved out of the now-deleted generic `tw-templates` (ids `tw-tmpl-*` preserved so `tw-decide` links resolve). **Rank & Percentile** generic `rp-templates` distributed into `rp-leaf-*` (ids preserved) + new `rp-tmpl-median`; container deleted. **Pair** (`normalize-bidirectional`) `nb-templates` 3-row table distributed into `nb-leaf-pool`/`canon`/`matchup`; container deleted, `#nb-templates` link repointed.
- **Window LAG/LEAD leaf** filled with 3 DuckDB-verified worked cards: Month-over-Month Revenue Growth by Region, Days Between Consecutive Logins, Detect Subscription Status Changes (uses `IS DISTINCT FROM` for the NULL-first row).

**SESSIONIZATION — rebuilt by OUTPUT SHAPE (the model she wants for the rest of the playbook).** Inside Window → Sessionization:
- **"Start here" card** (`id="sess-start"`): (1) one question — new session from a gap since the previous event (normal) or a timeout from when the session started (harder, different)? (2) a table mapping expected-output columns to a container, framed by the one decider: **is `session_id` a column in the expected output?** (a session belongs to a person, so "one row per session" output always carries the person id too — `person_id + session_id + a number` is the common shape); (3) a "you never need a JOIN — LAG is your previous row" warning (she hit this exact bug). Plus a "decode the prompt" phrase→move table and a "what is the session key" line (partition by the one id that defines a session; ignore request/product ids).
- **THREE output-shape containers** (plain labels, NO strategy numbers), one per table row: **"One row per session"** (`sess-out-persession`, 3 cards: Group Article Views, Workout Session Detection, Sessionize Trades by 15-Minute Gaps — output `person_id + session_id + a number`); **"One row per person"** (`sess-out-perperson`, 2 cards: #2173 Longest Winning Streak, Sessionize Player Match Events — `person_id + a number`, no session_id); **"One row per event"** (`sess-out-perevent`, template only — every original row kept, labeled with a `session_id`, no GROUP BY). Order in the leaf: session, person, event.
- Each container opens with ONE plain template + swap-in notes: the metric swaps in the SELECT; `session_start`/`session_end` = `MIN(ts)`/`MAX(ts)` (free from the group-by, no window function); "at least N events" → `HAVING COUNT(*) >= N`. "One row per person" adds the second group-by (per session, then per entity). "One row per event" is the same first steps with NO final GROUP BY.
- Live solves this session (all DuckDB-verified): Prior Auth Session Cycle Time (one row per session, MAX-MIN, HAVING COUNT>=2), Sessionize Trades (added session_start/end). Recurring bug she hits: reaching for a self-join (fans rows out) and skipping the final per-session rollup.

## SESSION 2026-06-12 — engine flavor expansion + Reshape restructure + many worked cards

This was a long session driven by Trinidad working through LeetCode problems live and asking me to (a) fix their solution, (b) add a teaching card to the playbook, and (c) add an engine flavor so nb01 can produce more practice in that shape.

### New engine flavors (sql_practice_utils.py) — 7 added this session

1. **`pivot.signed_aggregate`** (LeetCode #1393 Capital Gain/Loss shape) — opposing categories (Buy/Sell, debit/credit) collapsed into a single net total via `SUM(CASE +/- value)`.
2. **`pivot.membership_filter`** (LeetCode #1965 shape) — CASE in HAVING as a set membership gate (bought ALL of X, NONE of Y). Both `BOOL_OR` and `MAX(CASE) = 1` forms accepted.
3. **`pivot.threshold_per_category`** (LeetCode #1607-style — Trinidad's last solve) — `SUM(CASE) >= N` in HAVING as a numeric threshold gate across multiple categories ("spent >= $100 in EACH of June AND July"). Explicitly FORBIDS the common mistake of `GROUP BY entity + category HAVING category = 'A' AND category = 'B'` (impossible on a single row).
4. **`percentile_metrics.extreme_exclusion_per_group`** (LeetCode #1412 Quiet Students shape) — per partition `DENSE_RANK ASC + DESC` + `HAVING MIN(rn) > 1` across the entity's rows. Distinguishes from `extreme_exclusion` (whole population) by partitioning the rank windows AND aggregating per entity for the FOR ALL semantics. Forbids `BOOL_OR(rn > 1)` because that's EXISTS not FOR ALL.
5. **`union_islands.consecutive_day_streak_per_entity`** (LeetCode #1454 Active Users shape) — per entity streak detection with DUPLICATE same day source rows that must be deduped FIRST, then `HAVING COUNT(*) >= N` gate, then EXISTS / IN membership semantics. Gated to MEDIUM / HARD only.
6. **`series_generation` SHAPE E** — label spine via `VALUES (label, sort_order)` + CASE bucketing + LEFT JOIN actuals. Categorical bin shape (Session Duration Bins canonical example). Difficulty knob: easy single-table, medium dim + fact, hard multi-table + CTE staircase.
7. **`series_generation` SHAPE F** — active-in-period overlap (Monthly Pipeline Coverage shape). Period spine × dim entity CROSS JOIN × LEFT JOIN fact with HALF OPEN overlap predicate in ON: `created_date < period_start + INTERVAL '1 month' AND (ended_date IS NULL OR ended_date >= period_start)`. **Gated to medium / hard with a 25% probability roll** at the top of the `series_generation` branch (`random.random() < 0.25`). When the roll fires, the shape_hint is replaced with a STRONG PREFERENCE callout. Otherwise the LLM picks A-F organically.

### Other engine updates

- **`series_generation` SHAPE C** now explicitly requires `::date` cast on the LATERAL series output (the cast is the difference between dtype `date` and dtype `timestamp` in expected_output).
- **`series_generation` hard requirement #6**: any column from the date spine OR per-row date expansion MUST be reported with dtype `date` in expected_output AND the answer key MUST cast `::date`. Was added after Sleep Quality Streaks generator bug.
- **`pivot.multi_column_pivot`** now rotates 3 SOURCE TYPES: TYPE 1 (stored category column), TYPE 2 (DOW or month extracted via TO_CHAR), TYPE 3 (bucketed numeric range). TYPE 2 is the **default at medium / hard** and required to include the `TO_CHAR(date, 'Day')` padding trap (any of Mon/Tue/Thu/Fri/Sat/Sun in test data so the FM-vs-non-FM divergence fires; Wednesday is the lying test case because it's already 9 chars). Validator must accept `FMDay`, `TRIM(TO_CHAR(...))`, `EXTRACT(ISODOW)`, or `FMMonth` as the DOW expression.

### Playbook additions / rewrites (sql_problem_patterns.html)

- **NEW worked cards in `#reshape-series-generation`**: Total Sales Amount by Year (`#1384`-style with LATERAL generate_series + EXTRACT YEAR), Session Duration Bins by Minute Range (label spine via VALUES), Monthly Pipeline Coverage by Sales Team (overlap predicate teaching card). All three include trace tables and step bullets matching inline `-- N.` comments in the SQL.
- **NEW template in `#sg-templates`**: `#sg-tmpl-label-spine` "Literal label spine × bucketed CASE (categorical bins)" with the VALUES + sort_order pattern.
- **NEW leaf in `#enrich-aggregate`**: `#ea-leaf-membership` "Bought ALL of X, NONE of Y (set membership filter)" with the LeetCode #1965 worked card. Includes 3 ranked solutions (BOOL_OR, MAX(CASE), INTERSECT/EXCEPT) and the SUM-counting-trap watch out that Trinidad hit on the hidden tests.
- **NEW worked card in `#rp-multi-special`**: LeetCode #1412 Quiet Students with per partition DENSE_RANK ASC + DESC + HAVING MIN explanation. Shows the EXISTS (BOOL_OR) vs FOR ALL (MIN > 1) trap that Trinidad hit.
- **REWRITE of #1454 Active Users** in the per-entity island timelines leaf — was a stale MySQL `DATE_SUB` version with SELECT DISTINCT as the cosmetic fix. New version uses Postgres, 3 ranked solutions (EXISTS / IN, per user 2-stage aggregate, DISTINCT-form labeled as symptomatic), and explains why DISTINCT is treating the symptom not the cause (wrong grain in the final SELECT).
- **REWRITE of #1479 Sales by Day of the Week** in `#reshape-pivot` — was stale MySQL `DAYNAME()`. New version is Postgres-only, leads with the `TO_CHAR(date, 'Day')` padding trap as the marquee lesson, shows trace table with Monday/Wednesday/Friday padding mismatch, ships Rank 1 (single SELECT, zero CTEs, Items LEFT JOIN Orders) and Rank 2 (1-CTE form for complex aggregates), and Watch out list with 6 traps.
- **NEW worked card in `#topic-procedural-blocks`**: "Process Story View Events in Order (DO block, derived column update trap)" — Hard problem with a featured INFO callout in orange teaching the OLD-vs-NEW values trap inside a single UPDATE statement (the column on the right side of SET reads the OLD value, not the just-assigned NEW value). Shows the broken pattern with `total_views` highlighted in red and 3 fixes ranked: replicate the expression in CASE, compute into local variable, two sequential UPDATEs.

### Structural fix to Reshape tab

**10 sibling worked cards moved INSIDE `#reshape-series-generation`.** They were sitting at depth 2 inside `tab-reshape` (peers of the recipe containers, not children) — so the rendered tab showed worked cards floating outside any themed container, visible directly in the recipe list. The script-based move inserted them right before the recipe's outermost `</div>` and removed the original sibling block. After: all worked cards live INSIDE the recipe container; the recipe grew from 21.8K chars to 106K chars. Backup at `/tmp/backup_before_reshape_move.html`.

### Verification (end of session)

- Playbook: div 5128/5128, details 410/410 (perfectly balanced).
- All 5 reshape recipes at depth 2 in tab-reshape (no leaks).
- All 10 single-table recipes at depth 2 in tab-single.
- All 5 multi-table recipes at depth 2 in tab-multi.
- Engine imports cleanly with 31 qtypes.
- Flavor distribution smoke tests: pivot 4 flavors at ~25% each; percentile_metrics 5 flavors on Postgres ~20% each, 4 on MySQL; union_islands 5 flavors on medium/hard with 0% consecutive_day_streak_per_entity on easy; series_generation SHAPE F bias fires ~27.7% on medium/hard, 0% on easy.

### Reminder to Trinidad

After ANY .ipynb edit OR engine edit, **File → Reload Notebook from Disk** in JupyterLab BEFORE running cells. JupyterLab autosave will clobber the disk edits with its in-memory v1 if you save first.

---

## SESSION 2026-06-06 — single-table audit of Multi-Table Rank Within Groups

**17 single-table problems moved out of Multi-Table → Rank Within Groups (`#rank-partition`) into Single-Table → Rank & Percentile (`#rank-percentile`).** Trinidad observed LeetCode #1369 (Get the Second Most Recent Activity) was misplaced in Multi-Table even though it only uses one table (`UserActivity`). Audit of all 32 problems by their `Tables:` line found 17 that don't require a JOIN to compute the metric being ranked.

**5 new SHAPE based leaves added inside `#rank-percentile`** (parallel taxonomy to the existing 7 METHOD based leaves; users can navigate by window function OR by problem shape):
- `#rp-shape-top1-by-value` (8 problems): #1112 Highest Grade per Student, #1831 Maximum Transaction Each Day, #2112 Airport With Most Traffic, #2820 Election Results, #2984 Find Peak Calling Hours, #2988 Manager of Largest Department, #1951 All Pairs With Maximum Common Followers, #578 Get Highest Answer Rate Question
- `#rp-shape-top1-by-date` (4): #2314 First Day Max Recorded Degree, #2668 Find Latest Salaries, #2687 Bikes Last Time Used, #2752 Customers With Max Transactions on Consecutive Days
- `#rp-shape-topn` (1): #2991 Top Three Wineries
- `#rp-shape-nth` (2): #1369 Second Most Recent Activity, #2986 Find Third Transaction
- `#rp-shape-special` (2): #569 Median Employee Salary, #1867 Orders With Maximum Quantity Above Average

**Count badge changes:**
- `#rank-percentile`: 3 → **20 problems**
- `#rank-partition`: 32 → **15 problems**
- `#rp-multi-top1-by-value`: 15 → 7
- `#rp-multi-top1-by-date`: 8 → 4
- `#rp-multi-topn`: 3 → 2
- `#rp-multi-nth`: 2 → **no problems yet** (kept as placeholder for future multi-table Nth problems)
- `#rp-multi-special`: 5 → 3

**Classification rule used:** strict single-table = schema has exactly 1 table. Cases like #574 Winning Candidate (Candidate + Vote where the JOIN is just a dim lookup for the name) and #184 Department Highest Salary (Employee + Department similarly) were kept in Multi-Table because the output schema requires the JOIN.

**Verification:** div balance 5038/5038, details balance 398/398. Depth walk shows all 10 single-table recipes at depth 2 inside tab-single AND all 5 multi-table recipes at depth 2 inside tab-multi (no leaks). Every moved `#NNN` appears exactly in `#rank-percentile` and is gone from `#rank-partition`. Backup of pre-move file at `/tmp/backup_before_singletable_move.html`.



## Three active artifacts

1. **Playbook** — `/Users/trinidadcisneros/Documents/Development/Coding/bitterscientist.com/bitterscientist.com/folders/sql/sql_problem_patterns.html`
2. **Practice notebook (analytical SQL)** — `/Users/trinidadcisneros/Documents/Development/Coding/bitterscientist.com/bitterscientist.com/folders/ds_blogs/projects/sql_practice_generator/notebooks/nb01_sql_practice.ipynb` (engine: `sql_practice_utils.py` next to it)
3. **Interview drills notebook (analyst prep)** — `/Users/trinidadcisneros/Documents/Development/Coding/bitterscientist.com/bitterscientist.com/folders/ds_blogs/projects/sql_practice_generator/notebooks/nb02_analyst_interview_drills.ipynb` (engine: `nb02_drill_utils.py`). Claude-powered drill generator for Staff/Senior Product Analyst prep; its own CATEGORY catalog (Data Transformation Modeling, Critical Reasoning SQL, Product Metrics & KPIs, etc.). NOT yet touched in depth — same wiring idea as nb01 but a separate catalog.

Trinidad is prepping for SQL interviews (Solace Health DA assessment, SmarterDx senior product analyst). Day-to-day is Redshift/Snowflake/Databricks, comfortable with PostgreSQL.

## SESSION 2026-06-01 — major additions (most recent work)

**Generator qtype #31 added — `root_cause_analysis` (Postgres only):** followed the documented 3-edit recipe in `sql_practice_utils.py`.
- `QUESTION_TYPES["root_cause_analysis"]` near line 263 (label, description, `dialects: ["postgresql"]`).
- `_topic_specific_guidance` branch after `window_sessionization` (near line 2084). Rotates 7 archetypes per generation: `metric_drop_dimension`, `duplicate_inflation`, `missing_rows_antijoin`, `null_propagation`, `date_timezone_bug`, `stale_snapshot`, `two_source_mismatch`. Difficulty-aware (easy = 1 CTE / 2 tables / < 15 rows, medium = 2-3 CTEs / 3 tables, hard = 4+ CTEs / 3-4 tables + FULL JOIN or EXCEPT). Auto-appears in picker + `random_any` pool (postgres only).
- `CODE_REFERENCE["root_cause_analysis"]` near end of dict (~line 853). Ships the metric-drop CTE-staircase pattern + a 7-line cheat sheet mapping each archetype to its canonical Postgres feature (EXCEPT, FULL JOIN + IS DISTINCT FROM, date_trunc/AT TIME ZONE, DISTINCT ON, etc.).
- Total qtypes: **31** (was 30). Anti-pattern the guidance explicitly forbids: making the answer a single SELECT that just reports the broken metric — the WHOLE POINT is the answer surfaces the BUG ROWS.
- nb01 cells 10-13 are 4 NEW markdown cells (section header + 3 hand-crafted verified samples — null_propagation easy, metric_drop_dimension medium, two_source_mismatch hard). Cell 14 = original footer. No existing cells touched.

**Multi-Table Recipes Reference cards consolidated into one nested master:** the three top-level Reference cards (Technique Quick Reference, ON Clause Cheat Sheet, JOIN Checklist) merged into a single "**Multi-Table Quick Reference** (pick method → write JOIN → verify)" master card with three nested collapsible sub-sections that follow the natural workflow. The big sub-sections break further:
- Section 1 (Pick the method) has FOUR nested sub-containers grouping the original 14-row table by recipe family: 1a Join Techniques, 1b Aggregation After Join, 1c Ranking After Join (cross-links to single-table Rank & Percentile), 1d Combining Independent Results.
- Section 2 (Write the JOIN) splits the original 2-table seam: 2a What goes inside ON, 2b ON vs WHERE / the LEFT JOIN gotcha. `id="pitfall-on-vs-where"` was preserved on the section 2 wrapper so all existing in-playbook links to that anchor still work.
- Section 3 (Verify) kept as one section (1.8K of plain prose; nesting would be clicks-for-no-clarity).

**All 30 Generic Templates per Method converted to nested collapsible cards with step bullets.** Each `<h4 id="xx-tmpl-yyy">` template across 6 containers (Rank & Percentile 6, Window 7, enrich-aggregate 5, Gated Lookup 5, Matchup & Leaderboard 4, Series Generation 3) was wrapped into a `<div id="xx-tmpl-yyy" class="problem-card collapsed">` carrying: the original `(back to tree)` link in the header, the "Use when:" line in the excerpt, a "What this template does, step by step" ordered list above the SQL, then the original SQL skeleton verbatim. Anchor IDs preserved so all decision-tree links still resolve. Three levels of collapse now exist where templates live: recipe container → templates section → individual template card.

**`wrap_templates.py` BUG + FIX (2026-06-01):** the script's `body_end` regex `\n                  </div>\s*\n                </div>` (18-space + 16-space) for the LAST template in each container did NOT match `rp-templates`' actual indentation, so the rp-templates wrapper consumed the 7 Rank & Percentile leaves AND every recipe after it AND tab-multi AND tab-reshape — visually rendering Multi-Table Recipes and Reshape Recipes tabs as BLANK in the browser. The other 5 templates cards were not affected. **Fix (3 surgical edits, net zero new divs):** (1) added 2 closing divs after `rp-tmpl-pct-agg` to close rp-templates content + wrapper at the right spot; (2) added 2 closing divs after `rp-leaf-median` to close the rank-percentile RECIPE container right after its leaves end; (3) removed the 2 stray closing divs at end of tab-single that were the original rank-percentile closes living far away. After fix: div 4965/4965, all 6 tabs sibling (no nesting), all 10 single-table recipes at depth 2, all 5 multi-table recipes at depth 2, all 5 reshape recipes at depth 2. **Diagnostic tip for future regressions like this:** check recipe depths per tab (`<div class="problem-card" id="..."` should sit at depth 2 inside its tab pane); if any recipe is at depth 4 something earlier in the same tab leaked its closes.

**Worked cards added this session** (each verified in DuckDB before insertion):
- **Procedures → RETURNS TABLE:** *Sleep Quality Streaks Report* — multi-CTE totals + gaps-and-islands streaks. First worked card using the new step-bullet format (numbered bullets above the SQL, matching `-- 1.` `-- 2.` comments inside the SQL).
- **Procedures → RETURNS scalar:** *Count Top Leader Invites* — 3-CTE staircase, DENSE_RANK across the full player population, LEFT JOIN sent, CASE gate at the end. Watch-outs flag the NULL-return edge case (player_id with no `match_results` rows returns NULL not 0; fix: drive off `players` dim + LEFT JOIN rankings).
- **Single-Table → Rank & Percentile → NTILE leaf:** *Quartile Segmentation of Customer Basket Spend* (2nd card) — teaches the **`DESC NULLS FIRST` default trap** in Postgres NTILE windows. NTILE leaf is now at 2 problems; container at 3.
- **Multi-Table → Gated Lookup → `#gl-leaf-min-pick`:** *Squad Invite Cost by Match Completion Gate* (FROM-fact direction, sentinel = 0 not NULL) and *Reimbursement Cap by Vendor Status* (gate-on-A + filter-on-B both stacked in ON). Leaf at 3 problems; container at 4.
- **Multi-Table → Gated Lookup → new `#gl-leaf-rownumber-pick` leaf:** *Gig Platform Approved Worker Earliest Bid* — teaches the **"MIN of value vs value FROM the MIN-by-ordering row"** distinction. New template `#gl-tmpl-rownumber` added; decision-tree Q4 split into 4 cases (was 3) to route ordering picks.
- **Multi-Table → Matchup & Leaderboard:** *Saved Search Template Performance Leaderboard* — soccer-style 3/1/0 scoring with dim zero-fill.
- **Multi-Table → Match Eligibility card:** added Rank 3 CTE-staircase solution alongside the existing Rank 1 (CASE around MIN) and Rank 2 (gate in ON).
- **Reshape → Series Generation:** *Weekly Job Completion Report with Zero-Fill* — week spine × CROSS JOIN workers × LEFT JOIN completions with half-open `>= start AND < start + INTERVAL '7 days'` window.
- **Gaps-and-Islands → date-rn leaf:** *Monthly Writing Streak Analysis by Cohort* (first card in the previously-empty leaf) with the **dedupe-per-user-day-BEFORE-the-rn-trick** lesson. Rank 2 added later: a leaner 3-CTE solution using `COUNT(*) OVER (PARTITION BY user_id, grp)` as a window so each row carries its streak length and a single final GROUP BY computes both metrics in one pass.

**Gated Lookup decision tree Q3 sharpened** (lay-language order-of-operations framing):
- Q3 (drop vs keep) routes to Q3a or WHERE.
- Q3a explains in plain words: CASE runs AFTER the aggregate so it can only show / hide; ON runs BEFORE the aggregate so it decides what the aggregate even sees. Tell-tale signs you need ON not CASE: prompt has a status/date/category filter on the JOINED table AND non-qualifiers must appear.
- `gl-tmpl-onclause` template expanded with a "single gate on A" skeleton + a "stacked: entity gate on A AND row filter on B" skeleton.

**Multi-Table Rank Within Groups (originally 32 problems) — intro slimmed + regrouped:** intro wrapped into a "Recipe overview & key decision rules" Reference card (purple badge). 32 problems regrouped into 5 themed leaves by the ORDER BY pattern: `#rp-multi-top1-by-value`, `#rp-multi-top1-by-date`, `#rp-multi-topn`, `#rp-multi-nth`, `#rp-multi-special`. **NOTE (superseded 2026-06-06):** the audit above moved 17 single-table problems out of this container; current count is 15 problems, not 32. The remaining 15 are problems where computing the rankable metric truly requires a JOIN.

**Multi-Table `enrich-aggregate` (Join Tables Then Aggregate, 45 cards) standardized** to mirror the Rank Within Groups shape: intro wrapped into a "Recipe overview" Reference card; existing "Techniques used in Enrich Aggregate" cheat sheet preserved; new How-to-pick decision tree (`#ea-decide`) and new Generic templates per method (`#ea-templates` with 5 anchors); 5 themed leaves (`#ea-leaf-count` 11, `#ea-leaf-sumavg` 13, `#ea-leaf-rate` 5, `#ea-leaf-filter` 13, `#ea-leaf-datewin` 3 with Monthly Ad Revenue anchor).

**New Multi-Table recipe: `#gated-lookup` (Gated Lookup)** inserted between enrich-aggregate and matchup-leaderboard. Window-style scaffolding: Reference cheat sheet (4 moves table + the WHERE-drops/CASE-keeps trap callout + gate-reads-A-picked-value-reads-B core distinction), 4-question decision tree, generic templates (`#gl-tmpl-case`, `#gl-tmpl-onclause`, `#gl-tmpl-where`, `#gl-tmpl-distincton`, `#gl-tmpl-rownumber`), and 2 leaves (`#gl-leaf-min-pick`, `#gl-leaf-rownumber-pick`).

**New Multi-Table recipe: `#matchup-leaderboard` (Matchup & Leaderboard)** between enrich-aggregate and rank-partition. Window-style scaffolding + first card. Anchors: `#ml-decide`, `#ml-templates`, `#ml-tmpl-310`, `#ml-tmpl-winloss`, `#ml-tmpl-sumcol`, `#ml-tmpl-gfga`, `#ml-leaf-leaderboard`.

**New top-level Reshape recipe: `#reshape-series-generation` (Series Generation — calendar / number spine)** between cross-join and the next reshape recipe. Built by promoting the old "Date or number range" leaf out of CROSS JOIN; carries all 6 original anchors plus the new *Weekly Job Completion Report* (7 total). Anchors: `#sg-decide`, `#sg-templates`, `#sg-tmpl-literal`, `#sg-tmpl-data-bounds`, `#sg-tmpl-filtered-entities`.

**Sleep Quality Streaks problem JSON patched** (`20260530_142754_postgresql_returns_table_*.json`):
- Generator bug: `total_nights` was 2x or 3x actual count in expected outputs. Patched: example 12→6; test 30→10 and 24→8. avg_score and longest_streak were already correct.
- Prompt wording tightened to define `total_nights` (COUNT of non-NULL sleep_score rows), `avg_score` (AVG of those rounded to 2 decimals), `longest_streak` (longest run of consecutive calendar days at-or-above target) unambiguously.

**`prompt_to_bullets` numbered-list fix (engine):** added a branch that detects `1. 2. 3.` style inline numbered lists (digit + period + space, consecutive run starting at 1) and renders them as an `<ol>`. Previously only `(1) (2) (3)` parenthesis style was handled. Decimals (`0.10`), `DECIMAL(10,2)`, and a lone `1.` do not trigger it.

**Engine functions added this session and earlier:**
- `grade_diagnostic(problem, answers)` — extended to grade all 6 steps of the diagnostic worksheet (reads 17 answer keys, returns flat JSON with per-step feedback and correct/rethink flags).
- `walkthrough_diagnostic(problem)` — returns worked answers per step for Walkthrough mode (analysis only, never the final SQL).

**nb01 Diagnose section v2 (cell 5):** 6-step accordion with Solve / Walkthrough toggle. Interactive checkbox tables for Steps 3, 4, 5 with auto-fill of the text fields (recipe pick → fills "Named shape" sentence; composite-moves picks → fills moves outline; rule-out ticks → fills "Branches ruled out" + "Remaining branch"; adaptation ticks → fills notes). Guarded autofill (`_auto_last` + `_guarded_fill`) so manual edits aren't stomped. Step 5 also has a "Load skeleton for this problem" button calling `spu.get_code_reference(qtype, islands_flavor, percentile_flavor)`. Intro reads "**Interactive worksheet v2**" so you can confirm the right version loaded.

---

## SESSION 2026-05-26 — major additions (most recent work)

**Workflow that worked well this session (reuse it):** user pastes a generated problem + their solution → verify the solution in DuckDB (`pip install duckdb`) against the stated expected output → clean it up (drop cosmetic CTE `ORDER BY`s, unused columns, redundant COALESCE) → add it as a worked card in the right recipe. After EVERY html edit, verify structural integrity: `<div>` open==close AND stack depth never goes negative, and `<details>` open==close. Caught the "passes the sample but wrong per spec" bug class twice (Q1 archive `closed_date` vs `approval_date`; gig-workers `PERCENT_RANK` row-fraction vs `PERCENTILE_DISC` value-band; course-activity "courses with enrollment in range" vs "courses with completions").

**New decision-tree + leaf reorganizations in the playbook** (all use the same scannable style: short Setup bullets, Q1/Q2/Q3 with green "✓ use X" outcomes, one shared reference line):
- **Compare** (row-compare, now 18): "Compare to the previous or next row" container holds a decision tree + 3 reference tables (method→signs→code, edge/pitfall, trace) + an "Elapsed time by unit — EXTRACT(EPOCH) denominators" table (seconds 1, minutes 60, hours 3600, days 86400, weeks 604800, months ≈2629800, years ≈31557600; use DISC/AGE for calendar months/years) + 4 leaves: Compare to neighbour's value (#197), Measure the gap or delta (2: date follow-up visits + timestamp visit gap), Detect a fixed-length run (#180), Pair two rows by role (#1661). Gaps-and-islands umbrella unchanged (15).
- **Window** (time-window, 16): added "How to pick: decision tree" + "Generic templates per method" (copy-paste skeletons, two-way linked to the tree via `#tw-decide`/`#tw-templates` and per-leaf `tw-tmpl-*` anchors). Sessionization leaf now 3 (added Workout Session Detection with 20-Minute Gaps).
- **Pair / normalize-bidirectional** (4): added decision tree + "Template code — pick the approach" table + 3 leaves: Pool both columns count per entity (#602), Canonicalize the unordered pair (#1699, Messages), Matchup unpivot two-sided scored rows (#1212). The matchup recipe teaches "split AND score in one step" (CASE inside each UNION ALL branch, no gf/ga swap).
- **Look Up Columns / enrich-join** (16): reorganized the 14 flat problems into themed leaves via a depth-aware Python script (split top-level problem-card blocks, regroup, verify balance). Leaves: Straight lookup/enrich (7, incl. new "Orders in 2024 per Customer" ON-vs-WHERE problem and the anti-join #1581), Gated lookup (1, with its own mini decision tree), Self-join (3: #181, #1264, #1747), Cross join (1: #1280), Match each row to a per-group value (2: #512, #1303), Compound eligibility (2: #1811, #2041). Recipe-level decision tree at top (`#ej-decide`) routes to all leaves.

**New worked problems added (verified in DuckDB):** Compare gap (date follow-up + timestamp visit), gig-workers Top 10% PERCENT_RANK-vs-PERCENTILE_DISC contrast (in single-table rank-partition percentile cluster), Weekly Reorder Rate by Customer Segment (Reshape → Date or number range), Monthly Ad Revenue by Cohort (Multi → Join Tables Then Aggregate), Daily Course Activity Report zero-fill (Reshape → Date or number range, with the courses-in-range-not-completions fix), Workout Sessionization (Window), Matchup #1212 (Pair), Gated lookup products/pricing (enrich-join), Orders-in-2024 ON-vs-WHERE (enrich-join Straight lookup).

**Three new generator qtypes added to `sql_practice_utils.py`** (catalog entry + `_topic_specific_guidance` branch + `CODE_REFERENCE` template; auto-appear in picker and random_any; classification noted):
- `matchup_unpivot` (normalize-bidirectional) — wide two-sided scored row → UNION ALL split + score each branch + GROUP BY participant + LEFT JOIN dim for zero-fill.
- `gated_lookup` (enrich-join) — a threshold/flag in table A gates a per-entity pick (min/max/earliest) from table B; CASE fallback (keep all, 0/NULL) vs WHERE (drop). NOT a sum/avg aggregate.
- `left_join_on_filter` (enrich-join) — LEFT JOIN where a right-side filter MUST go in ON (keeps unmatched left rows) vs WHERE (silently turns it INNER, drops them); use COUNT(right_col) not COUNT(*). Catalog now 30 qtypes.

## RESPONSE RULES — non-negotiable

- **TASK-DONE FORMAT (hard rule, 2026-06-18):** when a task is complete, report it in ONE sentence, and add next steps in one more short line if any exist. NO blocks of text, NO multi-paragraph recaps. Trinidad does not want to read walls of text.
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

Tabs: Diagnostic Process | Decision Tree | Single-Table Recipes | Multi-Table Recipes | Reshape Recipes | Procedures

**Current recipe counts (2026-05-27):** Single-Table — Filter 27, Aggregate 35, Scalar 12, **Rank & Percentile 1 (7 leaves, full Window-style scaffolding)**, Transform 19 (still hosts the percentile cluster pending migration to Rank & Percentile), Compare 18, **Window 15 (lost Top-N leaf to Rank & Percentile)**, Pair 4, Dedup 2. Multi-Table — Look Up Columns From a Reference Table 16, Join Tables Then Aggregate 46, Rank Within Groups to Select Top-N 32, Combine Independent Queries 2. Reshape — union/pivot/unpivot/cross-join; cross-join leaves Fixed labels 1, Two dimensions 2, Date or number range 6.

**Single-Table Rank & Percentile container (2026-05-27, new):** `id="rank-percentile"` replaced the old `rank-stub`. Modeled after Window: header + intro + Signal words + Technique + cross-link, then Reference card (7 window function cheat sheet: ROW_NUMBER / RANK / DENSE_RANK / NTILE / PERCENT_RANK / PERCENTILE_CONT / PERCENTILE_DISC), How-to-pick decision tree (`#rp-decide`), Generic templates per method (`#rp-templates` with anchors `#rp-tmpl-rownum`, `#rp-tmpl-rank`, `#rp-tmpl-denserank`, `#rp-tmpl-ntile`, `#rp-tmpl-pctrank`, `#rp-tmpl-pct-agg`), and 7 leaves (`#rp-leaf-rownum`, `#rp-leaf-rank`, `#rp-leaf-denserank`, `#rp-leaf-ntile`, `#rp-leaf-pctrank`, `#rp-leaf-pct-agg`, `#rp-leaf-median`). Mutual exclusivity rule applied: Compare = LAG/LEAD neighbour; Window = frame aggregate (ROWS BETWEEN); Rank & Percentile = position selection or distributional scoring. ROW_NUMBER + filter is position selection, so the Window "Top N per group (ROW_NUMBER + filter)" leaf was moved into `#rp-leaf-rownum` with its one problem (#1164 Product Price at a Given Date); Window's decision tree now routes top-N to Rank & Percentile.

**NEXT (Phase C — pending):** Migrate the percentile cluster currently inside the Transform container (lines ~9670-10247 in the playbook: #2346 PERCENT_RANK per Partition, the gig-workers PERCENT_RANK vs PERCENTILE_DISC contrast, the teal "Percentile & Distribution Metrics" summary callout at 9966, the Top 10% Trial Sites anchor, the Quartile Bucketing of Monthly Box Revenue anchor, #2377) into the matching Rank & Percentile leaves (`#rp-leaf-pctrank`, `#rp-leaf-pct-agg`, `#rp-leaf-ntile`). After migration, Transform's count drops; Rank & Percentile's count rises.

**Rank & Percentile — first worked card added 2026-05-27:** NTILE leaf `#rp-leaf-ntile` now holds **Tutor Quartile Ranking by Completion Rate** (matchup_unpivot... wait, percentile_metrics ntile_buckets flavor). NTILE(4) OVER (ORDER BY completion_rate DESC); WHERE filters total_sessions > 0; per-row trace table; watch-outs cover integer division, NTILE literal-only, direction trick (DESC bucket 1 = best), uneven row splits going to lower buckets, tie-at-boundary split behaviour, and the redundant COALESCE. Verified in DuckDB. Container count went 1 → 2.

**Multi-Table — new "Matchup & Leaderboard" recipe added 2026-05-27:** `id="matchup-leaderboard"`, inserted between `enrich-aggregate` and `rank-partition`. Modeled on the Window / Rank & Percentile scaffolding: header + intro + Signal words + Technique + cross-link, then Reference card (4 moves cheat sheet: UNION ALL self-unpivot, CASE inside each branch, GROUP BY participant, LEFT JOIN dim + COALESCE 0), How-to-pick decision tree (`#ml-decide` with Q1 both-sides-in-one-row + Q2 scoring rule + Q3 zero-fill participants + traps section), Generic templates per method (`#ml-tmpl-310` soccer 3-1-0, `#ml-tmpl-winloss` 1-0 records, `#ml-tmpl-sumcol` sum-a-column, `#ml-tmpl-gfga` goals-for/against), and the first leaf `#ml-leaf-leaderboard` "Leaderboard with dim zero-fill" holding **Saved Search Template Performance Leaderboard** as the worked card. Cross-link points back to single-table Pair / Normalize Bidirectional (#1212 Win/Loss is the canonical no-dim anchor). Verified in DuckDB.

**Multi-Table Rank Within Groups (#rank-partition) intro slimmed 2026-05-27:** answered Trinidad's question — keep the 32-problem bank in Multi-Table (those problems genuinely need a JOIN to compute the rankable metric) but slim the intro to cross-reference single-table Rank & Percentile (#rank-percentile) for the technique source (decision tree, templates, cheat sheet). Added a blue callout "Why this lives in Multi-Table: position selection mechanics are identical; the JOIN is what makes them multi-table — treat this recipe as Rank & Percentile + JOIN, not a duplicate of the reference."

**Multi-Table Rank Within Groups regrouped 2026-05-27 into 5 themed leaves** (mirrors the depth-aware reorganization used for Compare / enrich-join / Pair / Window). Grouping axis = the ORDER BY pattern that distinguishes which rank function and direction to use:
- **`#rp-multi-top1-by-value`** (15 problems) — top 1 per group by a value column ORDER BY DESC: #184, #1077, #1112, #1831, #2112, #2324, #2362, #2820, #2984, #2988, #1951, #574, #578, #1194, #1596.
- **`#rp-multi-top1-by-date`** (8 problems) — top 1 per group by a date / timestamp (most recent or earliest): #1082, #1070, #1549, #1083, #2314, #2668, #2687, #2752. Mentions Postgres `DISTINCT ON` as an alternative.
- **`#rp-multi-topn`** (3 problems) — top N per group, N > 1: #185 (DENSE_RANK top 3 salaries), #1532 (ROW_NUMBER top 3 most recent), #2991 (top 3 wineries).
- **`#rp-multi-nth`** (2 problems) — Nth specific position: #1369 (2nd most recent activity), #2986 (3rd transaction). Notes the watch-out that groups with fewer than N rows vanish.
- **`#rp-multi-special`** (4 problems) — patterns where the rank feeds back: #569 (median asc/desc trick), #1867 (rank + per-group aggregate threshold), #1988 (cutoff score per school), #2175 (rank delta across snapshots).

Each leaf is a `qtype-group` container with header + count badge + excerpt + the original problem cards verbatim (no card content was edited). Prelude (intro + mnemonics + the existing Reference card) was preserved unchanged. Total still 32 problems.

**Rank Within Groups intro wrapped into a Reference container 2026-05-27:** the loose Signal/Technique/Why blue callout + green PARTITION BY mnemonic + orange multi-column ORDER BY tiebreaking callout were consolidated into a single nested Reference card titled "Recipe overview & key decision rules" (purple "Reference" badge, same pattern as `Techniques used in Window` etc.). The existing "Techniques used in Rank Within Groups" cheat-sheet Reference card stays separate. So the container now opens with TWO collapsed Reference cards (overview + technique cheat sheet), then the 5 themed leaves.

**Multi-Table — new Gated Lookup recipe added 2026-05-27 (`id="gated-lookup"`):** inserted between `enrich-aggregate` and `matchup-leaderboard`. Same Window-style scaffolding: Reference card "Recipe overview & key decision rules" (4-row technique cheat sheet: LEFT JOIN A→B, CASE around aggregate, gate in JOIN ON, WHERE filter, DISTINCT ON Postgres) + amber "Trap to watch" callout (WHERE drops, CASE/ON keep; gate reads A, picked value reads B), How-to-pick decision tree (`#gl-decide`, 4 Qs: one-row-per-entity? / gate-in-A? / non-qualifiers-appear? / what is the pick?), Generic templates (`#gl-tmpl-case`, `#gl-tmpl-onclause`, `#gl-tmpl-where`, `#gl-tmpl-distincton`), and first leaf `#gl-leaf-min-pick` "Earliest / latest pick with threshold gate" holding **Match Eligibility and Best Message Time** (dating-app gated lookup: `LEFT JOIN matches → messages, CASE WHEN score >= 70 THEN MIN(sent_at) ELSE NULL`). Two ranked solutions (CASE-around-aggregate and gate-in-ON-clause). Verified in DuckDB.

**Multi-Table — `enrich-aggregate` (Join Tables Then Aggregate) standardized 2026-05-27 to mirror the Rank Within Groups structure:**
- Intro (Signal/Technique + grey ON-vs-WHERE pitfall + orange WHERE-drops-zero trap with PostgreSQL code) wrapped into a "Recipe overview & key decision rules" Reference card.
- Existing "Techniques used in Enrich Aggregate" cheat-sheet Reference card preserved.
- New "How to pick: decision tree" card (`#ea-decide`): Q1 picks the aggregate type (count / sum / rate / aggregate-then-filter / cohort), Q2 the LEFT vs INNER decision, Q3 warns about multi-child fan-out.
- New "Generic templates per method" card (`#ea-templates`) with 5 anchored skeletons: `#ea-tmpl-count` (COUNT(b.col) not COUNT(*)), `#ea-tmpl-sumavg`, `#ea-tmpl-rate` (NULLIF the denominator), `#ea-tmpl-having` (HAVING and conditional CASE side by side), `#ea-tmpl-datewin` (DATE_TRUNC cohort).
- 5 themed leaves: `#ea-leaf-count` (11 problems), `#ea-leaf-sumavg` (13), `#ea-leaf-rate` (5), `#ea-leaf-filter` (13), `#ea-leaf-datewin` (3 — 2 numbered + Monthly Ad Revenue anchor). Total 45 cards. Card content preserved verbatim; the named anchor "Monthly Ad Revenue by Cohort Month" lives inside the datewin leaf.

**To re-group a flat recipe into themed leaves (reuse this method):** a depth-aware Python script that slices the recipe region by line numbers, splits top-level `<div class="problem-card collapsed">` blocks by counting `<div`/`</div>` per line (a block is depth 0→0), identifies each by its `#NNN` (use `#(\d{3,4})` filtered to the known id set so hex colors like `#2e7d32` and the `&#9660;` toggle don't false-match), then reassembles into leaf wrappers in theme order. Each leaf = `<div class="problem-card collapsed qtype-group">` + header (with count-badge) + excerpt + content-open + blocks + content-close + container-close. Net div change is balanced (each leaf adds 2 open + 2 close).

### Procedures tab (4 topics, restructured 2026-06-18)

No intro paragraph and no standalone top-level reference cards — the tab opens straight into the technique containers. `.qtype-card` styles sit once at the top. Each topic has ONE steel-blue "Reference" card (the scaffold(s) + a "when you'll see it" shape card) nested inside it; nothing reference-y sits outside that card.

1. **Functions** — Reference (RETURNS scalar + RETURNS TABLE scaffolds + both function shape cards) + 2 recipes:
   - RETURNS scalar — anchors: SLA breach rate, reviewer denial rate, avg engagement score, sleep adherence, **30-Day Readmission Rate (LAG previous discharge)**, **Trial Conversion Rate by Cohort (CTE staircase + denominator gotcha)**
   - RETURNS TABLE — anchors: #177 NthHighestSalary, #2230 Eligible for Discount, Patient Medication Adherence, Filter Claims by Denial Category, Therapy Engagement Score, **Loan Stage Duration (EXTRACT EPOCH)**, **Trial Conversion Report by Plan Tier (multi-table JOIN + time-window filter + inclusive day count)**

2. **Recursive Queries** — Reference (Recursive CTE shape) + Hierarchies, Paths, Chains recipe (Trace Transaction Approval Chain)

3. **Updates, Deletes, and Inserts** (`topic-dml`) — now ALSO the home for procedural blocks. The Reference card holds: FOR LOOP vs set-based decision guidance, the DML scaffold, the DO sequential + DO row-by-row scaffolds, and the UPDATE/DELETE/INSERT + DO Block shape cards. Recipes:
   - Single-Statement UPDATE — tiered subscription discount, fraud flag risk score, sleep logs goal achievement, **Apply Tiered Review Status Updates (multi-column CASE in one SET)**
   - Single-Statement DELETE — has Common DELETE cases table (7 cases: conditional, duplicates, orphans, cross-table, time-based pruning, two-condition, NULL-safe positive WHERE) + pitfalls table. Anchors: article views dedup, milestone purge, **Remove Incomplete Sleep Sessions (positive WHERE vs NOT IN + NULL handling)**
   - Single-Statement INSERT — archive approved loans
   - **(moved from Procedural Blocks)** Simple Sequential UPDATEs (set-based), Row-by-Row State Mutation (FOR LOOP — airline seats, refund queue, cohort enrollment, Sequential Medication Dose Adjustments, Apply Sequential No-Show Penalties), Process Story View Events in Order (DO block, derived-column update trap)

4. **Window Function Edges** — Reference only

**Procedural Blocks topic no longer exists** — fully folded into Updates/Deletes/Inserts above. The Decision Tree "Procedures" source lists these 4 topics; the Updates/Deletes/Inserts shape carries the DO $$ / Sequential UPDATEs / FOR LOOP tech cards. The Functions Reference still distinguishes `RETURN ( ... );` (scalar) from `RETURN QUERY ( ... );` (table).

### Single-Table Recipes — Gaps-and-Islands & percentile clusters

- **Gaps-and-Islands summary callout** (purple-bordered) sits before #601 Human Traffic of Stadium with three tables: pick approach by data shape (4 forms), GROUP BY + key pitfall per approach, trace examples per approach. Critical correction: form A (`PARTITION BY entity` outer) is NOT a superset of form B; if there's no entity column, you MUST use form B. Substituting status as the entity collapses every same-status row into one giant island.
- **#1225 Report Contiguous Dates** — has TWO ranked solutions: Rank 1 `rn_overall - rn_per_state` (dialect-agnostic), Rank 2 `date - (rn_per_state)::INT` (Postgres-friendly, no missing days)
- Yellow callout under #1225 explaining the calendar-vs-data-sequence distinction with the leap-year example
- **Anchor: Member Workout vs Skip Streaks** — leap-year trap (Feb 28 / Mar 1 / Mar 2 with Feb 29 missing) with per-row trace table
- **Anchor: Collapse Order Status Periods (UNION + per-entity partition)** — multi-entity timelines requiring `PARTITION BY order_id` on BOTH windows; GROUP BY three keys
- **Anchor: Identify Consecutive Portfolio ID Ranges (per group)** — added 2026-05-27 to the "Consecutive integer ids" leaf (now 5 problems; umbrella now 16). The integer `id - rn` flavor with a PARTITION BY twist: `ROW_NUMBER() OVER (PARTITION BY rebalance_strategy ORDER BY portfolio_id)`, GROUP BY `rebalance_strategy, grp`. Teaches that the `id - rn` anchor is NOT unique across groups (two strategies can both yield grp 106), so GROUP BY must include the partition key. Has a per-row trace table. Verified in DuckDB against the stated example output.
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
- **`series_generation`** (postgresql) — generate_series as the centerpiece: date/number spine over a fixed range, CROSS JOIN entities, LEFT JOIN actuals + COALESCE 0; integer series for fixed buckets; per-row range expansion via CROSS JOIN LATERAL. Ranges literal or MIN/MAX-derived, never CURRENT_DATE. **6 SUBTYPES (2026-06-18, match the playbook Series Generation leaves):** `full_date_spine` (SHAPE A), `bounds_from_data` (SHAPE D), `filtered_entities` (SHAPE A filtered-DISTINCT), `categorical_label_spine` (SHAPE E), `lateral_range_expansion` (SHAPE C), `period_overlap` (SHAPE F). A picked subtype PINS the shape; scenario + difficulty still apply on top.
- **`scalar_extract`** (postgresql, mysql) — NEW 2026-06-18, fills the LIMIT/OFFSET gap. A single table reduces to exactly one row/value. 4 SUBTYPES mirroring the Single-Table Scalar leaves: `single_aggregate` (whole-table MAX/MIN/SUM/COUNT), `top1` (ORDER BY ... LIMIT 1), `nth` (2nd/Nth highest via LIMIT 1 OFFSET N-1, or NULL-safe subquery-in-SELECT), `ratio` (percentage/weighted avg, NULLIF the denominator). Centers the WHERE-returns-0-rows-instead-of-NULL trap. Classification recipe = `scalar-extract`.
- **`matchup_unpivot`** (postgresql, mysql) — wide row holds both sides of a head-to-head event (host/guest + their scores). UNION ALL splits into one row per participant, scoring each branch in place (CASE inside the branch, no goals-for/against swap), then GROUP BY participant + LEFT JOIN a dimension for zero-game rows. Classification normalize-bidirectional.
- **`gated_lookup`** (postgresql, mysql) — two tables share an entity key; a threshold/flag/status/date in table A gates a per-entity pick (min/max/earliest/latest) from table B. CASE fallback (keep all entities, 0/NULL) vs WHERE (drop non-qualifiers). The gate reads table A's attribute, never the picked value. NOT a sum/avg. Classification enrich-join.
- **`left_join_on_filter`** (postgresql, mysql) — drills the ON-vs-WHERE trap: a right-side filter on a LEFT JOIN must go in ON to keep unmatched left rows; the same filter in WHERE silently turns it INNER and drops them. Data designed so at least one left entity has no qualifying right row. Use COUNT(right_col) not COUNT(*) (the latter counts the NULL-filled row as 1). Classification enrich-join.

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

### Cell 5 (Diagnostic form) — rebuilt 2026-05-26 as a six-step worksheet

Replaced the old flat 5-field form with a **6-panel Accordion** mirroring the nb02 Response Builder interactive style. One panel per step of Trinidad's diagnostic template:
- **Step 1 Map inputs/output** — `input_map_ta`, `output_columns_ta`, `output_grain_ta`, `row_direction_dd` (fewer/same/single)
- **Step 2 Classify inputs** — `input_dd` (single_table/join/reshape/union/procedural)
- **Step 3 Name the shape** — `named_shape_ta` ("this is a __ because __"), `recipe_dd` (RECIPE_VOCAB), `moves_ta`
- **Step 4 Decision tree by elimination** — `ruled_out_ta`, `remaining_ta`
- **Step 5 Grab recipe + adapt** — `recipe_template_ta`, `similar_problem_ta` (Text), `adaptations_ta`
- **Step 6 Sanity check** — `failure_mode_ta` + `_check_boxes` (6 checkboxes) + `_redflag_boxes` (3 checkboxes)

Top-level `paraphrase_ta` frames the problem above the accordion. Same dracula theme + Tab/Shift+Tab handling as cell 7; native Cmd+Z works.

**Solve vs Walkthrough toggle** (`mode_toggle`): Solve mode shows generic guidance in each `_step_hint[1..6]` HTML widget. Walkthrough mode reveals `walkthrough_btn` ("Show worked diagnostic") which calls `spu.walkthrough_diagnostic(problem)` and paints the worked answers into each step hint (cached per problem via `id(p)`); Trinidad reads them then paraphrases into the fields. `refresh_diagnostic_form()` drops the cache + resets hints on new-problem load (called from cell 9 on_next).

**Single "Get Feedback" button** grades the whole worksheet: `on_feedback` gathers all 17 answer keys and calls `spu.grade_diagnostic`. Checkbox groups are flattened to text before sending (`_ticked` for Step 6; `_ticked_labels` + `_combine` for Steps 3-5).

**GridBox checkbox tables in Steps 3, 4, 5** (added after the first build, mirroring the nb02 dbt-test table so options are scannable with lay definitions):
- `_make_check_table(specs, headers, col_template, max_height)` builds a single GridBox (header row + checkbox-per-row + HTML cells). It owns the only scrollbar.
- **GOTCHA — ipywidgets 8 removed `overflow_x`/`overflow_y` Layout traits** (they silently no-op; nb02 still passes them and they do nothing). Use the single `overflow` trait with the CSS two-value form `overflow='hidden auto'` (x=hidden so the table never stretches the page, y=auto to scroll inside). Columns are percentage-based + a final `auto` track; cells use `word-break:break-word`.
- Step 3 (`_recipe_pick_table` / `_recipe_pick_boxes`) and Step 4 (`_recipe_ruleout_table` / `_recipe_ruleout_boxes`) share `_RECIPE_SPECS` — all 15 RECIPE_VOCAB recipes with family + lay definition pulled from the playbook's shape-comparison tables. Step 3 = tick the recipe that fits (feeds the `recipe` answer); Step 4 = tick branches to rule out (unticked = remaining; feeds `ruled_out`).
- Step 5 (`_adapt_table` / `_adapt_boxes`) uses `_ADAPT_SPECS` — 9 adaptation items (join keys, column names, filters, output columns, grain, NULLs, duplicates, empty groups/zero-fill, sort/tiebreak); feeds the `adaptations` answer.
- The old `recipe_dd` dropdown was removed; the recipe checkbox table replaces it.

**INTERACTIVE v2 — checkbox tables auto-fill the text fields** (the intro shows "Interactive worksheet v2" so you can confirm the right version loaded):
- Auto-fill is GUARDED by `_auto_last` + `_guarded_fill(ta, fid, val)`: a field is filled only if empty or still holding the last auto value; once hand-edited it is left alone (clear it to re-enable). Each checkbox group has an `.observe(..., names='value')` handler.
- **Step 3** — ticking a recipe (`_recipe_pick_boxes`) fills `named_shape_ta` with "This is a <friendly> because <defn>." A second **moves** table (`_moves_table` / `_moves_boxes`, catalog `_MOVE_SPECS` = 18 SQL building blocks: filter, group+agg, having, join, left-join+zerofill, self-join, window rank, filter-on-rank, running total, lag/lead, date bucket, calendar spine, CASE, pivot, unpivot, dedupe, scalar subquery, CTE) fills `moves_ta` with a "Move 1: … Move 2: …" outline you reorder.
- **Step 4** — ticking branches in `_recipe_ruleout_boxes` fills `ruled_out_ta` with "Not <friendly> because " for ticked rows AND fills `remaining_ta` with the UNticked recipes (one per line). Observer only fires once ≥1 box is ticked so it doesn't dump all 15 on load.
- **Step 5** — `_adapt_boxes` fills `adaptations_ta` with "<item>: " lines. A `load_skeleton_btn` (`on_load_skeleton`) calls `spu.get_code_reference(qtype, islands_flavor, percentile_flavor)` using `STATE['problem']['_meta']` and force-fills `recipe_template_ta` with the canonical engine skeleton (same source as cell 7's Code Reference). No more copy-paste from the playbook.
- `on_feedback` now reads the text fields (which the checkboxes drive) plus the ticked recipe ids for the `recipe` answer.

**⚠ AUTOSAVE INCIDENT (2026-05-26):** the v1 checkbox-table build was silently reverted on disk because JupyterLab was open with the older v1 in memory and its autosave overwrote the .py-side notebook write. ALWAYS have Trinidad do **File → Reload Notebook from Disk BEFORE running** after any on-disk .ipynb edit, and confirm the intro reads "Interactive worksheet v2". If unsure, close the tab and reopen.

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
- **`prompt_to_bullets` now handles three list formats** (in priority order): (1) `•`/`-`/`+` markdown nesting; (2) inline `1. 2. 3.` digit-period numbered lists; (3) plain sentence split with `(N)` parenthesis-step detection. The digit-period branch (added 2026-05-26) fixed a bug where DO-block / DML prompts with numbered rules ("...in sequence: 1. Set tier... 2. Set tier...") rendered each "1." "2." as its own broken bullet because the sentence splitter broke on the period after each number. It detects a CONSECUTIVE run (1.,2.,3.,...) preceded by whitespace and followed by a space, renders the steps as an `<ol>`, prose before as intro bullets, prose after the last step as trailing bullets. Decimals (`0.10`), `DECIMAL(10,2)`, and a lone `1.` never trigger it (run must be length >= 2, marker needs a trailing space).

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
- `feedback_islands_form_choice.md` — Form A (PARTITION BY entity) is NOT a superset of form B; substituting status as the entity collapses every same-status row into one giant island. Use form A only when there's a real entity column.
- `reference_sql_project.md` — newest. Map of the three artifacts, points to this HANDOFF.md as canonical, and the 3-edit recipe for adding a generator qtype.

## COPY-PASTE TO RESUME IN A NEW COWORK (paste this verbatim)

> Continue my SQL prep work from `folders/sql/HANDOFF.md` (canonical). Read it first. Active job: the **recipe-card refactor** — convert every worked card to the two-container format (Problem case study with fabricated DuckDB-verified data + Solution with a `/* */` annotated SQL block), as specified under "NEW RECIPE-CARD FORMAT". Done so far in Single-Table → Window: the running-total, group-benchmark-compare, and LAG/LEAD leaves. **Resume at the "Sliding window aggregate (rolling N days)" leaf**, then FIRST_VALUE/LAST_VALUE, then Sessionization, then the rest of Single-Table, then Multi-Table, Reshape, Procedures. Only convert worked cards (difficulty badge), not templates or "How to pick" cards. Verify div/details balance + DuckDB-check each solution. **Response style: when a task is done, give me ONE sentence plus a one-line next step — no walls of text.** Hints not solutions, lay language, no brand names, no gratuitous hyphens.

## OPENING LINE FOR NEW COWORK

"Picking up your SQL prep. Active job is the recipe-card refactor (Problem + Solution two-container format); done through the LAG/LEAD leaf in Single-Table Window, resuming at the sliding-window leaf. I'll keep task summaries to one sentence + next step. What do you want to tackle?"

## RECENT MNEMONICS WORTH REMEMBERING

- **Pivot mental model:** "row, column, cell" — row key → GROUP BY; column key → CASE WHEN inside aggregate; cell value → THEN clause. SUM for additive, MAX for one value per cell.
- **Top X% direction trick:** order so the BEST rows sit at pr=0; filter `pr <= X/100`. DESC for "top X% highest", ASC for "top X% lowest". Same threshold both directions.
- **NTILE direction:** `ORDER BY metric DESC` for "highest in bucket 1"; ASC for "lowest in bucket 1". NTILE(n) only takes a literal integer.
- **Cross join build order:** skeleton FIRST (CROSS JOIN), actuals LAST (LEFT JOIN with ON). Reversing produces a syntax error or mis-attached actuals. Don't add `FROM <table>` to a `generate_series` CTE — multiplies the date count.
- **Calendar skeleton from data:** for "every week of the month X covers", use MIN(date)'s month bounds (DATE_TRUNC('month', MIN) + INTERVAL '1 month' - INTERVAL '1 day'). Plain MIN/MAX of dates misses trailing/leading empty weeks.
- **Multi-column tiered UPDATE:** two CASE expressions in one SET clause, same branch order in both, ELSE col_name on each. Sequential UPDATEs work for disjoint conditions but the prompt's "single UPDATE" constraint forces the CASE form.
- **DELETE NULL-safe positive WHERE:** write the WHERE for the rows you want to ACT on, not the inverse. `NOT IN` with NULLs evaluates to UNKNOWN for every row.

## 2026-06-20 — interactive Gated Lookup tree
Replaced gl-decide SVG with click-through `#gl-itree` (renderITree + glTree, lay language). 5 leaves: where/rownumber/distincton/case/onclause. Reusable: renderITree(id,tree) before </body>. div 6128/6128, 24 SVGs.

## 2026-06-20 — ALL root decision trees now interactive
Converted remaining 22 *-decide SVG cascades to click-through #{id}-itree (build_all_itrees.py). One renderITree (from gl block) + COWORK_ITREES map registered on load. Cascade->tree: each step yes->leaf, no->next; flat trees (rc/fn) one question many leaves; gi keeps the no-run option -> rc-decide. div 6150/6150, 2 SVGs left (non-tree).

## 2026-06-20 — itree leaves now show a generic code template
build_itree_code.py: added CODE map (101 leaves), code-aware renderITree (Generic template -> dark <pre>), consolidated to ONE script (removed old gl + COWORK_ITREES blocks). div 6148/6148.

## 2026-06-20 — itree leaves + answers now show example DATA
build_itree_examples.py (uses itree_specs.py + itree_content.py): each answer shows a result-preview mini-table; each leaf shows generic template + worked input->output example + recipe link. gl tree hand-authored with gone/NaN/extra cell highlights. 97 leaf anchors, 96 with EX/CODE (rc-decide pointer excluded). renderer itreeTable + renderITree, one script. div 6156/6156.

## 2026-06-20 — left_join_on_filter: 6 real subtypes + Filtered-Join leaves
Engine: SUBTYPES[left_join_on_filter]=date_window/status_category/numeric_threshold/both_sides/sum_coalesce/existence_flag; guidance forces the pinned shape (dropped force_shape_d preroll); _PB_QTYPE -> filtered-join; 6 _PB_SUBTYPE leaf maps. Playbook: added 5 leaves (fj-leaf-status/threshold/bothsides/sumcoalesce/existence) + reused ea-leaf-leftjoin-on for date_window, all DuckDB-verified (build_fj_leaves.py); fj-decide rebuilt as 3-question interactive itree -> 6 leaves with CODE+EX (itree_specs.py/itree_content.py). div 6236/6236, 2 SVGs. nb01 now prints the chosen shape as Subtype.

## 2026-06-21 — Date Operations container + subtypes
New Single-Table container id=date-operations (sibling to row-transform), 5 DuckDB-verified leaves: do-leaf-trunc/extract/arithmetic/duration/daycount (build_date_ops.py); do-decide interactive itree (2-question) -> 5 leaves with CODE+EX. Engine: SUBTYPES[date_operations]=date_trunc_cohort/extract_component/date_arithmetic/duration_between/day_count_boundaries; guidance forces pinned shape; _PB_QTYPE->date-operations; 5 _PB_SUBTYPE maps. nb01 auto-populates subtypes from spu.SUBTYPES (no nb edit). Added date-operations to tab-single header CSS lists. div 6337/6337, 24 itrees, 2 SVGs.

## 2026-06-21 — Date Ops: nested templates + EXTRACT accordion + relative-cutoff
build_date_ops_templates.py: added a collapsible Template card (generic SQL from itree_content.CODE) to all 5 do-leaf-* leaves. do-leaf-extract also gets an EXTRACT field cheatsheet accordion (.do-acc) with 11 expandable parts (year/quarter/month/week/day/dow/doy/hour/minute/second/epoch) + a Collapse all button (new collapseAllInBox JS, scoped to .do-acc). do-leaf-arithmetic gets a 2nd Template card for the "before/within N days" cutoff pattern (anchor to MAX(date) or literal, never CURRENT_DATE; shows WHERE and JOIN ON forms). Accordion items reuse the auto-wired .problem-card collapse. div 6410/6410.

## 2026-06-21 — Procedures root containers restyled to match Reshape
proc-topic/proc-recipe CSS was unused (0 matches); topic-* roots fell back to default (loud blue count badge, no pill/excerpt). build_proc_format.py: each topic-* root now has a grey category pill (Topic / Reference for window-edges), an excerpt line, flex title, and new CSS #tab-procedural .problem-card[id^=topic-] mirroring the #tab-reshape root rules (2.36rem title, pill mute, muted count chip overriding the global blue rule at ~1627). div 6451/6451.

## 2026-06-21 — all containers collapsed by default
Baked `collapsed` into every card-container markup (regex on class="problem-card..." excluding -header/-content etc; 20 roots like row-transform/date-operations/topic-* were missing it). Prevents flash-open before the JS collapse-on-load runs; deep-link hash still expands its target. div 6451/6451.

## 2026-06-21 — dd-decide reworked to surface ROW_NUMBER
The dedup tree now opens with "What decides which row survives?": latest/earliest/any non-id rule -> dd-leaf-rownumber (workhorse, tie-safe); lowest-id branch offers ROW_NUMBER (general) + MIN(id) shortcut + self-join. ROW_NUMBER now an endpoint in 2 paths. Rebuilt via build_itree_examples.py; div 6451/6451.

## 2026-06-21 — anti_join: engine guard + interactive method tree
Engine: anti_join guidance rule #4 forbids count-threshold framings (exactly one / never reordered / only one order); if HAVING COUNT(*)=N is the natural solution it must be rewritten as a true zero-match case. Playbook: converted the static "Which anti-join method?" dt-flow to an interactive itree (aj-method-itree). First question guards the count-threshold trap -> rf-leaf-having (HAVING COUNT); else NOT EXISTS / NOT IN / LEFT JOIN IS NULL. Added CODE+EX for rf-antijoin-notexists/notin/leftnull. 25 trees, div 6459/6459.

## 2026-06-21 — dd-leaf-rownumber composite-key recipe + leaner DELETE
build_dd_composite.py: added a 2nd worked recipe to dd-leaf-rownumber, "Remove Duplicate Refill Records per Patient (composite key)" — duplicate key spans 3 columns (patient_id, medication_code, refill_date); leaner form deletes losers by PK: `DELETE ... WHERE record_id IN (SELECT record_id FROM (... ROW_NUMBER() OVER (PARTITION BY <3 cols> ORDER BY created_at, record_id) AS rn) WHERE rn>1)`. Excerpt note added: "for a multi-column duplicate key, list every key column in PARTITION BY." Badge template-only → 1 problem. DuckDB-verified. Teaching point logged: prefer ROW_NUMBER over RANK (RANK keeps multiple on true ties) and delete-the-losers via IN over keep-survivors via NOT IN (NULL trap).

## 2026-06-21 — gaps-and-islands: entity-vs-label fix + merged-timeline recipe
gi-decide rewritten for the "which form by data shape" confusion: Q2 now "A separate date line per entity, or ONE shared timeline?" with a `sub` clarifier (the ENTITY gets its own line e.g. each student; a status/label like submitted/revised just segments a shared timeline; output-absent columns like student_id are passengers, not the entity). Q3 "CALENDAR-consecutive vs sequence-consecutive" with a `sub` (calendar = a missing day breaks the run; sequence = ignore gaps, runs break when the label changes). build_itree_examples.to_tree now carries an optional `sub` onto question nodes (cascade steps may include `'sub'`). build_gi_streak.py: added a 3rd worked recipe to gi-leaf-date-gap, "Consecutive Streaks by State (two-table merged timeline)" — two tables UNION ALL'd with a state label, then `ROW_NUMBER() OVER (ORDER BY event_date) - ROW_NUMBER() OVER (PARTITION BY state ORDER BY event_date)`; entity = the STATE, student_id dropped (passenger). DuckDB-verified. Badge 2 → 3. Confirmed union_islands/date_sequence maps to gi-leaf-date-gap (no new leaf needed). div 6471/6471.

## STATUS — engine subtype taxonomy (2026-06-21)
qtypes with real SUBTYPES now include: filter_strategies, anti_join, scalar_extract, series_generation, dml_delete, delete_duplicates, unpivot, enrich_join, union_islands, point_in_time, window_lag_lead, window_top_n_per_group, window_sessionization, window_frames, pivot (flavor), percentile_metrics (flavor), **left_join_on_filter (6: date_window/status_category/numeric_threshold/both_sides/sum_coalesce/existence_flag)**, **date_operations (5: date_trunc_cohort/extract_component/date_arithmetic/duration_between/day_count_boundaries)**. anti_join guidance hardened (rule #4) to forbid count-threshold framings — those belong to the HAVING-count recipe. nb01 Subtype dropdown auto-populates from `spu.SUBTYPES`, so engine subtype additions need no notebook edit. After engine edits: reload nb01 / restart kernel.
