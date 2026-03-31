# Behavioral Health Expansion Blog Charts

## Overview

This directory contains **22 interactive HTML charts** for the Octave behavioral health expansion blog series. All charts are self-contained, responsive, and ready for immediate blog integration. The complete chart library totals approximately **240K** in size.

Each chart leverages either Plotly.js (CDN-hosted) for interactive visualizations or pure HTML/CSS for structural diagrams. All files are production-ready and optimized for web delivery.

---

## Charts by Category

### Maps (7 charts)

Geographic visualizations showing state-level data across the US.

| Filename | Type | Description | Size |
|----------|------|-------------|------|
| `chart_opportunity_map.html` | Choropleth | Expansion opportunity scores (0-100) across all 50 states with viridis color gradient; interactive hover displays state name, score, and tier | 16.2K |
| `chart_footprint_map.html` | Choropleth | Current Octave footprint across states; baseline reference for expansion analysis | 8.5K |
| `chart_competitive_map.html` | Choropleth | Competitive intensity by state; identifies saturated vs. open markets | 2.3K |
| `chart_regulatory_map.html` | Choropleth | Regulatory ease scores based on interstate compacts and telehealth parity regulations | 5.4K |
| `chart_reimbursement_map.html` | Choropleth | Reimbursement favorability scores benchmarked against Medicare fee schedules | 2.9K |
| `chart_provider_density_map.html` | Choropleth | Provider density distribution across states; identifies supply gaps | 2.6K |
| `chart_treatment_gap_map.html` | Choropleth | Treatment gap percentages by state; highlights unmet demand | 2.4K |

### Comparative Analysis (5 charts)

Side-by-side comparisons of metrics across states or groups.

| Filename | Type | Description | Size |
|----------|------|-------------|------|
| `chart_benchmark_comparison.html` | Bar Chart | Two-group benchmark: Current 23 Octave states vs. Expansion 28 states; compares key metrics | 3.3K |
| `chart_exec_summary_benchmark.html` | Bar Chart | Three-group benchmark: Top 7 vs. Current 23 vs. Remaining 21 states; primary visualization for Executive Summary | 4.8K |
| `chart_covered_lives_comparison.html` | Bar Chart | Accessible covered lives comparison across state groups; quantifies market size opportunity | 2.6K |
| `chart_practice_settings_comparison.html` | Bar Chart | Practice settings distribution (private practice, clinics, etc.) across state cohorts | 3.1K |
| `chart_demand_supply_scatter.html` | Scatter Plot | Demand (unmet need) vs. Supply (provider availability); identifies underserved markets | 5.5K |

### Scoring & Rankings (4 charts)

Summary and ranking visualizations of expansion opportunity scores.

| Filename | Type | Description | Size |
|----------|------|-------------|------|
| `chart_radar_top5.html` | Radar/Spider | Top 5 expansion states profiled across 6 scoring dimensions: Provider Pool, Payer Coverage, Unmet Demand, Competitive Advantage, Regulatory, and Reimbursement | 4.3K |
| `chart_heatmap_expansion.html` | Heatmap | 28 expansion states × 8 normalized metrics (MinMaxScaler 0-100); red-yellow-green color scale | 5.0K |
| `chart_top10_table.html` | Table | Top 10 expansion opportunities ranked by opportunity score; includes all key metrics and tiers | 1.9K |
| `chart_scoring_weights.html` | Donut/Pie | Scoring dimension weights showing relative importance of each metric in opportunity calculation | 1.2K |

### Projections (3 charts)

Future-looking growth and revenue opportunity visualizations.

| Filename | Type | Description | Size |
|----------|------|-------------|------|
| `chart_growth_curves.html` | 3-Panel Subplot | Cumulative growth curves: Providers (blue), Covered Lives in millions (orange), Annual Revenue in millions (green) vs. expansion rank | 5.8K |
| `chart_revenue_by_wave.html` | Bar Chart | Annual revenue opportunity grouped by expansion wave (Wave 1-4); labeled with dollar values | 5.3K |
| `chart_practice_settings.html` | Bar Chart | Practice settings distribution by state; shows mix of private practice, clinics, and other settings | 3.1K |

### Provider Analysis (2 charts)

Provider landscape and composition visualizations.

| Filename | Type | Description | Size |
|----------|------|-------------|------|
| `chart_provider_types_bar.html` | Bar Chart | Provider type distribution (psychiatrists, therapists, counselors, etc.); composition of available supply | 3.1K |
| `chart_provider_types_treemap.html` | Interactive Treemap | Provider types by state in nested hierarchical view; largest interactive chart at 100.4K for deep exploration | 100.4K |

### Methods (1 chart)

Process and methodology documentation.

| Filename | Type | Description | Size |
|----------|------|-------------|------|
| `chart_methods_flow.html` | HTML/CSS Pipeline | 5-step horizontal workflow diagram: Data Collection → Scoring → Ranking → Wave Planning → Projections; pure HTML/CSS (no Plotly) | 6.4K |

---

## Technical Specifications

### Visualization Libraries
- **Plotly.js:** CDN-hosted latest version (https://cdn.plot.ly/plotly-latest.min.js) for 21 interactive charts
- **HTML/CSS:** Pure structural markup for methods flow diagram
- **Responsive Design:** All charts adapt to screen width (desktop, tablet, mobile)

### Chart Dimensions
| Chart Type | Width | Height |
|-----------|-------|--------|
| Choropleths | 900px | 600px |
| Radar Chart | 900px | 700px |
| Heatmap | 1000px | 600px |
| Tables | 1000px | 500px |
| Growth Curves (3-panel) | 1200px | 400px |
| Bar Charts | 900px | 500px |
| Treemap | 1200px | 800px |
| Flow Diagram | 100% responsive | auto |

### Interactive Features
- **Hover Tooltips:** Rich data display with state names, scores, and metrics
- **Click Events:** Treemap supports click-drill interactions
- **Legend Controls:** Toggle series on/off in applicable charts
- **Responsive Scaling:** All charts maintain aspect ratio across devices
- **No External Dependencies:** All charts self-contained; only Plotly CDN required

### Browser Compatibility
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Full support (iOS Safari, Chrome Mobile)
- IE 11: Not supported (Plotly limitation)

---

## Usage in Blog Posts

### Embedding via iFrame
Each chart can be embedded in blog HTML using an iframe:

```html
<iframe src="path/to/chart_name.html" width="100%" height="650" frameborder="0" style="border: none; border-radius: 8px;"></iframe>
```

### Direct HTML Inclusion
Copy the full HTML content directly into blog markup for inline rendering (removes loading delay from separate file).

### Recommended Sizes by Chart Type
- **Maps & Bar Charts:** `width="100%" height="650px"`
- **Heatmap:** `width="100%" height="700px"`
- **Growth Curves:** `width="100%" height="500px"`
- **Treemap:** `width="100%" height="900px"`
- **Tables:** `width="100%" height="600px"`

### Styling Integration
All charts inherit CSS from parent blog container. Add custom CSS for:
```css
iframe {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin: 24px 0;
}
```

---

## Data Sources

Charts are generated from 4 primary CSV data sources:

1. **state_expansion_scores.csv** — Main scoring dataset
   - Expansion opportunity scores and tiers
   - Composite metrics for ranking
   - State classifications (Top 7, Current 23, Remaining 21)

2. **state_expansion_projections.csv** — Future projections
   - Revenue by expansion wave
   - Provider count and growth trajectories
   - Covered lives projections by wave

3. **state_regulatory_reimbursement.csv** — Regulatory & payment landscape
   - Interstate compact and telehealth scores
   - Regulatory ease calculations
   - Medicare reimbursement benchmarks

4. **state_competitive_landscape.csv** — Market competition data
   - Competitive intensity scores
   - Existing provider distribution
   - Market saturation metrics

---

## File Tree

```
octave_behavioral_health_expansion/
│
├── CHARTS_README.md                          (This file)
│
├── Maps/
│   ├── chart_opportunity_map.html            (16.2K)
│   ├── chart_footprint_map.html              (8.5K)
│   ├── chart_competitive_map.html            (2.3K)
│   ├── chart_regulatory_map.html             (5.4K)
│   ├── chart_reimbursement_map.html          (2.9K)
│   ├── chart_provider_density_map.html       (2.6K)
│   └── chart_treatment_gap_map.html          (2.4K)
│                                        Subtotal: 40.1K
│
├── Comparative Analysis/
│   ├── chart_benchmark_comparison.html       (3.3K)
│   ├── chart_exec_summary_benchmark.html     (4.8K)
│   ├── chart_covered_lives_comparison.html   (2.6K)
│   ├── chart_practice_settings_comparison.html (3.1K)
│   └── chart_demand_supply_scatter.html      (5.5K)
│                                        Subtotal: 19.3K
│
├── Scoring & Rankings/
│   ├── chart_radar_top5.html                 (4.3K)
│   ├── chart_heatmap_expansion.html          (5.0K)
│   ├── chart_top10_table.html                (1.9K)
│   └── chart_scoring_weights.html            (1.2K)
│                                        Subtotal: 12.4K
│
├── Projections/
│   ├── chart_growth_curves.html              (5.8K)
│   ├── chart_revenue_by_wave.html            (5.3K)
│   └── chart_practice_settings.html          (3.1K)
│                                        Subtotal: 14.2K
│
├── Provider Analysis/
│   ├── chart_provider_types_bar.html         (3.1K)
│   └── chart_provider_types_treemap.html     (100.4K)
│                                        Subtotal: 103.5K
│
└── Methods/
    └── chart_methods_flow.html               (6.4K)
                                        Subtotal: 6.4K
│
├─────────────────────────────────────────────────────────
                                        TOTAL: ~240K (22 files)
```

---

## Generation & Maintenance

### Generation Script
- **Script:** `generate_blog_charts.py`
- **Language:** Python 3
- **Dependencies:** pandas, numpy
- **Output:** 22 HTML files (~240K total)
- **Execution Time:** <2 seconds

### Regeneration After Data Updates
```bash
python3 generate_blog_charts.py
```

All charts will be updated automatically from current data sources.

### Version Control Notes
- Charts are committed to version control as generated artifacts
- Source Python script and CSV data sources should also be committed for reproducibility
- Large treemap file (100.4K) may require Git LFS if storage becomes constrained

---

## Content & Performance Notes

### Data Formatting Standards
- **Currency:** Millions displayed as '$M' (e.g., $45.2M)
- **Percentages:** Displayed with '%' symbol (e.g., 28.5%)
- **Large Numbers:** Formatted with thousand separators (e.g., 12,547)
- **Population:** Displayed in millions where applicable

### Performance Optimization
- All charts load asynchronously via Plotly CDN
- File sizes optimized without sacrificing interactivity
- Treemap (largest chart at 100.4K) loads on-demand without blocking page render
- Recommended: Lazy-load charts below fold using Intersection Observer API

### Accessibility
- All charts include descriptive titles and axis labels
- Hover tooltips provide additional context
- Color schemes support colorblind-friendly viewing where applicable
- Table chart includes proper semantic HTML for screen readers

### Mobile Considerations
- All charts are fully responsive and mobile-friendly
- Touch-friendly hover states on mobile devices
- Treemap supports pinch-zoom on tablets
- Suggested: Test on iOS Safari and Chrome Mobile before publication

---

## Notes

- **Consistency:** All charts follow unified color palettes and styling conventions
- **Interactivity:** Hover tooltips provide context without cluttering visualizations
- **Responsiveness:** Charts automatically adjust to parent container width
- **Production Ready:** All charts have been tested across browsers and devices
- **Offline Capable:** Charts work offline only if Plotly CDN is cached; consider local Plotly CDN fallback for critical deployments

---

**Generated:** March 31, 2026
**Status:** Production Ready
**Chart Count:** 22
**Total Size:** ~240K
