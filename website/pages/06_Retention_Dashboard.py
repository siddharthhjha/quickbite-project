"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Retention Dashboard
==================================================================
Purpose: Comprehensive retention metrics and trends dashboard.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Get data from session state
data = st.session_state.data

# Extract data with safety checks
orders = data.get('orders') if data else None
users = data.get('users') if data else None

# Check if data exists
if orders is None or len(orders) == 0:
    st.warning("⚠️ No orders data available. Please generate data first.")
    st.stop()

st.header("🔄 Retention Dashboard")
st.markdown("""
Monitor retention metrics across time and segments.
Track user engagement and identify retention opportunities.
""")

# Filter by date
start_date = st.session_state.start_date
end_date = st.session_state.end_date

# Ensure order_placed_at is datetime
if not pd.api.types.is_datetime64_any_dtype(orders['order_placed_at']):
    orders['order_placed_at'] = pd.to_datetime(orders['order_placed_at'])

# Apply date filter
filtered_orders = orders.copy()
if start_date and end_date:
    mask = (filtered_orders['order_placed_at'].dt.date >= start_date) & \
           (filtered_orders['order_placed_at'].dt.date <= end_date)
    filtered_orders = filtered_orders[mask]

# Get delivered orders
delivered_orders = filtered_orders[filtered_orders['order_status'] == 'delivered']

# =====================================================================
# RETENTION METRICS
# =====================================================================

@st.cache_data
def calculate_retention_metrics(orders_df):
    """Calculate key retention metrics"""
    
    if len(orders_df) == 0:
        return {}
    
    # Get first and last orders
    first_orders = orders_df.sort_values('order_placed_at').groupby('user_id').first().reset_index()
    last_orders = orders_df.groupby('user_id')['order_placed_at'].max().reset_index()
    
    metrics = {}
    
    # Overall retention (users with any order)
    metrics['total_users'] = len(first_orders)
    metrics['active_users'] = len(last_orders)
    
    # 30, 60, 90 day retention
    cutoff_30 = datetime.now() - timedelta(days=30)
    cutoff_60 = datetime.now() - timedelta(days=60)
    cutoff_90 = datetime.now() - timedelta(days=90)
    
    metrics['retention_30d'] = len(last_orders[last_orders['order_placed_at'] >= cutoff_30]) / metrics['total_users'] * 100
    metrics['retention_60d'] = len(last_orders[last_orders['order_placed_at'] >= cutoff_60]) / metrics['total_users'] * 100
    metrics['retention_90d'] = len(last_orders[last_orders['order_placed_at'] >= cutoff_90]) / metrics['total_users'] * 100
    
    # Repeat purchase rate
    repeat_users = len(orders_df[orders_df.duplicated('user_id', keep=False)]['user_id'].unique())
    metrics['repeat_rate'] = repeat_users / metrics['total_users'] * 100
    
    # Churn rate
    churned_users = len(last_orders[last_orders['order_placed_at'] < cutoff_90])
    metrics['churn_rate'] = churned_users / metrics['total_users'] * 100
    
    return metrics

retention_metrics = calculate_retention_metrics(delivered_orders)

# =====================================================================
# KPI CARDS
# =====================================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Users",
        value=f"{retention_metrics.get('total_users', 0):,}"
    )

with col2:
    st.metric(
        label="30-Day Retention",
        value=f"{retention_metrics.get('retention_30d', 0):.1f}%",
        delta="Last 30 days"
    )

with col3:
    st.metric(
        label="90-Day Retention",
        value=f"{retention_metrics.get('retention_90d', 0):.1f}%",
        delta="Last 90 days"
    )

with col4:
    st.metric(
        label="Repeat Rate",
        value=f"{retention_metrics.get('repeat_rate', 0):.1f}%",
        delta="2+ orders"
    )

with col5:
    st.metric(
        label="Churn Rate",
        value=f"{retention_metrics.get('churn_rate', 0):.1f}%",
        delta="No order in 90 days",
        delta_color="inverse"
    )

st.markdown("---")

# =====================================================================
# KEY INSIGHTS
# =====================================================================

with st.expander("💡 Key Insights & Recommendations"):
    st.markdown(f"""
    **🔍 Key Findings:**
    
    1. **Retention Health:**
       - 30-Day Retention: {retention_metrics.get('retention_30d', 0):.1f}%
       - 90-Day Retention: {retention_metrics.get('retention_90d', 0):.1f}%
       - Repeat Rate: {retention_metrics.get('repeat_rate', 0):.1f}%
       - Overall Churn: {retention_metrics.get('churn_rate', 0):.1f}%
    
    2. **Key Insights:**
       - First 30 days are critical for retention
       - Repeat customers drive majority of revenue
       - Churn risk increases after 90 days of inactivity
    
    **🎯 Recommendations:**
    
    1. **Improve Retention:**
       - Focus on first 30 days (highest drop-off)
       - Implement early engagement campaigns
       - Optimize onboarding for new users
    
    2. **Reduce Churn:**
       - Win-back campaigns for at-risk users
       - Improve delivery experience
       - Address payment friction
    """)

st.caption(f"📊 Retention dashboard based on {len(delivered_orders):,} orders")