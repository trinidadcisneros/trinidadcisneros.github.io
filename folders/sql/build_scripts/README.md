# Playbook build scripts (persistent copies)

These are the generators for `../sql_problem_patterns.html`. They were developed in
the Cowork scratchpad (which is wiped each session) — this folder is the persistent
copy so the next session can re-run/extend them.

> Paths inside the scripts point at the Cowork VM mount
> (`/sessions/.../mnt/sql/sql_problem_patterns.html`). If you re-run them in a new
> session, update the `PATH=` line at the top of each script to the current mount,
> and make sure `eabuild.py` / `itree_specs.py` / `itree_content.py` are on
> `sys.path` (they `sys.path.insert(0, '/sessions/.../mnt/outputs')` — change to this
> folder, or copy these files into the scratchpad first).

## The interactive decision-tree system (current; replaced the old SVG flowcharts)

Every "How to pick" container holds `<div id="{id}-itree" class="itree"></div>`. A single
`<script>` near `</body>` defines `itreeTable()` + `renderITree()` and a `COWORK_ITREES`
map, registered on `DOMContentLoaded`. To change ANY tree:

1. `itree_specs.py` — `SPECS['{id}']` is a cascade: a list of steps, each
   `{'q':[lines], 'sub'(optional):'clarifier', 'branches':[ {'label','leaf':(title,sub,anchor)} | {'label','down':True} ]}`.
   One `down` per non-final step continues to the next step; `leaf` branches are endpoints.
2. `itree_content.py` — `CODE[anchor]` = generic template string; `EX[anchor] = (inCols, inRows, outCols, outRows)`
   worked example. Cells `'NaN'`/`'NULL'` auto-highlight.
3. `build_itree_examples.py` — rebuilds ALL trees: reads SPECS + CODE + EX, builds
   `ALLTREES` keyed by `{id}-itree`, removes the old `<script>`, writes ONE consolidated
   script, runs a div-balance assert, writes the file. The `gl` tree is hand-authored
   inline (rich gone/NaN/extra cells). `to_tree()` carries an optional `sub` clarifier
   onto a question node.

Run order to edit a tree: edit `itree_specs.py` (+ `itree_content.py` if new leaf
anchors) → `python3 build_itree_examples.py` → it re-asserts balance and writes.

## Worked recipe cards — `eabuild.py`

`build_card(card_dict)` renders the standard collapsed Problem + Solution two-container
card; `verify(card_dict)` runs the SQL in DuckDB and compares to `exp_rows` (use
`verify_sql` if the displayed SQL differs, `check_sql` for a trailing SELECT after a
DELETE/UPDATE). `find_block(text, anchor)` / `balance_report(text)` help splice.
One-off builders here (`build_fj_leaves.py`, `build_date_ops*.py`, `build_gi_streak.py`,
`build_dd_composite.py`, `build_proc_format.py`) show the pattern: define card dicts,
verify, then splice into a leaf's `problem-card-content` and bump its count badge.

## Invariant after EVERY edit
`<div>` opens == closes, final depth 0, min depth ≥ 0, `<svg>` == `</svg>`,
`function renderITree` appears exactly once. The build scripts assert these.
