"""
Pre-aggregates the cleaned master tables into small, dashboard-ready CSVs.

Why: the order and customer master tables are ~95K rows / 20-40MB each. Loading and
re-aggregating them on every callback would make the dashboard sluggish. This script runs
ONCE (or whenever a master table changes) and writes small summary tables the Dash app reads
directly - each a few hundred rows at most.

Run from the repo root or from dashboard/: `python prepare_dashboard_data.py`
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
DATA_VIZ = REPO_ROOT / "data-visualization"
DATA_CLEANING = REPO_ROOT / "data_cleaning"
RAW_ECOM = REPO_ROOT / "data" / "E-Commerce Dataset"
OUT_DIR = HERE / "data"
OUT_DIR.mkdir(exist_ok=True)


def load(name, **kwargs):
    return pd.read_csv(DATA_VIZ / name, **kwargs)


print("Loading cleaned master tables...")
sellers = load("cleaned_seller_level_master_table.csv")
customers = load("cleaned_customer_level_master_table.csv")
categories = load("cleaned_category_level_master_table.csv")
orders = load("cleaned_master_order_table.csv", parse_dates=[
    "order_purchase_timestamp", "order_delivered_customer_date"
])
market_funnel = load("cleaned_marketing_funnel_master_table.csv")
customer_reviews = pd.read_csv(DATA_CLEANING / "processed_customer_reviews.csv")

# ---------------------------------------------------------------------------
# 0. Product-quality-issue rate, by seller and by category - same join logic as
#    combined_eda.ipynb: order_items + products + review-topic mining, filtered
#    to reviews whose primary_topic mentions "product quality". This is where a
#    complaint theme ("what are people unhappy about") turns into a per-seller /
#    per-category rate that explains WHY a segment stands out.
# ---------------------------------------------------------------------------
print("Building product-quality-issue rates (seller + category)...")
products_raw = pd.read_csv(RAW_ECOM / "products_dataset.csv")
order_items_raw = pd.read_csv(RAW_ECOM / "order_items_dataset.csv")
product_category_raw = pd.read_csv(RAW_ECOM / "product_category_name_translation.csv")

items_products = order_items_raw.merge(products_raw, on="product_id", how="left")
items_products = items_products.merge(product_category_raw, on="product_category_name", how="left")
items_products = items_products.merge(
    customer_reviews[["order_id", "sentiment", "primary_topic"]], on="order_id", how="left"
)
quality_items = items_products[
    items_products["primary_topic"].str.contains("product quality", case=False, na=False)
]

seller_quality = (
    quality_items.groupby("seller_id").agg(quality_issues=("order_id", "nunique")).reset_index()
)
seller_deliveries = (
    items_products.groupby("seller_id").agg(total_deliveries=("order_id", "nunique")).reset_index()
)
seller_quality_summary = (
    seller_quality.merge(seller_deliveries, on="seller_id", how="right")
    .fillna({"quality_issues": 0})
)
seller_quality_summary["quality_issue_rate"] = (
    seller_quality_summary["quality_issues"] / seller_quality_summary["total_deliveries"] * 100
)
seller_quality_summary.to_csv(OUT_DIR / "seller_quality.csv", index=False)
print(f"seller_quality.csv: {seller_quality_summary.shape}")

category_quality = (
    items_products.groupby("product_category_name_english")
    .agg(
        total_orders=("order_id", "nunique"),
        quality_issues=("order_id", lambda x: x.isin(quality_items["order_id"]).sum()),
    )
    .reset_index()
    .rename(columns={"product_category_name_english": "product_category"})
)
category_quality["quality_issue_rate"] = (
    category_quality["quality_issues"] / category_quality["total_orders"] * 100
)
category_quality.to_csv(OUT_DIR / "category_quality.csv", index=False)
print(f"category_quality.csv: {category_quality.shape}")

# ---------------------------------------------------------------------------
# 1. Seller summary (already small enough to ship close to as-is; trim to the
#    columns the dashboard actually uses). Quality-issue rate is merged in here
#    (restricted to sellers with >100 deliveries, matching combined_eda.ipynb's
#    threshold for a stable rate) so the existing seller tab/table can use it
#    directly as one more column.
# ---------------------------------------------------------------------------
seller_cols = [
    "seller_id", "seller_state", "seller_city", "total_items_sold",
    "total_item_sales_value", "orders_handled", "avg_review_score", "review_count",
    "late_delivery_rate", "avg_delivery_delay_days", "review_risk_rate",
    "review_risk_flag", "has_reviews", "has_delivered_orders", "seller_tenure_days",
    "category_diversity",
]
seller_summary = sellers[seller_cols].copy()
value_cut = seller_summary["total_item_sales_value"].quantile(0.75)
seller_summary["value_tier"] = np.where(
    seller_summary["total_item_sales_value"] >= value_cut, "High-value", "Lower-value"
)

quality_for_merge = seller_quality_summary[seller_quality_summary["total_deliveries"] > 100][
    ["seller_id", "quality_issue_rate", "quality_issues", "total_deliveries"]
].rename(columns={"total_deliveries": "quality_eval_deliveries"})
seller_summary = seller_summary.merge(quality_for_merge, on="seller_id", how="left")
seller_summary["has_quality_data"] = seller_summary["quality_issue_rate"].notna()

seller_summary.to_csv(OUT_DIR / "seller_summary.csv", index=False)
print(f"seller_summary.csv: {seller_summary.shape}")

# ---------------------------------------------------------------------------
# 2. State-level rollup (region tab) - built from sellers AND customers so the
#    dashboard can show both supply-side and demand-side regional patterns
# ---------------------------------------------------------------------------
# Note: `review_risk_flagged_share` = share of sellers/customers in the state flagged as
# review-risk (a headcount rate). This is DIFFERENT from `review_risk_rate` on the seller
# table, which is each seller's own share of risky orders averaged across sellers - the two
# answer different questions ("how much of the base is risky" vs. "how risky is the average
# seller's order mix") and must not be relabeled interchangeably in the dashboard.
seller_state = (
    sellers.groupby("seller_state")
    .agg(
        seller_count=("seller_id", "count"),
        total_sales_value=("total_item_sales_value", "sum"),
        avg_review_score=("avg_review_score", "mean"),
        late_delivery_rate=("late_delivery_rate", "mean"),
        review_risk_flagged_share=("review_risk_flag", "mean"),
        avg_seller_order_risk_rate=("review_risk_rate", "mean"),
    )
    .reset_index()
    .rename(columns={"seller_state": "state"})
)
seller_state["role"] = "seller"

customer_state = (
    customers.groupby("customer_state")
    .agg(
        customer_count=("customer_unique_id", "count"),
        total_payment_value=("total_payment_value", "sum"),
        avg_review_score=("avg_review_score", "mean"),
        late_delivery_rate=("late_delivery_rate", "mean"),
        review_risk_flagged_share=("review_risk_flag", "mean"),
    )
    .reset_index()
    .rename(columns={"customer_state": "state"})
)
customer_state["role"] = "customer"

seller_state.to_csv(OUT_DIR / "state_seller_summary.csv", index=False)
customer_state.to_csv(OUT_DIR / "state_customer_summary.csv", index=False)
print(f"state_seller_summary.csv: {seller_state.shape}")
print(f"state_customer_summary.csv: {customer_state.shape}")

# ---------------------------------------------------------------------------
# 3. Category summary (73 rows) - quality-issue rate merged in (restricted to
#    categories with >=500 orders, matching combined_eda.ipynb's volume floor
#    so a category with 1-2 bad reviews doesn't look like a crisis).
# ---------------------------------------------------------------------------
quality_cat_for_merge = category_quality[category_quality["total_orders"] >= 500][
    ["product_category", "quality_issue_rate", "quality_issues", "total_orders"]
].rename(columns={"total_orders": "quality_eval_orders"})
categories = categories.merge(quality_cat_for_merge, on="product_category", how="left")
categories["has_quality_data"] = categories["quality_issue_rate"].notna()

categories.to_csv(OUT_DIR / "category_summary.csv", index=False)
print(f"category_summary.csv: {categories.shape}")

# ---------------------------------------------------------------------------
# 4. Delivery-delay bands (delivery tab) - pre-bin at order grain, then
#    collapse to band-level aggregates so the dashboard never touches the
#    95K-row order table directly
# ---------------------------------------------------------------------------
delivered = orders.loc[orders["actual_delivery_days"].notna()].copy()
delivered["delay_band"] = pd.cut(
    delivered["delivery_delay_days"],
    bins=[-np.inf, 0, 3, 7, np.inf],
    labels=["On or before estimate", "1-3 days late", "4-7 days late", "8+ days late"],
)
delay_band_summary = (
    delivered.groupby("delay_band", observed=True)
    .agg(
        orders=("order_id", "count"),
        avg_review_score=("review_score", "mean"),
        review_risk_rate=("review_risk_flag", "mean"),
    )
    .reset_index()
)
delay_band_summary.to_csv(OUT_DIR / "delay_band_summary.csv", index=False)
print(f"delay_band_summary.csv: {delay_band_summary.shape}")

# Monthly trend (purchase month vs. avg review score / late rate) - small, safe to ship
orders["purchase_month"] = orders["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
monthly_trend = (
    orders.dropna(subset=["purchase_month"])
    .groupby("purchase_month")
    .agg(
        orders=("order_id", "count"),
        avg_review_score=("review_score", "mean"),
        late_delivery_rate=("late_delivery_flag", "mean"),
    )
    .reset_index()
)
monthly_trend.to_csv(OUT_DIR / "monthly_trend.csv", index=False)
print(f"monthly_trend.csv: {monthly_trend.shape}")

# ---------------------------------------------------------------------------
# 5. Customer retention: repeat-vs-one-time split, and the value x satisfaction
#    quadrant used in combined_eda.ipynb to size the "who should we fix this
#    for" segment (high-value & unhappy customers).
# ---------------------------------------------------------------------------
print("Building customer retention & quadrant summary...")
customers = customers.copy()
high_value_cut = customers["total_payment_value"].quantile(0.75)
customers["high_value"] = customers["total_payment_value"] >= high_value_cut
customers["unhappy"] = customers["avg_review_score"] <= 2
customers["segment"] = np.select(
    [
        customers["high_value"] & customers["unhappy"],
        customers["high_value"] & ~customers["unhappy"],
        ~customers["high_value"] & customers["unhappy"],
    ],
    ["High-value & unhappy", "High-value & happy", "Low-value & unhappy"],
    default="Low-value & happy",
)
total_revenue = customers["total_payment_value"].sum()

quadrant_summary = (
    customers.groupby("segment")
    .agg(
        customers=("customer_unique_id", "count"),
        revenue=("total_payment_value", "sum"),
        avg_review_score=("avg_review_score", "mean"),
        late_delivery_rate=("late_delivery_rate", "mean"),
    )
    .reset_index()
)
quadrant_summary["revenue_share_pct"] = quadrant_summary["revenue"] / total_revenue * 100
quadrant_summary.to_csv(OUT_DIR / "customer_quadrant_summary.csv", index=False)
print(f"customer_quadrant_summary.csv: {quadrant_summary.shape}")

bands = pd.cut(
    customers["late_delivery_rate"], [-0.01, 0, 0.34, 0.67, 1.01],
    labels=["0% late", "1-33% late", "34-66% late", "67-100% late"],
)
delay_repeat_summary = (
    customers.assign(late_band=bands)
    .groupby("late_band", observed=True)
    .agg(
        customers=("customer_unique_id", "count"),
        avg_review_score=("avg_review_score", "mean"),
        repeat_rate=("repeat_customer_flag", "mean"),
    )
    .reset_index()
)
delay_repeat_summary.to_csv(OUT_DIR / "customer_delay_repeat_summary.csv", index=False)
print(f"customer_delay_repeat_summary.csv: {delay_repeat_summary.shape}")

repeat_overview = pd.DataFrame([{
    "repeat_customers": int((customers["customer_orders"] > 1).sum()),
    "one_time_customers": int((customers["customer_orders"] == 1).sum()),
    "repeat_rate": (customers["customer_orders"] > 1).mean(),
    "total_customers": len(customers),
}])
repeat_overview.to_csv(OUT_DIR / "customer_repeat_overview.csv", index=False)
print(f"customer_repeat_overview.csv: {repeat_overview.shape}")

# ---------------------------------------------------------------------------
# 6. Marketing / seller-acquisition funnel - conversion rate by channel and
#    business-type mix among converted leads, matching combined_eda.ipynb.
# ---------------------------------------------------------------------------
print("Building acquisition-funnel summary...")
origin_conversion = (
    market_funnel.assign(origin=market_funnel["origin"].fillna("unknown_missing"))
    .groupby("origin")
    .agg(leads=("mql_id", "count"), conversion_rate=("is_converted_flag", "mean"))
    .reset_index()
    .sort_values("conversion_rate", ascending=False)
)
origin_conversion.to_csv(OUT_DIR / "funnel_origin_conversion.csv", index=False)
print(f"funnel_origin_conversion.csv: {origin_conversion.shape}")

won = market_funnel[market_funnel["is_converted_flag"]]
business_type_share = (
    won["business_type"].value_counts(normalize=True).mul(100).rename("share_pct")
    .reset_index().rename(columns={"index": "business_type"})
)
business_type_share.to_csv(OUT_DIR / "funnel_business_type_share.csv", index=False)
print(f"funnel_business_type_share.csv: {business_type_share.shape}")

funnel_overview = pd.DataFrame([{
    "total_leads": len(market_funnel),
    "converted_leads": int(market_funnel["is_converted_flag"].sum()),
    "conversion_rate": market_funnel["is_converted_flag"].mean(),
}])
funnel_overview.to_csv(OUT_DIR / "funnel_overview.csv", index=False)
print(f"funnel_overview.csv: {funnel_overview.shape}")

print("\nAll dashboard data files written to:", OUT_DIR)
