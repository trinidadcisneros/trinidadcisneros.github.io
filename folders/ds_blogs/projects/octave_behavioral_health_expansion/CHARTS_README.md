# Behavioral Health Expansion Blog Charts

## Overview
This directory contains 8 interactive Plotly HTML charts for the behavioral health expansion blog post. All charts are self-contained, CDN-based, and ready for immediate blog integration.

## Generated Charts

### 1. Expansion Opportunity Map (`chart_opportunity_map.html`)
**Type:** Choropleth visualization of USA states  
**Data:** Expansion opportunity scores (0-100 composite metric)  
**Colors:** Viridis scale (yellow-to-purple gradient)  
**Interactivity:** Hover to see state name, score, and expansion tier  
**Size:** 8.0K

### 2. Top 5 Expansion States Profile (`chart_radar_top5.html`)
**Type:** Radar/spider chart (5 traces)  
**Data:** Top 5 expansion states filtered for non-Octave states  
**Dimensions:** 6 scoring metrics:
- Provider Pool Score
- Payer Coverage Score
- Unmet Demand Score
- Competitive Advantage Score
- Regulatory Score
- Reimbursement Score

**Colors:** 5 distinct trace colors  
**Size:** 4.0K

### 3. Expansion State Comparison Heatmap (`chart_heatmap_expansion.html`)
**Type:** Normalized heatmap (28 expansion states)  
**Data:** 8 normalized metrics per state (0-100 MinMaxScaler)  
**Metrics:**
- Total Population
- BH Providers count
- Accessible Covered Lives
- Treatment Gap %
- Competitive Intensity (inverted)
- Regulatory Ease Score
- Reimbursement Favorability
- Expansion Opportunity Score

**Colors:** RdYlGn scale (red-yellow-green)  
**Layout:** States on y-axis (sorted by opportunity score), metrics on x-axis  
**Size:** 8.0K

### 4. Top 10 Expansion Opportunities Table (`chart_top10_table.html`)
**Type:** Professional Plotly table  
**Data:** Top 10 expansion states by opportunity score  
**Columns:**
- Rank (1-10)
- State name
- Opportunity Score
- Expansion Tier
- Accessible Covered Lives (in millions)
- BH Providers (formatted with commas)
- Treatment Gap %
- Compact Score

**Styling:** Dark blue header (#1f4788), alternating row colors  
**Size:** 4.0K

### 5. Cumulative Growth Curves (`chart_growth_curves.html`)
**Type:** 3-column subplot visualization  
**Data:** Sorted by rank from projections data  
**Subplots:**
1. Cumulative Providers vs Rank (blue line)
2. Cumulative Covered Lives (millions) vs Rank (orange line)
3. Cumulative Annual Revenue (millions) vs Rank (green line)

**Interactivity:** Hover to see state abbreviation and metric value  
**Size:** 4.0K

### 6. Revenue by Expansion Wave (`chart_revenue_by_wave.html`)
**Type:** Bar chart with text labels  
**Data:** Annual revenue opportunity grouped by expansion wave  
**Display:** Revenue in millions ($M)  
**Colors:** Differentiated by wave (4 colors)  
**Labels:** Text labels displayed on top of each bar  
**Size:** 4.0K

### 7. Regulatory Ease Map (`chart_regulatory_map.html`)
**Type:** Choropleth of USA states  
**Data:** Regulatory ease scores based on interstate compacts and telehealth parity  
**Colors:** Greens scale  
**Hover Info:** State name, ease score, compact score, telehealth parity status  
**Size:** 8.0K

### 8. Reimbursement Favorability Map (`chart_reimbursement_map.html`)
**Type:** Choropleth of USA states  
**Data:** Reimbursement favorability scores (Medicare fee schedule benchmark)  
**Colors:** YlGnBu scale (yellow-green-blue)  
**Hover Info:** State name, favorability score, Medicare 90837 rate  
**Size:** 8.0K

## Technical Specifications

### Common Features
- **Plotly Version:** Latest (CDN-hosted: https://cdn.plot.ly/plotly-latest.min.js)
- **Responsive Design:** All charts adapt to screen size
- **Professional Styling:** Clean, modern appearance with proper spacing and colors
- **Hover Text:** Rich tooltips with relevant data
- **File Format:** Self-contained HTML (no external dependencies except CDN)

### Chart Dimensions
- **Choropleths:** 900px × 600px
- **Radar Chart:** 900px × 700px
- **Heatmap:** 1000px × 600px
- **Table:** 1000px × 500px
- **Growth Curves:** 1200px × 400px
- **Bar Chart:** 900px × 500px

### Browser Compatibility
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- IE 11: Not supported (Plotly limitation)

## Usage in Blog Posts

### Direct Embedding
Each HTML file is self-contained and can be embedded as an iframe:
```html
<iframe src="path/to/chart_opportunity_map.html" width="100%" height="650" frameborder="0"></iframe>
```

### Direct Inclusion
The HTML content can be copied directly into blog HTML for inline rendering.

## Data Sources

Charts are generated from 4 CSV sources:
1. **nb07_expansion_scoring/state_expansion_scores.csv** - Main scoring and tier data
2. **nb08_projections/state_expansion_projections.csv** - Revenue and provider projections
3. **nb06_regulatory_reimbursement/state_regulatory_reimbursement.csv** - Regulatory metrics
4. **nb05_competitive_landscape/state_competitive_landscape.csv** - Competition data

## Generation Script

**Script:** `generate_blog_charts.py`  
**Language:** Python 3  
**Dependencies:** pandas, numpy (no external Plotly package required - uses JSON/HTML approach)  
**Execution Time:** <1 second  
**Output:** 8 HTML files (96K total)

### Regeneration
To regenerate all charts after data updates:
```bash
python3 generate_blog_charts.py
```

## File Summary

```
data/outputs/blog_charts/
├── chart_opportunity_map.html          (8.0K)
├── chart_radar_top5.html               (4.0K)
├── chart_heatmap_expansion.html        (8.0K)
├── chart_top10_table.html              (4.0K)
├── chart_growth_curves.html            (4.0K)
├── chart_revenue_by_wave.html          (4.0K)
├── chart_regulatory_map.html           (8.0K)
└── chart_reimbursement_map.html        (8.0K)
                                  TOTAL: 48K
```

## Notes

- Charts automatically update colors, fonts, and sizing for professional appearance
- All numerical data is formatted appropriately (millions with 'M', currency with '$', percentages with '%')
- Hover tooltips provide context without cluttering the visualization
- Responsive design ensures charts work on mobile, tablet, and desktop

---
Generated: March 30, 2026  
Status: Production Ready
