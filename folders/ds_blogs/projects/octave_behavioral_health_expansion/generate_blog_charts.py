#!/usr/bin/env python3
"""
Generate interactive HTML charts for behavioral health expansion blog.
Creates 8 professional charts using Plotly JSON embedded in HTML.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
import sys


class ChartConfig:
    def __init__(self):
        self.base_dir = Path("/sessions/relaxed-beautiful-heisenberg/mnt/bitterscientist.com/folders/ds_blogs/projects/octave_behavioral_health_expansion")
        self.data_dir = self.base_dir / "data" / "outputs"
        self.output_dir = self.data_dir / "blog_charts"


def load_data(config: ChartConfig) -> Dict[str, pd.DataFrame]:
    """Load all required CSV files."""
    data = {}

    try:
        data['expansion_scores'] = pd.read_csv(
            config.data_dir / "nb07_expansion_scoring" / "state_expansion_scores.csv"
        )
        data['projections'] = pd.read_csv(
            config.data_dir / "nb08_projections" / "state_expansion_projections.csv"
        )
        data['regulatory'] = pd.read_csv(
            config.data_dir / "nb06_regulatory_reimbursement" / "state_regulatory_reimbursement.csv"
        )
        data['competitive'] = pd.read_csv(
            config.data_dir / "nb05_competitive_landscape" / "state_competitive_landscape.csv"
        )

        print(f"Successfully loaded {len(data)} datasets")
        return data
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        sys.exit(1)


def normalize_minmax(values: np.ndarray, invert: bool = False) -> np.ndarray:
    """Normalize values to 0-100 range using min-max scaling."""
    values = np.array(values, dtype=float)
    min_val = np.nanmin(values)
    max_val = np.nanmax(values)

    if max_val == min_val:
        normalized = np.ones_like(values) * 50
    else:
        normalized = (values - min_val) / (max_val - min_val) * 100

    if invert:
        normalized = 100 - normalized

    return normalized


def write_plotly_html(filename: Path, data: Dict, layout: Dict):
    """Write Plotly chart to HTML file."""
    plotly_json = json.dumps(data)
    layout_json = json.dumps(layout)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 100%;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #1f4788;
            margin-bottom: 10px;
        }}
        #plotDiv {{
            width: 100%;
            height: 100%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div id="plotDiv"></div>
    </div>
    <script>
        var data = {plotly_json};
        var layout = {layout_json};
        Plotly.newPlot('plotDiv', data, layout, {{responsive: true}});
    </script>
</body>
</html>"""

    with open(filename, 'w') as f:
        f.write(html)


def generate_chart_opportunity_map(data: Dict, config: ChartConfig):
    """Chart 1: Choropleth of expansion_opportunity_score."""
    df = data['expansion_scores'].copy()

    trace = {
        'type': 'choropleth',
        'locations': df['state_abbrev'].tolist(),
        'z': df['expansion_opportunity_score'].tolist(),
        'locationmode': 'USA-states',
        'colorscale': 'Viridis',
        'text': [f"{row['state_name']}<br>Score: {row['expansion_opportunity_score']:.1f}<br>Tier: {row['expansion_tier']}"
                for _, row in df.iterrows()],
        'hoverinfo': 'text',
        'colorbar': {'title': 'Score'}
    }

    layout = {
        'title': 'Expansion Opportunity Score by State (Composite 0-100)',
        'geo': {
            'scope': 'usa',
            'projection': {'type': 'albers usa'},
            'showland': True,
            'landcolor': 'rgb(243, 243, 243)'
        },
        'width': 900,
        'height': 600
    }

    write_plotly_html(config.output_dir / "chart_opportunity_map.html", [trace], layout)
    print("✓ chart_opportunity_map.html")


def generate_chart_radar_top5(data: Dict, config: ChartConfig):
    """Chart 2: Radar chart for top 5 expansion states."""
    df = data['expansion_scores'][data['expansion_scores']['is_octave_state'] == False].copy()
    top5 = df.nlargest(5, 'expansion_opportunity_score')

    dimensions = ['provider_pool_score', 'payer_coverage_score', 'unmet_demand_score',
                  'competitive_advantage_score', 'regulatory_score', 'reimbursement_score']

    dim_labels = ['Provider Pool', 'Payer Coverage', 'Unmet Demand',
                  'Competitive Advantage', 'Regulatory', 'Reimbursement']

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    traces = []

    for idx, (_, state) in enumerate(top5.iterrows()):
        values = [float(state[dim]) for dim in dimensions]
        values_complete = values + [values[0]]
        theta_complete = dim_labels + [dim_labels[0]]

        trace = {
            'type': 'scatterpolar',
            'r': values_complete,
            'theta': theta_complete,
            'fill': 'toself',
            'name': state['state_abbrev'],
            'line': {'color': colors[idx]},
            'opacity': 0.7
        }
        traces.append(trace)

    layout = {
        'title': 'Top 5 Expansion States: Scoring Profile',
        'polar': {
            'radialaxis': {
                'visible': True,
                'range': [0, 100]
            }
        },
        'width': 900,
        'height': 700,
        'showlegend': True
    }

    write_plotly_html(config.output_dir / "chart_radar_top5.html", traces, layout)
    print("✓ chart_radar_top5.html")


def generate_chart_heatmap_expansion(data: Dict, config: ChartConfig):
    """Chart 3: Heatmap of expansion states with normalized metrics."""
    df = data['expansion_scores'][data['expansion_scores']['is_octave_state'] == False].copy()
    df = df.sort_values('expansion_opportunity_score', ascending=False)

    columns_to_normalize = [
        'total_population', 'total_bh_providers', 'octave_accessible_covered_lives',
        'treatment_gap_pct', 'competitive_intensity_score', 'regulatory_ease_score',
        'reimbursement_favorability', 'expansion_opportunity_score'
    ]

    col_labels = [
        'Population', 'BH Providers', 'Accessible Covered Lives',
        'Treatment Gap %', 'Competitive Intensity', 'Regulatory Ease',
        'Reimbursement Favorability', 'Opportunity Score'
    ]

    heatmap_data = []
    for col, label in zip(columns_to_normalize, col_labels):
        if col in df.columns:
            invert = (col == 'competitive_intensity_score')
            normalized = normalize_minmax(df[col].values, invert=invert)
            heatmap_data.append(normalized.tolist())

    trace = {
        'type': 'heatmap',
        'z': heatmap_data,
        'x': df['state_abbrev'].tolist(),
        'y': col_labels,
        'colorscale': 'RdYlGn',
        'colorbar': {'title': 'Normalized\nScore'},
        'hovertemplate': '%{y}: %{z:.1f}<extra></extra>'
    }

    layout = {
        'title': f'Expansion State Comparison ({len(df)} States, Normalized 0-100)',
        'xaxis': {'title': 'State', 'tickangle': -45},
        'yaxis': {'title': 'Metric'},
        'width': 1000,
        'height': 600
    }

    write_plotly_html(config.output_dir / "chart_heatmap_expansion.html", [trace], layout)
    print("✓ chart_heatmap_expansion.html")


def generate_chart_top10_table(data: Dict, config: ChartConfig):
    """Chart 4: Table of top 10 expansion opportunities."""
    df = data['expansion_scores'][data['expansion_scores']['is_octave_state'] == False].copy()
    top10 = df.nlargest(10, 'expansion_opportunity_score')

    table_data = {
        'Rank': list(range(1, 11)),
        'State': top10['state_name'].tolist(),
        'Score': [round(x, 1) for x in top10['expansion_opportunity_score'].values],
        'Tier': top10['expansion_tier'].tolist(),
        'Accessible Covered Lives (M)': [round(x / 1e6, 2) for x in top10['octave_accessible_covered_lives'].values],
        'BH Providers': [f"{int(x):,}" for x in top10['total_bh_providers'].values],
        'Treatment Gap %': [round(x, 1) for x in top10['treatment_gap_pct'].values],
        'Compact Score': [int(x) for x in top10['compact_score'].values],
    }

    trace = {
        'type': 'table',
        'header': {
            'values': [f'<b>{col}</b>' for col in table_data.keys()],
            'fill': {'color': '#1f4788'},
            'align': 'center',
            'font': {'color': 'white', 'size': 12}
        },
        'cells': {
            'values': [table_data[col] for col in table_data.keys()],
            'fill': {'color': 'rgba(245, 245, 245, 0.5)'},
            'align': 'center',
            'font': {'size': 11},
            'height': 30
        }
    }

    layout = {
        'title': 'Top 10 Expansion Opportunities',
        'width': 1000,
        'height': 500
    }

    write_plotly_html(config.output_dir / "chart_top10_table.html", [trace], layout)
    print("✓ chart_top10_table.html")


def generate_chart_growth_curves(data: Dict, config: ChartConfig):
    """Chart 5: Three subplots showing cumulative growth metrics."""
    df = data['projections'].sort_values('rank').copy()

    trace1 = {
        'x': df['rank'].tolist(),
        'y': df['cumulative_providers'].tolist(),
        'mode': 'lines+markers',
        'name': 'Providers',
        'line': {'color': '#1f77b4', 'width': 2},
        'marker': {'size': 5},
        'hovertemplate': '<b>%{customdata}</b><br>Rank %{x}<br>Providers: %{y:,}<extra></extra>',
        'customdata': df['state_abbrev'].tolist(),
        'xaxis': 'x1',
        'yaxis': 'y1'
    }

    trace2 = {
        'x': df['rank'].tolist(),
        'y': (df['cumulative_covered_lives'] / 1e6).tolist(),
        'mode': 'lines+markers',
        'name': 'Covered Lives',
        'line': {'color': '#ff7f0e', 'width': 2},
        'marker': {'size': 5},
        'hovertemplate': '<b>%{customdata}</b><br>Rank %{x}<br>Lives: %{y:.1f}M<extra></extra>',
        'customdata': df['state_abbrev'].tolist(),
        'xaxis': 'x2',
        'yaxis': 'y2'
    }

    trace3 = {
        'x': df['rank'].tolist(),
        'y': (df['cumulative_annual_revenue'] / 1e6).tolist(),
        'mode': 'lines+markers',
        'name': 'Revenue',
        'line': {'color': '#2ca02c', 'width': 2},
        'marker': {'size': 5},
        'hovertemplate': '<b>%{customdata}</b><br>Rank %{x}<br>Revenue: $%{y:.1f}M<extra></extra>',
        'customdata': df['state_abbrev'].tolist(),
        'xaxis': 'x3',
        'yaxis': 'y3'
    }

    layout = {
        'title': 'Cumulative Growth as Expansion States Added (Ranked by Opportunity Score)',
        'width': 1200,
        'height': 400,
        'showlegend': False,
        'xaxis1': {'title': 'Rank', 'domain': [0, 0.32]},
        'xaxis2': {'title': 'Rank', 'domain': [0.34, 0.66]},
        'xaxis3': {'title': 'Rank', 'domain': [0.68, 1]},
        'yaxis1': {'title': 'Providers'},
        'yaxis2': {'title': 'Covered Lives (M)'},
        'yaxis3': {'title': 'Revenue ($M)'}
    }

    write_plotly_html(config.output_dir / "chart_growth_curves.html", [trace1, trace2, trace3], layout)
    print("✓ chart_growth_curves.html")


def generate_chart_revenue_by_wave(data: Dict, config: ChartConfig):
    """Chart 6: Bar chart of revenue by expansion wave."""
    df = data['projections'].copy()

    wave_revenue = df.groupby('expansion_wave')['annual_revenue_opportunity'].sum() / 1e6
    wave_revenue = wave_revenue.sort_index()

    waves = wave_revenue.index.tolist()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(waves)]

    trace = {
        'x': waves,
        'y': wave_revenue.values.tolist(),
        'type': 'bar',
        'text': [f'${v:.1f}M' for v in wave_revenue.values],
        'textposition': 'outside',
        'marker': {'color': colors},
        'hovertemplate': '<b>%{x}</b><br>Revenue: $%{y:.1f}M<extra></extra>'
    }

    layout = {
        'title': 'Hypothetical Annual Revenue by Expansion Wave (Conservative: 0.5% Penetration)',
        'xaxis': {'title': 'Expansion Wave'},
        'yaxis': {'title': 'Annual Revenue ($M)'},
        'width': 900,
        'height': 500,
        'showlegend': False,
        'plot_bgcolor': 'rgba(240, 240, 240, 0.5)'
    }

    write_plotly_html(config.output_dir / "chart_revenue_by_wave.html", [trace], layout)
    print("✓ chart_revenue_by_wave.html")


def generate_chart_regulatory_map(data: Dict, config: ChartConfig):
    """Chart 7: Choropleth of regulatory_ease_score."""
    df = data['expansion_scores'].copy()

    trace = {
        'type': 'choropleth',
        'locations': df['state_abbrev'].tolist(),
        'z': df['regulatory_ease_score'].tolist(),
        'locationmode': 'USA-states',
        'colorscale': 'Greens',
        'text': [f"{row['state_name']}<br>Ease: {row['regulatory_ease_score']}<br>Compact: {row['compact_score']}<br>Telehealth: {row['telehealth_parity']}"
                for _, row in df.iterrows()],
        'hoverinfo': 'text',
        'colorbar': {'title': 'Ease Score'}
    }

    layout = {
        'title': 'Regulatory Ease Score (Interstate Compacts + Telehealth Parity)',
        'geo': {
            'scope': 'usa',
            'projection': {'type': 'albers usa'},
            'showland': True,
            'landcolor': 'rgb(243, 243, 243)'
        },
        'width': 900,
        'height': 600
    }

    write_plotly_html(config.output_dir / "chart_regulatory_map.html", [trace], layout)
    print("✓ chart_regulatory_map.html")


def generate_chart_reimbursement_map(data: Dict, config: ChartConfig):
    """Chart 8: Choropleth of reimbursement_favorability."""
    df = data['expansion_scores'].copy()

    trace = {
        'type': 'choropleth',
        'locations': df['state_abbrev'].tolist(),
        'z': df['reimbursement_favorability'].tolist(),
        'locationmode': 'USA-states',
        'colorscale': 'YlGnBu',
        'text': [f"{row['state_name']}<br>Favorability: {row['reimbursement_favorability']}<br>Medicare 90837: ${row['medicare_90837_rate']}"
                for _, row in df.iterrows()],
        'hoverinfo': 'text',
        'colorbar': {'title': 'Favorability Score'}
    }

    layout = {
        'title': 'Reimbursement Favorability (Medicare Fee Schedule Benchmark)',
        'geo': {
            'scope': 'usa',
            'projection': {'type': 'albers usa'},
            'showland': True,
            'landcolor': 'rgb(243, 243, 243)'
        },
        'width': 900,
        'height': 600
    }

    write_plotly_html(config.output_dir / "chart_reimbursement_map.html", [trace], layout)
    print("✓ chart_reimbursement_map.html")


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("Generating Interactive Plotly Charts for Behavioral Health Expansion")
    print("="*70 + "\n")

    config = ChartConfig()
    config.output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {config.output_dir}\n")

    print("Loading data files...")
    data = load_data(config)
    print()

    print("Generating charts...\n")

    try:
        generate_chart_opportunity_map(data, config)
        generate_chart_radar_top5(data, config)
        generate_chart_heatmap_expansion(data, config)
        generate_chart_top10_table(data, config)
        generate_chart_growth_curves(data, config)
        generate_chart_revenue_by_wave(data, config)
        generate_chart_regulatory_map(data, config)
        generate_chart_reimbursement_map(data, config)

        print("\n" + "="*70)
        print("SUCCESS: All 8 charts generated successfully!")
        print("="*70)

        print("\nGenerated files:")
        for chart_file in sorted(config.output_dir.glob("*.html")):
            size = chart_file.stat().st_size / 1024
            print(f"  • {chart_file.name} ({size:.1f} KB)")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
