# Interactive Marketplace Dashboard

A Plotly Dash app answering the project's core question - why do so few customers come back, and
where should the marketplace intervene - by category, seller, region, delivery performance,
customer retention, and seller acquisition. This dashboard mirrors and lets a viewer freely
re-explore the narrative built in `../combined_eda.ipynb` and written up in
`../report/technical_report.tex`.

## Setup

```
pip install dash plotly pandas
```

## Run

```
python prepare_dashboard_data.py   # once, or whenever a cleaned master table / review file changes
python app.py
```

Open http://127.0.0.1:8050

## How it's structured

- `prepare_dashboard_data.py` reads the cleaned master tables from `../data-visualization/`
  (orders ~96K rows / 38MB, customers ~96K rows / 18MB, sellers, categories, marketing funnel),
  the mined review data (`../data_cleaning/processed_customer_reviews.csv`), and the raw
  order-items/products tables (`../data/E-Commerce Dataset/`) needed to compute product-quality-
  issue rates - then writes small, pre-aggregated CSVs into `data/` (a few hundred rows each, or
  fewer). This runs once, offline - the app itself never touches the large raw tables, so every
  filter/callback stays fast.
- `app.py` is the Dash app: a global filter bar (state / seller value tier / review-risk status)
  drives KPI cards and six tabs:
  - **By Category** - satisfaction and (new) product-quality-issue rate by category, click-to-drill.
  - **By Seller** - revenue concentration, value x risk quadrant, top/risky seller tables (now
    including each seller's quality-issue rate alongside review score and late-delivery rate).
  - **By Region** - review score and risk by state, click-to-drill detail.
  - **Delivery Performance** - review score by delay band, monthly trend.
  - **Customer Retention** *(new)* - the value x satisfaction quadrant that sizes the
    "high-value & unhappy" priority segment (~4,200 customers, ~11% of revenue, ~26% late-delivery
    rate), plus review score and repeat-purchase rate by delivery-delay band (with the same
    small-sample caveat on the middle bands documented in the notebook and report).
  - **Seller Acquisition** *(new)* - conversion rate by acquisition channel and business-type mix
    among converted sellers, from the marketing-funnel table.

  Every tab pairs an exploratory chart with a focused/comparison chart and, where relevant, a
  click-to-drill detail panel explaining *why* a selected category, seller, state, or customer
  segment stands out - directly answering the "see why a segment stands out" requirement.

## Product-quality-issue rate (new)

`prepare_dashboard_data.py` now joins raw order items + products + the review-topic mining output
(`processed_customer_reviews.csv`) to compute a `quality_issue_rate` per seller (restricted to
sellers with >100 deliveries) and per category (restricted to categories with >=500 orders) -
identical logic and thresholds to `combined_eda.ipynb`, so the numbers shown in the dashboard match
the report exactly. This is written to `data/seller_quality.csv` and `data/category_quality.csv`,
then left-joined onto `seller_summary.csv` / `category_summary.csv` as one more column
(`has_quality_data` flags whether a row cleared the volume threshold).

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
