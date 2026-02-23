# Tableau Story Plan: OB-GYN Provider Network Analysis
## Prepared for Pomelo Care Recruiter Walkthrough

---

## Story Structure (12 Sheets)

### SHEET 1 — Abstract
**Purpose:** Title card + project summary in 60 seconds
**Files:**
- `tableau_key_numbers_summary.csv` → **Text Table** (9 key metrics)
**Tableau Notes:** Use a dashboard with a large title text box at top ("Mapping OB-GYN Referral Networks & Maternal Health Outcomes") and the key numbers table below. Add annotations for the 3 most important numbers: 60,422 providers, 80% isolated, 54 target counties.

---

### SHEET 2 — Background
**Purpose:** Why maternal health networks matter — scope of the data
**Files:**
- `tableau_entity_type_breakdown.csv` → **Horizontal Bar Chart** (Individual vs Org vs Both)
- `tableau_obgyn_by_state.csv` → **Filled Map / Choropleth** (OB-GYN count by state)
**Tableau Notes:** Side-by-side layout. Left: entity type bar showing 80% are individual providers. Right: US map colored by OB-GYN count per state. Tooltip: state name, count, rank.

---

### SHEET 3 — Project Goal
**Purpose:** Define the research questions
**Files:**
- `tableau_subspecialty_distribution.csv` → **Bar Chart** (OB-GYN subspecialties)
- `tableau_nonobgyn_classifications_bubble.csv` → **Packed Bubble Chart** (81 non-OB-GYN types in network)
**Tableau Notes:** Left: What types of OB-GYNs are in the data? Right: Who do they share patients with? The bubble chart shows the breadth of the referral ecosystem. Caption box: "Research Questions: (1) How connected are OB-GYN providers? (2) Does connectivity relate to maternal outcomes?"

---

### SHEET 4 — Methods
**Purpose:** Explain data pipeline and network construction
**Files:**
- `tableau_edge_weight_by_type.csv` → **Side-by-Side Bars** (edge weight distribution by type)
- `tableau_sankey_obgyn_to_other.csv` → **Sankey Diagram** (OB-GYN referral flows to other specialties)
**Tableau Notes:** Left: How we measured relationships (shared patient counts). Right: Sankey showing referral flow from OB-GYN subspecialties to other provider types. For Sankey in Tableau, use the Sankey template or a dual-axis approach. Caption: "Data: CMS Physician Shared Patient Patterns 2015, 60-day window"

---

### SHEET 5 — Descriptive Stats: Provider Landscape
**Purpose:** Geographic distribution and subspecialty breakdown
**Files:**
- `tableau_treemap_state_subspecialty.csv` → **Treemap** (state × subspecialty)
- `tableau_heatmap_state_subspecialty.csv` → **Heatmap** (state × subspecialty intensity)
**Tableau Notes:** Treemap shows where different OB-GYN types practice. Heatmap version available as alternative view. Use a toggle or separate sheet. Color by provider count.

---

### SHEET 6 — Descriptive Stats: Network Connectivity
**Purpose:** The isolation finding — 80% of OB-GYNs have zero network connections
**Files:**
- `tableau_provider_tiers_pie.csv` → **Pie Chart** (Hub / Connected / Peripheral / Isolated)
- `tableau_state_degree_map.csv` → **Filled Map** (% connected by state)
**Tableau Notes:** This is the MOST IMPORTANT descriptive finding. Pie chart shows 80% isolated. Map shows which states have better/worse connectivity. Add a big annotation callout: "80% of OB-GYN providers share zero patients with any other provider in this dataset." Tooltip on map: state, pct_connected, mean_degree.

---

### SHEET 7 — Descriptive Stats: Network Structure
**Purpose:** Community detection and hub analysis
**Files:**
- `tableau_betweenness_distribution.csv` → **Bar Chart** (5 bins of betweenness centrality)
- `tableau_community_profiles.csv` → **Text Table** (provider communities with 5+ members)
- `tableau_state_tier_treemap.csv` → **Treemap** (state × provider tier)
**Tableau Notes:** Dashboard layout. Top-left: betweenness bar chart showing most providers have near-zero bridging power. Top-right: treemap showing tier distribution by state. Bottom: scrollable community profiles table. Caption: "Network analysis reveals tight local clusters with very few providers bridging between them."

---

### SHEET 8 — Descriptive Stats: Hub Providers
**Purpose:** Who are the most connected OB-GYNs?
**Files:**
- `tableau_hub_providers.csv` → **Symbol Map + Table** (top 50 hub providers)
- `tableau_state_network_scatter.csv` → **Scatter Plot** (state participation vs connectivity)
**Tableau Notes:** Left: Map with dots for hub provider locations (size by degree, color by betweenness). Right: Scatter plot of state-level network participation vs average connectivity — tooltip with state name. Caption: "Hub providers are concentrated in a handful of states and metro areas."

---

### SHEET 9 — Descriptive Stats: Maternal Morbidity
**Purpose:** Where are the worst maternal health outcomes?
**Files:**
- `tableau_state_morbidity_map.csv` → **Filled Map** (state morbidity rates)
- `tableau_top_morbidity_counties.csv` → **Table** (top 20 worst counties)
- `tableau_county_choropleth.csv` → **Filled Map** (county-level morbidity) — filter to morbidity_rate column
**Tableau Notes:** Dashboard with state map on left, county map on right, and scrollable table below. Color gradient: green (low) → red (high morbidity). Caption: "Severe maternal morbidity varies dramatically by geography."

---

### SHEET 10 — Modeling: Does Connectivity Predict Outcomes?
**Purpose:** The key null finding — network variables don't predict morbidity
**Files:**
- `tableau_density_vs_morbidity_scatter.csv` → **Scatter Plot** (provider density vs morbidity rate)
- `tableau_model_comparison.csv` → **Text Table** (5 models compared: OLS, WLS, Beta, NB, GLM)
- `tableau_best_model_coefficients.csv` → **Bar Chart** (Beta regression coefficients)
**Tableau Notes:** Dashboard. Top: scatter plot showing NO relationship between provider density and morbidity (flat trend line). Bottom-left: model comparison table highlighting all R² < 0.03. Bottom-right: coefficient bar chart from Beta regression. Caption: "Five regression models confirm: county-level network connectivity does not predict maternal morbidity rates (R² < 0.03)."

---

### SHEET 11 — Modeling: Target Counties
**Purpose:** Identifying intervention opportunities
**Files:**
- `tableau_target_counties.csv` → **Symbol Map + Table** (54 target counties)
- `tableau_target_vs_nontarget.csv` → **Comparison Table** (target vs non-target metrics)
**Tableau Notes:** Left: Map with 54 target county dots (high morbidity + weak networks). Right: side-by-side comparison table. Target counties have 98.8% higher morbidity and 93% isolated providers. Caption: "54 counties identified where high morbidity intersects with weak provider networks — prime candidates for virtual care intervention."

---

### SHEET 12 — Conclusion
**Purpose:** So-what for Pomelo Care
**Files:**
- `tableau_regression_conclusions.csv` → **Text Table** (key findings summary)
- `tableau_key_numbers_summary.csv` → **Text Table** (reuse from Sheet 1 for bookend effect)
**Tableau Notes:** Dashboard with conclusion text boxes. Key messages: (1) 80% of OB-GYNs are network-isolated. (2) Network structure alone doesn't predict outcomes — other factors at play. (3) 54 target counties represent opportunity for Pomelo's virtual care model. (4) This analysis framework can scale to other CMS datasets and time periods. Add a final callout: "Virtual care platforms like Pomelo can bridge the connectivity gaps this analysis reveals."

---

## File-to-Sheet Mapping Summary

| File | Sheet | Chart Type |
|------|-------|------------|
| tableau_key_numbers_summary.csv | 1, 12 | Text Table |
| tableau_entity_type_breakdown.csv | 2 | Horizontal Bar |
| tableau_obgyn_by_state.csv | 2 | Filled Map |
| tableau_subspecialty_distribution.csv | 3 | Bar Chart |
| tableau_nonobgyn_classifications_bubble.csv | 3 | Packed Bubble |
| tableau_edge_weight_by_type.csv | 4 | Side-by-Side Bars |
| tableau_sankey_obgyn_to_other.csv | 4 | Sankey Diagram |
| tableau_treemap_state_subspecialty.csv | 5 | Treemap |
| tableau_heatmap_state_subspecialty.csv | 5 | Heatmap |
| tableau_provider_tiers_pie.csv | 6 | Pie Chart |
| tableau_state_degree_map.csv | 6 | Filled Map |
| tableau_betweenness_distribution.csv | 7 | Bar Chart |
| tableau_community_profiles.csv | 7 | Text Table |
| tableau_state_tier_treemap.csv | 7 | Treemap |
| tableau_hub_providers.csv | 8 | Symbol Map + Table |
| tableau_state_network_scatter.csv | 8 | Scatter Plot |
| tableau_state_morbidity_map.csv | 9 | Filled Map |
| tableau_top_morbidity_counties.csv | 9 | Text Table |
| tableau_county_choropleth.csv | 9 | Filled Map |
| tableau_density_vs_morbidity_scatter.csv | 10 | Scatter Plot |
| tableau_model_comparison.csv | 10 | Text Table |
| tableau_best_model_coefficients.csv | 10 | Bar Chart |
| tableau_target_counties.csv | 11 | Symbol Map + Table |
| tableau_target_vs_nontarget.csv | 11 | Comparison Table |
| tableau_regression_conclusions.csv | 12 | Text Table |

**Files NOT used in story** (intermediate/raw data — kept in outputs root):
- community_summary.csv
- county_morbidity_rates.csv
- county_network_morbidity.csv
- obgyn_edges.csv
- obgyn_edges_individuals.csv
- obgyn_providers.csv
- obgyn_providers_network.csv
- other_providers.csv
- phase2_summary_stats.csv
- state_network_metrics.csv
- target_counties.csv
- tableau_individual_provider_types.csv (optional add to Sheet 3)
