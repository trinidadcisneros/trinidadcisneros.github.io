# Exam Prep Project 4 — Medi-Cal Market Share in Los Angeles County

Tableau + SQL + pandas practice project for the **Salesforce Certified Tableau Data Analyst** exam, built on public health plan data. Same series and angle as the earlier posts (`../tableau_medi_cal/`, `../tableau_hedis/`, `../tableau_star_ratings/`): use SQL and pandas as the reference point for what Tableau does under the hood, this time on **Medi-Cal managed care market share in Los Angeles County**, with statewide context.

**Why this project.** It doubles as onboarding for the L.A. Care analyst role. Medi-Cal is L.A. Care's core business (about 90% of members and essentially all of the roughly $11B in capitation revenue), and this data shows exactly how L.A. Care sits in its market: the county's dominant public plan under California's Two-Plan Model. See the standalone briefing `la_care_business_and_data_briefing.html` for the business context.

**Emphasis:** Explore and Analyze (the 41% domain), with the heaviest coverage of **Connect and Transform** in the series so far, because the raw data has three genuine cleaning problems (below). **LOD appears (plan share within county), and a dedicated Context (context filters) walkthrough appears** (Top N plan within a county is the classic context trap).

---

## The story

- **Los Angeles County Medi-Cal managed care market, June 2026:** L.A. Care 59.7% (2.10M), Health Net 30.7% (1.08M), Kaiser 9.6% (0.34M).
- **19 years of history:** the market went 1.16M members (2008) to 2.87M (2016, after the ACA Medicaid expansion) to 3.69M (2024 COVID peak) to 3.52M (2026, after redetermination unwinding began).
- **The Two-Plan Model is visible in the data:** L.A. Care is the "Local Initiative," Health Net is the "Commercial Plan."
- **Statewide context:** L.A. Care is the single largest Medi-Cal managed care plan in California.

## The data

- **Source:** [Medi-Cal Managed Care Enrollment Report](https://data.chhs.ca.gov/dataset/medi-cal-managed-care-enrollment-report), CalHHS Open Data Portal, pulled via the CKAN API so the pipeline never breaks on the monthly filename change.
- **Grain:** one row per enrollment month, per plan type, per county, per plan name. Monthly, January 2007 to June 2026 (234 months).
- **Fields:** Enrollment Month, Plan Type, County, Plan Name, Count of Enrollees, plus suppression annotation columns.

### The three cleaning problems (the Connect and Transform teaching content)

1. **The Plan Type label changed mid-series.** `Two-Plan` (Jan 2007 to Jul 2018) was replaced by `Local Initiative (2 Plan)` and `Commercial Plan (2 Plan)` (Aug 2018 on). The two eras do not overlap within a month, so normalizing them produces one continuous 19-year series.
2. **Plan names have ALL CAPS and renamed variants.** `LA CARE` became `L.A. Care Health Plan/Los Angeles`; `Health Net / LA` became `Health Net Community Solutions/Los Angeles`. These need a **Group** (same lesson as the Star Ratings parent orgs). Aliases are display only; a group changes numbers, so any group in a published figure must also be in the notebook.
3. **Six non-medical product lines are mixed in** (Dental, PACE, SCAN, Cal MediConnect, PCCM, Special Project). Market share is only meaningful over the medical managed care lines, so these are filtered out.
4. **Cell suppression:** small counts are suppressed with an annotation code; these become nulls, not zeros.

## Exam objectives this project targets

| Exam domain (weight) | Objectives exercised here |
|---|---|
| Connect and Transform (24%) | Normalizing the two Plan Type eras (a union-style reconciliation); **groups** to merge plan name variants; aliases; filtering product lines; assessing data quality (suppression); folders and field customization |
| Explore and Analyze (41%) | Table calcs (running total, year-over-year, percent of total, moving average); filters, **Top N and CONTEXT** (top plan within the county); parameters (pick the county or the metric); **LOD FIXED** (plan share within a county); groups and hierarchies (plan type to plan) |
| Create Content (26%) | Line, area, stacked area, bar; a **choropleth map** for the statewide county view; a dashboard with filter and highlight actions; formatting |
| Publish and Manage (9%) | Publish to Tableau Public |

## Working conventions (binding, carried from the earlier posts)

- SAVE AFTER EVERY INSTRUCTION SET (Cmd+S). Rename every new sheet BEFORE building on it.
- Voice: first person "I" or third person, NEVER "we". No hyphens or dashes except compound nouns.
- Tabs and sections named by the **method**, not the subject.
- Every SQL and pandas block preceded by plain-language bullets naming the approach.
- Show title and tab-name options and WAIT for approval before applying them across the page, landing, and posts.json.
- Trinidad drives all Tableau Desktop work one step at a time and returns screenshots; Claude does data prep, SQL/pandas parity, and the blog HTML.
- Every figure verified in Tableau, DuckDB SQL, and pandas before it goes in the post.

## Pipeline

- `notebooks/nb00_extract_la_market_share.ipynb` — pull the CKAN dataset, save raw, profile.
- `notebooks/nb01_clean_la_market_share.ipynb` — normalize eras, group name variants, filter to medical lines, output the two clean analysis files.
- `notebooks/nb01b_enrich_joins.ipynb` — write the two join-ready reference files for the enrichment joins: `ca_county_population.csv` (CA DOF E-2 2024, embedded and cited, for the penetration join) and `la_plan_quality.csv` (from the HEDIS project's `aqfs_clean.csv`, for the share-vs-quality join). Deterministic; run it to regenerate both.
- `notebooks/nb02_sql_pandas_parity.ipynb` — reproduce every published figure in DuckDB SQL and pandas, asserted against Tableau.

**The two enrichment joins (performed in Tableau, prepared by nb01b):**
1. County enrollment + county population -> Medi-Cal penetration rate (county grain, statewide map).
2. LA market share + HEDIS AQFS quality -> share vs quality (plan grain, LA rivals).
They are kept as separate joins at separate grains; the notebook aligns the join keys (county name, plan brand) so the Tableau joins are clean.

## Phases

- [x] Phase 0 — extract and profile (nb00, nb00b)
- [x] Phase 1 — clean (nb01, nb01b, nb01c): LA County market-share file + statewide file + enrichment references
- [x] Phase 2 — Tableau build (6 sheets, dashboard 1250x2427)
- [x] Phase 3 — dashboard published to Tableau Public (la_medi_cal_market_share/Dashboard1)
- [x] Phase 4 — nb02 parity (18/18 pass), blog page `ds_tableau_sql_pandas_la_market_share.html`, registered in posts.json + ds_blog_landing.html
