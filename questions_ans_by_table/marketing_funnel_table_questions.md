# Questions Answered by `cleaned_marketing_funnel_master_table.csv`

This table has one row per marketing-qualified lead (8,000 leads), tracking the acquisition funnel
from first contact through to becoming a seller. A lead is **converted**
(`is_converted_flag = True`) if it has a matching closed deal. It's the right table for any
question about **how sellers are acquired** — as opposed to the seller table, which describes
sellers once they're already on the platform.

Source: `data-visualization/cleaned_marketing_funnel_master_table.csv`
Cleaning notebook: `data_cleaning/clean_marketing_funnel_table.ipynb`
EDA notebook: `EDA/marketing-funnel-analysis.ipynb`

---

## 1. What is the overall conversion rate, and is it just a "too early to convert" artifact?

Overall conversion is **~10.5%** (842 of 8,000 leads become sellers). Converted and unconverted
leads have near-identical age distributions — every lead in this extract is already 3,000+ days
old — so the low conversion rate is not because leads haven't had time to convert yet; the ~90%
that don't convert are genuinely lost.

**Takeaway:** conversion improvement has to come from funnel quality (better-qualified leads,
better follow-up), not from waiting longer — there's no "still warming up" cohort hiding in the data.

---

## 2. Which acquisition channels bring in the most leads, and which actually convert best?

Volume and conversion quality tell different stories. `organic_search` and `paid_search` bring in
the most leads by far. But the channel with the *best conversion rate* is `unknown` (untracked
referral sources), followed by `paid_search`. Channels with real volume but weak conversion —
`social` and `email` — underperform the platform average despite each having 300+ leads (not a
small-sample fluke).

**Takeaway:** channel volume and channel quality are not the same thing. `social` and `email` are
candidates for either better lead qualification before follow-up or a different outreach approach,
since throwing more volume at them without fixing conversion won't move the needle proportionally.

---

## 3. What kind of sellers does the funnel actually produce?

Converted leads skew heavily toward **`reseller`** business type — roughly **2:1** over
`manufacturer` — and the largest single `lead_type` segment is **`online_medium`**.

**Takeaway:** this matches the marketplace's stated role as a platform connecting small/medium
resellers rather than large brands. This is a structural fact about who the funnel serves, not a
targeting failure — useful context whenever seller performance is broken down by these same
categories (e.g., in the seller-level analysis).

---

## 4. How long does it take to close a lead once it's qualified?

Median time-to-win is about **two weeks**, but the distribution is right-skewed with a long tail
past 100+ days — a small group of leads take far longer than the rest to close.

**Takeaway:** most leads close reasonably quickly, but the long-tail "stuck" leads matter for
sales-capacity planning — they occupy SDR/SR attention disproportionately relative to their small
number, and tracking them separately (rather than blending them into an average) would give
sales-ops a clearer signal.

---

## 5. Can the converted-lead numeric fields (declared revenue, catalog size) tell us anything reliable?

Only with heavy caveats. `declared_monthly_revenue` and `declared_product_catalog_size` were found
to be **0 for ~95% of converted deals** during cleaning — a pattern uniform across every lead type,
which is the signature of an unanswered survey field defaulting to 0, not a real declaration. These
were recoded to `NaN` with explicit `has_declared_revenue` / `has_declared_catalog_size` flags. Only
**45 of 842 converted deals (5.3%)** carry a usable, non-placeholder revenue figure.

**Takeaway:** any revenue-based segment comparison using these fields is illustrative at best, given
the tiny surviving sample — this is a genuine data-quality gap in the source, not something that can
be fixed by better analysis technique.

---

## 6. Are there any data-entry problems worth flagging?

Yes, a small one: **one converted deal** shows a negative `time_to_win_days` (recorded as won two
days *before* first contact), almost certainly an upstream data-entry error. It's flagged via
`time_to_win_valid_flag` and excluded from time-to-win statistics rather than silently kept in or
dropped from the table entirely.

**Takeaway:** the funnel data is otherwise clean, with only one clear anomaly out of 842 converted
records — worth noting in the technical report as an example of data validation during cleaning,
but not something that materially affects the conversion or timing findings above.

---

## Data caveat to flag in the report

Deal-side fields (`business_segment`, `lead_type`, `business_type`, `sdr_id`, `sr_id`, `won_date`,
etc.) are populated **only** for converted leads by construction of the join — a missing value
there means "this lead never converted," not "data is dirty." This is confirmed exactly: every
deal-side column is `NaN` precisely when `is_converted_flag` is `False`, with no mismatches. Any
analysis using these fields should be read as describing the composition of *won* deals, not a
comparison against lost leads.
