# Tableau + SQL + pandas: Medi-Cal Enrollment Project

Working checklist for blog post 1 and LA Care interview prep (SQL + Tableau test, Thursday July 9, 2026).

**Series angle:** every Tableau calculation shown side by side with the SQL and pandas that produce the identical result.

**Working conventions**

- **SAVE AFTER EVERY INSTRUCTION SET — NO EXCEPTIONS.** Update Tableau Public to 2026.2+ (supports local save), then File > Save (Cmd+S) to `folders/ds_blogs/projects/tableau_medi_cal/medi_cal_enrollment.twbx`. Lesson from the July 7 crash that lost Sheets 1 to 6 with zero save points.
- The moment a new sheet is created, rename it BEFORE doing anything else: right click the sheet tab > Rename
- Polish is part of the build: every sheet's formatting and labeling steps are completed in the same session the sheet is created, never deferred
- Sheet names below are the required names for each build step
- Sheet TITLES (the text shown above the view) must clearly and concisely state the purpose or key finding of the sheet — never cute or vague labels like "The Trap"
- **How to read the checklists:**
  - `- [ ]` checkbox = a verified, implementable action (exact formulas, real field names, tested logic)
  - **Question / Purpose / Note** lines in bold = read only context, nothing to click or type
  - Every formula in this file uses ONLY these fields: `Month`, `County`, `Plan Type`, `Plan Category`, `Plan`, `Plan Name Raw`, `Enrollees`, `Suppressed`, or a calculated field created in an earlier step

**Key files**

- `TABLEAU_MASTERY_AND_BLOG_CONTEXT.md` — series context and all confirmed decisions (PART 8)
- `notebooks/nb00_extract_medi_cal_enrollment.ipynb` — extract via CalHHS CKAN API
- `notebooks/nb01_clean_medi_cal_enrollment.ipynb` — clean, QA, export
- `data/medi_cal_enrollment_clean.csv` — the one file Tableau, SQL, and pandas all consume

---

## Phase 0 — Data Pipeline ✅ COMPLETE (July 5, 2026)

**Goal:** one tidy, QA verified CSV so all three tools see identical data.

- [x] nb00: pull latest CSV via CKAN `package_show` (survives monthly filename changes)
- [x] nb00: save date stamped raw copy + `extraction_log.json` (June 2026 vintage)
- [x] nb01: fix column names, drop empty column, parse Month, convert Enrollees to numeric
- [x] nb01: flag suppressed cells (689 rows)
- [x] nb01: harmonize plan names across the 2022 renaming (477 raw names → 184), keep `Plan Name Raw` audit column
- [x] nb01: drop Nov–Dec 2022 duals double reporting (4 rows)
- [x] nb01: merge SCAN product lines sharing one name (743 rows, sums preserved)
- [x] QA: 0 duplicate grain rows; L.A. Care unbroken 234 month series; yearly totals unchanged
- [x] Export `medi_cal_enrollment_clean.csv` (30,431 rows × 8 cols)

---

## Phase 1 — Tableau Orientation ✅ REBUILT July 8, 2026

**The July 7 crash wiped the first build; all 7 sheets were rebuilt July 8 in ~1 session using this file as the script, saved locally to `medi_cal_enrollment.twbx` (Tableau Public 2026.2 local save). All expected values reverified.**

**Goal:** verify the connection end to end by reproducing the nb01 pandas chart in Tableau — the first "same numbers, three ways" parity proof.

- [x] Connect: Connect pane > To a File > Text File > `medi_cal_enrollment_clean.csv`
- [x] Verify field types on the Data Source page (Month = Date, County = geographic role, Enrollees = number, Suppressed = Boolean)
- [x] Sheet 1 — `LA Care Trend` (verified once; REBUILD — expect 234 months matching the nb01 plot)
  - **Question:** how has L.A. Care's LA County enrollment changed month by month since 2007?
  - **Purpose:** prove the Tableau connection reads the data correctly by matching the pandas chart from nb01 exactly
  - [x] Rename the sheet immediately: right click the sheet tab > Rename > `LA Care Trend`
  - [x] Drag Month to the Columns shelf; right click the pill > continuous Month
  - [x] Drag Enrollees to the Rows shelf
  - [x] Filters shelf: County = Los Angeles, Plan = L.A. Care Health Plan, Plan Category = Medical
  - [x] Verify the line matches the nb01 QA plot

---

## Phase 2 — One Calculation Concept per Sheet

**Goal:** build one sheet per calculation type on real managed care data; these are the calculation types the LA Care test is most likely to ask about. One sheet = one blog tab.

### Calculated fields reference — what works and what doesn't

| # | Calculation | Formula | Works? | Why / gotcha |
|---|---|---|---|---|
| 1 | Avg Monthly Enrollment WRONG | `AVG([Enrollees])` | ✅ Yes | Valid but answers the wrong question: averages over plan rows, not months |
| 2 | Avg Monthly Enrollment RIGHT | `SUM([Enrollees]) / COUNTD([Month])` | ✅ Yes | Correct: total divided by number of months |
| 3 | Plan share as row level ratio | `[Enrollees] / county total` | ❌ No | "county total" is not a field; a row cannot see other rows, so the denominator must come from an LOD (see #4) |
| 4 | County Total FIXED | `{ FIXED [County] : SUM([Enrollees]) }` | ✅ Yes | Computes one total per county regardless of what is in the view |
| 5 | % of County | `SUM([Enrollees]) / SUM([County Total FIXED])` | ⚠️ Yes, with care | Works ONLY when the view shows one county and one month scope; a normal Month filter does NOT reduce the FIXED denominator — the Month filter must be added to context (right click the filter pill > Add to Context) |
| 6 | Avg per Plan INCLUDE | `{ INCLUDE [Plan] : SUM([Enrollees]) }` then aggregate with AVG | ✅ Yes | Totals each plan first, then AVG rolls those totals up to the view level |
| 7 | Statewide EXCLUDE | `{ EXCLUDE [County] : SUM([Enrollees]) }` | ✅ Yes | Same statewide value repeated on every county row |
| 8 | County % of State | `SUM([Enrollees]) / MIN([Statewide EXCLUDE])` | ✅ Yes | Must wrap the EXCLUDE in MIN (or AVG/ATTR), never SUM — SUM would multiply the repeated value by the number of underlying rows |
| 9 | County % of State with SUM | `SUM([Enrollees]) / SUM([Statewide EXCLUDE])` | ❌ No | Classic gotcha: the LOD value repeats on every underlying row, so SUM inflates the denominator massively |
| 10 | Running Total / YoY Growth | Quick Table Calculation menu | ✅ Yes | No formula to type; right click the measure pill > Quick Table Calculation |
| 11 | Metric swap CASE | `CASE [Metric Selector] WHEN 'Total Enrollees' THEN SUM([Enrollees]) WHEN 'Share of County' THEN [% of County] END` | ✅ Yes | Both branches are aggregates, so they mix fine |
| 12 | Metric swap including YoY % | CASE with a table calc branch | ❌ Avoid | Mixing a table calculation branch with aggregate branches in one CASE causes compute errors; keep YoY on its own sheet (Sheet 6) |

### Sheet builds

- [x] Sheet 2 — `Avg Enrollment Right vs Wrong` (grain aware aggregation) — built July 7; polish steps below remain
  - **Question:** what is LA County's average monthly Medical enrollment?
  - **Purpose:** show that the same word "average" gives two different numbers depending on the aggregation, because each row is one plan's month, not one month
  - **Field names used in the workbook:** `Incorrect Avg Monthly Enrollment` = `AVG([Enrollees])` and `Correct Avg Monthly Enrollment` = `SUM([Enrollees]) / COUNTD([Month])`
  - [x] Rename the sheet tab: right click the sheet tab > Rename > `Avg Enrollment Right vs Wrong` (was `The Trap`; renamed per title convention)
  - [x] Drag County to the Filters shelf > keep Los Angeles
  - [x] Drag Plan Category to the Filters shelf > keep Medical
  - [x] Create both calculated fields and place them on Text on the Marks card
- [x] Sheet 2 polish (verified once; REBUILD — expect Correct 2,546,791 vs Incorrect 437,233)
  - [x] Right click the sheet tab (currently `The Trap`) > Rename > `Avg Enrollment Right vs Wrong`
  - **Note:** Measure Names on Rows only works when the numbers come from ONE Measure Values pill on Text, not from two separate pills — steps below rebuild it that way
  - [x] Verify the formula: fixed July 7 — numerator was AVG instead of SUM; correct value confirmed at 2,546,791
  - [x] On the Marks card right click the `AGG(Correct...)` pill > Remove
  - [x] On the Marks card right click the `AGG(Incorrect...)` pill > Remove
  - [x] Drag Measure Values (bottom of the Data pane) onto the Text button on the Marks card
  - [x] On the Measure Values shelf that appears, right click every pill EXCEPT the two calculated fields (SUM(Enrollees), CNT(csv), Latitude, Longitude) > Remove
  - [x] Confirm Measure Names is on the Rows shelf (drag it there if not) — two labeled rows appear
  - [x] In the Data pane right click `Incorrect Avg Monthly Enrollment` > Default Properties > Number Format > Number (Custom) > 0 decimals, thousands separators
  - [x] Repeat the number format step for `Correct Avg Monthly Enrollment`
  - [x] Row header aliases: skipped — the renamed field names already read clearly as labels
  - [x] Format menu > Font > under Worksheet set Pane to size 14
  - [x] Double click the sheet title > line 1 `Aggregation Method Changes LA County's Average Enrollment 6x` > line 2 smaller font `Correct = 2.5M members per month; averaging plan rows gives 437K — LA County Medical, 2007 to 2026`

- [x] Sheet 3 — `FIXED % of County` (verified once; REBUILD — expect L.A. Care 59.4%, Health Net 30.5%, Kaiser 9.6%, sum 100%; BOTH Month and Plan Category filters in context)
  - **Question:** what share of LA County's Medi-Cal enrollment does each plan hold right now (June 2026)?
  - **Purpose:** a share needs a denominator (the county total) computed at a different level than the view; that is what FIXED does (table row 3 explains why no plain formula can do this)
  - [x] Rename the sheet immediately: right click the sheet tab > Rename > `FIXED % of County`
  - [x] Analysis menu > Create Calculated Field > name `County Total FIXED` > formula `{ FIXED [County] : SUM([Enrollees]) }` (table row 4)
  - [x] Analysis menu > Create Calculated Field > name `% of County` > formula `SUM([Enrollees]) / SUM([County Total FIXED])` (table row 5)
  - [x] Drag Month to the Filters shelf > choose Month/Year in the dialog > keep June 2026 only
  - [x] Right click the Month filter pill > Add to Context (the pill turns gray) — REQUIRED, see table row 5
  - [x] Drag County to the Filters shelf > keep Los Angeles
  - [x] Drag Plan Category to the Filters shelf > keep Medical
  - [x] Drag Plan to the Rows shelf
  - [x] Drag `% of County` to the Columns shelf (bar chart appears)
  - [x] On the toolbar click the sort descending button
  - [x] Right click the % of County axis > Format > set Numbers to Percentage, 1 decimal
  - Polish (do now, not later):
    - [x] Drag `% of County` from the Data pane to the Label button on the Marks card (each bar shows its %)
    - [x] In the toolbar open the Fit dropdown > Fit Width
    - [x] Right click the `Plan` field label above the row headers > Hide Field Labels for Rows
    - [x] Double click the sheet title > line 1 `L.A. Care Holds the Largest Share of LA County Medi-Cal` > line 2 smaller font `Plan share of county enrollment, Medical, June 2026 (FIXED LOD)`
  - **Note:** the bars should sum to 100% across plans; L.A. Care should be the largest at roughly half the county
  - **Lesson learned (July 7):** BOTH the Month filter AND the Plan Category filter had to be added to context; with Medical not in context the denominator included Dental and PACE and shares summed to 92.2%. Rule: a filter that should shrink the FIXED denominator goes in context; a filter that only hides slices stays normal. Also: mark labels have their own number format (pill > Format > Pane tab), separate from the axis format.
- [x] Sheet 4 — `INCLUDE Avg per Plan` (verified once; REBUILD — expect Local Initiative 652,110 vs 434,740; Plan Type on Rows, NOT Plan)
  - **Question:** what is the typical plan size within each plan type (Two-Plan vs COHS vs Regional)?
  - **Purpose:** "typical plan size" means total each plan FIRST, then average those totals; INCLUDE adds the plan level into the calculation even though the view only shows plan types
  - [x] Rename the sheet immediately: right click the sheet tab > Rename > `INCLUDE Avg per Plan`
  - [x] Analysis menu > Create Calculated Field > name `Avg per Plan INCLUDE` > formula `{ INCLUDE [Plan] : SUM([Enrollees]) }` (table row 6)
  - [x] Drag Month to the Filters shelf > choose Month/Year > keep June 2026 only
  - [x] Drag Plan Category to the Filters shelf > keep Medical
  - [x] Drag Plan Type to the Rows shelf
  - [x] Drag `Avg per Plan INCLUDE` to the Columns shelf
  - [x] Right click the `Avg per Plan INCLUDE` pill on the Columns shelf > Measure > Average
  - [x] Drag Enrollees to the Columns shelf, to the right of the existing pill
  - [x] Right click the SUM(Enrollees) pill > Measure > Average
  - Polish (do now, not later):
    - [x] In the Data pane right click `Avg per Plan INCLUDE` > Default Properties > Number Format > Number (Custom), 0 decimals, thousands separators
    - [x] Same number format for `Enrollees`
    - [x] Drag each measure pill's value to Label via the Label button on the Marks card (or tick Show mark labels)
    - [x] In the toolbar open the Fit dropdown > Fit Width
    - [x] Right click each axis > Edit Axis > rename titles to `Typical plan size (INCLUDE)` and `Avg of raw rows (misleading)`
    - [x] Double click the sheet title > line 1 `Typical Plan Size Differs Sharply by Plan Type` > line 2 smaller font `Average total enrollment per plan (INCLUDE LOD) — Medical, June 2026`
  - **Note:** now compare the two bars per plan type: AVG(Enrollees) averages raw county rows (small number), the INCLUDE version averages whole plan totals (the honest "typical plan size")
  - **Build note (July 7):** the view must sit at Plan Type (NOT Plan) on the Rows shelf for the INCLUDE comparison to mean anything — first attempt used Plan and was corrected.
- [x] Sheet 5 — `EXCLUDE Benchmark` (verified once; REBUILD — expect LA County 27.5%, 58 counties)
  - **Question:** what share of statewide enrollment does each county contribute?
  - **Purpose:** the denominator must ignore the county breakdown in the view; EXCLUDE removes a dimension from the calculation so one statewide number lands on every county row
  - [x] Rename the sheet immediately: right click the sheet tab > Rename > `EXCLUDE Benchmark`
  - [x] Analysis menu > Create Calculated Field > name `Statewide EXCLUDE` > formula `{ EXCLUDE [County] : SUM([Enrollees]) }` (table row 7)
  - [x] Analysis menu > Create Calculated Field > name `County % of State` > formula `SUM([Enrollees]) / MIN([Statewide EXCLUDE])` (table row 8 — note MIN, never SUM, see row 9)
  - [x] Drag Month to the Filters shelf > choose Month/Year > keep June 2026 only
  - [x] Drag Plan Category to the Filters shelf > keep Medical
  - [x] Drag County to the Rows shelf
  - [x] Drag `County % of State` to the Columns shelf
  - [x] On the toolbar click the sort descending button
  - [x] Right click the axis > Format > Numbers > Percentage, 1 decimal
  - Polish (do now, not later):
    - [x] Drag `County % of State` from the Data pane to the Label button on the Marks card
    - [x] In the toolbar open the Fit dropdown > Fit Height (58 counties need vertical room)
    - [x] Right click the `County` field label above the row headers > Hide Field Labels for Rows
    - [x] Double click the sheet title > line 1 `LA County Holds Roughly a Third of Statewide Medi-Cal Enrollment` > line 2 smaller font `County share of statewide enrollment (EXCLUDE LOD) — Medical, June 2026`
  - **Note:** LA County should be roughly a third of the state; all bars together sum to 100%

- [x] Sheet 6 — `Running Total + YoY` ✅ REBUILT July 8 (discrete YEAR+MONTH columns; axis format gotchas: avoid Currency, set Millions with 0 decimals)
  - **Question:** how fast is statewide enrollment growing, cumulatively and year over year?
  - **Purpose:** growth questions transform numbers ALREADY in the view (each month compared to prior months); that is what table calculations do and LODs cannot
  - [ ] Rename the sheet immediately: right click the sheet tab > Rename > `Running Total + YoY`
  - [ ] Drag Month to the Columns shelf > right click the pill > choose Year (UPPER discrete group)
  - [ ] Drag Month to the Columns shelf again, right of YEAR(Month) > right click it > choose Month (UPPER discrete group)
  - **Lesson from first build:** Year over Year Growth stays greyed out with a continuous month axis — it requires the discrete YEAR + MONTH hierarchy on Columns
  - [ ] Drag Plan Category to the Filters shelf > keep Medical
  - [ ] Drag Enrollees to the Rows shelf
  - [ ] Right click the SUM(Enrollees) pill on the Rows shelf > Quick Table Calculation > Running Total (table row 10)
  - [ ] Drag Enrollees to the Rows shelf again, to the right of the first pill (second axis appears below)
  - [ ] Right click the second SUM(Enrollees) pill > Quick Table Calculation > Year over Year Growth
  - Polish (do now, not later):
    - [ ] Right click the Running Total axis > Format > Numbers > Number (Custom) > Display Units: Millions, 1 decimal
    - [ ] Right click the YoY axis > Format > Numbers > Percentage, 1 decimal
    - [ ] Right click the Running Total axis > Edit Axis > title `Cumulative member months (millions)`
    - [ ] Right click the YoY axis > Edit Axis > title `Year over year growth`
    - [ ] In the toolbar open the Fit dropdown > Fit Width
    - [ ] Double click the sheet title > line 1 `Medi-Cal Grew Through ACA and COVID, Then Shrank With Redeterminations` > line 2 smaller font `Statewide running total and YoY change (table calculations) — Medical, 2007 to 2026`
  - **Note:** hover the 2014 months on the YoY line — the ACA expansion spike should be obvious; the 2024 months go negative (redeterminations)

- [x] Sheet 7 — `Top N + Metric Swap` ✅ BUILT July 8 — Top 10 statewide, L.A. Care 2,102,545; Share of County swap verified (L.A. Care 59.35% matches Sheet 3)
  - **Build notes (July 8):** parameter is a control knob, not a measure — the CASE field `Selected Metric` goes on Columns, never the parameter itself. Top N parameter: Step size 1.
  - **PREREQUISITE:** Sheet 3 must be built first — this sheet reuses the `% of County` calculated field created there
  - **Question:** what are the N biggest plans in California, viewed by whichever metric the reader picks?
  - **Purpose:** parameters let a viewer change N and swap the displayed metric without editing the sheet; a parameter does NOTHING until it is wired into a filter or calculation
  - [x] Rename the sheet immediately: right click the sheet tab > Rename > `Top N + Metric Swap`
  - [x] In the Data pane click the dropdown arrow (top right of the pane) > Create Parameter > name `Top N` > Data type Integer > Allowable values Range 5 to 20 > Current value 10
  - [x] In the Data pane click the dropdown arrow > Create Parameter > name `Metric Selector` > Data type String > Allowable values List > add `Total Enrollees` and `Share of County`
  - [x] Analysis menu > Create Calculated Field > name `Selected Metric` > formula `CASE [Metric Selector] WHEN 'Total Enrollees' THEN SUM([Enrollees]) WHEN 'Share of County' THEN [% of County] END` (table row 11; YoY stays out on purpose, see row 12)
  - [x] Drag Month to the Filters shelf > choose Month/Year > keep June 2026 only
  - [x] Right click the Month filter pill > Add to Context (needed because `% of County` uses FIXED)
  - [x] Drag Plan Category to the Filters shelf > keep Medical
  - [x] Drag Plan to the Filters shelf > in the filter dialog open the Top tab > By Field > Top, type `[Top N]` in the value box, by SUM(Enrollees)
  - [x] Drag Plan to the Rows shelf
  - [x] Drag `Selected Metric` to the Columns shelf
  - [x] Right click each parameter in the Data pane > Show Parameter (both controls appear on the right)
  - [x] Double click the sheet title > insert the parameter: click Insert > Parameters.Metric Selector
  - [x] Test: change Top N and Metric Selector in the controls and watch the chart respond
  - Polish (do now, not later):
    - [x] On the toolbar click the sort descending button
    - [x] Drag `Selected Metric` from the Data pane to the Label button on the Marks card
    - [x] In the toolbar open the Fit dropdown > Fit Width
    - [x] Right click the `Plan` field label above the row headers > Hide Field Labels for Rows
    - [x] Verify the dynamic title reads naturally with both Metric Selector values (it was inserted in the earlier title step)
    - **Note:** number formatting stays Number (Standard) here because the CASE swaps between a count and a percent; format per metric is not possible in one field

---

## Phase 3 — Dashboard Assembly and Publish ✅ COMPLETE (July 8, 2026)

**Goal:** assemble the sheets into one interactive dashboard (the LA Care test also covers dashboard construction) and publish it to Tableau Public so the blog can embed it.

- [x] New Dashboard: set size, drag in trend, TOP N bar, and map sheets using tiled layout containers
- [x] Build a KPI card sheet named `KPI Cards` (rename immediately; current statewide enrollment, YoY %)
- [x] Build a filled county map named `County Map` (rename immediately; County on Detail, Enrollees on Color, Marks card > Map)
- [x] Add a Filter action: Dashboard menu > Actions > Add Action > Filter (map → other sheets)
- [x] Add a Highlight action for Plan
- [x] Dynamic dashboard title driven by the Metric parameter
- [x] Check for stray filter pills skewing KPI numbers
- [x] Publish to Tableau Public and record the embed link
- [x] Practice saying out loud, for each sheet: WHY this calculation type (row level vs aggregate vs LOD vs table calc) and what the SQL equivalent is

---

**As built (differs from original plan):**

- Dashboard name: `Enrollment Explorer`; dashboard title carries context; sheet titles reduced to one line labels (design rule: one hierarchy, context stated once)
- Dashboard sheets: `KPI Cards` (horizontal strip, Entire View fit, title hidden, full number format), `County Trend` (duplicate of LA Care Trend with Plan/County filters removed so the map action drives it), `County Map` (stepped orange choropleth), `Top N + Metric Swap`
- One filter action `County click re ranks top plans`: source County Map, targets County Trend + Top N + KPI Cards; clearing shows statewide. GOTCHA: in the action dialog the Source/Target dropdowns must point at the DASHBOARD, then check sheets in the list — pointing them at a sheet leaves the checklist empty and the action never fires
- Highlight action skipped (only one dashboard sheet shows Plan)
- Dynamic parameter titles skipped (not copy paste friendly)
- **Published July 8:** https://public.tableau.com/views/CaliforniaMedi-CalManagedCareEnrollmentExplorer/EnrollmentExplorer
- Embed code saved to `tableau_embed.html` for the blog build

---

## Phase 4 — SQL + pandas Parity ✅ COMPLETE (July 8, 2026)

**Goal:** prove every Tableau number is reproducible in code — the heart of the blog's pedagogy.

- [x] nb02 (`nb02_sql_pandas_parity.ipynb`): DuckDB SQL + pandas side by side for all 6 concept sheets
- [x] Six parity tables exported to `data/parity/`
- [x] Verified to the digit against Tableau: 2,546,791/437,233 · FIXED 59.4/30.5/9.6 (Σ=100.0) · INCLUDE 652,110 vs 434,740 · EXCLUDE LA 27.5% (Σ=100.0) · June 2026 members 12,888,522, YoY -8.2% · LA Top N = 7 plans, L.A. Care 2,102,545
- **Note:** the Top N parity uses the redesigned logic (filter county first, then rank) matching the July 8 dashboard fix (Action (County) pill added to context on the Top N sheet)

---

## Phase 5 — Blog Build ✅ DRAFT COMPLETE (July 8, 2026) — pending Trinidad's review + git push

**Goal:** publish blog post 1 as a Data Story using the standalone tabbed HTML pattern (model: `ds_loan_default_tradeoff_matrix.html`).

- [x] Create `folders/ds_blogs/ds_tableau_sql_pandas_medi_cal.html` with 9 tabs:
  - [x] 1. The Data & The Question
  - [x] 2. Row Level vs Aggregate (the trap)
  - [x] 3. FIXED
  - [x] 4. INCLUDE
  - [x] 5. EXCLUDE
  - [x] 6. Table Calculations
  - [x] 7. Parameters
  - [x] 8. The Dashboard (Tableau Public embed)
  - [x] 9. Cheat Sheet (Tableau ↔ SQL ↔ pandas translation table)
- [x] Each concept tab: business question → Tableau (viz + click path) → SQL → pandas → parity table
- [x] Add entry to `static/data/posts.json` (category Data Stories, categoryClass `ds`)
- [x] Add card to `ds_blog_landing.html`
- [x] Hero counter left at "170+" (rounded hardcoded number, still accurate)
- [x] QA: div balance verified (101/101); Trinidad to eyeball in browser before push
- [ ] git push

---

## Later Posts (committed order)

1. **Post 2:** Managed Care Performance Monitoring Dashboard Report (HEDIS quality measures) — Trinidad wants to learn HEDIS
2. **Stretch:** HCAI Hospital ED Encounters by Facility (LA County DHS relevance)
