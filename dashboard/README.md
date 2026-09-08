# Interactive Marketplace Dashboard

A Plotly Dash app answering the project's core question by category, seller, and region:
where is customer satisfaction at risk, and why.

## Setup

```
pip install dash plotly pandas
```

## Run

```
python prepare_dashboard_data.py   # once, or whenever a cleaned master table changes
python app.py
```

Open http://127.0.0.1:8050

## How it's structured

- `prepare_dashboard_data.py` reads the cleaned master tables from `../data-visualization/`
  (orders ~96K rows / 38MB, customers ~96K rows / 18MB, sellers, categories) and writes small,
  pre-aggregated CSVs into `data/` (a few hundred rows each). This runs once, offline - the app
  itself never touches the large raw tables, so every filter/callback stays fast.
- `app.py` is the Dash app: a global filter bar (state / seller value tier / review-risk status)
  drives KPI cards and four tabs - **By Category**, **By Seller**, **By Region**, **Delivery
  Performance** - each with an exploratory chart, a focused/comparison chart, and a click-to-drill
  detail panel explaining why a selected category/state stands out.

## Known metric distinction (don't relabel interchangeably)

Two different "risk rate" concepts appear in the underlying data and are labeled explicitly to
avoid confusion:
- **Share of sellers/customers flagged review-risk** (`review_risk_flagged_share`) - what fraction
  of the population in view is flagged. Used in the KPI row and the region tab.
- **Average per-entity order-risk rate** (`review_risk_rate` on the seller/category tables) - each
  seller's or category's own share of risky orders, averaged. Used in the category detail panel.

## Known gap

No master table carries a live "active seller" signal - `active_seller_flag` in the seller table
is `True` for 100% of rows (see `EDA/eda_seller_master_table.ipynb`), so it isn't used anywhere in
this dashboard.
