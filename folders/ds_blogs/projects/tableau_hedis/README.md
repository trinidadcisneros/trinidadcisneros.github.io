# Tableau + SQL + pandas: Medi-Cal Plan Quality (HEDIS) Project

Working checklist for blog post 2. Same series and angle as post 1 (`../tableau_medi_cal/`): use SQL and pandas as the reference point to demystify what Tableau does under the hood, this time on plan quality data, and teach HEDIS along the way.

**Working conventions (carried from post 1, all still binding)**

- **SAVE AFTER EVERY INSTRUCTION SET, NO EXCEPTIONS.** File > Save (Cmd+S) to `folders/ds_blogs/projects/tableau_hedis/medi_cal_hedis.twbx` (local save, Tableau Public 2026.2)
- Rename every new sheet BEFORE doing anything else: right click the sheet tab > Rename
- Polish is part of the build, never deferred; sheet titles state the purpose or key finding
- Checkbox = a verified implementable action; bold Question / Purpose / Note lines = read only context
- Every formula references only fields that exist in the data or were created in an earlier step; cross sheet dependencies stated as a PREREQUISITE at the top
- Any text to enter (titles, subtitles) is delivered as one copy paste ready block
- Trinidad drives all Tableau work with step by step instructions; Claude does data prep, parity code, and blog HTML

**Key files**

- `notebooks/nb00_extract_mc_performance.ipynb` — downloads ALL 9 CSV resources via the CalHHS CKAN API and profiles each
- `data/raw/` — immutable raw downloads; `data/extraction_log.json` — what was pulled and when
- nb01 (cleaning) and nb02 (SQL + pandas parity) get created after the nb00 profile is reviewed

---

## HEDIS primer (read before Phase 0 — this is the learning goal of post 2)

- **What it is:** HEDIS (Healthcare Effectiveness Data and Information Set) is the standardized set of health care quality measures maintained by NCQA (the National Committee for Quality Assurance); most US health plans report it, which makes plans comparable
- **What a measure looks like:** a rate = numerator / denominator, e.g. Breast Cancer Screening = women 50 to 74 who got a mammogram (numerator) out of those who should have (denominator); higher is better for most measures, but some (like low value care) are better low, so always check the measure's direction
- **How DHCS uses it:** Medi-Cal managed care plans report HEDIS annually; DHCS holds plans to a Minimum Performance Level (MPL, typically the national Medicaid 50th percentile) and recognizes a High Performance Level (HPL, the 90th percentile); plans below MPL face corrective action
- **What THIS dataset actually contains (learned from the nb00 profile):** not individual measures, but the **AQFS (Aggregated Quality Factor Score)**: one composite rate per plan per region per year, combining performance across all DHCS selected HEDIS indicators, expressed as a percent of the national High Performance Level; 53.18 means "this plan performs at 53% of the national top decile"
- **Why it fits this series:** AQFS per plan per year is perfect LOD and benchmark material (plan vs statewide, plan vs rival), the same calculation methods as post 1 on new question types
- **Interview relevance:** LA Care's job posting mentions HEDIS and Stars; being able to define MPL/HPL and describe a measure as numerator over denominator is the expected baseline

---

## Phase 0 — Extract and Profile

**Goal:** all 9 CSVs downloaded reproducibly, each profiled, and a decision made about which files feed the post.

**The dataset** (confirmed on the portal, July 2026):

- Source: [Managed Care Performance Monitoring Dashboard Report](https://data.chhs.ca.gov/dataset/managed-care-performance-monitoring-dashboard-report), DHCS Managed Care Quality and Monitoring Division, via CalHHS Open Data Portal
- Coverage: 2017 to 2023, statewide, quarterly releases (last updated November 2025; files stamped April 2024 release)
- 9 CSV resources: **HEDIS** (the core), Population, Age, Sex, Ethnicity, Provider Ratios, Encounter Completeness, Grievance Demographics, Grievance Type; plus 1 PDF dashboard report

**Checklist:**

- [x] Run `nb00_extract_mc_performance.ipynb` locally (all 9 CSVs saved July 9, 2026; April 2024 release vintage)
- [x] Profiles reviewed: HEDIS file = AQFS composite only (436 rows: Year 2016 to 2023 x 56 reporting units x AQFS %); demographics files are statewide 2023 monthly; Encounter Completeness has shifted headers; Grievances are 2023 quarterly
- [x] **Scope decision: Option A, the plan quality scorecard.** Core = AQFS trends and benchmarks (L.A. Care vs Health Net vs statewide); companions = Grievance Type and Provider Ratios; individual HEDIS measures (DHCS report files) deferred
- [x] nb01 designed (`nb01_clean_mc_performance.ipynb`): splits Reporting Unit into Plan + Region, converts AQFS % to numeric, parses 202301 months, repairs Encounter Completeness headers, converts comma counts; exports 4 clean CSVs

**Next checklist:**

- [x] nb01 run July 9: aqfs_clean.csv (436 x 5, no missing AQFS, range 26.0 to 98.1), provider_ratios_clean.csv (372 rows, 31 plans), grievance_type_clean.csv (184 rows; Quality of Service is the top roll up at 216,256)
- [x] Plan abbreviations reviewed: 24 plans, single form each, NO harmonize map needed within this dataset ('LA Care' here = post 1's 'L.A. Care Health Plan' if a join ever happens)
- [x] L.A. Care confirmed: `LA Care - Los Angeles`, unbroken 2016 to 2023: 60.91, 66.67, 66.67, 66.84, 72.22, 59.47, 67.33, 59.33 (2021 pandemic dip; 2023 slide; rival `Health Net - Los Angeles` available for head to head)
- [x] Panel note: 53 reporting units per year 2016 to 2019, 56 from 2020 on (units enter over time; know this before averaging across years)
- [x] Encounter Completeness rerun clean July 9: 835 rows, junk rows 0, 9 grading periods (mixed CY/SFY regimes, a real data quirk to mention)
- [x] Data note: completeness can exceed 100% (AAH Professional CY 2019 = 102.26) when submissions beat the expected volume; check metric definitions before judging
- [x] **PHASE 0 COMPLETE (July 9, 2026).** Four clean CSVs in `data/`: aqfs_clean, provider_ratios_clean, grievance_type_clean, encounter_completeness_clean
- [ ] Next session: finalize the Phase 1 Tableau build plan from the candidate sheets below, connect Tableau to `aqfs_clean.csv`, save the workbook FIRST

**Candidate Phase 1 sheets (to be finalized next session):**

1. `AQFS Trend`: LA Care vs Health Net (both LA units) vs the statewide average line, 2016 to 2023 (the EXCLUDE benchmark pattern from post 1)
2. `2023 Ranking`: all reporting units ranked by AQFS with a statewide average reference line, LA Care highlighted
3. `Change Since 2016`: table calc on the year axis (difference / percent difference)
4. `Year Selector`: parameter driving the ranking sheet
5. Companions: grievances by roll up type; PCP ratio by plan
6. Dashboard + publish, then nb02 parity and the blog page, following post 1's phases

**Expected gotchas (from post 1 experience, verify in the profile):**

- Rates may arrive as text with % signs or footnote markers, like the comma formatted counts in post 1
- Plan names will need harmonization against post 1's `HARMONIZE` mapping if we ever join to enrollment
- Suppressed small cells likely appear as annotations or blanks
- Some measures are inverted (lower is better); the measure list must be checked before any "top plans" ranking

---

## Phase 1+ — To be planned after the Phase 0 profile

The Tableau build, dashboard, parity notebook, and blog page phases will be written into this file once the profiles show what the data supports. Post 1's README (`../tableau_medi_cal/README.md`) is the template: one sheet per concept, expected values recorded after each build, pitfalls documented as they happen.

**Candidate questions for the post (to validate against the data):**

- Which plans beat the statewide rate on each measure, and which sit below the MPL? (FIXED / EXCLUDE benchmarks)
- How has each plan's rate on a key measure moved 2017 to 2023? (table calcs)
- Let the viewer pick the measure and the year (parameters)
- How does L.A. Care compare to other large plans on women's health and chronic care measures? (the interview relevant cut)

## Color palette (locked July 9, 2026) — use on EVERY sheet and the dashboard

- LA Care - Los Angeles = green (the hero series; Trinidad does not use orange)
- Health Net - Los Angeles = blue (the rival)
- Statewide Average = gray (benchmark)
- Reference lines = red dashed
- One plan must be the same color on every sheet or the dashboard misleads

## Phase 2 — Parity notebook and blog page (July 8, 2026)

- [x] `notebooks/nb02_sql_pandas_parity.ipynb` created and run end to end: 14 parity checks, every blog number reproduced in DuckDB SQL and pandas against the Tableau value, all PASS
- [x] Blog page `ds_blogs/ds_tableau_sql_pandas_hedis.html` built (6 tabs: Overview, Benchmarks & LODs, Table Calculations, L.A. Care vs Health Net, Parameters, Dashboard); registered in posts.json + landing
- [x] Correctness fix: 2016 statewide average is 55.45 (recomputed mean), not 55.46
- [ ] Publish the workbook to Tableau Public so both embeds load (dashboard view `medi_cal_hedis/Medi-CalPlanQualityScorecard`; single sheet view for the change chart, confirm the `ChangeSince2016` view name matches)
