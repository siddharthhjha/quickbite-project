# QuickBite Product Analytics Platform

An end-to-end product analytics case study for a fictional food-delivery platform ("QuickBite"), built to demonstrate senior-level Product Analyst skills: database design, SQL, statistics, experimentation, and product decision-making — not just a dashboard.

## The Business Problem

QuickBite has seen declining retention, rising cancellations, slower deliveries, falling repeat purchases, and inconsistent city performance. This project builds the data foundation and analysis needed to diagnose *why*, and to make specific, ROI-justified product recommendations.

## Architecture

```
OLTP schema (Postgres)  →  synthetic data generator (Python)  →  CSVs / DB load
        │
        ├── sql/03_analytics_queries.sql   (business-question-driven SQL)
        ├── sql/02_indexes_and_star_schema.sql  (warehouse layer: facts + dims)
        └── python/                         (EDA, cohorts, RFM, churn model, A/B tests)
                        │
                        ▼
                Website / BI layer (Streamlit or Next.js — see roadmap)
```

## What's in this repo (Phase 1 — built)

| Path | Contents |
|---|---|
| `sql/01_schema.sql` | Full OLTP schema — 16 tables, PK/FK, column-level rationale |
| `sql/02_indexes_and_star_schema.sql` | Indexes + warehouse star schema (fact/dim tables), design notes on how a Zomato-scale org would actually run this pipeline |
| `sql/03_analytics_queries.sql` | 20 production-quality SQL queries spanning retention, funnels, SLA percentiles, moving averages, cohorts, LTV, experiments, support — every technique category the brief requires |
| `python/generate_synthetic_data.py` | Synthetic data generator. **Nothing is uniform-random** — rain increases cancellations, premium members spend more, referred users retain better, weekend demand spikes, etc. Verified against generated output (see below) |
| `docs/metrics_definitions.md` | Every core product metric: definition, formula, SQL + rationale |
| `docs/business_questions.md` | 80 business questions ranked Easy/Medium/Hard |
| `docs/experiments_design.md` | 7 full A/B test designs: hypothesis, sample size, guardrails, decision framework |

### Verified business logic (run yourself, or trust the output below)
```
Cancellation rate by weather:      clear 10.1%  →  heavy_rain 21.0%
Avg order value:                   non-premium ₹332  →  premium ₹413
Orders per user by channel:        push_reactivation 8.2  →  referral 16.3
```

## Quick start

```bash
# 1. Generate data (demo scale: 5K users / 60K orders, ~1 min)
python python/generate_synthetic_data.py --out ./data --scale demo

# 2. Load into Postgres
createdb quickbite
psql quickbite -f sql/01_schema.sql
psql quickbite -f sql/02_indexes_and_star_schema.sql
# \copy each table from data/*.csv

# 3. Run the analytics queries
psql quickbite -f sql/03_analytics_queries.sql
```

For portfolio/GitHub scale, rerun with `--scale full` (100K users / 1M orders / ~540 days) — same logic, bigger numbers. At that scale, generate on a machine with a few GB of RAM free and load via `\copy`, not pandas `to_sql`.

## Roadmap (Phases 2–4 — not yet built, scoped below)

This is intentionally scoped as a multi-phase build rather than a single unrealistic dump — that's also how real analytics platforms actually get built (schema first, then queries, then notebooks, then a UI on top).

**Phase 2 — Python analytics notebooks**, each as a standalone script/notebook reading the generated CSVs:
- `01_eda_and_cleaning.py`
- `02_cohort_retention.py`
- `03_rfm_segmentation.py`
- `04_funnel_analysis.py`
- `05_churn_prediction.py` (logistic regression / gradient boosting, with SHAP feature importance)
- `06_ab_testing_power_analysis.py` (implements the 7 tests in `experiments_design.md`)
- `07_market_basket_analysis.py` (association rules on `order_items`)
- `08_time_series_forecasting.py` (GMV/order forecasting with Prophet or statsmodels)
- `09_ltv_prediction.py` (BG/NBD or regression-based LTV)
- `10_anomaly_detection.py` (cancellation-rate anomaly detection)

**Phase 3 — Website** (recommend Streamlit for a portfolio-speed build, or Next.js if you want a polished public-facing app):
Pages: Executive Dashboard · SQL Explorer (run queries from `sql/03_analytics_queries.sql` live) · Cohort Analysis · Funnels · Customer Segments (RFM) · Retention · Experiments · ER Diagram · Data Dictionary · Methodology. Each page pairs a visualization with the specific business insight and recommendation it supports (see `docs/business_questions.md` for the question each page should answer).

**Phase 4 — Recommendations layer**: for each analysis, a structured card with Business Insight → Evidence → Expected Revenue Impact → Expected Retention Impact → Recommendation → Engineering Effort → Priority → Expected ROI. This is the artifact recruiters actually respond to — it shows product judgment, not just query-writing.

## Tech Stack
Postgres (OLTP + warehouse) · Python (pandas, numpy, scikit-learn, statsmodels/Prophet, scipy) · SQL (window functions, CTEs, percentiles) · Streamlit or Next.js (presentation layer only)

## Why this project, not a Kaggle dashboard
Every table, every synthetic-data relationship, and every SQL query in this repo is tied to a specific, real product question a Product Analyst at a food-delivery company would actually be asked — not a generic "top 10 products by revenue" demo. The synthetic data encodes causal business logic (weather → cancellations, premium → spend, referral → retention) so that the *analysis itself* has something true to discover, rather than fitting noise.

## Future Improvements
- Swap the synthetic generator's simple probability rules for a proper agent-based simulation (users with individual "satisfaction state" that decays with bad experiences).
- Add a real dbt project on top of the star schema with tests (uniqueness, referential integrity, freshness).
- Add a reverse-ETL step simulating pushing segments back to a CRM/marketing tool.
