# QuickBite Metrics Dictionary

Every metric below has: definition, formula, why it matters, and how to compute it in SQL and Python (pandas). This is the semantic-layer equivalent of what a real analytics org keeps in dbt metrics / LookML — one definition, used everywhere, so "retention" means the same thing on every dashboard.

## Engagement

**DAU / WAU / MAU**
- Definition: distinct users with at least one session in the trailing 1 / 7 / 30 days.
- SQL: `COUNT(DISTINCT user_id) FROM sessions WHERE session_start::date = :date` (adjust window for WAU/MAU).
- Python: `sessions.groupby(sessions.session_start.dt.date)['user_id'].nunique()`
- Why it matters: the top-line engagement pulse; used to detect product-market fit erosion before revenue drops.

**Stickiness (DAU/MAU ratio)**
- Formula: `DAU / MAU`
- Why: measures habit formation. Food delivery benchmarks are typically 15–25%; below that signals the app isn't a daily habit (expected — it's not supposed to be).

**Session Length**
- Formula: `AVG(session_end - session_start)`
- Why: proxy for browsing depth / decision friction; unusually long sessions can mean either high engagement or a confusing search experience — pair with conversion rate to disambiguate.

## Retention

**N-Day / N-Week Retention**
- Definition: % of a signup cohort that returns to order again within a given window.
- Formula: `users active in period N / users in cohort at period 0`
- SQL/Python: see `sql/03_analytics_queries.sql` Section A and `python/02_cohort_retention.py`.

**Repeat Purchase Rate**
- Formula: `users with 2+ orders within 60 days of first order / users with a first order`
- Why: the single best early indicator of whether a user found habitual value — more actionable than 90-day retention because it's observable within 2 months of a cohort's birth.

**Churn Rate**
- Formula: `users with no order in trailing 90 days / total active user base`
- Why: the inverse framing of retention, used for win-back targeting.

## Monetization

**GMV (Gross Merchandise Value)**
- Formula: `SUM(total_amount) WHERE order_status = 'delivered'`
- Why: top-line transaction volume; the number the board sees first.

**AOV (Average Order Value)**
- Formula: `GMV / delivered_orders`
- Why: AOV growth vs. order-count growth tells you whether growth is coming from basket size (upsell/premium mix) or frequency (retention/acquisition).

**LTV (Lifetime Value)**
- Formula (historical): `SUM(total_amount) per user to date`
- Formula (predictive): `AOV × purchase_frequency × projected_lifespan`, or a trained regression/BG-NBD model (see `python/09_ltv_prediction.py`)
- Why: the number LTV:CAC is built from — the single most important unit-economics ratio in the business.

**CAC (Customer Acquisition Cost)**
- Formula: `total spend on a channel / new users acquired via that channel`
- Why: paired with LTV, tells you which channels are actually profitable, not just cheap-looking on a CPM basis.

**LTV:CAC Ratio**
- Rule of thumb: > 3:1 is healthy, < 1:1 means the business loses money on every user acquired through that channel.

## Conversion & Funnel

**Conversion Rate**
- Formula: `orders placed / sessions with a restaurant view`
- SQL: see Section B, query B1.

**Cart Abandonment Rate**
- Formula: `1 - (orders completed / carts started)`
- Why: distinguishes "we can't get people interested" (top-of-funnel problem) from "we lose people at checkout" (friction/trust problem) — very different fixes.

**Cancellation Rate**
- Formula: `cancelled orders / total orders`
- Segment by: `cancelled_by` (user / restaurant / system) — each has a different root cause and owner.

## Operations

**Delivery SLA (P50/P90/P99 delivery time)**
- Why percentiles, not averages: a mean can look fine while 10% of orders take 90+ minutes and quietly drive churn. P90/P99 expose the tail that actually damages trust.

**Restaurant Acceptance Rate**
- Formula: `orders accepted / orders sent to restaurant`
- Why: a restaurant with low acceptance rate creates cancellations regardless of anything the platform does — a supply-quality metric, not a demand metric.

## Marketing / Promotions

**Coupon Redemption Rate**
- Formula: `orders with coupon applied / orders eligible for that coupon`

**Coupon ROI**
- Formula: `incremental GMV attributable to coupon / discount cost`
- Why: many coupons look "successful" (high redemption) while being unprofitable (redeemed mostly by users who would have ordered anyway) — this is the classic incrementality trap, see experiments design doc.

## Satisfaction

**NPS (Net Promoter Score)**
- Formula: `% Promoters (9–10) − % Detractors (0–6)`, from a post-delivery survey field.

**CSAT (Support)**
- Formula: `AVG(satisfaction_score)` from `support_tickets`, 1–5 scale.

## Feature Adoption

**Feature Adoption Rate**
- Formula: `users who used feature X in period / active users in period`
- Applied to: premium membership uptake, coupon usage, scheduled-order usage, etc.
