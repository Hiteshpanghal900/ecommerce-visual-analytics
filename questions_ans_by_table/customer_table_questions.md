# Questions Answered by `cleaned_customer_level_master_table.csv`

This table has one row per customer (96,096 unique customers), summarizing their entire lifetime
on the marketplace: total spend, order count, delivery experience, review behavior, and repeat
purchase status. It's the right table for any question about **customer-level behavior and
retention** — as opposed to the order-level tables, which answer per-transaction questions.

Source: `data-visualization/cleaned_customer_level_master_table.csv`
EDA notebook: `data-visualization/customer-master-analysis.ipynb`

---

## 1. Is customer revenue concentrated among a few "whale" customers, or spread across volume?

Mostly volume, not whales: the **top 20% of customers generate ~54%** of total revenue, and the
**median customer spends only R$108** (mean R$167, pulled up by a smaller number of bigger spenders).

**Takeaway:** this is not a business that can grow primarily by protecting a VIP tier — growth
depends on acquisition volume and retention across the broad base, since even the top-quintile
customers don't dominate revenue the way a true whale-driven business would show.

---

## 2. How much of the customer base ever comes back and buys again?

Very little: only **~3.1% of customers are repeat buyers** (made more than one purchase in the
observed period). A repeat buyer is worth roughly **2x** a one-time buyer in lifetime spend, and
the median gap between a repeat customer's first and second order is about **33 days**.

**Takeaway:** retention is almost entirely untapped. Given how much more valuable a repeat customer
already is even without any targeted effort, a working repeat-purchase program is one of the
highest-leverage growth levers available — more so than trying to raise average order value.

---

## 3. Does delivery experience relate to review score at the customer level?

Yes, and it's the single strongest signal in the dataset: customers whose orders are **mostly late**
average around **2.3** on review score vs. **~4.2** for mostly-on-time customers. Across the full
correlation ranking (`avg_review_score` against every other numeric field), the three delivery-delay
variables dominate every other candidate driver, including payment behavior and basket diversity.

This is an association, not a settled causal claim: a customer who is already dissatisfied for
unrelated reasons (product mismatch, price, expectations) isn't distinguishable here from one made
dissatisfied specifically by a delay. But the size and consistency of the gap (and that it beats
every other tested variable) makes delivery the leading lever to test operationally.

**Takeaway:** delivery reliability should be treated as the primary customer-experience lever,
ahead of payment terms, basket composition, or acquisition channel.

---

## 4. Does raw delivery speed matter on top of just "keeping the promise" (not being late)?

Yes. Delay-vs-promise (`avg_delivery_delay_days`) correlates with satisfaction at **-0.27**, but
raw delivery speed (`avg_actual_delivery_days`) correlates slightly *more* strongly at **-0.34** —
and even restricting to on-time deliveries only, faster orders still score higher: **4.42** for
deliveries under 7 days vs. **3.86** for those over 21 days, even though both counted as "on time"
against the estimate.

**Takeaway:** the lever isn't just "don't be late" — genuinely fast delivery earns a satisfaction
premium even when the promise was already being kept. Tightening actual transit time (not just
padding the estimate less aggressively) has real upside.

---

## 5. Which customer segment should the company act on first?

The **"High-value and Unhappy"** segment: about **4,200 customers**, representing **~11% of
observed revenue**, with a **~26% late-delivery rate** vs. only **~3%** for high-value *happy*
customers.

**Takeaway:** this segment combines real revenue weight with a delivery problem that's clearly
fixable (their late rate is ~8-9x the healthy high-value group's) — it's the highest-leverage
group to protect, since losing them would cost real GMV and the cause (delivery) is already
identified.

---

## 6. Are there regional differences in customer experience?

Yes: **RJ** stands out as the highest-priority large market — it has a meaningfully high
review-risk rate and carries real revenue share (12,380 customers). Several remote north/northeast
states (**MA, CE, PA, BA**, and smaller ones like **AL, SE**) show structurally worse outcomes
(higher review-risk rates, higher late-delivery rates), consistent with the same logistics-distance
pattern found in the seller-level analysis.

**Takeaway:** regional experience inequality is real and geography-driven (not just a seller-mix
artifact) — RJ is the priority market to fix given its size, while the northeast states may need a
structural logistics investment rather than a seller-level intervention.

---

## 7. Do payment behavior or basket diversity meaningfully affect satisfaction or risk?

Only weakly, and they're secondary to delivery: customers who pay in more installments (larger,
more financed baskets) rate marginally lower, and multi-seller baskets show almost no extra
late-delivery risk (correlation between `seller_diversity` and `late_delivery_rate` is essentially
zero, at **-0.01**). Neither comes close to the strength of the delivery-related correlations.

**Takeaway:** payment terms and basket composition are not meaningful levers on their own — delivery
reliability dominates the picture so thoroughly that other candidate drivers barely register by
comparison.

---

## 8. Does a good first-order experience predict whether a customer becomes a repeat buyer?

Not visibly, at this grain: repeat and one-time customers have **near-identical** average review
scores (gap of about **+0.02**) and late-delivery rates (gap of about **-0.01**). The customer-level
variables that *do* correlate strongly with being a repeat buyer (`customer_orders`, `review_count`,
`seller_diversity`) are mechanical consequences of having ordered more times, not independent causes
of repeat behavior.

**Takeaway:** "a clean first delivery earns the second order" is a plausible and testable hypothesis,
but this customer-level table (which aggregates a customer's whole history into one row) cannot
confirm or deny it — that requires an order-sequence-level test (first order's outcome vs. whether a
second order happened), which is a natural next step once customer and order tables are joined at
the order-sequence level.

---

## Data caveat to flag in the report

This table aggregates each customer's entire observed history into one row, so it describes
completed historical behavior over a fixed period, not a live view. Repeat-purchase rate is also
affected by how recently a customer joined (a customer who joined near the end of the observed
window has had less time to reorder) — the ~3% repeat rate should be read as a lower bound shaped
partly by this window effect, not purely by product/experience quality.
