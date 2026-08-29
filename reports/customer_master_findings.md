# Customer-Level Master — Findings Report

**Dataset:** Olist Brazilian E-Commerce (orders Sep 2016 – Oct 2018)
**Unit of analysis:** one row per `customer_unique_id` (the real person, not the per-order `customer_id`)
**Population:** 96,096 customers · R$16.0M total revenue represented
**Notebooks:** `data_cleaning/cleaning_customer_master_table.ipynb` → `data-visualization/customer-master-analysis.ipynb`
**Cleaned data:** `data_cleaning/cleaned_customer_level_master_table.csv`
**Figures:** embedded inline in the analysis notebook (set `SAVE_FIGURES = True` there to also export PNGs)

---

## 1. Scope & method

This report studies the marketplace's customers to answer one leadership question: **where should the
company invest vs. intervene to grow without breaking the customer experience?** Every metric below is
read at the *customer* grain and every relationship is **associational, not causal**.

**Cleaning applied** (light, fully documented in the cleaning notebook — nothing imputed or deleted):

| Action | Detail |
|---|---|
| Dropped `customer_id_count` | exact duplicate of `customer_orders` |
| Parsed dates | `first_order_date`, `last_order_date` → datetime |
| Coverage flags added | `has_review` (716 without), `has_delivery` (2,740 never delivered) |
| `zero_payment_flag` | 3 zero-value customers flagged, kept for counts, excluded from revenue math |
| Text standardised | city/state casing normalised |
| `total_payment_value_capped` | p99 winsorised column for robust plots (raw preserved) |

**Coverage:** 99.3% of customers left a review; 97.1% received a delivery. Views that use review or
delivery metrics are filtered to those populations, and sample sizes are shown on every chart.

---

## 2. Findings

### F1 — Growth is a *volume* story, not a *whale* story
The top 1% of customers account for only 10.5% of revenue; the top 20% for ~54%; median spend is
**R$108**. There is no high-value tier large enough to build a VIP programme around.
→ **Implication:** growth must come from **acquisition volume + retention**, not from deepening a
handful of big accounts. *(see §2 Value concentration in the analysis notebook)*

### F2 — Retention is nearly untapped, and it is the highest-leverage growth lever
Only **3.1%** of customers ever reorder (5.9% of revenue), yet a repeat buyer is worth **~R$315 vs
~R$162** for a one-time buyer — roughly **2×**. The median repeat customer places their second order
within **33 days**.
→ **Implication:** even a few points of repeat rate materially moves GMV. The lever to earn the second
order is a clean first delivery (see F3–F4).

### F3 — Delivery experience explains satisfaction at the person level
Banding each customer's share of late deliveries:

| Share of orders late | avg review | % review-risk |
|---|---|---|
| 0% late | **4.21** | 11% |
| 34–66% late | 3.08 | 27% |
| 67–100% late | **2.26** | **61%** |

The delay↔score correlation is **−0.27** and monotonic — the person-level echo of the order-level
"delivery cliff." → **Implication:** delivery, not price or product, is the primary satisfaction lever.
*(see §4 Delivery & satisfaction in the analysis notebook)*

### F4 — The one segment to act on first: **High-value & Unhappy**
Crossing value (top spend quartile) with satisfaction (avg review ≤ 2):

- **4,200 customers**, carrying **R$1.81M — 11.3% of all revenue**.
- Their late-delivery rate is **26%** vs just **3%** for high-value *happy* customers.

→ **Implication:** the marketplace's most valuable dissatisfied customers are dissatisfied because of
**late delivery**. Fixing delivery for this cohort defends ~11% of GMV — the single clearest business
case in the analysis. *(see §6 Priority segments in the analysis notebook)*

### F5 — Risk concentrates geographically; RJ is the priority market
- **RJ:** 13.4% of revenue but ~20% review-risk and ~12% late — a *large, valuable, underperforming*
  market, the highest-value fix.
- **MA, CE, PA, BA** (remote north/northeast): structurally worst (17–22% risk), driven by distance.
- **SP** (37.5% of revenue): the healthy anchor / benchmark.

→ **Implication:** a targeted RJ + northeast logistics intervention, not blanket seller crackdowns.
*(see §5 Geography in the analysis notebook)*

### F6 — Payment and basket signals are real but secondary
- **Installments:** more installments → larger baskets (financed purchases) and a *slightly* lower
  average review — a small effect next to delivery. *(see §7 Payment behaviour in the analysis notebook)*
- **Basket diversity:** buying from multiple sellers does **not** measurably raise a customer's
  late-delivery rate (correlation ≈ 0). Multi-origin baskets are not, on average, a risk driver.

→ **Implication:** don't over-index on payment or basket rules; delivery dominates.

### F7 — The base grew while satisfaction held broadly flat
New customers per month rose steadily across 2017–mid-2018 while average review score stayed roughly
level — the marketplace scaled acquisition **without** a visible collapse in experience, but also
without improving it. → **Implication:** experience is a *managed constant*, not yet a competitive
advantage; the delivery fixes above are how it becomes one. *(see §9 Acquisition cohort in the analysis notebook)*

---

## 3. Questions this analysis raises (next steps)

These are answerable with joins to the other master tables and would sharpen the recommendations:

1. **Where are the late days created?** Decompose delivery into *seller handling* vs *carrier transit*
   vs *ETA padding* using the order table's five timestamps. This turns "delivery is bad" into a
   specific, fixable link.
2. **Do multi-seller baskets fail because of one slow seller?** The customer-level null result (F6)
   may hide item-level variance — needs the `order_items` join.
3. **What is the retention curve?** Do customers with a *clean first delivery* reorder at a higher
   rate? A first-order-experience → repeat-rate cohort analysis would price F2 precisely.
4. **Which acquisition channels feed the risky regions?** Link the marketing funnel
   (`closed_deals` → seller → orders) to see whether fast recruiting brought the sellers behind the
   high-risk states — the core growth-vs-quality question.
5. **Is RJ a distance problem or a seller problem?** Decompose RJ's underperformance by seller origin
   vs. carrier leg to choose the right intervention.

---

## 4. Recommended actions (from this table alone)

1. **Delivery-promise SLA** — protect the promised date; pad ETAs conservatively. Start with the
   High-value & Unhappy cohort (defends ~11% of GMV).
2. **Second-order retention nudge** — triggered only after a clean first delivery, to convert the
   untapped 97% of one-time buyers.
3. **RJ / northeast logistics programme** — regional carrier support, benchmarked against SP.

---

## 5. Constraints & limitations

- **Associational, not causal** — no controlled comparison; delivery and satisfaction move together
  but confounders (category, seller) are not held constant here.
- **Coverage** — 0.7% of customers have no review and 2.9% no delivery; these are excluded per view,
  never imputed.
- **Time edges** — 2016 and late-2018 cohorts are thin and are excluded from the trend window.
- **Grain limits** — customer-level aggregates can mask order-level and item-level variance; several
  open questions above require finer grains to resolve.

---

## 6. Reproducibility

| Artifact | Path |
|---|---|
| Cleaning notebook | `data_cleaning/cleaning_customer_master_table.ipynb` |
| Cleaned dataset | `data_cleaning/cleaned_customer_level_master_table.csv` |
| Analysis notebook | `data-visualization/customer-master-analysis.ipynb` |
| Figures | embedded inline in the analysis notebook (`SAVE_FIGURES=True` to export PNGs) |

Both notebooks run top-to-bottom with no manual steps and resolve their own paths whether run from the
repo root or the notebook folder.
