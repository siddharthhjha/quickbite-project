# QuickBite Experimentation Design

Seven realistic A/B tests, each with hypothesis, metrics, sample size, and decision framework. This is the section that most differentiates a Product Analyst from a report-writer — the same statistical framework applies to all seven, only the specifics change.

---

### 1. Free Delivery Threshold
- **Hypothesis:** Lowering the free-delivery threshold from ₹299 to ₹199 increases order conversion enough to offset the delivery-fee revenue lost.
- **Primary metric:** Checkout conversion rate.
- **Guardrails:** AOV (shouldn't collapse as users no longer need to add items to hit the threshold), delivery-fee revenue per session, cancellation rate.
- **Sample size:** To detect a 2 percentage-point lift on a ~28% baseline conversion rate at 80% power, α=0.05 (two-sided): ~4,300 users per arm (using a two-proportion z-test power calculation).
- **Test:** Two-proportion z-test on conversion; Welch's t-test on AOV.
- **Decision framework:** Ship if conversion lift is significant AND AOV drop doesn't exceed the point where GMV is net-negative; hold if guardrails breach; kill if conversion is flat.

### 2. Recommendation Algorithm (collaborative filtering vs. popularity-based)
- **Hypothesis:** A collaborative-filtering "restaurants for you" rail increases orders-per-session vs. the current popularity-ranked rail.
- **Primary metric:** Orders per session.
- **Guardrails:** Session length (shouldn't balloon — that's more friction, not more value), restaurant diversity (avoid over-concentrating orders on a few restaurants).
- **Sample size:** Orders-per-session is a count metric with high variance; typically needs a larger sample (~15–20K sessions/arm) — recommend a sequential/CUPED-adjusted design to reduce required sample size given pre-experiment session history as a covariate.
- **Test:** Mann-Whitney U (count data is rarely normal) or a negative-binomial regression with arm as a covariate.
- **Decision framework:** Ship only if lift holds across both new and returning users — a common failure mode is the algorithm working only for high-history users.

### 3. Coupon Size (₹75 flat vs. 20% up to ₹100)
- **Hypothesis:** Percentage-based coupons drive higher AOV (basket-building incentive) than flat coupons, at similar cost-per-redemption.
- **Primary metric:** Revenue-per-discount-rupee (incrementality-adjusted).
- **Guardrails:** Redemption rate (percentage coupons might feel less compelling and see lower uptake).
- **Sample size:** ~6,000 eligible users/arm for 80% power on a 5% AOV lift.
- **Test:** t-test on AOV; ratio-metric bootstrap for revenue-per-discount-rupee (ratio metrics need bootstrapped CIs, not a plain t-test).
- **Decision framework:** Ship the arm with higher revenue-per-discount-rupee, not higher raw AOV — a coupon that costs more than it earns back is a loss regardless of AOV lift.

### 4. Checkout UI (single-page vs. multi-step)
- **Hypothesis:** Single-page checkout reduces drop-off by removing a navigation step.
- **Primary metric:** Checkout-start → order-placed conversion.
- **Guardrails:** Payment failure rate (fewer confirmation screens could mean more mis-clicks), time-to-checkout.
- **Sample size:** ~3,000 sessions/arm for an 80%-power detection of a 3pp lift on ~65% baseline checkout completion.
- **Test:** Two-proportion z-test.
- **Decision framework:** Ship if conversion lift is significant with no payment-failure regression; if payment failures rise, investigate before shipping even with a conversion win.

### 5. Delivery Fee Structure (flat ₹30 vs. distance-based)
- **Hypothesis:** Distance-based pricing improves unit economics on long-distance orders without hurting short-distance order volume.
- **Primary metric:** Contribution margin per order.
- **Guardrails:** Order volume by distance bucket (watch for long-distance orders disappearing entirely).
- **Sample size:** Segmented by distance bucket; need power within each bucket, not just overall — recommend stratified randomization by distance_km bucket.
- **Test:** ANCOVA controlling for distance bucket.
- **Decision framework:** Ship if margin improves and long-distance order volume doesn't drop more than a pre-agreed tolerance (e.g., 10%).

### 6. Restaurant Ranking (rating-weighted vs. acceptance-rate-weighted)
- **Hypothesis:** Weighting search ranking by acceptance rate (not just rating) reduces cancellations without hurting order volume.
- **Primary metric:** Cancellation rate.
- **Guardrails:** Orders per session, restaurant-side complaints about visibility.
- **Sample size:** ~10,000 sessions/arm for detecting a 1.5pp cancellation reduction on ~9% baseline.
- **Test:** Two-proportion z-test on cancellation rate; secondary check on orders/session with t-test.
- **Decision framework:** Ship if cancellation drops significantly and order volume is non-inferior (pre-register a non-inferiority margin, e.g., -2%).

### 7. Push Notification Timing (immediate post-cart-abandon vs. 30-min delay)
- **Hypothesis:** A 30-minute delay reduces notification fatigue (lower opt-out) while still recovering abandoned carts, vs. an immediate nudge that feels naggy.
- **Primary metric:** Cart-recovery rate within 24 hours.
- **Guardrails:** Push opt-out rate, notification open rate.
- **Sample size:** ~5,000 abandoned-cart events/arm for 80% power on a 3pp recovery-rate lift.
- **Test:** Two-proportion z-test on recovery rate; monitor opt-out rate as a hard guardrail (any statistically significant increase halts the test regardless of primary metric result).
- **Decision framework:** Ship the delayed variant if recovery rate is non-inferior AND opt-out rate improves — this is a case where the guardrail, not the primary metric, is likely to be the deciding factor.

---

## General Decision Framework (applies to all tests)
1. Pre-register the hypothesis, primary metric, guardrails, and minimum detectable effect *before* looking at data.
2. Run a power analysis to set sample size / test duration — don't peek and stop early (this inflates false-positive rate, a classic experimentation pitfall).
3. Check for sample-ratio mismatch (SRM) before trusting any result — an unequal split between arms usually means an instrumentation bug, not a "control lost."
4. Primary metric significant + guardrails clean → ship.
5. Primary metric significant + guardrail regression → hold, investigate root cause.
6. Primary metric not significant → do not ship on "it felt better"; either kill or redesign with a clearer mechanism.
7. Always report the confidence interval, not just the point estimate and p-value — a lift of "+2%, 95% CI [-1%, +5%]" is a very different decision than "+2%, 95% CI [+1.5%, +2.5%]".
