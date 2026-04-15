"""
nb01 — Plotly HTML chart generator.

Reads the clean dataset saved by nb01 and produces embed-ready Plotly HTML
for each of the four static charts. Each chart is written to:
    ../data/outputs/nb01/nb01_<name>_interactive.html

Design notes (applied to every figure):
  * `config={'responsive': True}` so charts resize to container width on the blog
  * `include_plotlyjs='cdn'` so only one CDN load is needed across the page
  * Generous top/bottom/left margins + `automargin=True` on axes so rotated
    tick labels, legends, and titles never get cut off
  * Rotated x-tick labels (-20 to -30 deg) on long category names
  * Explicit y-axis ranges where helpful (rates forced to [0, max*1.15])
  * Consistent color palette aligned to the original matplotlib output
"""

import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.abspath(os.path.join(HERE, "..", "data", "outputs", "nb01"))
CSV_PATH = os.path.join(OUT_DIR, "nb01_hillstrom_clean.csv")
os.makedirs(OUT_DIR, exist_ok=True)

COLORS = {
    "Mens E-Mail": "#4C8BB8",
    "Womens E-Mail": "#5FA85F",
    "No E-Mail": "#E89B4C",
    "Match": "#2ECC71",
    "Mismatch": "#E74C3C",
    "Mixed": "#F39C12",
    "Control": "#95A5A6",
}

PLOTLY_KW = dict(include_plotlyjs="cdn", full_html=True,
                 config={"responsive": True, "displaylogo": False})

BASE_LAYOUT = dict(
    template="plotly_white",
    font=dict(family="Arial, sans-serif", size=13),
    title_x=0.5,
    margin=dict(l=70, r=40, t=90, b=90),
    hoverlabel=dict(bgcolor="white", font_size=12),
)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = pd.read_csv(CSV_PATH)
segment_order = ["Mens E-Mail", "No E-Mail", "Womens E-Mail"]
match_order = ["Match", "Mismatch", "Mixed", "Control"]


# ---------------------------------------------------------------------------
# Chart 1 — Treatment group distribution
# ---------------------------------------------------------------------------
def chart_group_distribution():
    counts = df["segment"].value_counts().reindex(segment_order)
    pct = (counts / counts.sum() * 100).round(1)
    text = [f"{c:,}<br>({p:.1f}%)" for c, p in zip(counts, pct)]

    fig = go.Figure(
        go.Bar(
            x=counts.index, y=counts.values,
            text=text, textposition="outside",
            marker_color=[COLORS[s] for s in counts.index],
            marker_line=dict(color="black", width=1),
            hovertemplate="<b>%{x}</b><br>Customers: %{y:,}<extra></extra>",
        )
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title="Distribution of Customers Across Treatment Groups",
        xaxis=dict(title="Treatment Segment", automargin=True),
        yaxis=dict(title="Number of Customers", automargin=True,
                   range=[0, counts.max() * 1.15]),
        showlegend=False, height=500,
    )
    path = os.path.join(OUT_DIR, "nb01_group_distribution_interactive.html")
    fig.write_html(path, **PLOTLY_KW)
    print(f"  ✓ {path}")


# ---------------------------------------------------------------------------
# Chart 2 — Outcomes by treatment group (3 panels)
# ---------------------------------------------------------------------------
def chart_outcomes_by_group():
    grp = df.groupby("segment")
    visit = grp["visit"].mean().reindex(segment_order)
    conv = grp["conversion"].mean().reindex(segment_order)
    spenders = df[df["spend"] > 0]

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Visit Rate by Treatment Group",
                        "Conversion Rate by Treatment Group",
                        "Spending Distribution<br>(Among Spenders Only)"),
        horizontal_spacing=0.10,
    )

    # Visit
    fig.add_trace(go.Bar(
        x=visit.index, y=visit.values,
        text=[f"{v:.1%}" for v in visit.values], textposition="outside",
        marker_color=[COLORS[s] for s in visit.index],
        marker_line=dict(color="black", width=1),
        hovertemplate="<b>%{x}</b><br>Visit rate: %{y:.2%}<extra></extra>",
        showlegend=False,
    ), row=1, col=1)

    # Conversion
    fig.add_trace(go.Bar(
        x=conv.index, y=conv.values,
        text=[f"{v:.1%}" for v in conv.values], textposition="outside",
        marker_color=[COLORS[s] for s in conv.index],
        marker_line=dict(color="black", width=1),
        hovertemplate="<b>%{x}</b><br>Conversion rate: %{y:.2%}<extra></extra>",
        showlegend=False,
    ), row=1, col=2)

    # Spend (box among spenders)
    for seg in segment_order:
        data = spenders.loc[spenders["segment"] == seg, "spend"]
        fig.add_trace(go.Box(
            y=data, name=seg, marker_color=COLORS[seg],
            boxmean=True, showlegend=False,
            hovertemplate=f"<b>{seg}</b><br>$%{{y:.2f}}<extra></extra>",
        ), row=1, col=3)

    fig.update_yaxes(title_text="Visit Rate", tickformat=".0%",
                     range=[0, max(visit) * 1.25], automargin=True, row=1, col=1)
    fig.update_yaxes(title_text="Conversion Rate", tickformat=".1%",
                     range=[0, max(conv) * 1.3], automargin=True, row=1, col=2)
    fig.update_yaxes(title_text="Spend Amount ($)", automargin=True, row=1, col=3)
    fig.update_xaxes(tickangle=-20, automargin=True)

    fig.update_layout(
        **{**BASE_LAYOUT, "margin": dict(l=70, r=40, t=110, b=110)},
        title="Outcomes by Treatment Group",
        height=560,
    )
    path = os.path.join(OUT_DIR, "nb01_outcomes_by_group_interactive.html")
    fig.write_html(path, **PLOTLY_KW)
    print(f"  ✓ {path}")


# ---------------------------------------------------------------------------
# Chart 3 — Covariate balance (2x3 grid)
# ---------------------------------------------------------------------------
def chart_covariate_balance():
    continuous = ["recency", "history"]
    binary = ["newbie", "mens", "womens"]

    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=("Recency by Group", "History by Group", "Newbie by Group",
                        "Mens by Group", "Womens by Group",
                        "History Segment by Group"),
        horizontal_spacing=0.09, vertical_spacing=0.18,
    )

    # Row 1 col 1-2: continuous box plots
    for i, col in enumerate(continuous, start=1):
        for seg in segment_order:
            data = df.loc[df["segment"] == seg, col]
            fig.add_trace(go.Box(
                y=data, name=seg, marker_color=COLORS[seg],
                showlegend=False, boxmean=True,
                hovertemplate=f"<b>{seg}</b><br>{col}: %{{y}}<extra></extra>",
            ), row=1, col=i)
        fig.update_yaxes(title_text=col.capitalize(), automargin=True, row=1, col=i)

    # Row 1 col 3 + Row 2 col 1-2: binary bar plots (mean by group)
    placements = [(1, 3, "newbie"), (2, 1, "mens"), (2, 2, "womens")]
    for r, c, col in placements:
        means = df.groupby("segment")[col].mean().reindex(segment_order)
        fig.add_trace(go.Bar(
            x=means.index, y=means.values,
            text=[f"{v:.3f}" for v in means.values], textposition="outside",
            marker_color=[COLORS[s] for s in means.index],
            marker_line=dict(color="black", width=1), showlegend=False,
            hovertemplate="<b>%{x}</b><br>Mean: %{y:.3f}<extra></extra>",
        ), row=r, col=c)
        fig.update_yaxes(title_text=col.capitalize(), range=[0, 1],
                         automargin=True, row=r, col=c)

    # Row 2 col 3: history_segment stacked/grouped bars
    hs_pct = (df.groupby(["segment", "history_segment"]).size()
              .unstack(fill_value=0))
    hs_pct = hs_pct.div(hs_pct.sum(axis=1), axis=0) * 100
    hs_pct = hs_pct.reindex(segment_order)
    palette = ["#66C2A5", "#FEE08B", "#8DA0CB", "#FC8D62",
               "#5E89A6", "#F4A460", "#A6D854"]
    for i, cat in enumerate(hs_pct.columns):
        fig.add_trace(go.Bar(
            x=hs_pct.index, y=hs_pct[cat], name=cat,
            marker_color=palette[i % len(palette)],
            hovertemplate=f"<b>%{{x}}</b><br>{cat}: %{{y:.1f}}%<extra></extra>",
            legendgroup="hs", showlegend=True,
        ), row=2, col=3)
    fig.update_yaxes(title_text="Percentage (%)", automargin=True, row=2, col=3)

    fig.update_xaxes(tickangle=-25, automargin=True)

    fig.update_layout(
        **{**BASE_LAYOUT, "margin": dict(l=70, r=150, t=100, b=120)},
        title="Covariate Balance Across Treatment Groups",
        height=780, barmode="group",
        legend=dict(title="History Segment", x=1.02, y=0.25,
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="#ccc", borderwidth=1),
    )
    path = os.path.join(OUT_DIR, "nb01_covariate_balance_interactive.html")
    fig.write_html(path, **PLOTLY_KW)
    print(f"  ✓ {path}")


# ---------------------------------------------------------------------------
# Chart 4 — Outcomes by email-purchase history match status
# ---------------------------------------------------------------------------
def chart_email_match_outcomes():
    grp = df.groupby("email_match_simple")
    visit = grp["visit"].mean().reindex(match_order)
    conv = grp["conversion"].mean().reindex(match_order)
    spend = grp["spend"].mean().reindex(match_order)

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Visit Rate", "Conversion Rate", "Average Spend ($)"),
        horizontal_spacing=0.12,
    )

    def add_bar(values, col, fmt, hover_fmt, ymax_mult=1.2):
        fig.add_trace(go.Bar(
            x=values.index, y=values.values,
            text=[fmt.format(v) for v in values.values], textposition="outside",
            marker_color=[COLORS[s] for s in values.index],
            marker_line=dict(color="black", width=1), showlegend=False,
            hovertemplate="<b>%{x}</b><br>" + hover_fmt + "<extra></extra>",
        ), row=1, col=col)
        fig.update_yaxes(automargin=True, range=[0, values.max() * ymax_mult],
                         row=1, col=col)

    add_bar(visit, 1, "{:.1%}", "Visit rate: %{y:.2%}")
    add_bar(conv,  2, "{:.2%}", "Conversion rate: %{y:.3%}")
    add_bar(spend, 3, "${:.2f}", "Avg spend: $%{y:.2f}")

    fig.update_yaxes(title_text="Rate", tickformat=".0%", row=1, col=1)
    fig.update_yaxes(title_text="Rate", tickformat=".2%", row=1, col=2)
    fig.update_yaxes(title_text="Dollars", row=1, col=3)
    fig.update_xaxes(tickangle=0, automargin=True)

    fig.update_layout(
        **{**BASE_LAYOUT, "margin": dict(l=70, r=40, t=110, b=90)},
        title="Outcomes by Email-Purchase History Match Status",
        height=520,
    )
    path = os.path.join(OUT_DIR, "nb01_email_match_outcomes_interactive.html")
    fig.write_html(path, **PLOTLY_KW)
    print(f"  ✓ {path}")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Reading: {CSV_PATH}")
    print(f"Writing interactive HTML to: {OUT_DIR}\n")
    chart_group_distribution()
    chart_outcomes_by_group()
    chart_covariate_balance()
    chart_email_match_outcomes()
    print("\nDone. All four charts saved as responsive Plotly HTML.")
