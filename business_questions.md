# QuickBite Business Questions Bank (80)

Ranked by difficulty. "Easy" = single table, basic aggregation. "Medium" = multi-table joins, window functions, or segmentation. "Hard" = requires statistical reasoning, causal thinking, or multi-step analysis (often Python, not just SQL).

## Retention & Churn

| # | Question | Difficulty |
|---|---|---|
| 1 | What is the overall 30-day retention rate? | Easy |
| 2 | Which signup cohort (by month) has the best 90-day retention? | Medium |
| 3 | Why are repeat purchases declining quarter over quarter? | Hard |
| 4 | Which city has the worst retention, and is it a supply or demand problem? | Hard |
| 5 | Do premium members retain better than free users — and is that causal or selection bias? | Hard |
| 6 | What's the churn rate by acquisition channel? | Easy |
| 7 | Do referred users have measurably better LTV than paid-acquired users? | Medium |
| 8 | Is churn concentrated in a specific age band or device type? | Medium |
| 9 | Does a bad delivery experience (late/cancelled) in a user's first order predict churn? | Hard |
| 10 | What's the "resurrection rate" — churned users who return after a win-back push? | Medium |
| 11 | Are premium members churning at a higher rate recently, and why? | Hard |
| 12 | Which restaurant categories have customers with the highest repeat rate? | Medium |
| 13 | Does opening a support ticket predict a user won't order again? | Hard |
| 14 | What's the relationship between session frequency in week 1 and 90-day retention? | Hard |

## Delivery Operations

| # | Question | Difficulty |
|---|---|---|
| 15 | What is the average delivery time platform-wide? | Easy |
| 16 | Which city has the slowest P90 delivery time? | Medium |
| 17 | Is delivery time trending up or down over the last 6 months? | Medium |
| 18 | How much of the cancellation rate is explained by weather vs traffic vs restaurant acceptance? | Hard |
| 19 | Do longer delivery times causally reduce repeat orders, or do slow restaurants also happen to be lower quality? | Hard |
| 20 | Which delivery partner shift type (full-time vs part-time) delivers faster? | Medium |
| 21 | What's the marginal effect of 1 additional traffic-index point on delivery time? | Hard |
| 22 | Are cancellations more likely to be restaurant-caused or system-caused during dinner rush? | Medium |
| 23 | Which restaurants have acceptance rates low enough to warrant deprioritizing in search? | Medium |
| 24 | Does rain increase cancellations more in Tier 1 or Tier 3 cities? | Hard |
| 25 | What % of delivery delay is prep-time vs. actual transit time? | Medium |
| 26 | Is there a delivery partner supply shortage at specific hours in specific cities? | Hard |
| 27 | What's the relationship between distance_km and delivery time — linear or does it break down at long distances? | Hard |

## Funnel & Conversion

| # | Question | Difficulty |
|---|---|---|
| 28 | What is the overall checkout conversion rate? | Easy |
| 29 | Where in the funnel (view → cart → checkout → payment → order) is the biggest drop-off? | Medium |
| 30 | Why are users abandoning checkout — payment failure, delivery fee shock, or indecision? | Hard |
| 31 | Does cart abandonment vary by hour of day? | Medium |
| 32 | Do first-time users convert at a different rate than returning users? | Easy |
| 33 | What's the impact of showing estimated delivery time on conversion? | Hard |
| 34 | Which payment method has the highest failure rate? | Easy |
| 35 | Is COD associated with a higher cancellation rate than prepaid methods? | Medium |
| 36 | Does search-result position affect restaurant click-through and order rate? | Hard |

## Monetization / Revenue

| # | Question | Difficulty |
|---|---|---|
| 37 | What is total GMV this month vs last month? | Easy |
| 38 | What is the AOV by city? | Easy |
| 39 | Is GMV growth coming from more orders or higher AOV? | Medium |
| 40 | Do premium members spend more per order, and is the subscription fee worth it net of that lift? | Medium |
| 41 | What's the LTV:CAC ratio by acquisition channel? | Hard |
| 42 | Which cuisines maximize repeat purchases and should get more search real estate? | Medium |
| 43 | What's the revenue concentration — what % of GMV comes from top 10% of users? | Medium |
| 44 | Is delivery-fee revenue cannibalizing order volume (price elasticity)? | Hard |
| 45 | What's the expected revenue impact of reducing delivery fee by ₹10 platform-wide? | Hard |

## Coupons & Promotions

| # | Question | Difficulty |
|---|---|---|
| 46 | What's the coupon redemption rate by coupon type? | Easy |
| 47 | Do coupons improve first-order conversion? | Medium |
| 48 | Do users who used a welcome coupon retain better than those who didn't? | Hard |
| 49 | What's the incremental GMV from coupons vs. GMV that would've happened anyway? | Hard |
| 50 | Which coupon has the best revenue-per-discount-rupee? | Medium |
| 51 | Is the win-back coupon (COMEBACK100) actually reactivating churned users at a profitable rate? | Hard |

## Cities & Market Health

| # | Question | Difficulty |
|---|---|---|
| 52 | Which city has grown the fastest in the last quarter? | Easy |
| 53 | Which cities are declining, and is it a supply, demand, or ops problem? | Hard |
| 54 | Is Tier 3 city growth sustainable, or is it discount-subsidized? | Hard |
| 55 | Which city has the best restaurant supply density relative to user demand? | Medium |
| 56 | Should QuickBite launch in 3 more Tier 3 cities based on current unit economics? | Hard |

## Engagement / Product Usage

| # | Question | Difficulty |
|---|---|---|
| 57 | What is DAU/WAU/MAU trending over the last 90 days? | Easy |
| 58 | What is the platform's stickiness ratio (DAU/MAU)? | Easy |
| 59 | Does iOS or Android have deeper engagement (session length, orders/session)? | Medium |
| 60 | What's the average session length, and has it changed after the last app redesign? | Medium |
| 61 | Which entry_source (push, deep link, organic) drives the most valuable sessions? | Medium |

## Support / CX

| # | Question | Difficulty |
|---|---|---|
| 62 | What's the most frequent support issue category? | Easy |
| 63 | Which issue category has the worst resolution time? | Easy |
| 64 | Is CSAT correlated with resolution time or resolution type (refund vs. apology credit)? | Medium |
| 65 | What % of users with a support ticket order again within 90 days vs. users without? | Hard |
| 66 | Are support tickets concentrated around specific restaurants (quality control signal)? | Medium |

## Experimentation

| # | Question | Difficulty |
|---|---|---|
| 67 | Did the free-delivery-threshold experiment increase conversion without hurting AOV? | Hard |
| 68 | What sample size is needed to detect a 2% lift in conversion rate at 80% power? | Hard |
| 69 | Did the new recommendation algorithm increase orders-per-session? | Hard |
| 70 | Is the checkout UI experiment result statistically significant or noise? | Hard |
| 71 | Are experiment guardrail metrics (cancellation rate, refund rate) holding steady under treatment? | Medium |
| 72 | Should we ship the push-notification-timing experiment given mixed primary/guardrail results? | Hard |

## Segmentation & Personalization

| # | Question | Difficulty |
|---|---|---|
| 73 | What are the natural user segments via RFM analysis? | Hard |
| 74 | Which segment should get a win-back campaign vs. an upsell campaign? | Medium |
| 75 | Do "Champions" (RFM) users show early warning signs before they churn? | Hard |
| 76 | What items are frequently bought together (market basket), and should we bundle them? | Hard |
| 77 | Can we predict which new users will become repeat purchasers within their first 3 orders? | Hard |

## Forecasting / Anomaly Detection

| # | Question | Difficulty |
|---|---|---|
| 78 | What's the GMV forecast for next quarter given current trend and seasonality? | Hard |
| 79 | Was last week's cancellation spike an anomaly or a new normal? | Hard |
| 80 | Can we forecast delivery-partner supply needs by city/hour to avoid shortages? | Hard |

**Distribution:** 18 Easy / 26 Medium / 36 Hard — intentionally skewed hard, because a portfolio project that only answers easy questions doesn't demonstrate senior-analyst judgment.
