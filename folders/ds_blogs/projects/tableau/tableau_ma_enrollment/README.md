# Exam Prep Project 2 — Medicare Advantage Enrollment and Market Share

Tableau + SQL + pandas practice project for the **Salesforce Certified Tableau Data Analyst** exam, built on public health plan data. Same series and angle as the Medi-Cal posts (`../tableau_hedis/`, `../tableau_medi_cal/`): use SQL and pandas as the reference point for what Tableau does under the hood, this time on Medicare Advantage enrollment and plan market share, while deliberately covering exam objectives.

**Emphasis:** Explore and Analyze (the 41% domain), with the heaviest coverage of **Connect and Transform** (unions and a Tableau Prep flow). **LOD appears in this project, and so does a dedicated Context (context filters) walkthrough**, since Top N within a geography is the classic context trap.

---

## Working conventions (binding, carried from the Medi-Cal posts)

- **SAVE AFTER EVERY INSTRUCTION SET, NO EXCEPTIONS.** File > Save (Cmd+S) to the project `.twbx`
- Rename every new sheet BEFORE doing anything else (right click tab > Rename)
- Polish is part of the build, never deferred; sheet titles state the purpose or key finding
- **Voice: first person "I" or third person, NEVER "we"** anywhere in the blog output
- **No hyphens or dashes except compound nouns**
- Tabs and sections named by the **method**, not the subject
- Every SQL and pandas code block is preceded by plain-language bullets naming the approach
- No internal dev-note captions in the final output
- Show title and tab-name options and WAIT for approval before applying them across the page, landing, and posts.json
- Trinidad drives all Tableau Desktop work step by step and returns screenshots; Claude does data prep, SQL/pandas parity code, and the blog HTML
- Every figure verified in Tableau, DuckDB SQL, and pandas before it goes in the post

---

## Exam objectives this project targets

| Exam domain (weight) | Objectives exercised here |
|---|---|
| Connect and Transform (24%) | **Unions** to stack the monthly files; a **Tableau Prep** flow (clean, aggregate, pivot, output); Data Interpreter; extract vs live; extract and data source filters |
| Explore and Analyze (41%) | Table calcs (running total, year-over-year percent, percent of total, moving average); filters, **Top N and CONTEXT** (top plans in one county); parameters (pick the county or metric); **LOD FIXED** (plan share within a county); groups and hierarchies (parent org to plan) |
| Create Content (26%) | Line, area, bar; **choropleth market share map**; a dashboard with a filter action; formatting |
| Publish and Manage (9%) | Publish workbook and a published data source; schedule an extract refresh |

---

## Key files

- `notebooks/nb00_extract_ma_enrollment.ipynb` — download several monthly CMS enrollment files (state/county/contract) and the contract info; log what was pulled
- `data/raw/` — immutable raw downloads; `data/extraction_log.json`
- `nb01_clean_ma_enrollment.ipynb` — union the monthly files, parse dates, clean counts, join contract names
- `nb02_sql_pandas_parity.ipynb` — reproduce every blog figure in DuckDB SQL and pandas, asserted against Tableau

---

## Data source

- **CMS Monthly Medicare Advantage Enrollment by State, County, Contract:** https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-advantagepart-d-contract-and-enrollment-data
- Companion: the contract/plan crosswalk for readable plan names
- Notes to verify in the profile: the small-cell suppression (rows with 10 or fewer enrollees), consistent columns across months for the union, and the county FIPS or SSA code for mapping

---

## Phases

### Phase 0 — Extract and Profile
- [ ] `nb00` downloads N consecutive monthly enrollment files plus the contract crosswalk; save raw + `extraction_log.json`
- [ ] Profile: confirm identical columns across months (union safe), grain (contract by county by month), suppression, and the geographic key for maps
- [ ] Scope decision: which state or metro to feature (a California and Los Angeles cut for the LA Care flavor), and how many months of history

### Phase 1 — Tableau build (candidate sheets)
1. `Enrollment Trend`: statewide or national enrollment over time with a **running total** and **year-over-year** table calc
2. `Plan Market Share`: each plan's share within a county using a **FIXED LOD** denominator, with the **Context section** showing why the county filter must be added to context
3. `Top Plans in a County`: a **Top N** filter driven by a parameter, done correctly with Add to Context
4. `Market Share Map`: a **choropleth** of the leading plan or a plan's share by county
5. `Prep Flow`: a Tableau Prep flow that unions the monthly files and pivots them, exported as a clean source

### Phase 2 — Dashboard and publish
- [ ] Assemble a market dashboard wired by one county filter action; publish to Tableau Public with a scheduled extract refresh noted

### Phase 3 — Parity notebook and blog page
- [ ] `nb02` reproduces every figure in DuckDB SQL and pandas, all asserts pass
- [ ] Blog page following the Medi-Cal post skeleton, with a dedicated Context tab and LOD woven throughout; registered in posts.json and the landing page

---

## Context teaching note (applies to every project)

Every project includes one plain-language Context section: context filters run first, the SQL analog is "move the condition into the WHERE clause," and a worked pitfall shows a Top N or a FIXED denominator that comes out wrong until the filter is added to context.
