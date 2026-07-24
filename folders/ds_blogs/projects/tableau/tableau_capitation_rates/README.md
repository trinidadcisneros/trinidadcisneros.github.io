# tableau_capitation_rates

Post 5 of the Tableau + SQL + pandas series. The revenue side of Medi-Cal managed care: what DHCS pays health plans per member per month (capitation), by plan model, county, health plan, and category of aid.

Blog title: TBD (on hold until the finding emerges).

## Dataset

- Medi-Cal Managed Care Capitation Rates by Managed Care Plan Models (consolidated), CHHS open data portal, publisher DHCS.
  https://data.chhs.ca.gov/dataset/medi-cal-managed-care-capitation-rates-by-managed-care-plan-models-consolidated
- Seven CSVs, one per plan model (Two-Plan, COHS, GMC, Regional, Single Plan, SCAN, PACE), identical nine column schema: Rating Period, Calendar Year, Model, County, Health Plan, Category of Aid, Lower Bound, Midpoint, Upper Bound.
- Coverage 2021 to 2026, updated annually. Rates are published as ranges (lower bound, midpoint, upper bound).
- Secondary data: the Medi-Cal managed care enrollment extract already prepared for the enrollment and market share posts, joined to rates inside Tableau.

## Design decisions (approved July 23, 2026)

- Python prepares the data only: pull and clean. No joins and no unions in Python; each model stays its own clean CSV.
- The union of the seven model files happens in Tableau (wildcard union), as does every join (rates to enrollment on County, Health Plan, Year). This is the Connect & Transform post.
- Tableau Prep Builder is not part of free Tableau Public, so reshaping uses union, pivot, and Data Interpreter inside Tableau Desktop.
- Required Tableau features: parameters (prominent, including a what-if rate scenario), LOD expressions where applicable, a context filter section (series standard).
- Trinidad builds every sheet herself, one step at a time. Rate figures verified in DuckDB SQL and pandas before appearing in the post.
- Blog page reuses the ds_tableau_sql_pandas_la_market_share.html framework: layout, tab structure (Overview, The Dashboard, Methods with nested sub tabs), language format, and content organization.

## Exam domains exercised

- Connect & Transform (24%): unions, pivots, Data Interpreter, joins across files.
- Explore & Analyze (41%): LODs, parameters, table calculations on rate trends.
- Create Content and Publish & Manage: dashboard assembly, Tableau Public publishing.

## Pipeline

1. `notebooks/nb00_data_pull.ipynb` pulls the seven raw CSVs and the DHCS read me to `data/raw/` and prints structure diagnostics.
2. `notebooks/nb01_clean.ipynb` (written after nb00 diagnostics) standardizes columns and rate values, outputs one clean CSV per model to `data/clean/`.
3. Tableau build (union, joins, LODs, parameters), publish to Tableau Public.
4. `notebooks/nb02_sql_pandas_parity.ipynb` verifies every published figure in DuckDB SQL and pandas.
5. Blog page, then register in posts.json and the Data Stories landing page.

## Status

- July 23, 2026: project scaffolded, nb00 written, awaiting first run and diagnostics.
