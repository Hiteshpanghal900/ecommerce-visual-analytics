# Questions Answered by `cleaned_category_level_master_table.csv`

This table has one row per product category (73 categories), built by joining order items to
products and translating category names to English, then rolling up to sales volume, seller count,
and the same satisfaction/delivery metrics used at the order/seller/customer grain. It's the right
table for any question about **which product categories drive revenue or satisfaction risk** — a
dimension none of the other cleaned tables carry, since category information is lost when orders are
aggregated to the order level.

Source: `data-visualization/cleaned_category_level_master_table.csv`
Cleaning notebook: `data_cleaning/clean_category_master_table.ipynb`

---

## 1. How many product categories are there, and is revenue concentrated among a few of them?

There are **73 categories**, and revenue is heavily concentrated: the **top 10 categories generate
~63.2%** of total sales value, and the top 20% of categories (14 categories) account for **~75.3%**.
The single largest category, **health_beauty**, alone brings in **R$1,258,681** across 492 sellers
and 8,836 orders.

**Takeaway:** like the seller base, the category mix is a long-tail story — a handful of categories
(health & beauty, watches & gifts, bed/bath/table, sports & leisure, computer accessories) drive the
majority of marketplace GMV, so category-level investment (search placement, promotions, seller
recruitment) should weight these top categories disproportionately.

---

## 2. Do bigger, higher-revenue categories have better or worse satisfaction?

Essentially no relationship: the correlation between a category's total sales value and its average
review score is **~0.01** — effectively zero. Some of the biggest categories by revenue
(`bed_bath_table` at 3.92, `furniture_decor` at 3.95) sit below the overall average, while some much
smaller categories (`books_general_interest`, `books_imported`) have among the best scores.

**Takeaway:** category size and category satisfaction are independent problems — a large category
isn't automatically "safe" just because it's popular, and a small category isn't automatically
low-risk just because it's low-volume. Each needs to be checked on its own terms.

---

## 3. Which categories have the worst average review scores?

Among categories with a reasonable review volume (20+ reviews), the lowest-scoring are
**office_furniture** (3.51, but with a large 1,654 reviews and R$273,961 in sales — a real,
high-volume risk), **fixed_telephony** (3.76), **fashion_male_clothing** (3.76), **audio** (3.84),
and **home_confort** (3.85).

**Takeaway:** `office_furniture` stands out as the most important one to act on — it's not a small
or obscure category, it does real volume, and its review score is meaningfully below the
marketplace's overall weighted average of **~4.08**.

---

## 4. Which categories have the best average review scores?

Also among categories with 20+ reviews: **books_general_interest** (4.51), **books_imported**
(4.51), **costruction_tools_tools** (4.44), **small_appliances_home_oven_and_coffee** (4.44), and
**flowers** (4.42). Books categories in particular stand out as consistently high-scoring.

**Takeaway:** these categories could be used as a benchmark for "what good looks like" when
diagnosing why lower-scoring categories underperform — e.g. comparing typical delivery times or
seller practices in `books_general_interest` against `office_furniture`.

---

## 5. Does late delivery hurt satisfaction at the category level too?

Only weakly at the category-aggregate level: the correlation between a category's late-delivery
rate and its average review score is **~-0.05** — much weaker than the seller-level (-0.42) or
order-level correlations. The categories with the *highest* late-delivery rates
(`home_comfort_2` at 14.8%, `furniture_mattress_and_upholstery` at 13.5%, `audio` at 11.5%) do tend
to also have below-average review scores, but the relationship is noisy once averaged across an
entire category.

**Takeaway:** this doesn't contradict the strong order/seller-level delivery-satisfaction link — it
shows that at the category grain, other factors (product type, price point, seller mix within the
category) dilute the signal. Delivery reliability is still the right lever, but it should be
diagnosed at the seller or order level within a category, not from the category-level correlation
alone.

---

## 6. How much of the category data is trustworthy (any missing or fabricated values)?

All 73 categories have complete `has_reviews` and `has_delivery_data` coverage (no category-level
gaps) — this is thanks to the cleaning step, which dropped only the 610 products (1.9% of the raw
product catalog) with no category at all, so the 73 categories that remain are fully populated with
real (not imputed) satisfaction and delivery metrics.

**Takeaway:** the category-level numbers in this table can be used directly and confidently — unlike
some other tables in this project, there's no fake-zero or 100%-flat-flag data-quality issue hiding
in this one.

---

## Data caveat to flag in the report

Two categories (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`) have no official
English translation in the source data and are kept under their original Portuguese name rather
than dropped, so they appear differently formatted from the other 71 categories in any category-name
chart or table. This is a labeling quirk only — the underlying metrics for these two categories are
just as complete and reliable as any other category's.
