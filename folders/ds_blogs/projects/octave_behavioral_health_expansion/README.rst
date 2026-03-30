=====================================================
Octave Behavioral Health Expansion Analysis
=====================================================

This project analyzes the U.S. behavioral health landscape at the state level
to model Octave Health Group's expansion from 23 states to all 50. It combines
provider workforce data, insurance/payer mix, mental health demand indicators,
competitive intelligence, state regulatory environments, and reimbursement
economics to produce data-driven recommendations for expansion sequencing —
framed through the lens of a Sr. Data Analyst, Providers who would own provider
performance analytics, payer reporting, and recruitment strategy.

The pipeline is organized into four stages across nine notebooks.


Context
=======

Octave Health Group is a modern behavioral health practice operating in 23
states + DC via in-person and virtual therapy. They partner with major payers
(Aetna, Anthem, BCBS, Cigna, UnitedHealthcare/Optum, and others) to provide
in-network therapy with reimbursement rates 10-40% above standard insurance
rates. Their model solves the "insured but can't access care" problem by
recruiting quality therapists into an active in-network provider network.

**Current footprint (23 states + DC):**
Arizona, California, Colorado, Connecticut, Florida, Georgia, Illinois,
Maryland, Massachusetts, Minnesota, New Jersey, New York, North Carolina,
Ohio, Oregon, Pennsylvania, South Carolina, Tennessee, Texas, Virginia,
Washington, Washington DC, Wisconsin

**Current insurance partners:**
Aetna, Anthem Blue Cross of California, Blue Shield of California,
BCBS plans, Centivo, Florida Blue, Health Net, Highmark, Horizon Health NJ,
MHN, UMR for Mt. Sinai, Cigna, Evernorth, UnitedHealthcare/Optum

**Direct competitors:**
Rula (all 50 states, 10K+ providers, 120M+ covered lives),
Grow Therapy (all 50, 10K+ providers, accepts Medicaid/Medicare),
Headway (all 50, 60K+ providers, 100M+ covered lives),
Alma (all 50, 20K+ providers, membership model at $125/mo for providers)


Business Questions
==================

**Provider Supply & Recruitment**

1. How many behavioral health providers (psychiatrists, psychologists,
   therapists, LCSWs, counselors) exist in each state?
2. What is the provider-to-population ratio, and which states have
   the most severe shortages?
3. What is the recruitable provider population for Octave in each state?

**Payer Mix & Covered Lives**

4. What is the insurance coverage breakdown (commercial, Medicare,
   Medicaid, uninsured) by state?
5. For Octave's existing payer partners, how many lives are covered
   in each state — both current 23 and expansion states?
6. How many additional covered lives would Octave gain by expanding
   to all 50 states through existing payer relationships?

**Mental Health Demand**

7. Where is unmet need greatest — states with high mental illness
   prevalence but low provider-to-population ratios?
8. What is the treatment gap (% with mental illness who did NOT
   receive treatment) by state?

**Competitive Landscape**

9. How do Rula, Grow Therapy, Headway, and Alma compete in each
   state on provider counts, payer partnerships, and covered lives?
10. What is the competitive intensity per state, and where does
    Octave's quality-focused model have room to differentiate?

**Regulatory & Licensing Environment**

11. Which states participate in interstate compacts (PSYPACT for
    psychologists, Counseling Compact, Social Work Compact) that
    enable faster provider credentialing?
12. What are the licensing fees, credential types, and processing
    timelines for behavioral health providers by state?
13. Do all states allow telehealth for behavioral health, and are
    there parity requirements?

**Reimbursement Economics**

14. What are the Medicare reimbursement rates for common therapy
    CPT codes (90834, 90837, 90791) by state/locality?
15. What are Medicaid reimbursement rates by state, and how do they
    compare to Medicare?
16. What does the reimbursement landscape tell us about where Octave
    can sustain its 10-40% above-market provider pay model?

**Expansion Strategy**

17. Which non-Octave states represent the highest-value expansion
    targets when combining all dimensions?
18. What is the recommended expansion sequence, and what operational
    considerations (credentialing speed, telehealth laws, payer
    presence) should inform the rollout?


Directory Structure
===================

::

  octave_behavioral_health_expansion/
  |
  |-- data/
  |   |-- inputs/                            <- Raw downloaded datasets, API configs
  |   |
  |   +-- outputs/
  |       |-- nb01_census_population/        <- State population and demographics
  |       |-- nb02_provider_landscape/       <- Provider counts by state and specialty
  |       |-- nb03_payer_mix/               <- Insurance coverage by state and payer
  |       |-- nb04_mental_health_demand/     <- Prevalence, treatment gaps, rankings
  |       |-- nb05_competitive_landscape/    <- Competitor analysis, facility density
  |       |-- nb06_regulatory_reimbursement/ <- Licensing, compacts, telehealth, rates
  |       |-- nb07_expansion_scoring/        <- Composite opportunity scores
  |       |-- nb08_projections/              <- Covered lives and provider projections
  |       +-- nb09_visualizations/           <- Charts, maps, and final deliverables
  |
  +-- notebooks/
      |-- 1_data_collection/                 <- Ingest and clean all data sources
      |-- 2_state_analysis/                  <- Analyze each dimension by state
      |-- 3_expansion_modeling/              <- Score, rank, and project growth
      +-- 4_visualizations_recommendations/  <- Produce deliverables


Data Sources
============

All datasets are publicly available and free. No authentication is required
except a free Census API key.

**Provider Data:**

- CMS NPPES/NPI Registry API — provider counts by specialty and state
  https://npiregistry.cms.hhs.gov/api-page

- BLS Occupational Employment Statistics — behavioral health workforce
  counts and wages by state (SOC codes: 21-1011, 21-1023, 29-1066, 29-1223)
  https://www.bls.gov/oes/

- SAMHSA National Directory of Mental Health Treatment Facilities — facility
  counts by state (XLSX download)
  https://www.samhsa.gov/data/

**Payer/Insurance Data:**

- Census ACS Health Insurance Tables — coverage type by state (commercial,
  Medicare, Medicaid, uninsured, military)
  https://www.census.gov/data/tables/time-series/demo/health-insurance/acs-hi.html

- CMS Medicaid Enrollment Data — state Medicaid enrollment
  https://data.medicaid.gov/

- CMS Medicare Enrollment Dashboard — state Medicare enrollment
  https://data.cms.gov/tools/medicare-enrollment-dashboard

**Mental Health Demand:**

- SAMHSA NSDUH State Estimates — serious mental illness, major depressive
  episode, substance use disorder prevalence by state (CSV download)
  https://www.samhsa.gov/data/data-we-collect/nsduh-national-survey-drug-use-and-health/state-releases

- Mental Health America State Rankings — composite state mental health
  rankings, access to care indicators
  https://mhanational.org/the-state-of-mental-health-in-america/

**Demographics:**

- Census Population Estimates API — state population, age, demographics
  https://www.census.gov/data/developers/data-sets/popest-popproj/popest.html

**Competitive/Telehealth:**

- Direct Competitor Intelligence — Rula, Grow Therapy, Headway, Alma
  state coverage, provider counts, insurance partnerships, funding,
  and market positioning (from company websites, CB Insights, and
  industry comparison sources)

- SAMHSA FindTreatment.gov — behavioral health facility counts by state
  https://findtreatment.samhsa.gov/

- FCC Broadband Data — broadband penetration by state (telehealth readiness)
  https://www.fcc.gov/health/maps-overview

**Regulatory & Licensing:**

- PSYPACT (Psychology Interjurisdictional Compact) — 42 member jurisdictions
  https://psypact.gov/page/psypactmap

- Counseling Compact — 39+ states enacted, 3 live (AZ, MN, OH)
  https://counselingcompact.gov/map/compact-states/

- Social Work Licensure Compact — 30+ member states, targeting 2026 launch
  https://swcompact.org/compact-map/

- CCHP State Telehealth Laws Report (Fall 2025) — telehealth parity,
  audio-only rules, reimbursement policies for all 50 states
  https://www.cchpca.org/resources/state-telehealth-laws-and-reimbursement-policies-report-fall-2025/

**Reimbursement Data:**

- CMS Medicare Physician Fee Schedule — therapy CPT codes (90834, 90837,
  90791) by state/locality, downloadable carrier-specific pricing files
  https://www.cms.gov/medicare/physician-fee-schedule/search
  https://pfs.data.cms.gov/

- State Medicaid Fee Schedules — individual state behavioral health
  reimbursement rates (varies by state; Excel/PDF/CSV)

- FAIR Health Benchmarking — commercial payer reimbursement benchmarks
  https://www.fairhealth.org/benchmark-data-products


What Each Notebook Does
=======================

Stage 1 — Data Collection
--------------------------

**NB01 State Population & Demographics**
  Pulls state-level population estimates from the Census API. Builds a
  base table of all 50 states + DC with population, age distribution
  (adult 18+ as primary since Octave serves adults), and urban/rural
  split. Flags the 23 current Octave states. This becomes the denominator
  for all per-capita calculations downstream.

**NB02 Behavioral Health Provider Landscape**
  Queries the NPI Registry API and BLS OES data to count behavioral health
  providers (psychiatrists, psychologists, therapists, LCSWs, counselors)
  by state. Calculates provider-to-population ratios, identifies shortage
  states, and estimates the recruitable provider pool. Also ingests the
  SAMHSA facility directory for facility counts. Produces both current
  Octave states and expansion states side by side.

**NB03 Payer Mix & Insurance Coverage**
  Ingests Census ACS health insurance tables and CMS enrollment data to
  build a state-level payer mix profile: what percent of each state's
  population is covered by commercial insurance, Medicare, Medicaid, or
  is uninsured. Maps Octave's existing payer partners (Aetna, Anthem,
  BCBS, Cigna, UHC/Optum) to estimate covered lives by state — both
  for the current 23 states and expansion targets.

**NB04 Mental Health Demand Indicators**
  Loads SAMHSA NSDUH state prevalence data and MHA rankings to quantify
  mental health need by state: serious mental illness rates, depression
  prevalence, substance use, and the treatment gap (% with mental illness
  who did NOT receive treatment). Cross-references with provider supply
  from NB02 to identify the highest-need, lowest-supply states.

Stage 2 — State-Level Analysis
-------------------------------

**NB05 Competitive Landscape**
  Analyzes Octave's four direct competitors — Rula, Grow Therapy, Headway,
  and Alma — mapping each competitor's state footprint, insurance
  partnerships, provider counts, and estimated covered lives. Also ingests
  SAMHSA facility directory data and FCC broadband data to assess overall
  market density and telehealth readiness. Produces a competitive intensity
  score per state that feeds into the expansion scoring model. Highlights
  where Octave's quality-focused differentiators (outcome tracking, higher
  pay, no-show pay, physical clinics) create the strongest positioning.

**NB06 Regulatory Environment & Reimbursement Economics**
  Builds a state-by-state regulatory profile:

  - Interstate compact membership: PSYPACT (psychology, 42 states),
    Counseling Compact (39+ states), Social Work Compact (30+ states)
  - Telehealth laws: full parity, conditional parity, or no parity
  - Licensing requirements: credential types, fees, processing timelines
  - Medicaid behavioral health acceptance and restrictions

  Also pulls Medicare reimbursement rates from the CMS Physician Fee
  Schedule for key therapy CPT codes (90834, 90837, 90791) by state/
  locality. Compares Medicaid rates where available. Calculates a
  "reimbursement favorability" index — states where rates are high enough
  to sustain Octave's 10-40% above-market provider pay model.

  This is critical for the provider analyst role: credentialing speed and
  reimbursement economics directly impact provider recruitment viability.

Stage 3 — Expansion Modeling
-----------------------------

**NB07 Expansion Opportunity Scoring**
  Builds a composite scoring model that ranks all 50 states on expansion
  attractiveness using dimensions from NB01-NB06:

  - Provider recruitment pool (NB02)
  - Payer coverage alignment (NB03)
  - Unmet mental health demand (NB04)
  - Competitive density (NB05)
  - Regulatory ease — compact membership, telehealth parity (NB06)
  - Reimbursement favorability (NB06)

  Weights are configurable. Segments states into tiers: current Octave
  states, high-priority expansion, medium-priority, and long-term targets.
  Also benchmarks how the current 23 Octave states score on the same
  model to validate the framework.

**NB08 Covered Lives & Provider Projections**
  Models the incremental impact of expanding to all 50 states:

  - Additional providers available for recruitment per state
  - Additional covered lives through existing payer partnerships per state
  - Revenue opportunity estimates based on Octave's session economics
    ($28 avg copay, $107-123/hr provider pay, insurer reimbursement spread)
  - Cumulative growth curves as states are added in priority order
  - Credentialing timeline estimates based on compact membership (NB06)

Stage 4 — Visualizations & Recommendations
--------------------------------------------

**NB09 Visualizations & Strategic Recommendations**
  Produces the final deliverables:

  - Choropleth maps: provider density, payer coverage, demand gap,
    competitive intensity, regulatory ease, opportunity score
  - State comparison heatmap across all dimensions
  - Expansion priority waterfall chart (cumulative lives added)
  - Payer coverage gap analysis by state (where Octave needs new partners)
  - Reimbursement rate comparison maps (Medicare, Medicaid by state)
  - Provider recruitment funnel estimates per expansion tier
  - Regulatory barrier matrix (compact status, telehealth parity)

  Written strategic recommendations for expansion sequencing, including:

  - Recommended expansion waves (which states first, second, third)
  - Operational considerations: credentialing speed via compacts,
    telehealth-only vs. physical clinic needs
  - Payer strategy: states where existing partners already cover the
    most lives vs. states needing new payer negotiations
  - Provider recruitment strategy: states with the largest recruitable
    pool and most favorable reimbursement economics
  - Competitive positioning: where to lead with quality differentiators
    vs. where volume competitors are weakest


Key Metrics Produced
====================

- Behavioral health providers per 100K population by state
- Insurance coverage breakdown (%) by state and payer type
- Estimated covered lives per Octave payer partner per state
- Mental illness prevalence and treatment gap by state
- Behavioral health facility density by state
- Interstate compact membership score per state (0-3 compacts)
- Telehealth parity status per state (full/conditional/none)
- Medicare reimbursement rates for CPT 90834/90837/90791 by state
- Medicaid reimbursement rates by state (where available)
- Reimbursement favorability index per state
- Competitive intensity score per state
- Composite expansion opportunity score (0-100) per state
- Projected incremental providers and covered lives from expansion
- State tier classification (high/medium/low priority)
- Credentialing timeline estimate per state


Interview Discussion Points
============================

This project demonstrates competencies directly relevant to the
Sr. Data Analyst, Providers role at Octave:

1. **End-to-end pipeline design** — ingesting from 10+ public APIs and
   datasets, cleaning, joining, and modeling into actionable output

2. **Provider analytics** — the core of the role; building metrics around
   provider supply, distribution, recruitment opportunity, and the
   economics that drive provider retention

3. **Payer relationship intelligence** — understanding how insurance
   coverage translates to addressable market and covered lives,
   directly supporting payer negotiations and contract renewals

4. **Regulatory awareness** — understanding that expansion isn't just
   about demand; credentialing, licensing, and telehealth laws directly
   impact how fast Octave can recruit providers in a new state

5. **Reimbursement economics** — demonstrating that you understand the
   financial model: Octave pays providers 10-40% above market, so the
   base reimbursement rate determines whether that's sustainable

6. **Strategic thinking** — not just descriptive analytics but prescriptive
   recommendations on where to expand, in what order, and what
   operational preparations are needed

7. **Healthcare domain knowledge** — working with CMS, SAMHSA, Census,
   and state regulatory data shows fluency with the data ecosystem

8. **Visualization for stakeholders** — choropleth maps and executive
   dashboards that make complex state-level data actionable for
   leadership, operations, and payer relations teams


Python Dependencies
===================

::

  pandas
  numpy
  requests
  plotly
  folium
  matplotlib
  seaborn
  scipy
  openpyxl
  jupyter
  geopandas
  us
