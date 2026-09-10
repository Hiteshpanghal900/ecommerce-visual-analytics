"""
Interactive Marketplace Dashboard - E-Commerce Visual Analytics
Data Visualization Design, IIT Madras

Run: python app.py   (then open http://127.0.0.1:8050)

Reads only the small, pre-aggregated CSVs in dashboard/data/ (built by
prepare_dashboard_data.py) - never the raw ~95K-row master tables - so every
callback stays fast regardless of dataset size.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html, callback_context

DATA_DIR = Path(__file__).resolve().parent / "data"

seller_summary = pd.read_csv(DATA_DIR / "seller_summary.csv")
state_seller = pd.read_csv(DATA_DIR / "state_seller_summary.csv")
state_customer = pd.read_csv(DATA_DIR / "state_customer_summary.csv")
category_summary = pd.read_csv(DATA_DIR / "category_summary.csv")
delay_band_summary = pd.read_csv(DATA_DIR / "delay_band_summary.csv")
monthly_trend = pd.read_csv(DATA_DIR / "monthly_trend.csv", parse_dates=["purchase_month"])
seller_quality = pd.read_csv(DATA_DIR / "seller_quality.csv")
category_quality = pd.read_csv(DATA_DIR / "category_quality.csv")
customer_quadrant_summary = pd.read_csv(DATA_DIR / "customer_quadrant_summary.csv")
customer_delay_repeat_summary = pd.read_csv(DATA_DIR / "customer_delay_repeat_summary.csv")
customer_repeat_overview = pd.read_csv(DATA_DIR / "customer_repeat_overview.csv").iloc[0]
funnel_origin_conversion = pd.read_csv(DATA_DIR / "funnel_origin_conversion.csv")
funnel_business_type_share = pd.read_csv(DATA_DIR / "funnel_business_type_share.csv")
funnel_overview = pd.read_csv(DATA_DIR / "funnel_overview.csv").iloc[0]

QUADRANT_ORDER = ["High-value & happy", "Low-value & happy", "High-value & unhappy", "Low-value & unhappy"]
DELAY_REPEAT_ORDER = ["0% late", "1-33% late", "34-66% late", "67-100% late"]

DELAY_BAND_ORDER = ["On or before estimate", "1-3 days late", "4-7 days late", "8+ days late"]
STATES = sorted(state_seller["state"].unique())

PALETTE = dict(navy="#1b2a4a", red="#d1495b", green="#2a9d8f",
               amber="#e9c46a", orange="#e76f51", grey="#8d99ae", blue="#4c78a8")

CARD_STYLE = {
    "background": "#ffffff", "borderRadius": "10px", "padding": "18px 22px",
    "boxShadow": "0 1px 3px rgba(0,0,0,0.08)", "flex": "1", "minWidth": "180px",
}
SECTION_STYLE = {"background": "#f5f6f8", "padding": "24px", "minHeight": "100vh"}

app = Dash(__name__, title="Marketplace Dashboard", suppress_callback_exceptions=True)
server = app.server  # for deployment (gunicorn/render/etc.)


def kpi_card(label, value, sub=None, color=PALETTE["navy"]):
    children = [
        html.Div(label, style={"fontSize": "13px", "color": "#666", "marginBottom": "6px"}),
        html.Div(value, style={"fontSize": "26px", "fontWeight": "700", "color": color}),
    ]
    if sub:
        children.append(html.Div(sub, style={"fontSize": "12px", "color": "#999", "marginTop": "4px"}))
    return html.Div(children, style=CARD_STYLE)


def empty_state_note(text):
    return html.Div(text, style={"color": "#999", "fontSize": "13px", "fontStyle": "italic", "padding": "8px 0"})


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
app.layout = html.Div([
    html.Div([
        html.H2("Marketplace Satisfaction & Risk Dashboard", style={"margin": "0 0 4px 0"}),
        html.Div(
            "Explore customer satisfaction and seller/delivery risk by category, seller, and region. "
            "Filters apply across every chart on the page.",
            style={"color": "#666", "fontSize": "14px", "marginBottom": "18px"},
        ),
    ]),

    # Global filter bar
    html.Div([
        html.Div([
            html.Label("State", style={"fontSize": "12px", "fontWeight": "600"}),
            dcc.Dropdown(
                id="state-filter",
                options=[{"label": "All states", "value": "ALL"}] + [{"label": s, "value": s} for s in STATES],
                value="ALL", clearable=False, style={"minWidth": "220px"},
            ),
        ], style={"marginRight": "24px"}),
        html.Div([
            html.Label("Seller value tier", style={"fontSize": "12px", "fontWeight": "600"}),
            dcc.Dropdown(
                id="tier-filter",
                options=[{"label": "All tiers", "value": "ALL"},
                         {"label": "High-value (top 25% by sales)", "value": "High-value"},
                         {"label": "Lower-value", "value": "Lower-value"}],
                value="ALL", clearable=False, style={"minWidth": "260px"},
            ),
        ], style={"marginRight": "24px"}),
        html.Div([
            html.Label("Review-risk status", style={"fontSize": "12px", "fontWeight": "600"}),
            dcc.Dropdown(
                id="risk-filter",
                options=[{"label": "All sellers", "value": "ALL"},
                         {"label": "Review-risk flagged only", "value": "RISK"},
                         {"label": "Healthy only", "value": "HEALTHY"}],
                value="ALL", clearable=False, style={"minWidth": "240px"},
            ),
        ]),
    ], style={"display": "flex", "flexWrap": "wrap", "gap": "12px", "marginBottom": "20px",
              "background": "#fff", "padding": "16px 20px", "borderRadius": "10px",
              "boxShadow": "0 1px 3px rgba(0,0,0,0.08)"}),

    # KPI row (reacts to filters)
    html.Div(id="kpi-row", style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "20px"}),

    dcc.Tabs(id="tabs", value="tab-category", children=[
        dcc.Tab(label="By Category", value="tab-category"),
        dcc.Tab(label="By Seller", value="tab-seller"),
        dcc.Tab(label="By Region", value="tab-region"),
        dcc.Tab(label="Delivery Performance", value="tab-delivery"),
        dcc.Tab(label="Customer Retention", value="tab-retention"),
        dcc.Tab(label="Seller Acquisition", value="tab-funnel"),
    ]),
    html.Div(id="tab-content", style={"marginTop": "18px"}),
], style=SECTION_STYLE)


# ---------------------------------------------------------------------------
# Filtering helpers - every callback below re-derives its own filtered slice
# from these small in-memory frames; nothing here touches disk after startup.
# ---------------------------------------------------------------------------
def filter_sellers(state, tier, risk):
    df = seller_summary
    if state != "ALL":
        df = df[df["seller_state"] == state]
    if tier != "ALL":
        df = df[df["value_tier"] == tier]
    if risk == "RISK":
        df = df[df["review_risk_flag"]]
    elif risk == "HEALTHY":
        df = df[~df["review_risk_flag"]]
    return df


# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
@app.callback(Output("kpi-row", "children"),
              Input("state-filter", "value"), Input("tier-filter", "value"), Input("risk-filter", "value"))
def update_kpis(state, tier, risk):
    df = filter_sellers(state, tier, risk)
    if df.empty:
        return [empty_state_note("No sellers match the current filters.")]

    n_sellers = len(df)
    total_sales = df["total_item_sales_value"].sum()
    avg_review = df.loc[df["has_reviews"], "avg_review_score"].mean()
    late_rate = df["late_delivery_rate"].mean()
    risk_rate = df["review_risk_flag"].mean()

    return [
        kpi_card("Sellers in view", f"{n_sellers:,}"),
        kpi_card("Total sales value", f"R$ {total_sales:,.0f}", color=PALETTE["blue"]),
        kpi_card("Avg. review score", f"{avg_review:.2f} / 5" if pd.notna(avg_review) else "n/a",
                 color=PALETTE["green"] if pd.notna(avg_review) and avg_review >= 4 else PALETTE["orange"]),
        kpi_card("Avg. late-delivery rate", f"{late_rate:.1%}",
                 color=PALETTE["red"] if late_rate > 0.1 else PALETTE["navy"]),
        kpi_card("Sellers flagged review-risk", f"{risk_rate:.1%}",
                 color=PALETTE["red"] if risk_rate > 0.1 else PALETTE["navy"]),
    ]


# ---------------------------------------------------------------------------
# Tab content
# ---------------------------------------------------------------------------
@app.callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_tab(tab):
    if tab == "tab-category":
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Which categories have the best / worst satisfaction?"),
                    dcc.Graph(id="category-review-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
                html.Div([
                    html.H4("Sales value vs. satisfaction (bubble = order volume)"),
                    dcc.Graph(id="category-scatter-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
            ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
            html.Div([
                html.H4("Selected category detail"),
                html.Div(id="category-detail"),
            ], style={**CARD_STYLE, "marginTop": "16px"}),
        ])

    if tab == "tab-seller":
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Revenue concentration across sellers (Lorenz curve)"),
                    dcc.Graph(id="seller-lorenz-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
                html.Div([
                    html.H4("Value tier x review-risk quadrant"),
                    dcc.Graph(id="seller-quadrant-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
            ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
            html.Div([
                html.H4("Top / bottom sellers in current view"),
                html.Div(id="seller-table"),
            ], style={**CARD_STYLE, "marginTop": "16px"}),
        ])

    if tab == "tab-region":
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Review score by state (sellers)"),
                    dcc.Graph(id="region-review-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
                html.Div([
                    html.H4("Late-delivery & review-risk rate by state"),
                    dcc.Graph(id="region-risk-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
            ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
            html.Div([
                html.H4("Why does this state stand out?"),
                html.Div(id="region-detail"),
            ], style={**CARD_STYLE, "marginTop": "16px"}),
        ])

    if tab == "tab-delivery":
        return html.Div([
            html.Div([
                html.Div([
                    html.H4("Review score by delivery-delay band"),
                    dcc.Graph(id="delay-band-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
                html.Div([
                    html.H4("Monthly trend: order volume, review score, late rate"),
                    dcc.Graph(id="monthly-trend-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
            ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
        ])

    if tab == "tab-retention":
        return html.Div([
            html.Div(
                f"Only {customer_repeat_overview['repeat_rate']:.1%} of "
                f"{int(customer_repeat_overview['total_customers']):,} customers ever place a second "
                f"order. The charts below size exactly who is unhappy, how much revenue they "
                f"represent, and why.",
                style={"color": "#666", "fontSize": "13px", "marginBottom": "12px"},
            ),
            html.Div([
                html.Div([
                    html.H4("Who stands out? Value × satisfaction quadrant"),
                    dcc.Graph(id="quadrant-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
                html.Div([
                    html.H4("Review score & repeat rate by delivery-delay band"),
                    dcc.Graph(id="delay-repeat-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
            ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
            html.Div([
                html.H4("Selected segment detail"),
                html.Div(id="quadrant-detail"),
            ], style={**CARD_STYLE, "marginTop": "16px"}),
        ])

    if tab == "tab-funnel":
        return html.Div([
            html.Div(
                f"{funnel_overview['conversion_rate']:.1%} of "
                f"{int(funnel_overview['total_leads']):,} marketing-qualified leads convert into an "
                f"active seller ({int(funnel_overview['converted_leads']):,} sellers). Volume and "
                f"conversion quality are not the same channel.",
                style={"color": "#666", "fontSize": "13px", "marginBottom": "12px"},
            ),
            html.Div([
                html.Div([
                    html.H4("Conversion rate by acquisition channel"),
                    dcc.Graph(id="funnel-origin-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
                html.Div([
                    html.H4("Business type mix among converted sellers"),
                    dcc.Graph(id="funnel-business-chart"),
                ], style={**CARD_STYLE, "flex": "1"}),
            ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"}),
        ])

    return html.Div()


# ---------------------------------------------------------------------------
# Category tab callbacks
# ---------------------------------------------------------------------------
@app.callback(Output("category-review-chart", "figure"), Input("tabs", "value"))
def category_review_chart(_):
    df = category_summary[category_summary["has_reviews"]].sort_values("avg_review_score")
    top_bottom = pd.concat([df.head(8), df.tail(8)])
    colors = [PALETTE["red"] if v < 3.8 else PALETTE["green"] for v in top_bottom["avg_review_score"]]
    fig = go.Figure(go.Bar(
        x=top_bottom["avg_review_score"], y=top_bottom["product_category"],
        orientation="h", marker_color=colors,
        customdata=top_bottom[["total_sales_value", "review_count"]],
        hovertemplate="%{y}<br>Avg review: %{x:.2f}<br>Sales: R$ %{customdata[0]:,.0f}<br>Reviews: %{customdata[1]:,}<extra></extra>",
    ))
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=420,
                       xaxis_title="Average review score", yaxis_title="")
    return fig


@app.callback(Output("category-scatter-chart", "figure"), Input("tabs", "value"))
def category_scatter_chart(_):
    df = category_summary[category_summary["has_reviews"]]
    fig = px.scatter(
        df, x="total_sales_value", y="avg_review_score", size="unique_orders",
        color="late_delivery_rate", color_continuous_scale="RdYlGn_r",
        hover_name="product_category", size_max=40,
        labels={"total_sales_value": "Total sales value (R$)", "avg_review_score": "Avg review score",
                "late_delivery_rate": "Late-delivery rate"},
    )
    fig.update_xaxes(type="log")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=420)
    return fig


@app.callback(Output("category-detail", "children"), Input("category-review-chart", "clickData"))
def category_detail(click_data):
    if not click_data:
        return empty_state_note("Click a bar in the left chart to see why that category stands out.")
    cat_name = click_data["points"][0]["y"]
    row = category_summary[category_summary["product_category"] == cat_name].iloc[0]
    quality_text = (
        f" Product-quality-issue rate: {row['quality_issue_rate']:.1f}% "
        f"(from review-text mining, {int(row['quality_eval_orders']):,} orders evaluated)."
        if row.get("has_quality_data") else
        " Not enough order volume (<500) to report a reliable product-quality-issue rate."
    )
    return html.Div([
        html.H5(cat_name.replace("_", " ").title()),
        html.P([
            f"{row['unique_orders']:,} orders across {row['unique_sellers']:,} sellers, "
            f"R$ {row['total_sales_value']:,.0f} in sales value. ",
            f"Average review score {row['avg_review_score']:.2f}/5 over {row['review_count']:,} reviews. ",
            f"Late-delivery rate {row['late_delivery_rate']:.1%}, "
            f"{row['review_risk_rate']:.1%} of this category's orders are review-risk flagged.",
            quality_text,
        ]),
    ])


# ---------------------------------------------------------------------------
# Seller tab callbacks
# ---------------------------------------------------------------------------
@app.callback(Output("seller-lorenz-chart", "figure"),
              Input("state-filter", "value"), Input("tier-filter", "value"), Input("risk-filter", "value"))
def seller_lorenz_chart(state, tier, risk):
    df = filter_sellers(state, tier, risk).sort_values("total_item_sales_value", ascending=False)
    if df.empty:
        return go.Figure()
    total = df["total_item_sales_value"].sum()
    cum_share = df["total_item_sales_value"].cumsum() / total * 100
    x = (pd.Series(range(1, len(df) + 1)) / len(df) * 100).values
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=cum_share, mode="lines", fill="tozeroy",
                              line_color=PALETTE["navy"], name="Sellers"))
    fig.add_trace(go.Scatter(x=[0, 100], y=[0, 100], mode="lines",
                              line=dict(dash="dash", color=PALETTE["grey"]), name="Perfect equality"))
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=380,
                       xaxis_title="Sellers ranked by sales (cum. %)", yaxis_title="Cum. share of sales (%)")
    return fig


@app.callback(Output("seller-quadrant-chart", "figure"),
              Input("state-filter", "value"), Input("tier-filter", "value"), Input("risk-filter", "value"))
def seller_quadrant_chart(state, tier, risk):
    df = filter_sellers(state, tier, risk).copy()
    if df.empty:
        return go.Figure()
    df["segment"] = df["value_tier"] + " / " + df["review_risk_flag"].map({True: "At-risk", False: "Healthy"})
    counts = df["segment"].value_counts().reset_index()
    counts.columns = ["segment", "sellers"]
    colors = {s: (PALETTE["red"] if "At-risk" in s else PALETTE["green"]) for s in counts["segment"]}
    fig = px.bar(counts.sort_values("sellers"), x="sellers", y="segment", orientation="h",
                 color="segment", color_discrete_map=colors)
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=380,
                       xaxis_title="Number of sellers", yaxis_title="")
    return fig


@app.callback(Output("seller-table", "children"),
              Input("state-filter", "value"), Input("tier-filter", "value"), Input("risk-filter", "value"))
def seller_table(state, tier, risk):
    df = filter_sellers(state, tier, risk)
    if df.empty:
        return empty_state_note("No sellers match the current filters.")
    cols = ["seller_id", "seller_state", "total_item_sales_value", "avg_review_score",
            "late_delivery_rate", "review_risk_flag", "quality_issue_rate"]
    top = df.nlargest(5, "total_item_sales_value")[cols]
    risky = df[df["review_risk_flag"]].nlargest(5, "total_item_sales_value")[cols]

    def fmt_quality(v):
        return f"{v:.1f}%" if pd.notna(v) else "n/a"

    def to_table(sub_df, title):
        return html.Div([
            html.Div(title, style={"fontWeight": "600", "marginBottom": "6px"}),
            html.Table([
                html.Thead(html.Tr([html.Th(c) for c in
                    ["Seller", "State", "Sales (R$)", "Review", "Late %", "At risk", "Quality-issue %"]])),
                html.Tbody([
                    html.Tr([
                        html.Td(r.seller_id[:10] + "..."), html.Td(r.seller_state),
                        html.Td(f"{r.total_item_sales_value:,.0f}"),
                        html.Td(f"{r.avg_review_score:.2f}" if pd.notna(r.avg_review_score) else "n/a"),
                        html.Td(f"{r.late_delivery_rate:.1%}"),
                        html.Td("Yes" if r.review_risk_flag else "No"),
                        html.Td(fmt_quality(r.quality_issue_rate)),
                    ]) for r in sub_df.itertuples()
                ]),
            ], style={"width": "100%", "fontSize": "12px", "borderCollapse": "collapse"}),
        ], style={"flex": "1"})

    return html.Div([to_table(top, "Top 5 sellers by sales"),
                      to_table(risky, "Top 5 highest-value sellers flagged as review-risk")],
                     style={"display": "flex", "gap": "24px", "flexWrap": "wrap"})


# ---------------------------------------------------------------------------
# Region tab callbacks
# ---------------------------------------------------------------------------
@app.callback(Output("region-review-chart", "figure"), Input("tabs", "value"))
def region_review_chart(_):
    df = state_seller.sort_values("avg_review_score")
    fig = px.bar(df, x="avg_review_score", y="state", orientation="h",
                 color="avg_review_score", color_continuous_scale="RdYlGn")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=520, coloraxis_showscale=False,
                       xaxis_title="Average review score", yaxis_title="")
    return fig


@app.callback(Output("region-risk-chart", "figure"), Input("tabs", "value"))
def region_risk_chart(_):
    df = state_seller.sort_values("review_risk_flagged_share", ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["state"], y=df["late_delivery_rate"] * 100, name="Late-delivery rate (%)",
                          marker_color=PALETTE["orange"]))
    fig.add_trace(go.Bar(x=df["state"], y=df["review_risk_flagged_share"] * 100,
                          name="Share of sellers flagged review-risk (%)", marker_color=PALETTE["red"]))
    fig.update_layout(barmode="group", margin=dict(l=10, r=10, t=10, b=10), height=520,
                       yaxis_title="Rate (%)", legend=dict(orientation="h", y=-0.15))
    return fig


@app.callback(Output("region-detail", "children"), Input("region-risk-chart", "clickData"))
def region_detail(click_data):
    if not click_data:
        return empty_state_note("Click a bar in the right chart to see the detail behind that state.")
    state = click_data["points"][0]["x"]
    s_row = state_seller[state_seller["state"] == state].iloc[0]
    c_row = state_customer[state_customer["state"] == state]
    c_text = ""
    if not c_row.empty:
        c_row = c_row.iloc[0]
        c_text = f" On the customer side, {c_row['customer_count']:,} customers there average a {c_row['avg_review_score']:.2f}/5 review score."
    return html.Div([
        html.H5(state),
        html.P(
            f"{s_row['seller_count']:,} sellers, R$ {s_row['total_sales_value']:,.0f} in sales value. "
            f"Average review score {s_row['avg_review_score']:.2f}/5, late-delivery rate {s_row['late_delivery_rate']:.1%}, "
            f"{s_row['review_risk_flagged_share']:.1%} of sellers flagged review-risk." + c_text
        ),
    ])


# ---------------------------------------------------------------------------
# Delivery tab callbacks
# ---------------------------------------------------------------------------
@app.callback(Output("delay-band-chart", "figure"), Input("tabs", "value"))
def delay_band_chart(_):
    df = delay_band_summary.set_index("delay_band").reindex(DELAY_BAND_ORDER).reset_index()
    colors = [PALETTE["green"], PALETTE["amber"], PALETTE["orange"], PALETTE["red"]]
    fig = go.Figure(go.Bar(x=df["delay_band"], y=df["avg_review_score"], marker_color=colors,
                            text=df["orders"].apply(lambda n: f"{n:,} orders"), textposition="outside"))
    fig.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=420,
                       yaxis_title="Average review score", yaxis_range=[0, 5.3])
    return fig


@app.callback(Output("monthly-trend-chart", "figure"), Input("tabs", "value"))
def monthly_trend_chart(_):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly_trend["purchase_month"], y=monthly_trend["avg_review_score"],
                              name="Avg review score", line=dict(color=PALETTE["green"]), yaxis="y1"))
    fig.add_trace(go.Scatter(x=monthly_trend["purchase_month"], y=monthly_trend["late_delivery_rate"] * 100,
                              name="Late-delivery rate (%)", line=dict(color=PALETTE["red"]), yaxis="y2"))
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10), height=420,
        yaxis=dict(title="Avg review score", range=[0, 5]),
        yaxis2=dict(title="Late-delivery rate (%)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.15),
    )
    return fig


# ---------------------------------------------------------------------------
# Customer Retention tab callbacks
# ---------------------------------------------------------------------------
@app.callback(Output("quadrant-chart", "figure"), Input("tabs", "value"))
def quadrant_chart(_):
    df = customer_quadrant_summary.set_index("segment").reindex(QUADRANT_ORDER).reset_index()
    colors = [PALETTE["green"] if "happy" in s else PALETTE["red"] for s in df["segment"]]
    fig = go.Figure(go.Bar(
        x=df["revenue_share_pct"], y=df["segment"], orientation="h", marker_color=colors,
        customdata=df[["customers", "late_delivery_rate"]],
        hovertemplate="%{y}<br>Revenue share: %{x:.1f}%<br>Customers: %{customdata[0]:,}"
                      "<br>Late-delivery rate: %{customdata[1]:.1%}<extra></extra>",
        text=df["revenue_share_pct"].apply(lambda v: f"{v:.1f}%"), textposition="outside",
    ))
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=380,
                       xaxis_title="Share of total revenue (%)", yaxis_title="")
    return fig


@app.callback(Output("delay-repeat-chart", "figure"), Input("tabs", "value"))
def delay_repeat_chart(_):
    df = customer_delay_repeat_summary.set_index("late_band").reindex(DELAY_REPEAT_ORDER).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["late_band"], y=df["avg_review_score"], name="Avg review score",
                          marker_color=PALETTE["blue"], yaxis="y1"))
    fig.add_trace(go.Scatter(x=df["late_band"], y=df["repeat_rate"] * 100, name="Repeat rate (%)",
                              marker_color=PALETTE["red"], yaxis="y2", mode="lines+markers"))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=380,
        yaxis=dict(title="Avg review score", range=[0, 5.3]),
        yaxis2=dict(title="Repeat rate (%)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


@app.callback(Output("quadrant-detail", "children"), Input("quadrant-chart", "clickData"))
def quadrant_detail(click_data):
    notes = {
        "High-value & unhappy": (
            "This is the single highest-leverage group: real revenue at stake, and a "
            "late-delivery rate roughly 8-9x higher than equally valuable, satisfied customers. "
            "Fixing delivery for this segment protects revenue without a platform-wide overhaul."
        ),
        "High-value & happy": "The core of the business - high spend, low late-delivery rate. Protect this segment's experience, don't disrupt it.",
        "Low-value & happy": "Largest segment by headcount and a healthy delivery experience - a natural pool to grow into higher-value customers.",
        "Low-value & unhappy": "Smaller revenue exposure than the high-value-unhappy group, but the highest late-delivery rate of all four segments.",
    }
    if not click_data:
        seg = "High-value & unhappy"
    else:
        seg = click_data["points"][0]["y"]
    row = customer_quadrant_summary[customer_quadrant_summary["segment"] == seg].iloc[0]
    return html.Div([
        html.H5(seg),
        html.P(
            f"{row['customers']:,} customers, {row['revenue_share_pct']:.1f}% of total revenue, "
            f"avg review score {row['avg_review_score']:.2f}/5, "
            f"late-delivery rate {row['late_delivery_rate']:.1%}. {notes.get(seg, '')}"
        ),
    ])


# ---------------------------------------------------------------------------
# Seller Acquisition (funnel) tab callbacks
# ---------------------------------------------------------------------------
@app.callback(Output("funnel-origin-chart", "figure"), Input("tabs", "value"))
def funnel_origin_chart(_):
    df = funnel_origin_conversion.sort_values("conversion_rate")
    fig = go.Figure(go.Bar(
        x=df["conversion_rate"] * 100, y=df["origin"], orientation="h", marker_color=PALETTE["blue"],
        customdata=df[["leads"]],
        hovertemplate="%{y}<br>Conversion rate: %{x:.1f}%<br>Leads: %{customdata[0]:,}<extra></extra>",
        text=df.apply(lambda r: f"{r['conversion_rate']*100:.1f}% (n={r['leads']:,})", axis=1),
        textposition="outside",
    ))
    fig.add_vline(x=funnel_overview["conversion_rate"] * 100, line_dash="dash", line_color=PALETTE["red"],
                  annotation_text="Overall avg")
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=420,
                       xaxis_title="Conversion rate (%)", yaxis_title="")
    return fig


@app.callback(Output("funnel-business-chart", "figure"), Input("tabs", "value"))
def funnel_business_chart(_):
    df = funnel_business_type_share.sort_values("share_pct", ascending=False)
    fig = go.Figure(go.Bar(
        x=df["business_type"], y=df["share_pct"], marker_color=PALETTE["green"],
        text=df["share_pct"].apply(lambda v: f"{v:.1f}%"), textposition="outside",
    ))
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=420,
                       yaxis_title="Share of converted leads (%)", xaxis_title="")
    return fig


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
