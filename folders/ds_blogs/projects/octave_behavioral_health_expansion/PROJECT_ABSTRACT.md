# Octave Behavioral Health Expansion Analysis: Project Abstract

## 1. Introduction

Octave Health Group is a behavioral health company that provides therapy and psychiatric services through a hybrid model of virtual telehealth and in-person clinics. As of early 2025, Octave operates in 23 states and partners with major commercial insurers (UnitedHealthcare, Aetna, Cigna, Anthem BCBS, and regional BCBS plans) to serve an estimated 40 million covered lives nationally.

This analysis models a hypothetical expansion from 23 states to all 50 states plus the District of Columbia, examining the question: if Octave were to expand nationally, which states represent the strongest opportunities and what factors should inform the sequencing?

**Important disclaimer:** This is an independent analytical exercise using publicly available data. The wave-based expansion framework presented here is a hypothetical scenario designed to demonstrate how multi-dimensional data can inform strategic decisions. It does not reflect Octave's actual expansion plans, internal priorities, or proprietary business strategy.

## 2. Project Goal

Build a reproducible, data-driven scoring model that evaluates each of the 28 non-Octave states across six dimensions relevant to behavioral health market entry:

1. **Provider recruitment pool** — How many licensed behavioral health providers (psychiatrists, psychologists, counselors, marriage/family therapists, social workers, PMHNPs) are available to recruit?
2. **Payer coverage** — How many commercially insured lives are accessible through Octave's existing payer partnerships?
3. **Unmet demand** — What is the mental health treatment gap (the share of adults with a mental illness who do not receive treatment)?
4. **Competitive landscape** — How saturated is the market with existing telehealth competitors (Rula, Grow Therapy, Headway, Alma) and brick-and-mortar behavioral health facilities?
5. **Regulatory environment** — How many interstate licensure compacts (PSYPACT, Counseling Compact, Social Work Compact) has the state joined, and does it have telehealth parity laws?
6. **Reimbursement favorability** — What are the Medicare fee schedule rates for common therapy codes (CPT 90834, 90837), which serve as a floor benchmark for commercial reimbursement?

The deliverable is a ranked list of expansion states with composite scores, tier assignments, and projected economic impact under conservative assumptions.

## 3. Methodology

### 3.1 Data Sources

| Source | What it provides | Notebook |
|--------|-----------------|----------|
| **US Census Bureau ACS (2023)** | State population by age (total, 18+, under 18) | NB01 |
| **Bureau of Labor Statistics OES** | Occupational employment counts for BH provider types by state | NB02 |
| **HRSA NPPES (NPI Registry)** | Individual provider counts, used to cross-validate BLS estimates and estimate PMHNP counts | NB02 |
| **Kaiser Family Foundation (KFF)** | Health insurance coverage by type (employer, individual, Medicaid, Medicare, uninsured) by state | NB03 |
| **Insurer market share reports** | UHC, Aetna, Cigna, Anthem BCBS, regional BCBS state-level commercial market shares | NB03 |
| **SAMHSA NSDUH (2022-2023)** | State-level prevalence of any mental illness (AMI), serious mental illness (SMI), major depressive episodes, substance use disorders, and treatment receipt rates | NB04 |
| **Mental Health America (MHA)** | State-level mental health burden rankings and treatment access scores | NB04 |
| **SAMHSA Behavioral Health Treatment Locator** | Count of licensed BH treatment facilities by state (~18,000 nationally) | NB05 |
| **FCC Broadband Data** | Percentage of households with broadband access by state (proxy for telehealth feasibility) | NB05 |
| **PSYPACT, Counseling Compact, Social Work Compact** | Interstate compact membership rosters (which states participate in each compact) | NB06 |
| **CMS Physician Fee Schedule (2024)** | Medicare reimbursement rates for CPT 90834, 90837, 90791 by state/locality | NB06 |
| **Octave public website & support pages** | Current state footprint, payer partnerships, therapist licensure policies | NB03, NB06 |

### 3.2 Payer Model Coverage

The payer model (NB03) estimates covered lives for 5 major payer categories: UnitedHealthcare/Optum, Aetna, Cigna (including Evernorth), Anthem BCBS, and regional BCBS plans (which includes Florida Blue, Highmark, Horizon Health NJ, and Blue Shield of California).

Octave lists 14 named insurance partners. Of these, 10 are captured directly or through their parent BCBS affiliation. Four smaller payers are **not modeled individually**: Centivo (self-funded plan administrator), Health Net (Centene subsidiary, primarily CA/OR), MHN (Health Net behavioral health subsidiary), and UMR for Mt. Sinai (UHC's third-party administrator arm — partially captured under UHC). These omissions likely undercount accessible covered lives by an estimated 2-5%, making our estimates conservative.

**Limitation — Payer-by-state activation:** The model assumes that if Octave partners with a payer nationally (e.g., UHC), that payer's state-level market share is accessible in every state. In practice, payer contracts may need to be activated state-by-state, meaning expansion states may not immediately have full payer coverage. This is a business execution variable that cannot be modeled from public data alone. Conversely, Octave could expand its payer set in new states — competitors like Rula accept 27+ insurance plans (including Ambetter, Kaiser, Tricare) and Alma partners with 20+ plans across all 50 states. Octave's current 14-payer roster is narrower than competitors, representing both a limitation and a growth opportunity.

**Competitive payer context:** Competitor intelligence shows that Grow Therapy's reimbursement rates for CPT 90834 range from $70-100+ per session depending on state (higher in CA, NY, NJ, MA; lower in AR, AL, MS, OK), and CPT 90837 ranges $80-120+. Our model's $130 average session reimbursement assumption aligns with Octave's premium positioning (provider pay of $107-123/hr per Octave careers page, vs. Grow Therapy's ~$86/hr for LCSWs). Alma charges providers a $95/month membership fee but takes no per-session cut from cash-pay clients.

### 3.3 Key Assumptions

1. **Network access rate = 40%.** Octave reports ~40M covered lives across 23 states. Our bottom-up payer model estimates ~82M raw payer lives in those states. The implied conversion rate (~49%) suggests not all commercially insured lives in a payer's book are in-network with Octave. We apply a conservative 40% rate uniformly. Every covered-lives figure in this analysis uses this adjusted number (column: `octave_accessible_covered_lives`), not the raw theoretical maximum.

2. **Per-capita normalization.** The scoring model uses rates (providers per 100K adults, accessible covered lives as % of population) rather than raw counts to avoid large-state bias. Texas has more providers than Maine in absolute terms, but Maine may have a more favorable per-capita provider density for recruitment.

3. **Percentile-based tier thresholds.** States are assigned to Tier 1 (above 75th percentile of expansion scores), Tier 2 (50th-75th percentile), or Tier 3 (below 50th percentile). This ensures the tier distribution reflects the actual score distribution rather than arbitrary fixed thresholds.

4. **Commercial-only focus.** Octave's current business model centers on commercially insured patients. Medicare reimbursement rates are included as a benchmark floor (commercial plans typically reimburse at ~130-196% of Medicare per Milliman 2025 research), not as a direct revenue source.

5. **Therapist licensure = place-of-service rule.** A therapist must hold a license in the state where the patient is physically located at the time of the session. Interstate compacts expand the recruitable provider pool (a PSYPACT-member psychologist in Ohio can serve patients in any PSYPACT state) but do not eliminate the licensing requirement. Octave's own policy page confirms this rule.

6. **Revenue projections use 0.5% penetration (conservative).** At 0.5% of accessible covered lives becoming Octave patients, with 20 sessions/year at $130 average reimbursement (CPT 90834), the model estimates ~$95M incremental annual revenue across all 28 expansion states. This is a floor estimate; moderate (1%) and optimistic (2%) scenarios would yield $190M and $380M respectively.

### 3.4 Scoring Model

Each state receives a normalized score (0-100) on six dimensions, combined with these weights:

| Dimension | Weight | Metric | Direction |
|-----------|--------|--------|-----------|
| Provider Pool | 20% | Licensed BH providers per 100K adults | Higher = better (more to recruit) |
| Payer Coverage | 25% | Accessible covered lives as % of adult population | Higher = better (more patients reachable) |
| Unmet Demand | 20% | Treatment gap % (adults with mental illness not receiving care) | Higher = better (more need) |
| Competitive Advantage | 10% | Inverse of competitive intensity (competitor density + BH facilities + broadband) | Lower competition = better |
| Regulatory Ease | 15% | Interstate compact membership + telehealth parity laws | More compacts = better |
| Reimbursement | 10% | Medicare fee schedule rates for therapy codes (proxy for commercial floor) | Higher rates = better |

### 3.5 Analysis Pipeline

The analysis is organized as a 9-notebook pipeline across four phases:

- **Phase 1 — Data Collection (NB01-NB04):** Gather and clean population, provider, payer, and demand data for all 51 jurisdictions (50 states + DC).
- **Phase 2 — State Analysis (NB05-NB06):** Build competitive landscape and regulatory/reimbursement profiles.
- **Phase 3 — Expansion Modeling (NB07-NB08):** Compute composite scores, assign tiers, and project economic impact.
- **Phase 4 — Visualizations & Recommendations (NB09):** Produce interactive maps, heatmaps, and a dashboard synthesizing all findings.

## 4. Main Findings

**4.1 The expansion opportunity is meaningful but measured.** The 28 non-Octave states contain 61.5M adults and an estimated 7.3M accessible covered lives through existing payer partnerships (at the 40% network access rate). This represents a 22% increase over the current 32.8M covered lives — significant but not a doubling, because Octave already operates in the most populous states.

**4.2 Seven states emerge as Tier 1 priorities.** Maine (59.5), Kentucky (59.0), Indiana (58.4), Delaware (55.4), Missouri (52.7), New Hampshire (52.6), and West Virginia (52.2) score highest on the composite model. These states combine favorable per-capita provider density, high treatment gaps (55-60%), strong compact membership, and relatively low competitive intensity.

**4.3 Competition is nationwide but not prohibitive.** All four major telehealth BH competitors (Rula, Grow Therapy, Headway, Alma) already operate in all 50 states. However, 26 of 28 expansion states have lower competitive intensity than the average of Octave's current 23 states. If Octave can compete in its existing markets, it can compete in these.

**4.4 Interstate compacts are the key speed differentiator.** Of all 51 jurisdictions, 28 belong to all three major compacts (PSYPACT, Counseling, Social Work), enabling provider credentialing in 2-4 weeks. States with zero compacts face 12-20 week timelines. Five of seven Tier 1 expansion states have 3 compacts.

**4.5 Revenue projections are conservative by design.** At 0.5% market penetration, the 28 expansion states yield ~$95M in incremental annual revenue. The top 7 (Tier 1) states alone account for ~$48M. These are floor estimates using conservative assumptions; actual performance depends on provider recruitment velocity, payer contracting, and local market execution.

## 5. Recommendations

**Note:** These recommendations are analytical outputs from the scoring model. They demonstrate how data can inform expansion prioritization, not what Octave should or will do.

1. **Prioritize states where multiple dimensions align.** The Tier 1 states score well not because of any single factor but because provider availability, payer coverage, unmet demand, and regulatory ease all converge. Entering a state that is strong on one dimension but weak on others creates execution risk.

2. **Use compact membership to sequence market entry.** States with 3 compacts allow faster provider onboarding (2-4 weeks vs. 12-20). If speed-to-market matters, the 5 Tier 1 states with 3 compacts (ME, KY, DE, MO, NH) represent the lowest-friction entry points.

3. **Frame covered lives realistically.** The 40% network access rate assumption is critical. Reporting "82M raw payer lives" without the access rate adjustment would overstate Octave's addressable market by 2.5x. Any internal analysis should distinguish between raw payer market share and in-network accessible lives.

4. **Monitor competitive dynamics, don't avoid them.** All expansion states have existing competitors. The analysis shows competition is a function of market attractiveness — states with no competitors likely have unfavorable fundamentals. The question is not "where is there no competition" but "where does Octave's differentiation (outcomes tracking, provider economics, hybrid model) create an edge."

5. **Treat the scoring model as a starting point.** The weights (25% payer, 20% provider, etc.) reflect reasonable priors, but different strategic priorities would produce different rankings. A sensitivity analysis varying these weights would strengthen confidence in the Tier 1 selections.

## 6. Conclusions

This analysis demonstrates that a multi-dimensional, data-driven approach can meaningfully inform geographic expansion decisions for a behavioral health company. The key insight is not any single number (the $95M revenue estimate, or the 7.3M covered lives) but the framework itself: by normalizing heterogeneous data sources to a common scoring scale and weighting them by strategic relevance, we can systematically compare 28 states that might otherwise be evaluated ad hoc.

The scoring model reveals that the strongest expansion opportunities are not the largest states (TX, FL are already Octave states) but mid-sized states where provider density, treatment gaps, and regulatory ease create favorable conditions simultaneously. This is a finding that intuition alone — which tends to favor population size — would miss.

For the Sr. Data Analyst, Providers role, this type of analysis is directly applicable: the same pipeline (collect → normalize → score → project → visualize) can be applied to provider recruitment funnel optimization, credentialing pipeline tracking, market penetration monitoring, and competitive benchmarking — all of which become increasingly complex and data-intensive as Octave expands its geographic footprint.

---

## Notebook-to-Section Mapping

| Section | Primary Notebooks | Key Figures / Tables |
|---------|------------------|---------------------|
| **Introduction** | — | — |
| **Data Collection** | NB01 (population), NB02 (providers), NB03 (payers), NB04 (demand) | NB01: state population table; NB02: provider counts by type, provider density map; NB03: payer mix bar charts, covered lives by state; NB04: treatment gap choropleth, AMI prevalence |
| **State Analysis** | NB05 (competitive landscape), NB06 (regulatory/reimbursement) | NB05: competitive intensity scores, competitor benchmark table, facility density; NB06: compact membership counts, Medicare fee schedule comparison, regulatory ease scores |
| **Scoring Model** | NB07 (expansion scoring) | NB07: composite score table, radar charts (top states), scatter plot (score vs. covered lives), tier assignments |
| **Economic Projections** | NB08 (covered lives projections) | NB08: cumulative covered lives waterfall, growth curves (providers/lives/revenue), expansion wave timeline, top 10 summary table |
| **Visualizations & Recommendations** | NB09 (final dashboard) | NB09: 7 choropleth maps (footprint, provider density, treatment gap, competition, opportunity score, regulatory ease, reimbursement), state comparison heatmap, executive dashboard (7 panels) |

## Detailed Notebook Reference

| Notebook | Phase | Input | Output | Rows × Cols | Key Metric |
|----------|-------|-------|--------|-------------|------------|
| NB01 | Data Collection | Census ACS API | `state_population_base.csv` | 51 × 8 | 262.3M total adult population |
| NB02 | Data Collection | BLS OES + NPPES | `state_provider_counts.csv` | 51 × 29 | 623,478 total BH providers nationwide |
| NB03 | Data Collection | KFF + insurer reports | `state_octave_covered_lives.csv` | 51 × 24 | 40.1M national accessible covered lives (at 40% access rate) |
| NB04 | Data Collection | SAMHSA NSDUH + MHA | `state_mental_health_demand.csv` | 51 × 21 | 55.4% avg treatment gap nationwide |
| NB05 | State Analysis | SAMHSA locator + FCC | `state_competitive_landscape.csv` | 51 × 13 | 4 national competitors (Rula, Grow, Headway, Alma) |
| NB06 | State Analysis | Compact rosters + CMS | `state_regulatory_reimbursement.csv` | 51 × 19 | 28 states with 3 compacts (fastest credentialing) |
| NB07 | Expansion Modeling | NB01-NB06 outputs | `state_expansion_scores.csv` | 51 × 33 | Score range: 27.4-62.9; 7 Tier 1, 7 Tier 2, 14 Tier 3 |
| NB08 | Expansion Modeling | NB07 output | `state_expansion_projections.csv` | 28 × 22 | $95.2M total expansion revenue (conservative) |
| NB09 | Visualizations | NB01-NB08 outputs | 7 HTML maps + dashboard PNG + heatmap PNG | — | Executive dashboard with all dimensions |
