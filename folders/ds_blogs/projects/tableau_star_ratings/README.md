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
- [ ] `nb00` downloads the Star Ratings summary tables for the last several years plus plan/contract info and enrollment; save raw + `extraction_log.json`
- [ ] Profile each file: grain, row counts, join keys, measure list, missing/suppressed handling
- [ ] Scope decision: which measures and years feed the post; pick a hero contract or parent org for the LA Care flavored narrative (a California D-SNP if available)

### Phase 1 — Tableau build (candidate sheets)
1. `Overall Star Trend`: a contract's overall star vs the national (and state) average over years — **FIXED LOD benchmark + a Context section** showing how a state filter must be added to context to shrink the benchmark
2. `Year over Year Star Change`: Difference From table calc (relative to Previous)
3. `Star Tier Distribution`: bins or sets grouping contracts into star tiers
4. `Measure Explorer`: a parameter to pick the quality measure, driving the ranking and a reference line
5. `Stars by State`: choropleth map of average overall stars
6. `Live vs Extract`: the same table connected live to Snowflake, next to an extract, to narrate the difference

### Phase 2 — Dashboard and publish
- [ ] Assemble a quality scorecard dashboard with a filter and a highlight action; publish to Tableau Public
- [ ] Locked palette to be set on the first sheet and reused everywhere

### Phase 3 — Parity notebook and blog page
- [ ] `nb02` reproduces every figure in DuckDB SQL and pandas, all asserts pass
- [ ] Blog page in `folders/ds_blogs/` following the Medi-Cal post skeleton: Overview, method tabs (with a dedicated Context tab), the dashboard, LOD woven throughout; registered in posts.json and the landing page

---

## Context teaching note (applies to every project)

Every project includes one plain-language Context section: context filters run first, the SQL analog is "move the condition into the WHERE clause," and a worked pitfall shows a FIXED benchmark or a Top N that comes out wrong until the filter is added to context.
