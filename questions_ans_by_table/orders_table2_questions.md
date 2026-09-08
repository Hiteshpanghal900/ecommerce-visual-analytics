# Questions Answered by `cleaned_master_order_table2.csv`

This table has one row per order (95,830 orders), focused on **sales, payment, and delivery
mechanics** — order size, freight cost, number of sellers/products involved, and delivery timing.
It complements `cleaned_master_order_table1.csv` (customer/order/review identity fields) by holding
the order-economics columns that drive the delivery and satisfaction story.

Source: `data-visualization/cleaned_master_order_table2.csv`
Cleaning notebook: `data_cleaning/cleaning_master_order_table.ipynb`
EDA notebook: `EDA/eda_master_orders_table.ipynb`

---

## 1. How strong is the link between delivery delay and review score?

Very strong, and it holds at every level of granularity checked:
- Orders delivered **on time**: average review score **4.29**.
- Orders delivered **late**: average review score **2.27**, and **53.78%** of these get a 1-star
  review (vs. **6.62%** for on-time orders).
- Banding by exact delay: **1–2 days late → 3.51**, **3–5 days late → 2.47**, **6–10 days late →
  1.77**, **>10 days late → 1.71**. Satisfaction falls sharply with even a small delay and then
  keeps falling, though the drop-off flattens out past ~6 days.

**Takeaway:** delivery delay is the single clearest, most consistent driver of dissatisfaction in
the order-level data. This is an association across a large sample (95,830 orders) with a
consistent dose-response shape (more delay → worse score at every band), which is stronger evidence
than a single correlation coefficient — but it's still not a controlled experiment, so "delay
causes the drop" is the best-supported explanation here rather than a proven one.

---

## 2. Does the number of sellers in an order affect satisfaction?

Yes, and the drop-off is severe: **1-seller orders** average **4.17** with a late-delivery rate of
**6.74%**; **2-seller orders** average **2.89** with a *lower* late rate of just **1.00%**;
**3+-seller orders** average **2.24** with a **0%** observed late rate.

**Takeaway:** multi-seller orders score worse *despite* better on-paper delivery timing, so the
dissatisfaction here is not explained by lateness — something about coordinating multiple sellers in
one order (partial shipments, mismatched packaging, split communication) is plausibly the real
driver. This should be treated as an association to investigate further, not a settled cause,
especially since the 3+-seller group is small (59 orders) and easy to over-read.

---

## 3. Does order size (number of items) affect satisfaction?

Yes: **1-item orders** average **4.21** (8.50% 1-star); by **6+ items** the average falls to
**3.25** (31.69% 1-star) — despite late-delivery rates staying flat (6.82% → 6.58%, no clear trend).

**Takeaway:** larger orders are less satisfying independent of delivery timing, suggesting order
complexity itself (more chances for something to go wrong, higher expectations for a bigger
purchase) matters — not just whether the order arrived on time.

---

## 4. Does buying more distinct products in one order affect satisfaction?

Yes, similarly to order size: **1-product orders** average **4.18**; by **6+ distinct products**
the average falls to **2.86** — again without a corresponding rise in late-delivery rate (both ends
show 0–9% late).

**Takeaway:** product-mix complexity tracks with lower satisfaction the same way item-count does,
reinforcing that "order complexity" (not just delivery lateness) is a real, separate risk factor
worth its own investigation.

---

## 5. Does freight cost affect satisfaction?

Yes, moderately: the **high-freight quartile** (avg R$45.38) scores **3.94** with a **14.24%**
1-star rate; the **low-freight quartile** (avg R$10.45) scores **4.31** with **6.61%** 1-star. Late
delivery is also somewhat higher in the high-freight group (7.81% vs. 4.35%), so freight cost and
delivery lateness are not fully independent here.

**Takeaway:** high freight is a real but secondary dissatisfaction signal; because it correlates
with late-delivery rate too, some of this effect likely overlaps with the delivery story rather than
being a fully separate "shipping cost annoys people" effect.

---

## 6. Does freight *burden* (freight as a share of order value) affect satisfaction?

Only weakly: average review score declines slightly from **4.20** (lowest freight-ratio quartile)
to **4.11** (highest), with late-delivery rates staying broadly flat across quartiles.

**Takeaway:** unlike absolute freight cost, freight *burden* is not a meaningful standalone driver
of dissatisfaction — customers don't appear to punish orders where shipping is expensive relative
to the item's value nearly as much as they punish orders that arrive late.

---

## 7. What share of orders are late, and how bad is the 1-star problem overall?

**6.66%** of orders are late. Overall, **9.76%** of all reviews are 1-star, while **78.93%** are
4–5 stars and the overall average review score is **4.16** (matching `orders_table1`'s findings on
the shared review-score field).

**Takeaway:** the marketplace is broadly healthy on reviews, but the 1-star share is not trivial and
is heavily concentrated among the ~6.7% of orders that arrive late — a relatively small, targetable
slice of the order volume drives a disproportionate share of the worst outcomes.

---

## Data caveat to flag in the report

The multi-seller (`2 sellers`, `3+ sellers`) and multi-product-count segments used above are small
in absolute terms (e.g., 59 orders for 3+ sellers) relative to the 95,830-order base. Percentage
comparisons involving these groups are directionally useful but should not be treated as precise or
heavily over-interpreted given the sample size.
