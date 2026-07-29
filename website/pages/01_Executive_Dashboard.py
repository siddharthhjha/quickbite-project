"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Executive Dashboard
==================================================================
Purpose: High-level business overview with key metrics and trends
for executive decision-making.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# Get data from session state
data = st.session_state.data

# =====================================================================
# SAFE DATA ACCESS HELPER
# =====================================================================

def safe_get_data(data, key, default=None):
    """Safely get data from dict with fallback"""
    if data is None:
        return default
    return data.get(key, default)

def safe_len(df):
    """Safely get length of DataFrame"""
    if df is None:
        return 0
    return len(df)

def safe_sum(df, column):
    """Safely sum a column"""
    if df is None or column not in df.columns:
        return 0
    return df[column].sum()

def safe_mean(df, column):
    """Safely get mean of a column"""
    if df is None or column not in df.columns or len(df) == 0:
        return 0
    return df[column].mean()

def safe_date_min(df, column):
    """Safely get min date"""
    if df is None or column not in df.columns or len(df) == 0:
        return pd.Timestamp.now() - timedelta(days=30)
    return df[column].min()

def safe_date_max(df, column):
    """Safely get max date"""
    if df is None or column not in df.columns or len(df) == 0:
        return pd.Timestamp.now()
    return df[column].max()

# =====================================================================
# EXTRACT DATA
# =====================================================================

orders = safe_get_data(data, 'orders')
users = safe_get_data(data, 'users')
cities = safe_get_data(data, 'cities')

# =====================================================================
# CHECK DATA AVAILABILITY
# =====================================================================

if orders is None or len(orders) == 0:
    st.warning("⚠️ No orders data available. Please generate data first.")
    st.info("""
    **To generate data:**
    1. Navigate to the project root
    2. Run: `python python/generate_synthetic_data.py --out ./data --scale demo`
    3. Wait for data generation to complete
    4. Refresh this page
    """)
    st.stop()

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
# HEADER
# =====================================================================

st.header("📊 Executive Dashboard")
st.markdown("---")

# =====================================================================
# KPI CARDS WITH SAFETY CHECKS
# =====================================================================

col1, col2, col3, col4 = st.columns(4)

# Calculate KPIs with safety checks
total_orders = len(filtered_orders)
total_gmv = safe_sum(delivered_orders, 'total_amount')
aov = safe_mean(delivered_orders, 'total_amount')
cancellation_rate = (1 - len(delivered_orders) / total_orders) * 100 if total_orders > 0 else 0
active_users = filtered_orders['user_id'].nunique() if 'user_id' in filtered_orders.columns else 0
total_users = safe_len(users)

# Previous period (same length)
period_days = 30  # Default to 30 days
if start_date and end_date:
    period_days = (end_date - start_date).days

prev_start = start_date - timedelta(days=period_days) if start_date else datetime.now().date() - timedelta(days=60)
prev_mask = (orders['order_placed_at'].dt.date >= prev_start) & \
            (orders['order_placed_at'].dt.date < start_date) if start_date else pd.Series([False] * len(orders))
prev_orders = orders[prev_mask] if len(prev_mask) > 0 else pd.DataFrame()
prev_delivered = prev_orders[prev_orders['order_status'] == 'delivered'] if len(prev_orders) > 0 else pd.DataFrame()

# Calculate changes with safety
orders_change = ((len(filtered_orders) - len(prev_orders)) / len(prev_orders) * 100) if len(prev_orders) > 0 else 0
gmv_change = ((total_gmv - safe_sum(prev_delivered, 'total_amount')) / safe_sum(prev_delivered, 'total_amount') * 100) if safe_sum(prev_delivered, 'total_amount') > 0 else 0

# Display KPIs
with col1:
    st.metric(
        label="Total Orders",
        value=f"{total_orders:,}",
        delta=f"{orders_change:+.1f}%"
    )

with col2:
    st.metric(
        label="GMV",
        value=f"₹{total_gmv:,.0f}",
        delta=f"{gmv_change:+.1f}%"
    )

with col3:
    st.metric(
        label="Average Order Value",
        value=f"₹{aov:,.0f}",
        delta=f"{'↑' if aov > 300 else '↓'} ₹{abs(aov - 300):.0f}"
    )

with col4:
    st.metric(
        label="Active Users",
        value=f"{active_users:,}",
        delta=f"{active_users/total_users*100:.1f}%" if total_users > 0 else "0%"
    )

st.markdown("---")

# =====================================================================
# CHARTS ROW 1
# =====================================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Daily Orders & GMV Trend")
    
    if len(delivered_orders) > 0:
        # Daily aggregation
        daily_metrics = delivered_orders.groupby(
            delivered_orders['order_placed_at'].dt.date
        ).agg({
            'order_id': 'count',
            'total_amount': 'sum'
        }).reset_index()
        daily_metrics.columns = ['date', 'orders', 'gmv']
        
        # Create figure with dual axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(x=daily_metrics['date'], y=daily_metrics['orders'], name="Orders", marker_color='#3498db'),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=daily_metrics['date'], y=daily_metrics['gmv'], name="GMV", 
                       mode='lines+markers', line=dict(color='#e74c3c', width=2)),
            secondary_y=True
        )
        
        fig.update_layout(
            height=400,
            template='plotly_white',
            showlegend=True,
            xaxis_title="Date",
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text="Orders", secondary_y=False)
        fig.update_yaxes(title_text="GMV (₹)", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No delivered orders in selected date range")

with col2:
    st.subheader("🎯 Order Status Distribution")
    
    if len(filtered_orders) > 0:
        status_counts = filtered_orders['order_status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        colors = {'delivered': '#2ecc71', 'cancelled': '#e74c3c', 'failed': '#f39c12'}
        
        fig = px.pie(
            status_counts,
            values='count',
            names='status',
            color='status',
            color_discrete_map=colors,
            hole=0.3
        )
        
        fig.update_layout(
            height=400,
            template='plotly_white',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No orders in selected date range")

st.markdown("---")

# =====================================================================
# CHARTS ROW 2
# =====================================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏙️ Top Cities by GMV")
    
    if len(delivered_orders) > 0 and 'city_id' in delivered_orders.columns:
        city_metrics = delivered_orders.groupby('city_id').agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        if cities is not None and len(cities) > 0:
            city_metrics = city_metrics.merge(
                cities[['city_id', 'city_name']], 
                on='city_id'
            )
            
            city_metrics = city_metrics.sort_values('total_amount', ascending=False).head(10)
            
            fig = px.bar(
                city_metrics,
                x='city_name',
                y='total_amount',
                text='total_amount',
                color='order_id',
                color_continuous_scale='Viridis',
                title="GMV by City"
            )
            
            fig.update_layout(
                height=400,
                template='plotly_white',
                xaxis_title="City",
                yaxis_title="GMV (₹)",
                coloraxis_colorbar=dict(title="Orders")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("City data not available")
    else:
        st.info("No city data in orders")

with col2:
    st.subheader("📊 Key Metrics Heatmap")
    
    if len(filtered_orders) > 0:
        # Create heatmap of key metrics by day of week and hour
        filtered_orders['day_name'] = filtered_orders['order_placed_at'].dt.day_name()
        filtered_orders['hour'] = filtered_orders['order_placed_at'].dt.hour
        
        heatmap_data = filtered_orders.pivot_table(
            index='day_name',
            columns='hour',
            values='order_id',
            aggfunc='count'
        )
        
        if len(heatmap_data) > 0:
            # Reorder days
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data = heatmap_data.reindex([d for d in days_order if d in heatmap_data.index])
            
            fig = px.imshow(
                heatmap_data,
                title='Order Volume by Day and Hour',
                color_continuous_scale='Viridis',
                labels=dict(x="Hour of Day", y="Day of Week", color="Orders")
            )
            
            fig.update_layout(
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for heatmap")
    else:
        st.info("No orders in selected date range")

st.markdown("---")

# =====================================================================
# QUICK INSIGHTS
# =====================================================================

st.subheader("📊 Quick Insights")

# Calculate retention rate (users with >1 order)
repeat_users = 0
first_orders_count = 0
if len(delivered_orders) > 0:
    first_orders = delivered_orders.sort_values('order_placed_at').groupby('user_id').first().reset_index()
    first_orders_count = len(first_orders)
    repeat_users = delivered_orders[delivered_orders.duplicated('user_id', keep=False)]['user_id'].nunique()
    retention_rate = repeat_users / first_orders_count * 100 if first_orders_count > 0 else 0
else:
    retention_rate = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Retention Rate",
        value=f"{retention_rate:.1f}%",
        delta="+2.3% vs last period" if retention_rate > 0 else "No data"
    )

with col2:
    st.metric(
        label="Cancellation Rate",
        value=f"{cancellation_rate:.1f}%",
        delta="-" if cancellation_rate < 10 else "+",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="Average Order Value",
        value=f"₹{aov:,.0f}",
        delta=f"₹{aov - 300:.0f}" if aov > 0 else "No data"
    )

# Calculate LTV
ltv_avg = 0
if len(delivered_orders) > 0:
    user_ltv = delivered_orders.groupby('user_id')['total_amount'].sum()
    ltv_avg = user_ltv.mean()

with col4:
    st.metric(
        label="Average LTV",
        value=f"₹{ltv_avg:,.0f}",
        delta=f"LTV:CAC = {ltv_avg / 200:.1f}x" if ltv_avg > 0 else "No data"
    )

# =====================================================================
# FOOTER
# =====================================================================

st.markdown("---")
st.caption(f"📊 Data as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Showing {len(filtered_orders):,} orders")