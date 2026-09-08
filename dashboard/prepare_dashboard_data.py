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

# ---------------------------------------------------------------------------
# 1. Seller summary (already small enough to ship close to as-is; trim to the
#    columns the dashboard actually uses)
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
# 3. Category summary (already small - 73 rows - ship as-is)
# ---------------------------------------------------------------------------
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

print("\nAll dashboard data files written to:", OUT_DIR)
