# Handoff: Trinidad's SQL Practice & Playbook

Updated 2026-06-06. Pick up here for the next cowork session. This file is canonical; the copy in `Coding Support/cowork_handoff.md` is the paste-ready opener.

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
- **`series_generation`** (postgresql) — generate_series as the centerpiece: date/number spine over a fixed range, CROSS JOIN entities, LEFT JOIN actuals + COALESCE 0; integer series for fixed buckets; per-row range expansion via CROSS JOIN LATERAL. Ranges literal or MIN/MAX-derived, never CURRENT_DATE.
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

## OPENING LINE FOR NEW COWORK

"Picking up your SQL prep — playbook (`sql_problem_patterns.html`) + two notebooks (`nb01_sql_practice` analytical, `nb02_analyst_interview_drills`). Generator has **31 qtypes** incl. the recent `root_cause_analysis` (postgres-only, 7 archetypes, difficulty-aware). Multi-Table tab now has a merged Quick Reference master card + 5 recipes (Look Up Columns, Join Tables Then Aggregate, Gated Lookup, Matchup & Leaderboard, Rank Within Groups). Reshape tab has 5 recipes (Series Generation is now top-level). All 30 generic templates per method are nested collapsable cards with step bullets. Hints not solutions, single sentences, lay language, atomic table cells, no brand names. What are you working on?"

## RECENT MNEMONICS WORTH REMEMBERING

- **Pivot mental model:** "row, column, cell" — row key → GROUP BY; column key → CASE WHEN inside aggregate; cell value → THEN clause. SUM for additive, MAX for one value per cell.
- **Top X% direction trick:** order so the BEST rows sit at pr=0; filter `pr <= X/100`. DESC for "top X% highest", ASC for "top X% lowest". Same threshold both directions.
- **NTILE direction:** `ORDER BY metric DESC` for "highest in bucket 1"; ASC for "lowest in bucket 1". NTILE(n) only takes a literal integer.
- **Cross join build order:** skeleton FIRST (CROSS JOIN), actuals LAST (LEFT JOIN with ON). Reversing produces a syntax error or mis-attached actuals. Don't add `FROM <table>` to a `generate_series` CTE — multiplies the date count.
- **Calendar skeleton from data:** for "every week of the month X covers", use MIN(date)'s month bounds (DATE_TRUNC('month', MIN) + INTERVAL '1 month' - INTERVAL '1 day'). Plain MIN/MAX of dates misses trailing/leading empty weeks.
- **Multi-column tiered UPDATE:** two CASE expressions in one SET clause, same branch order in both, ELSE col_name on each. Sequential UPDATEs work for disjoint conditions but the prompt's "single UPDATE" constraint forces the CASE form.
- **DELETE NULL-safe positive WHERE:** write the WHERE for the rows you want to ACT on, not the inverse. `NOT IN` with NULLs evaluates to UNKNOWN for every row.
