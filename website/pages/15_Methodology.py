"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Methodology
==================================================================
Purpose: Comprehensive documentation of the project methodology,
design decisions, and analytical approaches.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st

st.header("📖 Methodology")
st.markdown("""
Complete documentation of the project methodology, including
design decisions, analytical approaches, and business logic.
""")

# ---------------------------------------------------------------------
# PROJECT OVERVIEW
# ---------------------------------------------------------------------

st.subheader("🎯 Project Overview")

st.markdown("""
The QuickBite Product Analytics Platform is designed to demonstrate
real-world product analytics practices used at companies like
Zomato, Uber, DoorDash, and Swiggy.

**Core Objectives:**
1. Diagnose declining retention, increasing cancellations, and slow delivery
2. Build a complete analytics foundation (schema → data → analysis → recommendations)
3. Demonstrate industry-standard SQL, Python, and product thinking
4. Provide actionable business recommendations with ROI estimates
""")

# ---------------------------------------------------------------------
# DATA DESIGN PHILOSOPHY
# ---------------------------------------------------------------------

st.subheader("🗄️ Data Design Philosophy")

st.markdown("""
**OLTP Schema Design:**
- 16 tables designed for transaction processing
- Each table has clear business purpose
- Foreign keys maintain referential integrity
- Denormalized fields for performance (weather, traffic in orders)

**Star Schema Design:**
- Facts: orders, user_activity_daily, funnel_events
- Dimensions: date, user, restaurant, delivery_partner, coupon
- Designed for analytics query performance
- Aggregated facts for common queries (DAU, retention)

**Data Generation Logic:**
- No random data - all relationships encode business logic
- Weather increases cancellations by 2x
- Premium users spend 25% more
- Referral users have 30% better retention
- Weekend demand spikes 35%
""")

# ---------------------------------------------------------------------
# ANALYTICAL APPROACHES
# ---------------------------------------------------------------------

st.subheader("📊 Analytical Approaches")

analytics = {
    'Cohort Analysis': {
        'method': 'Monthly cohort retention with heatmaps',
        'purpose': 'Identify retention patterns and seasonality',
        'output': 'Retention matrices, channel comparison'
    },
    'RFM Segmentation': {
        'method': 'Quartile-based scoring with K-means validation',
        'purpose': 'Identify high-value segments and at-risk users',
        'output': 'Segment profiles, recommendations'
    },
    'Funnel Analysis': {
        'method': 'Step-by-step conversion tracking with segmentation',
        'purpose': 'Identify drop-off points and optimization opportunities',
        'output': 'Conversion rates, abandonment reasons'
    },
    'Churn Prediction': {
        'method': 'XGBoost with SHAP feature importance',
        'purpose': 'Proactive identification of at-risk users',
        'output': 'Risk scores, intervention recommendations'
    },
    'Market Basket': {
        'method': 'Apriori algorithm with association rules',
        'purpose': 'Identify cross-selling opportunities',
        'output': 'Item associations, recommendation engine'
    },
    'LTV Prediction': {
        'method': 'Random Forest with early behavior features',
        'purpose': 'Optimize acquisition spend and retention',
        'output': 'LTV:CAC ratios, channel optimization'
    },
    'Time Series': {
        'method': 'ARIMA, Prophet, Exponential Smoothing',
        'purpose': 'Forecast orders, GMV, and detect anomalies',
        'output': 'Forecasts, anomaly detection, seasonality'
    }
}

for method, details in analytics.items():
    with st.expander(f"**{method}**"):
        st.markdown(f"**Method:** {details['method']}")
        st.markdown(f"**Purpose:** {details['purpose']}")
        st.markdown(f"**Output:** {details['output']}")

# ---------------------------------------------------------------------
# STATISTICAL METHODS
# ---------------------------------------------------------------------

st.subheader("📈 Statistical Methods")

st.markdown("""
**A/B Testing Framework:**
- Two-proportion z-test for conversion metrics
- Welch's t-test for continuous metrics (AOV, session length)
- Bootstrapping for ratio metrics (revenue per discount rupee)
- Sequential testing with pre-registered sample sizes
- Power analysis for sample size determination

**Predictive Modeling:**
- XGBoost with cross-validation for churn prediction
- Random Forest for LTV prediction
- SHAP for feature importance interpretation
- ROC curves and AUC for model evaluation

**Time Series Analysis:**
- ADF test for stationarity
- Seasonal decomposition (STL)
- Prophet for automatic seasonality detection
- ARIMA for short-term forecasting
- Exponential smoothing for trend detection
""")

# ---------------------------------------------------------------------
# BUSINESS METRICS
# ---------------------------------------------------------------------

st.subheader("📊 Core Business Metrics")

metrics = {
    'Retention': 'Users active in period / users in cohort × 100',
    'Churn Rate': 'Users with no order in 90 days / total users × 100',
    'Repeat Purchase Rate': 'Users with 2+ orders within 60 days / total first-order users × 100',
    'LTV': 'Sum of delivered order amounts per user to date',
    'CAC': 'Total channel spend / users acquired through that channel',
    'LTV:CAC Ratio': 'LTV / CAC (>3:1 is healthy)',
    'GMV': 'Sum of all delivered order totals',
    'AOV': 'GMV / number of delivered orders',
    'Conversion Rate': 'Orders / sessions with a restaurant view × 100',
    'Cancellation Rate': 'Cancelled orders / total orders × 100',
    'Delivery SLA': 'P50, P90, P99 delivery times',
    'Stickiness': 'DAU / MAU × 100'
}

for metric, formula in metrics.items():
    st.markdown(f"**{metric}**: `{formula}`")

# ---------------------------------------------------------------------
# DECISION FRAMEWORK
# ---------------------------------------------------------------------

st.subheader("🎯 Decision Framework")

st.markdown("""
**Experiment Decision Framework:**
1. Pre-register hypothesis, metrics, and sample size
2. Run experiment to completion (no early peeking)
3. Check sample-ratio mismatch (SRM)
4. Primary metric significant + guardrails clean → **SHIP**
5. Primary metric significant + guardrail breach → **HOLD**
6. Primary metric not significant → **KILL**

**Recommendation Prioritization:**
- **P0**: Immediate action (within 30 days)
- **P1**: Short-term (within 90 days)
- **P2**: Long-term (within 6 months)

**ROI Classification:**
- **High**: Revenue impact > effort
- **Medium**: Revenue impact ≈ effort
- **Low**: Revenue impact < effort
""")

# ---------------------------------------------------------------------
# TECHNOLOGY STACK
# ---------------------------------------------------------------------

st.subheader("🛠️ Technology Stack")

st.markdown("""
**Database:**
- PostgreSQL (OLTP)
- Star schema (Data Warehouse)

**Data Generation:**
- Python (pandas, numpy)
- Business-logic-driven relationships

**Analytics:**
- Python (pandas, numpy, scikit-learn, statsmodels)
- SQL (window functions, CTEs, percentiles)
- ML (XGBoost, Random Forest, SHAP)

**Visualization:**
- Streamlit (frontend)
- Plotly (interactive charts)
- Matplotlib/Seaborn (static charts)

**Experimentation:**
- Scipy (statistical tests)
- Bootstrap resampling
- Power analysis
""")

st.caption("📖 Methodology documentation v2.0")