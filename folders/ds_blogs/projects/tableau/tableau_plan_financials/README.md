# tableau_plan_financials

Post 6 of the Tableau + SQL + pandas series. The profit and loss of a Medi-Cal plan: where L.A. Care and Health Net Community Solutions make and lose money, from DMHC (Department of Managed Health Care) public financial filings.

Blog title: TBD (on hold until the finding emerges).

## Questions

- The anatomy of a capitation dollar: medical costs vs administration vs margin, against the 85% Medical Loss Ratio floor.
- Net income over time, lined up against the rate cycle from the capitation rates post (the 2022 cut, the 2024 rebuild).
- Revenue per member month vs medical cost per member month vs administrative cost per member month.
- Tangible Net Equity (the required reserve floor) vs actual reserves, the cushion that absorbs losing years.

## Data

- DMHC Financial Summary Data hub: https://www.dmhc.ca.gov/DataResearch/FinancialSummaryData.aspx
- Financial Summary web app (quarterly and annual per plan): http://wpso.dmhc.ca.gov/flash/
- Financial Stability Dashboard: https://wpso.dmhc.ca.gov/dashboard/Finances.aspx
- FSSB Financial Summary of Medi-Cal Managed Care Plans (PDF, fallback source): https://www.dmhc.ca.gov/Portals/0/Docs/OFR/FSSB/Aug25/FinancialSummaryofMediCalManagedHealthPlans.pdf
- Enrollment for the per member month math: reuse `tableau_la_market_share/data/la_market_share_clean.csv`.

## Design decisions (approved July 24, 2026)

- Plans: L.A. Care and Health Net Community Solutions only; Kaiser's license mixes its whole business and cannot isolate Medi-Cal (stated caveat, not a silent gap).
- Python prepares the data only; the union or joins and every visual happen in Tableau.
- New Tableau ground: a waterfall chart (Gantt mark + running total table calculation), dashboard actions, an 85% Medical Loss Ratio reference line, parameter reuse.
- Diagnostics first: no extraction format is promised until the probe run reports what the DMHC pages actually serve.
- All repo files are overwritten in place, never versioned.

## Pipeline

1. `notebooks/nb00_data_probe.ipynb` probes the DMHC sources, saves raw snapshots to `data/raw/probe/`, and prints structure diagnostics.
2. `notebooks/nb01_data_pull.ipynb` pulls the Financial Summary report per plan per window (all 13 financial measures plus enrollment, annual and quarterly), saving raw HTML snapshots and parsed CSVs to `data/raw/`.
3. `notebooks/nb02_clean.ipynb` cleans each raw CSV into a Tableau ready CSV in `data/clean/` (numeric parsing, Plan display name, Period Type, Period End Date, Year, Quarter, Quarter Label). No unions or joins in Python; Tableau wildcard unions the 8 clean files.
4. Tableau build (wildcard union, calculated fields, Select Plan parameter, parameter action dashboard), published to Tableau Public as `medi_cal_plan_financials/Dashboard1`.
5. `notebooks/nb03_sql_pandas_parity.ipynb` verifies every dashboard figure in DuckDB SQL and pandas against live captured control totals.
6. Blog page on the series framework, then registration in posts.json and the Data Stories landing page.

## Status

- July 24, 2026: project scaffolded, probe step written, awaiting first run and diagnostics.
- July 25, 2026 (later): diagnostics COMPLETE after browser assisted debugging. The Financial Summary report posts to `flash.aspx`; dates must be month name plus year; long windows time out, chunked windows of at most 5 years work. L.A. Care Medi-Cal entity confirmed as license 933 0355 (Local Initiative Health Authority for Los Angeles County, DBA L.A. Care Health Plan); the Joint Powers Authority license 933 0504 is excluded. Report verified live for both plans (L.A. Care 2025 annual revenue $15.8B; Health Net Community Solutions Q4 2025 net loss $18.9M). nb01_data_pull written, awaiting first run.
- July 25, 2026 (later still): nb01 first run complete, 8 of 8 pulls, identical 21 column layout, per plan 81 rows (16 annual 2010 to 2025, 65 quarterly Q1 2010 to Q1 2026), no duplicate periods across windows. nb02_clean written, awaiting first run.
- July 25, 2026 (evening): nb02 run clean (0 parse failures, control total exact). Tableau dashboard BUILT and PUBLISHED (4 worksheets, Select Plan parameter + parameter action, 85% MLR reference line, PMPM and TNE calculated fields). nb03 parity written, awaiting first run.
- July 25, 2026 (late): nb03 RUN CLEAN, 54 of 54 checks pass in both engines. Blog page ds_tableau_sql_pandas_plan_financials.html WRITTEN to folders/ds_blogs/ (md5 cf66f69b39dd1163a46211c8b978b2cd). Working title 'The Profit and Loss of a Medi-Cal Plan'; awaiting title pick + posts.json/landing registration. Waterfall dropped (ratio reconciliation deviates 25.72 pts, so revenue->net income cannot be decomposed from the summary columns; stated as a finding + future-post hook).
- July 25, 2026: first probe run complete. All sources reachable. License identifiers confirmed (L.A. Care Health Plan Joint Powers Authority 933 0504, Health Net Community Solutions 933 0426). FSSB PDF ruled out as a data source (4 page slide deck, no tables). Stage 2 added to nb00: submit the Financial Summary form per plan and the eFiling search, awaiting second run.
