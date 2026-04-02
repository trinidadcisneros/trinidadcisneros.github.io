# PROJECT_ABSTRACT.md — The Documentation Gap

## Title
**The Documentation Gap: How Much Revenue Are U.S. Hospitals Losing to Missed Diagnoses?**

## Abstract

U.S. hospitals are paid through the Medicare Severity Diagnosis Related Group (MS-DRG) system, where payment is determined by the diagnosis and procedure codes documented in the patient's medical record. When clinicians deliver care but fail to document the full clinical picture — a missed comorbidity, an undocumented complication — the hospital receives a lower payment than the patient's actual severity warrants. This "documentation gap" is the central problem that Clinical Documentation Improvement (CDI) programs and AI platforms like SmarterDx, Iodine Software, and 3M/Solventum are built to solve.

This analysis uses exclusively public CMS data to quantify the scope of the documentation gap across approximately 3,400 Medicare-participating acute care hospitals. The approach has three components:

1. **Peer-group CMI benchmarking:** Comparing each hospital's Case Mix Index (CMI) to a peer group of similar hospitals (matched on bed size, teaching status, and ownership type) to identify hospitals with unexpectedly low CMI — a potential signal of under-documentation.

2. **DRG severity tier analysis:** Examining the distribution of discharges across the three severity tiers (without CC, with CC, with MCC) within the same DRG families. Hospitals with an unusually high proportion of cases in the lowest severity tier — relative to peers treating similar patient populations — may have documentation that does not fully capture the conditions present.

3. **Revenue impact estimation:** Modeling the financial impact of severity tier shifts using CMS DRG weights and base rates. If a hospital's under-documentation rate is X%, the estimated revenue gap is the number of shifted cases multiplied by the average payment difference between severity tiers.

The analysis is framed as an independent exploration of publicly available data, not an endorsement of any specific CDI platform. It is designed as a portfolio piece demonstrating healthcare data fluency, pipeline design, and analytical thinking relevant to product analytics roles in the clinical AI / RCM space.

## Methodology Summary

- **Data:** CMS IPPS Impact Files, Case Mix Index Files, Medicare Inpatient PUF, Care Compare quality data, KFF claim denial data, MS-DRG definitions and weights
- **Hospitals:** ~3,400 IPPS-participating acute care hospitals
- **Peer groups:** Hospitals matched on bed size bucket (6 tiers) × teaching status (teaching/non-teaching) × ownership (for-profit/nonprofit/government)
- **Scoring:** Peer-relative CMI gap + severity tier distribution deviation + quality score correlation
- **Visualizations:** Interactive Plotly charts embedded in a tabbed HTML blog post

## Key Questions

1. How much variation exists in CMI across hospitals of similar size and type?
2. Which hospital segments show the largest gap between expected and actual CMI?
3. What is the estimated national revenue at stake from documentation-driven under-coding?
4. Is there a relationship between documentation accuracy (proxied by CMI patterns) and CMS quality scores?
5. How does the claim denial landscape intersect with documentation quality?
