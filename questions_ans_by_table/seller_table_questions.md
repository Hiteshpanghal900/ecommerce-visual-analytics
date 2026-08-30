# Questions Answered by `cleaned_seller_level_master_table.csv`

This table has one row per seller (3,095 sellers) summarizing their entire history on the marketplace: volume, sales, delivery performance, reviews, and tenure. It's the right table for any question about **seller-level behavior** — as opposed to the master order table, which answers order-level questions.

Source: `data-visualization/cleaned_seller_level_master_table.csv`
Cleaning notebook: `data_cleaning/clean_seller_master_table.ipynb`

---

## 1. How many sellers are there, and where are they located?

There are **3,095 sellers** spread across **23 Brazilian states**, but the distribution is heavily skewed geographically:

| State | Sellers |
|---|---|
| SP | 1,849 (60%) |
| PR | 349 |
| MG | 244 |
| SC | 190 |
| RJ | 171 |
| RS | 129 |

**Takeaway:** The seller base is concentrated in São Paulo (SP), which alone accounts for 6 in 10 sellers. Any regional strategy (logistics investment, seller recruitment) should recognize that SP is not "one region among many" — it *is* most of the marketplace.

---

## 2. How concentrated is revenue among sellers? (Is this a "long tail" marketplace?)

Yes — sales are highly concentrated:
- The **top 10% of sellers generate 67.5%** of total item sales value.
- The **top 1% of sellers generate 25.7%** of total item sales value.
- The single largest seller (SP) sold **R$229,472** worth of items; the median seller sold far less.

**Takeaway:** This is a classic long-tail marketplace. A small number of power sellers drive the majority of GMV. Losing even one or two top sellers would be far more damaging than losing dozens of small ones — which matters for how "seller risk" should be prioritized (see Q6).

---

## 3. What does a typical review score look like, and how many sellers have no reviews yet?

- Average review score across sellers: **~4.0 / 5** (mean 3.997, median 4.18).
- **3,090 of 3,095 sellers (99.8%)** have at least one review; only **5 sellers** have zero reviews so far (flagged via `has_reviews = False` rather than dropped, since they're still valid active sellers).

**Takeaway:** Review scores are generally high and only a handful of sellers are "unreviewed" — this isn't a meaningful gap to worry about, but the flag exists so downstream analyses can exclude them cleanly instead of treating a missing score as a zero.

---

## 4. Does late delivery hurt seller reviews?

Yes, clearly. Correlations across sellers with both a review and at least one delivered order:

| | late_delivery_rate | avg_review_score | review_risk_rate |
|---|---|---|---|
| **late_delivery_rate** | 1.00 | **-0.42** | **+0.40** |
| **avg_review_score** | -0.42 | 1.00 | **-0.91** |

- Sellers with a higher share of late deliveries have meaningfully lower average review scores (correlation -0.42).
- `review_risk_rate` (share of a seller's orders that are "at risk" reviews) is almost perfectly inversely related to average review score (-0.91), which is expected since they're derived from similar signals — but it confirms the risk flag is a trustworthy proxy for review quality.

**Takeaway:** Delivery reliability is one of the strongest seller-level levers on customer satisfaction. This directly supports the project's core question — late delivery is not just an operational issue, it is a satisfaction and retention issue.

---

## 5. Are sellers, on average, delivering early, on time, or late?

- Average delivery delay across sellers with delivered orders: **-12.2 days** (negative = early).
- **2,873 of 2,970 sellers (97%)** have a *negative* average delay — i.e., most sellers beat the estimated delivery date on average.
- However, the late-delivery **rate** distribution shows real variation: **1,821 sellers (59%)** have a 0% late-delivery rate, but **230 sellers (7.4%)** have a late-delivery rate above 20%.

**Takeaway:** The marketplace as a whole over-delivers against its own estimates, but there's a meaningful tail of consistently-late sellers. Because delivery lateness correlates with worse reviews (Q4), this tail of ~230 sellers is a natural intervention target — flagging or coaching them could disproportionately improve satisfaction without touching the majority who already perform well.

---

## 6. Which sellers combine high business value with high review risk? (Where should the company intervene?)

**208 sellers (6.7%)** are flagged `review_risk_flag = True`, meaning a high share of their orders end in risky/low reviews. Since `active_seller_flag` is `True` for all 3,095 sellers in this dataset (see note below), all 208 risky sellers are currently active — i.e., they are live and actively affecting customer experience today, not legacy/inactive accounts.

Combined with Q2 (revenue concentration) and Q5 (late-delivery tail), the actionable segment is:
- **High-volume sellers with high late-delivery rate and/or review-risk flag** — these sellers do enough business to matter for growth, but their delivery/quality problems are actively suppressing satisfaction. This is exactly the "where should the company intervene" segment leadership asked about.
- Low-volume, low-risk sellers are lower priority — intervening there has little marketplace-wide impact.

**Takeaway:** A prioritized seller-health dashboard should rank sellers by a combination of **sales contribution × review risk × late-delivery rate**, not by risk alone — a small risky seller matters far less than a large risky one.

---

## 7. Does selling a wider variety of product categories correlate with more sales?

Weak positive correlation (**+0.32**) between `category_diversity` and `total_item_sales_value`. Sellers who list across more categories tend to sell somewhat more, but this is a mild effect, not a strong driver — most of a seller's sales volume is explained by other factors (order volume, tenure, pricing), not catalogue breadth.

**Takeaway:** Encouraging catalogue diversification is a plausible but secondary growth lever — it shouldn't be oversold as a primary strategy.

---

## 8. Does seller tenure (how long they've been selling) predict better performance?

Essentially no relationship:
- Tenure vs. average review score: **+0.08** (negligible)
- Tenure vs. late-delivery rate: **+0.01** (negligible)

**Takeaway:** Longevity on the platform does not automatically translate into better service quality. Seller quality appears to be a function of how they operate, not how long they've been around — so "new seller" is not, by itself, a red flag, and "veteran seller" is not automatically a mark of reliability.

---

## 9. Does order/sales volume relate to review quality?

Splitting sellers at the median for `total_items_sold`:

| Segment | Avg review score | Late delivery rate |
|---|---|---|
| High-volume sellers | 4.11 | 6.4% |
| Low-volume sellers | 3.90 | 6.1% |
| Difference | +0.22 | ≈0.3 pts |

**Takeaway:** Higher-volume sellers actually have slightly *better* average reviews despite a marginally higher late-delivery rate — likely because experienced/high-volume sellers have more efficient fulfillment operations overall. This pushes back against an assumption that "scaling up onboarding" inherently degrades quality; the data suggests the opposite at the seller level.

---

## 10. How does freight cost behave across sellers and regions?

- The freight-to-sales ratio (`total_item_freight_value / total_item_sales_value`) averages **26.5%** across sellers, with wide variation (0–353%, driven by a few extreme outliers likely selling low-value/high-shipping-cost items).
- The states with the **highest freight ratios** are all outside the Southeast core: **PE (35.5%), CE (35.4%), PB (35.3%), MA (33.3%), MT (32.0%)** — consistent with these being geographically farther from the main logistics hubs.

**Takeaway:** Sellers in outlying states pay a real shipping-cost penalty relative to their sales value. This is a structural, geography-driven cost — worth surfacing in the dashboard as context when comparing seller performance across regions, so a seller in PE isn't unfairly judged against one in SP on cost efficiency alone.

---

## Data caveat to flag in the report

`active_seller_flag` is `True` for **100% of rows** in this table — it currently carries no discriminating information (in this dataset, it does not distinguish active from inactive sellers). This should either be revisited upstream (in `data-processing-seller_master.ipynb`, where the flag is computed) or explicitly excluded from any "active vs. inactive" analysis/dashboard filter until fixed, since as-is it cannot support that comparison.
