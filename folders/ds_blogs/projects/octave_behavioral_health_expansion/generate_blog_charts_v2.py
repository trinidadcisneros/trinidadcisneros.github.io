#!/usr/bin/env python3
"""
Generate comprehensive interactive HTML charts for behavioral health expansion blog.
Creates 16 professional Plotly charts with all requested fixes and enhancements.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import sys


class ChartConfig:
    def __init__(self):
        self.base_dir = Path("/sessions/relaxed-beautiful-heisenberg/mnt/bitterscientist.com/folders/ds_blogs/projects/octave_behavioral_health_expansion")
        self.data_dir = self.base_dir / "data" / "outputs"
        self.output_dir = self.data_dir / "blog_charts"
        self.output_dir.mkdir(parents=True, exist_ok=True)


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
        data['providers'] = pd.read_csv(
            config.data_dir / "nb02_provider_landscape" / "state_provider_counts.csv"
        )
        data['demand'] = pd.read_csv(
            config.data_dir / "nb04_mental_health_demand" / "state_mental_health_demand.csv"
        )
        data['covered_lives'] = pd.read_csv(
            config.data_dir / "nb03_payer_mix" / "state_octave_covered_lives.csv"
        )
        data['population'] = pd.read_csv(
            config.data_dir / "nb01_census_population" / "state_population_base.csv"
        )
        print(f"Successfully loaded {len(data)} datasets")
        return data
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        sys.exit(1)


def sanitize_json(obj):
    """Convert NaN/Inf values to None for JSON serialization, and ensure boolean types are preserved."""
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, (int, np.integer)):
        return int(obj)
    elif isinstance(obj, (np.ndarray, pd.Series)):
        return [sanitize_json(item) for item in obj]
    elif isinstance(obj, (list, tuple)):
        return [sanitize_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    return obj


def write_plotly_html(filename: Path, data: List, layout: Dict):
    """Write Plotly chart to HTML file with white background."""
    # Sanitize data and layout
    data_clean = sanitize_json(data)
    layout_clean = sanitize_json(layout)

    plotly_json = json.dumps(data_clean)
    layout_json = json.dumps(layout_clean)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 10px; background-color: white; }}
        #plotDiv {{ width: 100%; height: 100%; }}
    </style>
</head>
<body>
    <div id="plotDiv"></div>
    <script>
        var data = {plotly_json};
        var layout = {layout_json};
        Plotly.newPlot('plotDiv', data, layout, {{responsive: true}});
    </script>
</body>
</html>"""

    with open(filename, 'w') as f:
        f.write(html)
    print(f"Generated: {filename.name}")


def chart_treatment_gap_map(data: Dict, config: ChartConfig):
    """Chart 1: Treatment Gap Map"""
    df = data['expansion_scores'].copy()
    df = df.sort_values('treatment_gap_pct', ascending=False)

    trace = {
        'type': 'choropleth',
        'locations': df['state_abbrev'].tolist(),
        'z': df['treatment_gap_pct'].tolist(),
        'colorscale': 'Reds',
        'locationmode': 'USA-states',
        'colorbar': {
            'title': 'Treatment Gap (%)',
            'thickness': 20,
            'len': 0.7
        },
        'hovertemplate': '<b>%{text}</b><br>Treatment Gap: %{z:.1f}%<extra></extra>',
        'text': df['state_name'].tolist(),
        'zmin': 45,
        'zmax': 65
    }

    layout = {
        'title': {
            'text': 'More Than Half of Adults with Mental Illness Go Untreated in Most States',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'geo': {
            'scope': 'usa',
            'projection': {'type': 'albers usa'},
            'showlakes': bool(True),
            'lakecolor': 'rgb(255, 255, 255)'
        },
        'width': 1000,
        'height': 600,
        'annotations': [
            {
                'text': 'Percentage of adults with Any Mental Illness (AMI) who did not receive treatment',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': 0.95,
                'showarrow': bool(False),
                'font': {'size': 12, 'color': '#666'}
            },
            {
                'text': 'The treatment gap ranges from 48% to 64% across states, meaning at least half of adults with mental illness go untreated everywhere.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.12,
                'showarrow': bool(False),
                'font': {'size': 11, 'color': '#333'}
            },
            {
                'text': 'Source: SAMHSA National Survey on Drug Use and Health (NSDUH), 2022-2023<br>Data: samhsa.gov/data/nsduh',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.18,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_treatment_gap_map.html', [trace], layout)


def chart_demand_supply_scatter(data: Dict, config: ChartConfig):
    """Chart 2: Demand Supply Scatter with quadrant labels"""
    df = data['expansion_scores'].copy()
    df = df.dropna(subset=['providers_per_100k', 'treatment_gap_pct'])

    # Add full state names to trace
    df['state_label'] = df['state_name'] + ' (' + df['state_abbrev'] + ')'

    # Get quartiles for reference lines
    x_median = df['providers_per_100k'].median()
    y_median = df['treatment_gap_pct'].median()

    # Calculate bubble sizes: sqrt scale normalized to 5-40px range
    pop_array = df['total_population'].values
    sqrt_pop = np.sqrt(pop_array)
    max_sqrt = sqrt_pop.max()
    sizes = (sqrt_pop / max_sqrt * 35) + 5

    trace = {
        'type': 'scatter',
        'mode': 'markers',
        'x': df['providers_per_100k'].tolist(),
        'y': df['treatment_gap_pct'].tolist(),
        'text': df['state_abbrev'].tolist(),
        'textposition': 'top center',
        'textfont': {'size': 9, 'color': '#333'},
        'marker': {
            'size': sizes.tolist(),
            'sizemode': 'diameter',
            'color': df['treatment_gap_pct'].tolist(),
            'colorscale': 'RdYlGn_r',
            'showscale': bool(False),
            'line': {'width': 0.5, 'color': 'white'},
            'opacity': 0.7
        },
        'hovertemplate': '<b>%{customdata[0]}</b><br>Providers per 100k: %{x:.1f}<br>Treatment Gap: %{y:.1f}%<extra></extra>',
        'customdata': df[['state_name', 'state_abbrev']].values.tolist()
    }

    layout = {
        'title': {
            'text': 'States with Fewer Providers Per Capita Have Higher Unmet Treatment Needs',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'xaxis': {
            'title': 'Behavioral Health Providers per 100,000 Adults',
            'zeroline': bool(False)
        },
        'yaxis': {
            'title': 'Treatment Gap (% of Adults with Any Mental Illness Not Receiving Treatment)',
            'zeroline': bool(False)
        },
        'width': 1000,
        'height': 650,
        'hovermode': 'closest',
        'shapes': [
            {
                'type': 'line',
                'x0': df['providers_per_100k'].min(),
                'x1': df['providers_per_100k'].max(),
                'y0': y_median,
                'y1': y_median,
                'line': {'color': '#999', 'width': 2, 'dash': 'dash'}
            },
            {
                'type': 'line',
                'x0': x_median,
                'x1': x_median,
                'y0': df['treatment_gap_pct'].min(),
                'y1': df['treatment_gap_pct'].max(),
                'line': {'color': '#999', 'width': 2, 'dash': 'dash'}
            }
        ],
        'annotations': [
            {
                'text': 'High Need<br>Low Supply',
                'x': df['providers_per_100k'].min() + 20,
                'y': df['treatment_gap_pct'].max() - 3,
                'showarrow': bool(False),
                'font': {'size': 11, 'color': '#d62728', 'family': 'Arial Black'}
            },
            {
                'text': 'Low Need<br>High Supply',
                'x': df['providers_per_100k'].max() - 40,
                'y': df['treatment_gap_pct'].min() + 2,
                'showarrow': bool(False),
                'font': {'size': 11, 'color': '#2ca02c', 'family': 'Arial Black'}
            },
            {
                'text': 'Sources: Bureau of Labor Statistics OES 2023, SAMHSA NSDUH 2022-2023',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.2,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ],
        'margin': {'bottom': 120}
    }

    write_plotly_html(config.output_dir / 'chart_demand_supply_scatter.html', [trace], layout)


def chart_provider_density_map(data: Dict, config: ChartConfig):
    """Chart 3: Provider Density Map with improved color scale"""
    df = data['expansion_scores'].copy()

    trace = {
        'type': 'choropleth',
        'locations': df['state_abbrev'].tolist(),
        'z': df['providers_per_100k'].tolist(),
        'colorscale': 'Turbo',
        'locationmode': 'USA-states',
        'colorbar': {
            'title': 'Providers<br>per 100k',
            'thickness': 20,
            'len': 0.7
        },
        'hovertemplate': '<b>%{text}</b><br>Providers per 100k: %{z:.1f}<extra></extra>',
        'text': df['state_name'].tolist(),
        'zmin': df['providers_per_100k'].min(),
        'zmax': df['providers_per_100k'].max()
    }

    layout = {
        'title': {
            'text': 'Where Are the Providers? Behavioral Health Workforce Varies 5x Across States',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'geo': {
            'scope': 'usa',
            'projection': {'type': 'albers usa'},
            'showlakes': bool(True),
            'lakecolor': 'rgb(255, 255, 255)'
        },
        'width': 1000,
        'height': 600,
        'annotations': [
            {
                'text': 'Licensed behavioral health providers per 100,000 adults',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': 0.95,
                'showarrow': bool(False),
                'font': {'size': 12, 'color': '#666'}
            },
            {
                'text': 'Northeastern states (Massachusetts, Vermont, Connecticut) have 3-5x more providers per capita than Southern states (Alabama, Mississippi, Texas)',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.12,
                'showarrow': bool(False),
                'font': {'size': 11, 'color': '#333'}
            },
            {
                'text': 'Sources: Bureau of Labor Statistics OES 2023, Health Resources and Services Administration (HRSA) NPPES',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.18,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_provider_density_map.html', [trace], layout)


def chart_provider_types_bar(data: Dict, config: ChartConfig):
    """Chart 4: Provider Types Bar Chart with legend fix"""
    df = data['providers'].copy()

    # Select top 15 states by total providers
    df_top = df.nlargest(15, 'total_bh_providers')

    provider_types = {
        'psychiatrists': 'Psychiatrists',
        'psychologists': 'Psychologists',
        'mh_counselors': 'Mental Health Counselors',
        'mft_therapists': 'Marriage & Family Therapists',
        'sw_social_workers': 'Social Workers',
        'sa_counselors': 'Substance Abuse Counselors'
    }

    traces = []
    for col, label in provider_types.items():
        traces.append({
            'type': 'bar',
            'name': label,
            'x': df_top['state_abbrev'].tolist(),
            'y': df_top[col].tolist(),
            'hovertemplate': f'<b>%{{x}}</b><br>{label}: %{{y}}<extra></extra>'
        })

    layout = {
        'title': {
            'text': 'Mental Health Counselors and Social Workers Make Up the Majority of the Behavioral Health Workforce',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 17}
        },
        'barmode': 'stack',
        'xaxis': {'title': 'State'},
        'yaxis': {'title': 'Number of Providers'},
        'width': 950,
        'height': 650,
        'legend': {
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.15,
            'xanchor': 'center',
            'x': 0.5
        },
        'annotations': [
            {
                'text': 'Source: Bureau of Labor Statistics Occupational Employment Statistics (OES), 2023',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.08,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ],
        'margin': {'top': 100}
    }

    write_plotly_html(config.output_dir / 'chart_provider_types_bar.html', traces, layout)


def chart_competitive_map(data: Dict, config: ChartConfig):
    """Chart 5: Competitive Intensity Map"""
    df = data['expansion_scores'].copy()

    trace = {
        'type': 'choropleth',
        'locations': df['state_abbrev'].tolist(),
        'z': df['competitive_intensity_score'].tolist(),
        'colorscale': 'RdYlGn_r',
        'locationmode': 'USA-states',
        'colorbar': {
            'title': 'Competition<br>Score',
            'thickness': 20,
            'len': 0.7
        },
        'hovertemplate': '<b>%{text}</b><br>Competitive Intensity: %{z:.1f}<extra></extra>',
        'text': df['state_name'].tolist(),
        'zmin': 0,
        'zmax': 100
    }

    layout = {
        'title': {
            'text': 'Where Is Competition Highest? A Composite View of Market Saturation',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'geo': {
            'scope': 'usa',
            'projection': {'type': 'albers usa'},
            'showlakes': bool(True),
            'lakecolor': 'rgb(255, 255, 255)'
        },
        'width': 1000,
        'height': 600,
        'annotations': [
            {
                'text': 'Competitive intensity is a composite score (0-100) combining: (1) estimated competitor provider density per 100k, (2) brick-and-mortar behavioral health facility density from approximately 18,000 SAMHSA-listed facilities, and (3) broadband access as a proxy for telehealth viability. This score was calculated for this analysis and is NOT published by SAMHSA.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': 0.92,
                'showarrow': bool(False),
                'font': {'size': 11, 'color': '#666'},
                'align': 'center'
            },
            {
                'text': '26 of 28 expansion target states have lower competitive intensity than the average of Octave\'s current operating states.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.12,
                'showarrow': bool(False),
                'font': {'size': 11, 'color': '#333'}
            },
            {
                'text': 'Sources: SAMHSA Treatment Locator (facility counts), Federal Communications Commission (FCC) broadband data. Composite scoring by author.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.18,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_competitive_map.html', [trace], layout)


def chart_footprint_map(data: Dict, config: ChartConfig):
    """Chart 6: Octave Footprint Map with legend"""
    df = data['expansion_scores'].copy()

    # Create two traces: one for current, one for expansion
    current = df[df['is_octave_state'] == True]
    expansion = df[(df['is_octave_state'] == False) & (df['expansion_tier'].notna())]

    trace_current = {
        'type': 'choropleth',
        'locations': current['state_abbrev'].tolist(),
        'z': [1] * len(current),
        'colorscale': [[0, 'lightblue'], [1, '#1f77b4']],
        'locationmode': 'USA-states',
        'showscale': bool(False),
        'hovertemplate': '<b>%{text}</b><br>Current Operating State<extra></extra>',
        'text': current['state_name'].tolist(),
        'name': 'Current Operating States',
        'marker': {'line': {'color': 'white', 'width': 2}}
    }

    trace_expansion = {
        'type': 'choropleth',
        'locations': expansion['state_abbrev'].tolist(),
        'z': [0.5] * len(expansion),
        'colorscale': [[0, 'lightyellow'], [1, '#ff7f0e']],
        'locationmode': 'USA-states',
        'showscale': bool(False),
        'hovertemplate': '<b>%{text}</b><br>Expansion Target State<extra></extra>',
        'text': expansion['state_name'].tolist(),
        'name': 'Expansion Target States',
        'marker': {'line': {'color': 'white', 'width': 2}}
    }

    layout = {
        'title': {
            'text': 'Octave\'s Current Footprint Covers 23 States Plus Washington D.C., Leaving 28 Expansion Opportunities',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 17}
        },
        'geo': {
            'scope': 'usa',
            'projection': {'type': 'albers usa'},
            'showlakes': bool(True),
            'lakecolor': 'rgb(255, 255, 255)'
        },
        'width': 1000,
        'height': 600,
        'legend': {
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.12,
            'xanchor': 'center',
            'x': 0.5
        },
        'annotations': [
            {
                'text': 'Source: Octave Health Group website, March 2026',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.18,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_footprint_map.html', [trace_current, trace_expansion], layout)


def chart_covered_lives_comparison(data: Dict, config: ChartConfig):
    """Chart 7: Covered Lives Comparison - Top 15 states"""
    df = data['covered_lives'].copy()
    df = df.nlargest(15, 'octave_raw_payer_lives')

    traces = [
        {
            'type': 'bar',
            'name': 'Raw Payer Model Estimate (Theoretical Maximum)',
            'x': df['state_abbrev'].tolist(),
            'y': (df['octave_raw_payer_lives'] / 1e6).tolist(),
            'hovertemplate': '<b>%{x}</b><br>Raw Estimate: %{y:.2f}M<extra></extra>'
        },
        {
            'type': 'bar',
            'name': 'Adjusted Estimate (40% Network Access Rate)',
            'x': df['state_abbrev'].tolist(),
            'y': (df['octave_accessible_covered_lives'] / 1e6).tolist(),
            'hovertemplate': '<b>%{x}</b><br>Adjusted: %{y:.2f}M<extra></extra>'
        }
    ]

    layout = {
        'title': {
            'text': 'The 40% Network Access Rate Cuts Theoretical Payer Coverage in Half',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'barmode': 'group',
        'xaxis': {'title': 'State'},
        'yaxis': {'title': 'Covered Lives (Millions)'},
        'width': 1000,
        'height': 600,
        'legend': {
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.12,
            'xanchor': 'center',
            'x': 0.5
        },
        'annotations': [
            {
                'text': 'Raw payer model estimate vs. adjusted estimate after applying 40% network access rate',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': 0.95,
                'showarrow': bool(False),
                'font': {'size': 12, 'color': '#666'}
            },
            {
                'text': 'Octave reports approximately 40 million covered lives. Our raw model estimates 82 million, suggesting that roughly 40% of commercially insured lives in partner payer books are actively accessible.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.12,
                'showarrow': bool(False),
                'font': {'size': 11, 'color': '#333'}
            },
            {
                'text': 'Sources: Kaiser Family Foundation (KFF) insurance coverage data, insurer market share reports, Octave public disclosures',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.18,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ],
        'margin': {'top': 120}
    }

    write_plotly_html(config.output_dir / 'chart_covered_lives_comparison.html', traces, layout)


def chart_scoring_weights(data: Dict, config: ChartConfig):
    """Chart 8: Scoring Weights - Pie/Donut Chart"""
    labels = [
        'Provider Pool',
        'Payer Coverage',
        'Unmet Demand',
        'Competitive Advantage',
        'Regulatory Ease',
        'Reimbursement Favorability'
    ]
    values = [20, 25, 20, 10, 15, 10]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

    trace = {
        'type': 'pie',
        'labels': labels,
        'values': values,
        'hole': 0.4,
        'marker': {'colors': colors},
        'textinfo': 'label+percent',
        'textposition': 'auto',
        'hovertemplate': '<b>%{label}</b><br>Weight: %{value}%<extra></extra>'
    }

    layout = {
        'title': {
            'text': 'How We Weighted the Six Expansion Dimensions',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        'width': 700,
        'height': 400,
        'showlegend': bool(True)
    }

    write_plotly_html(config.output_dir / 'chart_scoring_weights.html', [trace], layout)


def chart_opportunity_map(data: Dict, config: ChartConfig):
    """Chart 9: Opportunity Score Map"""
    df = data['expansion_scores'].copy()
    df = df[df['is_octave_state'] == False]  # Only expansion states

    trace = {
        'type': 'choropleth',
        'locations': df['state_abbrev'].tolist(),
        'z': df['expansion_opportunity_score'].tolist(),
        'colorscale': 'Viridis',
        'locationmode': 'USA-states',
        'colorbar': {
            'title': 'Opportunity<br>Score',
            'thickness': 20,
            'len': 0.7
        },
        'hovertemplate': '<b>%{text}</b><br>Opportunity Score: %{z:.1f}<extra></extra>',
        'text': df['state_name'].tolist(),
        'zmin': df['expansion_opportunity_score'].min(),
        'zmax': df['expansion_opportunity_score'].max()
    }

    layout = {
        'title': {
            'text': 'Mid-Size States Emerge as the Strongest Expansion Opportunities',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'geo': {
            'scope': 'usa',
            'projection': {'type': 'albers usa'},
            'showlakes': bool(True),
            'lakecolor': 'rgb(255, 255, 255)'
        },
        'width': 1000,
        'height': 600,
        'annotations': [
            {
                'text': 'Composite expansion opportunity score (0-100) across six weighted dimensions',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': 0.95,
                'showarrow': bool(False),
                'font': {'size': 12, 'color': '#666'}
            },
            {
                'text': 'The top expansion targets are not the largest remaining states but mid-size states where provider density, unmet demand, and regulatory ease converge favorably.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.12,
                'showarrow': bool(False),
                'font': {'size': 11, 'color': '#333'}
            },
            {
                'text': 'Source: Multi-dimensional scoring model using Census, Bureau of Labor Statistics (BLS), Kaiser Family Foundation (KFF), SAMHSA, Centers for Medicare and Medicaid Services (CMS), and compact roster data',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.18,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_opportunity_map.html', [trace], layout)


def chart_heatmap_expansion(data: Dict, config: ChartConfig):
    """Chart 10: Expansion Heatmap"""
    df = data['expansion_scores'].copy()
    df = df[df['is_octave_state'] == False].copy()
    df = df.sort_values('expansion_opportunity_score', ascending=False).head(28)

    dimensions = [
        ('provider_pool_score', 'Providers'),
        ('payer_coverage_score', 'Payer Coverage'),
        ('unmet_demand_score', 'Unmet Need'),
        ('competitive_advantage_score', 'Low Competition'),
        ('regulatory_score', 'Regulatory Ease'),
        ('reimbursement_score', 'Reimbursement'),
        ('expansion_opportunity_score', 'Overall Score')
    ]

    z_data = []
    for col, _ in dimensions:
        z_data.append(df[col].fillna(0).tolist())

    trace = {
        'type': 'heatmap',
        'z': z_data,
        'x': df['state_abbrev'].tolist(),
        'y': [label for _, label in dimensions],
        'colorscale': 'RdYlGn',
        'zmin': 0,
        'zmax': 100,
        'colorbar': {'title': 'Score'},
        'hovertemplate': '<b>%{y}</b><br>%{x}: %{z:.1f}<extra></extra>'
    }

    layout = {
        'title': {
            'text': 'How Each Expansion State Scores Across Six Dimensions',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'xaxis': {'title': 'State'},
        'yaxis': {'title': 'Dimension'},
        'width': 1200,
        'height': 700,
        'margin': {'left': 150, 'bottom': 100},
        'annotations': [
            {
                'text': 'Source: Multi-dimensional scoring model',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.1,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_heatmap_expansion.html', [trace], layout)


def chart_top10_table(data: Dict, config: ChartConfig):
    """Chart 11: Top 10 Expansion Opportunities Table"""
    df = data['expansion_scores'].copy()
    df = df[df['is_octave_state'] == False].copy()
    df = df.nlargest(10, 'expansion_opportunity_score').reset_index(drop=True)
    df['rank'] = range(1, len(df) + 1)

    def format_number(val):
        if pd.isna(val):
            return ''
        if val >= 1e6:
            return f'{val/1e6:.1f}M'
        elif val >= 1e3:
            return f'{val/1e3:.0f}K'
        return f'{int(val)}'

    def clean_tier(tier):
        if pd.isna(tier):
            return ''
        return tier.split(':')[0].strip()

    header = [
        '<b>Rank</b>',
        '<b>State</b>',
        '<b>Overall Score</b>',
        '<b>Tier</b>',
        '<b>Accessible Covered Lives</b>',
        '<b>Behavioral Health Providers</b>',
        '<b>Treatment Gap %</b>',
        '<b>Interstate Compacts</b>'
    ]

    cells = {
        'Rank': df['rank'].astype(int).tolist(),
        'State': df['state_name'].tolist(),
        'Overall Score': [f'{x:.1f}' for x in df['expansion_opportunity_score']],
        'Tier': [clean_tier(x) for x in df['expansion_tier']],
        'Accessible Covered Lives': [format_number(x) for x in df['octave_accessible_covered_lives']],
        'Providers': [format_number(x) for x in df['total_bh_providers']],
        'Treatment Gap': [f'{x:.1f}%' for x in df['treatment_gap_pct']],
        'Compacts': [int(x) if not pd.isna(x) else '' for x in df['compact_score']]
    }

    trace = {
        'type': 'table',
        'header': {
            'values': header,
            'fill': {'color': '#1f4788'},
            'font': {'color': 'white', 'size': 11},
            'align': 'center'
        },
        'cells': {
            'values': [
                cells['Rank'],
                cells['State'],
                cells['Overall Score'],
                cells['Tier'],
                cells['Accessible Covered Lives'],
                cells['Providers'],
                cells['Treatment Gap'],
                cells['Compacts']
            ],
            'fill': {'color': [['#f0f0f0', 'white'] * (len(df)//2 + 1)][:len(df)]},
            'align': 'center',
            'font': {'size': 10}
        }
    }

    layout = {
        'title': {
            'text': 'Top 10 Expansion Opportunities: Where Multiple Factors Align',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'width': 1200,
        'height': 500
    }

    write_plotly_html(config.output_dir / 'chart_top10_table.html', [trace], layout)


def chart_radar_top5(data: Dict, config: ChartConfig):
    """Chart 12: Radar Chart for Top 5 Expansion States"""
    df = data['expansion_scores'].copy()
    df = df[df['is_octave_state'] == False].copy()
    df_top5 = df.nlargest(5, 'expansion_opportunity_score')

    categories = [
        'Provider Pool',
        'Payer Coverage',
        'Unmet Demand',
        'Competitive Advantage',
        'Regulatory Ease',
        'Reimbursement'
    ]

    traces = []
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    for idx, (_, row) in enumerate(df_top5.iterrows()):
        values = [
            row['provider_pool_score'],
            row['payer_coverage_score'],
            row['unmet_demand_score'],
            row['competitive_advantage_score'],
            row['regulatory_score'],
            row['reimbursement_score']
        ]
        values.append(values[0])  # Close the polygon

        trace = {
            'type': 'scatterpolar',
            'r': values,
            'theta': categories + [categories[0]],
            'fill': 'toself',
            'name': f'{row["state_abbrev"]} ({row["state_name"]})',
            'line': {'color': colors[idx]},
            'fillcolor': colors[idx]
        }
        traces.append(trace)

    layout = {
        'title': {
            'text': 'Top 5 Expansion States Show Balanced Profiles Across All Dimensions',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'polar': {
            'radialaxis': {
                'visible': bool(True),
                'range': [0, 100]
            }
        },
        'width': 900,
        'height': 700,
        'legend': {
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.1,
            'xanchor': 'center',
            'x': 0.5
        },
        'annotations': [
            {
                'text': 'Source: Multi-dimensional scoring model',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.1,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_radar_top5.html', traces, layout)


def chart_growth_curves(data: Dict, config: ChartConfig):
    """Chart 13: Growth Curves (Subplots)"""
    df = data['projections'].copy().sort_values('rank')
    df = df.head(20)  # First 20 waves

    traces = [
        {
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': df['rank'].tolist(),
            'y': df['cumulative_providers'].tolist(),
            'name': 'Cumulative Providers',
            'xaxis': 'x',
            'yaxis': 'y'
        },
        {
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': df['rank'].tolist(),
            'y': (df['cumulative_covered_lives'] / 1e6).tolist(),
            'name': 'Cumulative Covered Lives (M)',
            'xaxis': 'x2',
            'yaxis': 'y2'
        },
        {
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': df['rank'].tolist(),
            'y': (df['cumulative_annual_revenue'] / 1e6).tolist(),
            'name': 'Cumulative Revenue (M)',
            'xaxis': 'x3',
            'yaxis': 'y3'
        }
    ]

    layout = {
        'title': {
            'text': 'Adding States in Priority Order Yields Steepest Early Growth',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'xaxis': {'domain': [0, 1], 'title': 'State Rank'},
        'yaxis': {'domain': [0.65, 1], 'title': 'Providers'},
        'xaxis2': {'domain': [0, 1], 'anchor': 'y2'},
        'yaxis2': {'domain': [0.33, 0.65], 'anchor': 'x2', 'title': 'Covered Lives (M)'},
        'xaxis3': {'domain': [0, 1], 'anchor': 'y3'},
        'yaxis3': {'domain': [0, 0.33], 'anchor': 'x3', 'title': 'Revenue (M)'},
        'width': 1000,
        'height': 800,
        'showlegend': bool(False),
        'annotations': [
            {
                'text': 'Source: Expansion projections using 0.5% market penetration, 20 sessions/year, $130/session',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.05,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_growth_curves.html', traces, layout)


def chart_revenue_by_wave(data: Dict, config: ChartConfig):
    """Chart 14: Revenue by Wave"""
    df = data['projections'].copy()

    # Extract wave number from expansion_wave
    df['wave_num'] = df['expansion_wave'].str.extract('Wave (\d+)').astype(int)
    wave_revenue = df.groupby('wave_num').agg({
        'annual_revenue_opportunity': 'sum',
        'state_name': 'count'
    }).reset_index()
    wave_revenue.columns = ['wave', 'annual_revenue', 'num_states']

    trace = {
        'type': 'bar',
        'x': [f'Wave {int(x)}' for x in wave_revenue['wave']],
        'y': (wave_revenue['annual_revenue'] / 1e6).tolist(),
        'text': [f'${x:.0f}M' for x in wave_revenue['annual_revenue'] / 1e6],
        'textposition': 'auto',
        'marker': {'color': '#1f77b4'},
        'hovertemplate': '<b>%{x}</b><br>Annual Revenue: $%{y:.0f}M<extra></extra>'
    }

    layout = {
        'title': {
            'text': 'Wave 1 States Deliver the Highest Revenue Per State Due to Favorable Scoring Profiles',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 17}
        },
        'xaxis': {'title': 'Expansion Wave'},
        'yaxis': {'title': 'Cumulative Annual Revenue (Millions USD)'},
        'width': 900,
        'height': 500,
        'annotations': [
            {
                'text': 'Hypothetical annual revenue under conservative assumptions (0.5% penetration)',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': 0.95,
                'showarrow': bool(False),
                'font': {'size': 12, 'color': '#666'}
            },
            {
                'text': 'These waves are a hypothetical analytical exercise and do not reflect Octave\'s actual expansion plans.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.15,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#d62728', 'style': 'italic'}
            },
            {
                'text': 'Source: NB08 expansion projections',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.22,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_revenue_by_wave.html', [trace], layout)


def chart_regulatory_map(data: Dict, config: ChartConfig):
    """Chart 15: Regulatory/Compact Map"""
    df = data['expansion_scores'].copy()

    trace = {
        'type': 'choropleth',
        'locations': df['state_abbrev'].tolist(),
        'z': df['compact_score'].tolist(),
        'colorscale': 'Greens',
        'locationmode': 'USA-states',
        'colorbar': {
            'title': 'Compacts',
            'thickness': 20,
            'len': 0.7,
            'tickvals': [0, 1, 2, 3],
            'ticktext': ['0', '1', '2', '3']
        },
        'hovertemplate': '<b>%{text}</b><br>Compacts: %{z}<extra></extra>',
        'text': df['state_name'].tolist(),
        'zmin': 0,
        'zmax': 3
    }

    layout = {
        'title': {
            'text': 'Interstate Compacts Enable Faster Market Entry in 28 States',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'geo': {
            'scope': 'usa',
            'projection': {'type': 'albers usa'},
            'showlakes': bool(True),
            'lakecolor': 'rgb(255, 255, 255)'
        },
        'width': 1000,
        'height': 600,
        'annotations': [
            {
                'text': 'Regulatory ease reflects how quickly a company can credential providers in a new state. States are scored based on membership in three interstate licensure compacts: Psychology Interjurisdictional Compact (PSYPACT) allows psychologists to practice across state lines. The Counseling Compact does the same for licensed professional counselors. The Social Work Compact applies to licensed clinical social workers. States belonging to all three compacts enable provider credentialing in 2-4 weeks vs. 12-20 weeks for non-compact states. Telehealth parity laws (requiring insurers to reimburse telehealth at the same rate as in-person) also factor into the score.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': 0.92,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'},
                'align': 'center'
            },
            {
                'text': 'Source: PSYPACT Commission, Counseling Compact, Social Work Compact official rosters',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.18,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_regulatory_map.html', [trace], layout)


def chart_reimbursement_map(data: Dict, config: ChartConfig):
    """Chart 16: Reimbursement Map"""
    df = data['expansion_scores'].copy()

    trace = {
        'type': 'choropleth',
        'locations': df['state_abbrev'].tolist(),
        'z': df['reimbursement_favorability'].tolist(),
        'colorscale': 'Blues',
        'locationmode': 'USA-states',
        'colorbar': {
            'title': 'Reimbursement<br>Score',
            'thickness': 20,
            'len': 0.7
        },
        'hovertemplate': '<b>%{text}</b><br>Medicare 90837 Rate: $%{customdata:.0f}<br>Favorability: %{z:.1f}<extra></extra>',
        'text': df['state_name'].tolist(),
        'customdata': df['medicare_90837_rate'].tolist(),
        'zmin': df['reimbursement_favorability'].min(),
        'zmax': df['reimbursement_favorability'].max()
    }

    layout = {
        'title': {
            'text': 'Higher Reimbursement States Are More Attractive for Provider Recruitment',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        'geo': {
            'scope': 'usa',
            'projection': {'type': 'albers usa'},
            'showlakes': bool(True),
            'lakecolor': 'rgb(255, 255, 255)'
        },
        'width': 1000,
        'height': 600,
        'annotations': [
            {
                'text': 'Reimbursement favorability is based on Medicare fee schedule rates for common therapy codes (Current Procedural Terminology codes 90834 and 90837). Medicare sets national base rates adjusted by state-level Geographic Practice Cost Indices (GPCI). These serve as a floor benchmark because commercial insurance plans typically reimburse at 130-196% of Medicare rates (Milliman 2025). Important caveat: this does not account for cost of living differences. A state with lower reimbursement but also lower cost of living may be equally or more attractive to providers.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': 0.92,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'},
                'align': 'center'
            },
            {
                'text': 'States with higher Medicare rates generally have higher commercial reimbursement, but cost of living varies—a consideration not captured in this model.',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.12,
                'showarrow': bool(False),
                'font': {'size': 11, 'color': '#333'}
            },
            {
                'text': 'Sources: Centers for Medicare and Medicaid Services (CMS) Physician Fee Schedule 2024, Milliman commercial reimbursement benchmarks',
                'xref': 'paper', 'yref': 'paper',
                'x': 0.5, 'y': -0.18,
                'showarrow': bool(False),
                'font': {'size': 10, 'color': '#666'}
            }
        ]
    }

    write_plotly_html(config.output_dir / 'chart_reimbursement_map.html', [trace], layout)


def main():
    """Generate all charts."""
    config = ChartConfig()
    data = load_data(config)

    print("\nGenerating 16 Blog Charts...")
    print("-" * 50)

    chart_treatment_gap_map(data, config)
    chart_demand_supply_scatter(data, config)
    chart_provider_density_map(data, config)
    chart_provider_types_bar(data, config)
    chart_competitive_map(data, config)
    chart_footprint_map(data, config)
    chart_covered_lives_comparison(data, config)
    chart_scoring_weights(data, config)
    chart_opportunity_map(data, config)
    chart_heatmap_expansion(data, config)
    chart_top10_table(data, config)
    chart_radar_top5(data, config)
    chart_growth_curves(data, config)
    chart_revenue_by_wave(data, config)
    chart_regulatory_map(data, config)
    chart_reimbursement_map(data, config)

    print("-" * 50)
    print(f"All charts generated successfully in: {config.output_dir}")
    print(f"Total files: 16")


if __name__ == '__main__':
    main()
