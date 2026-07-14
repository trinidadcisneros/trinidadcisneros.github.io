# Exam Prep Project 1 — Medicare Advantage Star Ratings (Plan Quality)

Tableau + SQL + pandas practice project for the **Salesforce Certified Tableau Data Analyst** exam, built on public health plan data. Same series and angle as the Medi-Cal posts (`../tableau_hedis/`, `../tableau_medi_cal/`): use SQL and pandas as the reference point for what Tableau does under the hood, this time on Medicare Advantage plan quality (CMS Star Ratings), while deliberately covering exam objectives.

**Emphasis:** Explore and Analyze (the 41% domain). **LOD appears in this project, and so does a dedicated Context (context filters) walkthrough.** This project is also the designated **live database connection** practice: one sheet connects live to a Snowflake table so the exam's "live vs extract / relational database" objective is covered.

---

## Working conventions (binding, carried from the Medi-Cal posts)

- **SAVE AFTER EVERY INSTRUCTION SET, NO EXCEPTIONS.** File > Save (Cmd+S) to the project `.twbx`
- Rename every new sheet BEFORE doing anything else (right click tab > Rename)
- Polish is part of the build, never deferred; sheet titles state the purpose or key finding
- **Voice: first person "I" or third person, NEVER "we"** anywhere in the blog output
- **No hyphens or dashes except compound nouns** (e.g. "year-over-year" is fine, gratuitous hyphens are not)
- Tabs and sections named by the **method**, not the subject
- Every SQL and pandas code block is preceded by plain-language bullets naming the approach ("SQL approach: a window function to...")
- No internal dev-note captions in the final output
- Show title and tab-name options and WAIT for approval before applying them across the page, landing, and posts.json
- Trinidad drives all Tableau Desktop work step by step and returns screenshots; Claude does data prep, SQL/pandas parity code, and the blog HTML
- Every figure verified in Tableau, DuckDB SQL, and pandas before it goes in the post

---

## Exam objectives this project targets

| Exam domain (weight) | Objectives exercised here |
|---|---|
| Connect and Transform (24%) | Live vs extract; connect to a relational database (**Snowflake**); join Star Ratings + plan/contract info + enrollment; rename fields; organize fields into folders |
| Explore and Analyze (41%) | Calculated fields (logical, number, type conversion); table calcs (difference, year-over-year, rank); filters and **CONTEXT** (benchmark within a state); parameters (pick measure or year, with a reference line); sets and bins (star tiers); hierarchies (parent org to contract to plan); Analytics pane (reference lines); **LOD FIXED** (plan vs national or state benchmark) |
| Create Content (26%) | Bar, line, scatter, dual axis; a dashboard with filter and highlight actions; formatting |
| Publish and Manage (9%) | Publish workbook to Tableau Public; the live Snowflake data source |

---

## Key files

- `notebooks/nb00_extract_star_ratings.ipynb` — download the CMS Star Ratings tables, plan/contract info, and enrollment; log what was pulled
- `data/raw/` — immutable raw downloads; `data/extraction_log.json`
- `nb01_clean_star_ratings.ipynb` — clean and join into analysis CSVs (created after the nb00 profile is reviewed)
- `nb02_sql_pandas_parity.ipynb` — reproduce every blog figure in DuckDB SQL and pandas, asserted against Tableau

---

## Data source

- **CMS Part C and D Star Ratings** (contract and plan level, multiple years): https://www.cms.gov/medicare/health-drug-plans/part-c-d-performance-data
- Companion: CMS Medicare Advantage enrollment (contract level) for plan size context
- Notes to verify in the profile: suppressed or masked values, the contract ID as the join key, measure name changes across years, and the star scale (1 to 5, half-star increments)

---

## Phases

### Phase 0 — Extract and Profile
- [x] `nb00` run July 10, 2026: pulled 2024, 2025, 2026 Star Ratings Data Table ZIPs (consistent format), unzipped and profiled; `extraction_log.json` written
- [x] `nb01` run: `data/star_summary_clean.csv` (2415 rows = one row per contract per year; 769 to 857 contracts/year; Overall stars 2.0 to 5.0, 833 rows unrated/NaN). National average overall star: 2024 = 3.68, 2025 = 3.65, 2026 = 3.65 (the benchmark)
- [x] **Hero decided: L.A. Care Health Plan, contract H1224** (parent: Local Initiative Health Authority for LA County). Overall stars: 2024 = not rated (too new), 2025 = 3.0, 2026 = 3.0. Below the ~3.65 national average; the narrative is a new Medicare plan that launched below the bar and has held at 3.0.
- [x] `nb01` Part 2 (measure level) run: `data/star_measures_clean.csv` (110,458 rows; 66,329 rated). One row per contract per year per measure, with its Domain. Two-row header (Domain row above Measure row) and Windows-1252 encoding both handled in the notebook.
- [x] **The finding.** L.A. Care improved underneath but stayed at 3.0 overall: Part C 2.5 to 3.0, Part D 3.5 to 4.0 (2025 to 2026). The drag is the health plan side, specifically post-discharge care and member experience. 2026 measures furthest below the national average: Medication Reconciliation Post-Discharge 1.0 vs 3.82; Care Coordination 1.0 vs 3.49; Customer Service 1.0 vs 3.46; Transitions of Care 1.0 vs 3.11; Plan All-Cause Readmissions 1.0 vs 2.94; Care for Older Adults Medication Review 2.0 vs 4.14. Strongest: Reducing the Risk of Falling 5.0 vs 2.71, and the Part D drug measures. Weakest domains: Member Experience with Health Plan (2.17), Managing Chronic Conditions (2.53, 15 measures).

**Data quirks to document in the post:**
- The measure set changes year to year (46 measures in 2024 and 2025, 45 in 2026) and codes are reused with new meanings (C04 was "Monitoring Physical Activity" in 2024/2025 and "Improving or Maintaining Physical Health" in 2026), so a measure code CANNOT be naively compared across years.
- The Summary file has NO state or county, so a choropleth needs a join to CMS enrollment (contract to state). Maps are therefore deferred to Project 3.
- L.A. Care has only two rated years, so year-over-year and trend table calcs are demonstrated on the national average and on parent-org rollups; L.A. Care's own flat 3.0 is itself the finding.

### Phase 1 — Tableau build: PROGRESS (workbook `medicare_star_ratings.twbx`, 2 data sources: star_summary_clean + star_measures_clean)

- [x] **Sheet 1 `Stars vs National`** — DONE. L.A. Care (filtered Contract = H1224) vs the national benchmark. Calc `National Avg Star` = `{ FIXED [Year] : AVG([Overall Stars]) }`. Dual axis + Synchronize, right axis header hidden. Context demo performed and reverted (Add to Context collapsed the benchmark to 3.0 and the two lines overlapped; proof that Context decides what a FIXED calc can see). Values: L.A. Care blank 2024, 3.0 in 2025 and 2026; national 3.68 / 3.65 / 3.65.
- [x] **Sheet 2 `Star Distribution 2026`** — DONE. Overall Stars as a discrete dimension on Columns, CNTD(Contract) on Rows, Year = 2026, nulls excluded. Calcs `LA Care Star` = `{ FIXED [Year] : MAX(IF [Contract] = "H1224" THEN [Overall Stars] END) }` and `Beats L.A. Care` = `[Overall Stars] > [LA Care Star]` on Color. Counts: 2.0=2, 2.5=21, 3.0=111, 3.5=175, 4.0=116, 4.5=73, 5.0=18 (516 rated). **382 of 516 (74%) beat L.A. Care.**
- [x] **Sheet 3 `Where L.A. Care Loses Stars`** — DONE (uses star_measures_clean). Calcs `National Avg by Measure` = `{ FIXED [Year], [Measure Code] : AVG([Stars]) }` and `Gap vs National` = `AVG([Stars]) - AVG([National Avg by Measure])`. Diverging bars sorted ascending, Entire View, 2 unrated measures filtered out, one long label aliased to `Follow-up after ED Visit (High-Risk Chronic)`.
- [ ] **Sheet 4 `Improving Underneath`** — nearly done. Slope chart, 2025 to 2026 (2024 excluded, L.A. Care unrated). Measure Values on Rows with AVG(Overall Star), AVG(PartC Stars), AVG(PartD Stars); Measure Names on Color; axis fixed 1 to 5; labels on. Aliases: `Overall`, `Part C (health plan)`, `Part D (drug plan)`. NOTE: `Overall Star` is a DUPLICATE of `Overall Stars`, created so this sheet can alias it "Overall" while Sheet 1 keeps the "L.A. Care" alias (aliases are data-source wide). **Remaining: add the sheet title.** Finding: Part C 2.5 to 3.0, Part D 3.5 to 4.0, Overall flat at 3.0.
- [x] **Sheet 4 `Improving Underneath`** — DONE. Slope chart 2025 to 2026 (2024 excluded, unrated). Measure Values on Rows (AVG of `Overall Star`, `PartC Stars`, `PartD Stars`), Measure Names on Color, axis fixed 1 to 5, labels on. `Overall Star` is a DUPLICATE of `Overall Stars` so this sheet can alias it "Overall" while Sheet 1 keeps "L.A. Care" (aliases are data-source wide). Finding: Part C 2.5 to 3.0, Part D 3.5 to 4.0, Overall flat at 3.0.
- [x] **Sheet 5 `Parent Org Quality.`** — DONE. Tableau-native cleaning practiced here: `Parent Org (group)` merges the Molina and Samaritan duplicates, and the 12 ALL CAPS members were renamed inside the Edit Group dialog (group fields have no Aliases option; rename = "group of one, then rename"). Nulls filtered (45 parents with no rated contract). Parameter `Min Rated Contracts` (Integer, range 1 to 10, current 5) + calcs `Rated Contracts` = `COUNTD(IF NOT ISNULL([Overall Stars]) THEN [Contract] END)` and `Meets Min Contracts` = `[Rated Contracts] >= [Min Rated Contracts]` (boolean on Filters = True; a measure filter's value box will NOT accept a parameter, hence the boolean). Rated Contracts also sits on Rows as a DISCRETE pill so the count is its own column, not a second number on the bar. Parameter is inserted live in the title. At 5: 17 companies, Alignment 4.4 top, Centene/HCSC/Molina 3.3 bottom. At 10: the 8 giants.
- [x] **Sheet 6 `Who Is Improving`** — DONE. Highlight table (Square mark), Year on Columns, `Parent Org (group)` on Rows, AVG(Overall Stars) with a **Difference From table calc, Relative to First, Compute Using Table (across)**, duplicated onto Color (Red-Blue Diverging, colorblind safe). Filter `Big Company` = `{ FIXED [Parent Org (group)] : COUNTD(IF [Year] = 2026 AND NOT ISNULL([Overall Stars]) THEN [Contract] END) } >= [Min Rated Contracts]` (a view-level COUNTD would count per YEAR and punch holes in the trend; FIXED pins it to the company). Finding: Devoted Health is the highest-scoring giant yet down 0.5 since 2024, while Centene (+0.4) and Molina (+0.3), the lowest scorers, are climbing.
- [ ] **NEXT: dashboard `L.A. Care Medicare Scorecard`**, then publish, then the Snowflake live-connection exercise, then nb02 parity, then the blog page.
- **Important:** Tableau Public allows **extracts only, no live database connections**, so the Snowflake live connection cannot be published. Do it as a local exercise and use the limitation itself as the live-vs-extract teaching point in the blog.

### Phase 1 — original candidate sheets
1. `Overall Star Trend`: a contract's overall star vs the national (and state) average over years — **FIXED LOD benchmark + a Context section** showing how a state filter must be added to context to shrink the benchmark
2. `Year over Year Star Change`: Difference From table calc (relative to Previous)
3. `Star Tier Distribution`: bins or sets grouping contracts into star tiers
4. `Measure Explorer`: a parameter to pick the quality measure, driving the ranking and a reference line
5. `Stars by State`: choropleth map of average overall stars
6. `Live vs Extract`: the same table connected live to Snowflake, next to an extract, to narrate the difference

### Phase 2 — Dashboard and publish
- [ ] Assemble a quality scorecard dashboard with a filter and a highlight action; publish to Tableau Public
- [ ] Locked palette to be set on the first sheet and reused everywhere

### Blog page: add a DATA PREP tab (decided during the build)

- Explain the Tableau-native cleaning layer (Aliases, Groups) and show the **SQL and pandas equivalents** of each (an alias is a display-only relabel with no SQL equivalent; a Group is a `CASE WHEN ... THEN 'Molina Healthcare, Inc.'` / `.replace()` mapping).
- Include a **data flow diagram** showing WHERE changes exist and where they do not: the raw CMS source and the cleaned CSV are unchanged; the `.twbx` adds a presentation layer on top that relabels and merges members without altering the data underneath.
- Document the real gotchas found: (a) CMS truncates Parent Org at 50 characters; (b) 12 names are ALL CAPS; (c) `Molina Healthcare, Inc.,` (trailing comma) and `Samaritan Health Services` vs `, Inc.` split one company into two; (d) **aliases set on `Parent Org` do NOT carry to `Parent Org (group)`**, because the group is a separate field with its own member list.
- Rule to state plainly: aliases never change a number, groups do, so any group that appears in a published figure must also be applied in `nb01` or `nb02` parity will fail.

### Phase 3 — Parity notebook and blog page
- [ ] `nb02` reproduces every figure in DuckDB SQL and pandas, all asserts pass
- [ ] Blog page in `folders/ds_blogs/` following the Medi-Cal post skeleton: Overview, method tabs (with a dedicated Context tab), the dashboard, LOD woven throughout; registered in posts.json and the landing page

---

## Context teaching note (applies to every project)

Every project includes one plain-language Context section: context filters run first, the SQL analog is "move the condition into the WHERE clause," and a worked pitfall shows a FIXED benchmark or a Top N that comes out wrong until the filter is added to context.
