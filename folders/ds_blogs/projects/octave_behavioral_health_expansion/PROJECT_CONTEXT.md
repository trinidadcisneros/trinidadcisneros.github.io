# PROJECT_CONTEXT.md — Octave Behavioral Health Expansion Analysis

**Last Updated:** 2026-03-30
**Project Path:** `bitterscientist.com/folders/ds_blogs/projects/octave_behavioral_health_expansion/`
**Purpose:** Portfolio blog post + interview discussion piece for Octave Health Group Sr. Data Analyst, Providers interview (April 1, 2026)

---

## What This Project Is

A 9-notebook data analysis pipeline that models Octave Health Group's expansion from 23 states to all 50. It combines provider workforce data, insurance/payer mix, mental health demand, competitive intelligence, state regulatory environments, and reimbursement economics to produce data-driven expansion recommendations — framed through the lens of the Sr. Data Analyst, Providers role.

This project lives in the `ds_blogs/projects/` folder because it will become a published blog post on bitterscientist.com, but it is specifically designed as an interview discussion piece. The analysis demonstrates domain knowledge, pipeline design skills, and strategic thinking directly relevant to the Octave role.

**Related project:** `job_posting_resume_optimizer/` — contains the resume pipeline, study guides, and interview prep materials for the same job search.

---

## Octave Health Group — Key Facts

- **What they do:** Modern behavioral health practice (therapy + psychiatry), in-person and virtual
- **Current footprint:** 23 states + DC
- **States:** AZ, CA, CO, CT, FL, GA, IL, MD, MA, MN, NJ, NY, NC, OH, OR, PA, SC, TN, TX, VA, WA, DC, WI
- **Provider model:** 1099 independent contractors, paid $107-123/hr (10-40% above standard insurance rates)
- **Patient copay:** ~$28 average
- **Payer partners (14):** Aetna, Anthem Blue Cross of CA, Blue Shield of CA, BCBS plans, Centivo, Florida Blue, Health Net, Highmark, Horizon Health NJ, MHN, UMR, Cigna, Evernorth, UnitedHealthcare/Optum
- **Differentiators:** Outcome tracking, no-show pay for providers, physical clinic locations, quality-focused recruitment

## Competitors

| Competitor | States | Providers | Covered Lives | Funding | Model |
|---|---|---|---|---|---|
| Rula | All 50 | 10K+ | 120M+ | $200M+ | Insurance marketplace |
| Grow Therapy | All 50 | 10K+ | Undisclosed | $175M+ | Medicaid/Medicare accepted |
| Headway | All 50 | 60K+ | 100M+ | $225M+ | Volume-first, insurance admin |
| Alma | All 50 | 20K+ | Undisclosed | $130M+ | Membership model ($125/mo) |

All four competitors are already in all 50 states — Octave's expansion is catching up, not pioneering.

---

## Pipeline Architecture

### Stage 1 — Data Collection (NB01-NB04)

| Notebook | Status | What It Does |
|---|---|---|
| NB01 | ✅ Complete | Census API → state population, adult 18+, Octave state flag. Saves `state_population_base.csv`, `project_reference.json` |
| NB02 | ✅ Complete | BLS OES + NPI Registry → 7 provider types (psychiatrists, psychologists, MH counselors, MFTs, social workers, SA counselors, NPs/PMHNPs). Dual PMHNP estimation: 5% of total NPs (AANP) + NPI taxonomy 363LP0200X validation. Prescriber vs. therapist breakdown. Saves `state_provider_counts.csv` |
| NB03 | ✅ Complete | Census ACS insurance → payer mix by state. Maps Octave's 14 payer partners to estimated covered lives using market share (UHC 15%, Anthem 12%, Aetna 8%, Cigna 7%, Regional BCBS 6%). Saves `state_payer_mix.csv` |
| NB04 | ✅ Complete | SAMHSA NSDUH + MHA rankings → mental illness prevalence, treatment gap, demand indicators. Saves `state_mental_health_demand.csv` |

### Stage 2 — State Analysis (NB05-NB06)

| Notebook | Status | What It Does |
|---|---|---|
| NB05 | ✅ Complete | Competitor profiles, SAMHSA facility counts, FCC broadband → competitive intensity score per state. Saves `state_competitive_landscape.csv` |
| NB06 | ✅ Complete | Interstate compacts (PSYPACT 42 states, Counseling Compact 39+, Social Work Compact 30+), telehealth parity (23 full, 5 conditional, 22 none), licensing fees, Medicare/Medicaid CPT rates (90834 ~$104, 90837 ~$140, 90791 ~$170 national avg), reimbursement favorability index. Saves `state_regulatory_reimbursement.csv` |

### Stage 3 — Expansion Modeling (NB07-NB08)

| Notebook | Status | What It Does |
|---|---|---|
| NB07 | ✅ Complete | Composite scoring model (6 dimensions, configurable weights), state tier classification (high/medium/low priority) |
| NB08 | ✅ Complete | Expansion waterfall, revenue projections, credentialing timelines, 4 expansion waves |

### Stage 4 — Visualizations & Recommendations (NB09)

| Notebook | Status | What It Does |
|---|---|---|
| NB09 | ✅ Complete | 7 choropleth maps, heatmap, executive dashboard, 6 strategic recommendations |

---

## Key Technical Details

### Data Sources & APIs
- **Census API** (no key needed for limited use): Population estimates, ACS insurance tables
- **BLS OES** (no key needed): Provider employment by SOC code and state
- **NPI Registry / NPPES API** (no key needed): Provider counts by taxonomy code — paginated (limit 200, skip pagination). Taxonomy `363LP0200X` = PMHNP
- **SAMHSA NSDUH**: Mental health prevalence state estimates (CSV download)
- **CMS Physician Fee Schedule**: Medicare reimbursement rates by CPT code and locality
- **FCC Broadband Data**: State-level broadband penetration

### Provider Types (7 SOC codes)
- `211011` — SA/Behavioral Disorder Counselors
- `211013` — Marriage and Family Therapists
- `211014` — Mental Health Counselors
- `211023` — MH/SA Social Workers
- `291223` — Psychiatrists
- `291071` — Clinical/School Psychologists
- `291171` — Nurse Practitioners (all specialties; filtered to PMHNP via 5% AANP estimate + NPI validation)

### PMHNP Estimation (added in latest session)
- BLS doesn't break NPs by specialty. Two methods:
  1. **National average:** 5% of total NPs = estimated PMHNPs (AANP survey data)
  2. **NPI Registry:** Query NPPES with taxonomy `363LP0200X`, paginate with limit=200
- `pmhnp_best_estimate` column uses NPI where available, BLS 5% as fallback
- `total_prescribers` = psychiatrists + PMHNP best estimate (key metric for med management capacity)

### Octave State List (23)
```python
OCTAVE_STATES = [
    'Arizona', 'California', 'Colorado', 'Connecticut', 'Florida',
    'Georgia', 'Illinois', 'Maryland', 'Massachusetts', 'Minnesota',
    'New Jersey', 'New York', 'North Carolina', 'Ohio', 'Oregon',
    'Pennsylvania', 'South Carolina', 'Tennessee', 'Texas', 'Virginia',
    'Washington', 'Wisconsin', 'District of Columbia'
]
```

---

## Output Files

All CSVs live in `data/outputs/nb{XX}_{name}/`:

- `nb01_census_population/state_population_base.csv` — 51 rows (50 states + DC)
- `nb01_census_population/state_population_overview.png`
- `nb02_provider_landscape/state_provider_counts.csv` — includes NP/PMHNP columns
- `nb02_provider_landscape/provider_supply_by_state.png`
- `nb03_payer_mix/state_payer_mix.csv`
- `nb04_mental_health_demand/state_mental_health_demand.csv`
- `nb05_competitive_landscape/state_competitive_landscape.csv`
- `nb06_regulatory_reimbursement/state_regulatory_reimbursement.csv`
- `nb07_expansion_scoring/` — composite scores and tier assignments
- `nb08_projections/` — expansion waterfall and revenue projections
- `nb09_visualizations/` — all final charts, maps, dashboards
- `data/inputs/project_reference.json` — shared reference (states, payers, competitors, FIPS, abbreviations)

---

## Known Issues & Fixes Applied

1. **NB01 TypeError in barh chart:** Census API returns Puerto Rico (52 rows); `STATE_ABBREV` mapping produces NaN. **Fix:** Added `df_pop = df_pop.dropna(subset=['state_abbrev'])` after mapping. Now 51 rows.

2. **NB02 NPI Registry returning all 1s:** NPPES API `result_count` only reflects current page, not total. With `limit: 1`, every state returned 1. **Fix:** Paginate with `limit: 200`, increment `skip`, sum pages until `result_count < 200`.

3. **NB02 fallback data cell prints nothing when Census API succeeds:** Expected — the fallback is gated by `if df_pop is None:`, which is False when API works.

---

## Interview Discussion Points

This project demonstrates competencies for the Sr. Data Analyst, Providers role:

1. **End-to-end pipeline design** — 10+ public data sources, cleaning, joining, modeling
2. **Provider analytics** — supply metrics, recruitment opportunity, prescriber vs. therapist breakdown, PMHNP estimation via triangulation
3. **Payer intelligence** — covered lives by partner, addressable market sizing
4. **Regulatory awareness** — compacts, licensing, telehealth laws impact on expansion speed
5. **Reimbursement economics** — understanding whether Octave's above-market pay model is sustainable per state
6. **Strategic recommendations** — prescriptive expansion sequencing, not just descriptive analytics
7. **Healthcare data fluency** — CMS, SAMHSA, Census, NPI, PSYPACT, BLS
8. **Stakeholder-ready visualizations** — choropleths, heatmaps, executive dashboards

---

## Session Log

### Session 1 (2026-03-29)
- Created project structure, README.rst, all 9 notebooks (NB01-NB09)
- Built full pipeline with fallback data for all API calls
- Added NB06 (regulatory/reimbursement) based on user request to include credentialing, licensing fees, telehealth allowance, reimbursement rates by payer
- Expanded from 8 to 9 notebooks

### Session 2 (2026-03-30)
- Fixed NB01 TypeError (Puerto Rico NaN in state_abbrev)
- Added 7th provider type to NB02: Nurse Practitioners (SOC 291171) with PMHNP estimation
  - BLS 5% estimate + NPI Registry taxonomy 363LP0200X validation
  - Added prescriber vs. therapist breakdown, prescribers_per_100k metric
  - Fixed NPI pagination bug (result_count only reflects page, not total)
- Created PROJECT_CONTEXT.md and NEXT_SESSION_PROMPT.md for this project

---

## Quick-Start for New Sessions

1. Read this file first
2. Read `README.rst` for the full business question list and data source URLs
3. Check the Session Log above to see what was done last
4. Read `NEXT_SESSION_PROMPT.md` for specific continuation instructions
5. The notebooks are in `notebooks/` organized by stage (1_data_collection, 2_state_analysis, 3_expansion_modeling, 4_visualizations_recommendations)
6. All shared reference data is in `data/inputs/project_reference.json`
