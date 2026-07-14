# Exam Prep Project 3 — County Population Health (Member Area Needs)

Tableau + SQL + pandas practice project for the **Salesforce Certified Tableau Data Analyst** exam, built on public health data. Same series and angle as the Medi-Cal posts (`../tableau_hedis/`, `../tableau_medi_cal/`): use SQL and pandas as the reference point for what Tableau does under the hood, this time on the population health and social drivers of the counties a health plan serves, while deliberately covering exam objectives.

**Emphasis:** Explore and Analyze (the 41% domain), with the heaviest coverage of **maps** and the **Analytics pane**, which the first two projects touch less. **LOD appears in this project (county vs state benchmark), and so does a dedicated Context (context filters) walkthrough.**

---

## Working conventions (binding, carried from the Medi-Cal posts)

- **SAVE AFTER EVERY INSTRUCTION SET, NO EXCEPTIONS.** File > Save (Cmd+S) to the project `.twbx`
- Rename every new sheet BEFORE doing anything else (right click tab > Rename)
- Polish is part of the build, never deferred; sheet titles state the purpose or key finding
- **Voice: first person "I" or third person, NEVER "we"** anywhere in the blog output
- **No hyphens or dashes except compound nouns**
- Tabs and sections named by the **method**, not the subject
- Every SQL and pandas code block is preceded by plain-language bullets naming the approach; where a topic is GUI only (mapping, Analytics pane), the parallel is dropped and the section becomes a guided build
- No internal dev-note captions in the final output
- Show title and tab-name options and WAIT for approval before applying them across the page, landing, and posts.json
- Trinidad drives all Tableau Desktop work step by step and returns screenshots; Claude does data prep, SQL/pandas parity code, and the blog HTML
- Every figure verified in Tableau, DuckDB SQL, and pandas before it goes in the post

---

## Exam objectives this project targets

| Exam domain (weight) | Objectives exercised here |
|---|---|
| Connect and Transform (24%) | Connect to files; join the health measures to a demographics or region table; assess data quality; folders and field customization |
| Explore and Analyze (41%) | **Maps: symbol, choropleth, density, mark layers**; the **Analytics pane** (reference lines and bands, trend lines, distribution bands, forecast); calculated fields (number, string, logical, spatial); **groups, bins, sets** (risk tiers); hierarchies (state to county); filters and **CONTEXT**; **LOD FIXED** (county vs its state benchmark) |
| Create Content (26%) | Scatter, filled map, highlight table; a dashboard with a highlight action; formatting and a device layout |
| Publish and Manage (9%) | Publish the workbook; a custom view |

---

## Key files

- `notebooks/nb00_extract_county_health.ipynb` — download the County Health Rankings analytic file (and, if used for trend or forecast, a few prior annual releases); log what was pulled
- `data/raw/` — immutable raw downloads; `data/extraction_log.json`
- `nb01_clean_county_health.ipynb` — select measures, reshape from wide to long where needed, attach state and FIPS keys
- `nb02_sql_pandas_parity.ipynb` — reproduce every non-map figure in DuckDB SQL and pandas, asserted against Tableau

---

## Data source

- **County Health Rankings and Roadmaps, 2025 Annual Data** (about 80 county measures): https://www.countyhealthrankings.org/health-data
- Alternative or companion: **CDC PLACES county data**: https://www.cdc.gov/places/index.html
- Notes to verify in the profile: the county FIPS code as the map and join key, which measures are rates vs counts (for correct aggregation), measure direction (higher vs lower is better), and how many annual releases are available if a trend or forecast is wanted

---

## Phases

### Phase 0 — Extract and Profile
- [ ] `nb00` downloads the 2025 analytic file (plus prior releases if trend or forecast is in scope); save raw + `extraction_log.json`
- [ ] Profile: grain (one row per county), the FIPS key, the measure list with directions and whether each is a rate, and California and Los Angeles County coverage for the plan flavored narrative
- [ ] Scope decision: pick 3 to 5 member-relevant measures (for example uninsured rate, a chronic disease measure, primary care access, a social driver)

### Phase 1 — Tableau build (candidate sheets)
1. `Measure Map`: a **choropleth** of a chosen health measure by county, with a parameter to switch measures
2. `County vs State`: each county against its **state benchmark** using a **FIXED LOD**, with the **Context section** showing the state filter added to context
3. `Risk Tiers`: **bins, groups, or sets** placing counties into tiers on a measure
4. `Drivers Scatter`: two measures on a scatter with a **trend line** and **reference bands** from the Analytics pane
5. `Symbol and Density`: a symbol map and a density map of the same measure to contrast mark types
6. (optional) `Trend and Forecast`: stack a few annual releases and apply a **forecast** if the history supports it

### Phase 2 — Dashboard and publish
- [ ] Assemble a population health dashboard with a highlight action and a device layout; publish to Tableau Public and save a custom view

### Phase 3 — Parity notebook and blog page
- [ ] `nb02` reproduces every non-map figure in DuckDB SQL and pandas, all asserts pass
- [ ] Blog page following the Medi-Cal post skeleton, with a dedicated Context tab and LOD woven throughout; registered in posts.json and the landing page

---

## Context teaching note (applies to every project)

Every project includes one plain-language Context section: context filters run first, the SQL analog is "move the condition into the WHERE clause," and a worked pitfall shows a FIXED benchmark or a Top N that comes out wrong until the filter is added to context.
