# Resume & Interview Material

## Project Name
**QuickBite Product Analytics Platform** — a food-delivery product analytics case study (database design → SQL → Python → experimentation → recommendations)

## Resume Bullet Points (pick 2-3, tailor to the role)
- Designed and built a 16-table relational schema and star-schema data warehouse for a simulated food-delivery platform, modeling 100K+ users and 1M+ orders with causally-consistent synthetic data (weather, traffic, and restaurant quality driving delivery SLA and cancellations).
- Wrote 20+ production-quality SQL queries (window functions, CTEs, percentile-based SLA analysis, cohort retention) to diagnose declining repeat-purchase rate and city-level performance variance, translating findings into 8 ranked product recommendations with estimated revenue/retention impact.
- Designed 7 full A/B test specifications (hypothesis, power analysis, guardrail metrics, statistical test selection) covering pricing, ranking, and UX experiments, including a non-inferiority framework for ops-sensitive changes.
- Defined a 25-metric product analytics dictionary (DAU/WAU/MAU, LTV:CAC, repeat purchase rate, delivery SLA percentiles) mirroring the semantic-layer approach used at companies like Zomato and Uber Eats.
- Built a synthetic data generator encoding 8+ real business relationships (e.g., rain increases cancellation rate by 2x, referred users order 30%+ more than paid-acquired users) to create a dataset where the analysis has something true to discover.

## ATS Keywords
SQL, PostgreSQL, Python, pandas, numpy, scikit-learn, A/B testing, experimentation, statistical significance, power analysis, cohort analysis, retention analysis, RFM segmentation, funnel analysis, churn prediction, LTV, CAC, data warehousing, star schema, dimensional modeling, dbt, ETL, product metrics, product analytics, data storytelling, Streamlit, data visualization, hypothesis testing, window functions, CTEs, market basket analysis, time series forecasting.

## Recruiter Elevator Pitch (30 seconds)
"I built a full-stack product analytics case study simulating a food-delivery company — not just a dashboard, but the whole pipeline: a realistic relational database, a synthetic data generator where every relationship is business-logic-driven rather than random, 20+ SQL queries answering real product questions like 'why is repeat purchase declining,' and 7 fully-specified A/B tests with power analysis and guardrail metrics. It's meant to show how I'd actually operate as a Product Analyst — going from ambiguous business problem to specific, ROI-justified recommendation."

## Interview Talking Points
- **"Walk me through your schema design."** Explain the OLTP-to-warehouse split, why `fact_user_activity_daily` is pre-aggregated (query performance at scale), and why `weather`/`traffic` exist as separate dimension tables rather than columns crammed onto `orders` (exogenous variables need to be queryable independent of any single order).
- **"How did you validate your synthetic data?"** Point to the verification step — grouping by weather condition and checking cancellation rate actually moves in the expected direction, confirming the generator's causal assumptions show up in the output rather than washing out as noise.
- **"Why percentiles instead of average delivery time?"** A mean hides tail latency; P90/P99 orders are the ones that actually damage user trust and drive churn, even if the average looks healthy.
- **"How would you decide whether to ship an experiment with a significant primary metric but a borderline guardrail?"** Discuss non-inferiority margins, pre-registration, and why "guardrail breach halts the ship regardless of primary metric" is the right default posture for ops-sensitive changes (push-notification opt-out example in `experiments_design.md`).
- **"What would you do differently at 10x this scale?"** Streaming aggregation (Kafka/Flink) instead of batch for `fact_user_activity_daily`, partitioning `fact_orders` by date, and a proper dbt project with tests instead of hand-written CSVs.
