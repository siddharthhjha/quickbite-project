"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Cohort Analysis
==================================================================
Purpose: Analyze user retention through cohort analysis with
interactive heatmaps and retention curves.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Get data from session state
data = st.session_state.data
orders = data['orders']
users = data['users']
delivered_orders = orders[orders['order_status'] == 'delivered']

# Filter by date
start_date = st.session_state.start_date
end_date = st.session_state.end_date
mask = (delivered_orders['order_placed_at'].dt.date >= start_date) & \
       (delivered_orders['order_placed_at'].dt.date <= end_date)
filtered_orders = delivered_orders[mask]

st.header("📈 Cohort Retention Analysis")
st.markdown("""
Analyze how different user cohorts retain over time. 
Cohorts are defined by signup month, and retention is measured by 
the percentage of users who continue to order in subsequent months.
""")

# ---------------------------------------------------------------------
# COHORT CALCULATION
# ---------------------------------------------------------------------

@st.cache_data
def calculate_cohort_retention(orders_df, users_df):
    """Calculate cohort retention matrix"""
    
    # Get first order for each user
    first_orders = orders_df.sort_values('order_placed_at').groupby('user_id').first().reset_index()
    first_orders['cohort_month'] = first_orders['order_placed_at'].dt.to_period('M')
    
    # Merge with user signup month for comparison
    users_df['signup_month'] = users_df['signup_date'].dt.to_period('M')
    first_orders = first_orders.merge(
        users_df[['user_id', 'signup_month']], 
        on='user_id', 
        how='left'
    )
    
    # Use signup month as cohort
    first_orders['cohort'] = first_orders['signup_month']
    
    # Create activity data
    orders_df['order_month'] = orders_df['order_placed_at'].dt.to_period('M')
    activity = orders_df.groupby(['user_id', 'order_month']).size().reset_index(name='orders')
    
    # Merge with cohort info
    activity = activity.merge(
        first_orders[['user_id', 'cohort']], 
        on='user_id', 
        how='inner'
    )
    
    # Calculate cohort size
    cohort_size = first_orders.groupby('cohort').size().reset_index(name='cohort_size')
    
    # Calculate retention
    retention_data = []
    
    for cohort in activity['cohort'].unique():
        cohort_users = first_orders[first_orders['cohort'] == cohort]['user_id'].unique()
        total_users = len(cohort_users)
        
        # Get all months
        cohort_activity = activity[activity['cohort'] == cohort]
        
        # Find period numbers
        all_months = sorted(activity['order_month'].unique())
        cohort_idx = all_months.index(cohort) if cohort in all_months else -1
        
        if cohort_idx != -1:
            for period_idx, month in enumerate(all_months[cohort_idx:], 0):
                active_users = cohort_activity[cohort_activity['order_month'] == month]['user_id'].nunique()
                retention_rate = active_users / total_users if total_users > 0 else 0
                
                retention_data.append({
                    'cohort': str(cohort),
                    'period': period_idx,
                    'active_users': active_users,
                    'total_users': total_users,
                    'retention_rate': retention_rate
                })
    
    retention_df = pd.DataFrame(retention_data)
    
    # Pivot to matrix
    retention_matrix = retention_df.pivot_table(
        index='cohort',
        columns='period',
        values='retention_rate'
    )
    
    # Add cohort size
    size_map = cohort_size.set_index('cohort')['cohort_size']
    retention_matrix['cohort_size'] = retention_matrix.index.map(size_map)
    
    return retention_matrix, retention_df

# Calculate cohort data
with st.spinner("Calculating cohort retention..."):
    retention_matrix, retention_df = calculate_cohort_retention(
        filtered_orders, 
        users
    )

# ---------------------------------------------------------------------
# COHORT HEATMAP
# ---------------------------------------------------------------------

st.subheader("🔥 Cohort Retention Heatmap")

# Prepare heatmap data
heatmap_data = retention_matrix.drop('cohort_size', axis=1).copy()
heatmap_data = heatmap_data * 100  # Convert to percentage

# Get recent cohorts (last 12 months for readability)
recent_cohorts = heatmap_data.index[-min(12, len(heatmap_data)):]
heatmap_data = heatmap_data.loc[recent_cohorts]

# Create heatmap
fig = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns.astype(str),
    y=heatmap_data.index,
    colorscale='RdYlGn',
    zmin=0,
    zmax=100,
    text=heatmap_data.values.round(1).astype(str) + '%',
    texttemplate='%{text}',
    textfont={"size": 10},
    hoverongaps=False,
    colorbar=dict(title="Retention Rate (%)")
))

fig.update_layout(
    height=500,
    title="Monthly Cohort Retention",
    xaxis_title="Months Since Signup",
    yaxis_title="Cohort (Signup Month)",
    template='plotly_white'
)

st.plotly_chart(fig, use_container_width=True)

# Show cohort sizes
st.caption(f"📊 Showing {len(heatmap_data)} cohorts | Data includes {len(filtered_orders):,} orders")

# ---------------------------------------------------------------------
# RETENTION CURVES
# ---------------------------------------------------------------------

st.subheader("📈 Retention Curves")

# Select cohorts to display
cohort_options = retention_matrix.index.tolist()
default_cohorts = cohort_options[-min(5, len(cohort_options)):] if len(cohort_options) > 5 else cohort_options

selected_cohorts = st.multiselect(
    "Select cohorts to display",
    options=cohort_options,
    default=default_cohorts
)

if selected_cohorts:
    fig = go.Figure()
    
    for cohort in selected_cohorts:
        cohort_data = retention_matrix.loc[cohort].drop('cohort_size')
        fig.add_trace(go.Scatter(
            x=cohort_data.index,
            y=cohort_data.values * 100,
            mode='lines+markers',
            name=str(cohort),
            line=dict(width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        height=400,
        title="Retention Curves by Cohort",
        xaxis_title="Months Since Signup",
        yaxis_title="Retention Rate (%)",
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Add average line
    avg_retention = retention_df.groupby('period')['retention_rate'].mean() * 100
    fig.add_trace(go.Scatter(
        x=avg_retention.index,
        y=avg_retention.values,
        mode='lines',
        name='Average',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# COHORT STATISTICS
# ---------------------------------------------------------------------

st.subheader("📊 Cohort Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    # Best performing cohort
    avg_retention = retention_df.groupby('cohort')['retention_rate'].mean()
    best_cohort = avg_retention.idxmax()
    st.metric(
        label="🏆 Best Performing Cohort",
        value=best_cohort,
        delta=f"{avg_retention.max()*100:.1f}% avg retention"
    )

with col2:
    # Retention at month 3
    month_3_retention = retention_df[retention_df['period'] == 3]['retention_rate'].mean()
    st.metric(
        label="📊 Month 3 Retention",
        value=f"{month_3_retention*100:.1f}%",
        delta=f"Avg across all cohorts"
    )

with col3:
    # Average retention
    avg_retention_all = retention_df['retention_rate'].mean()
    st.metric(
        label="📈 Average Retention",
        value=f"{avg_retention_all*100:.1f}%",
        delta="All periods combined"
    )

# ---------------------------------------------------------------------
# CHANNEL COHORT COMPARISON
# ---------------------------------------------------------------------

st.subheader("📱 Cohort Retention by Acquisition Channel")

# Calculate channel-specific retention
@st.cache_data
def calculate_channel_retention(orders_df, users_df):
    """Calculate retention by acquisition channel"""
    
    # Get first order for each user
    first_orders = orders_df.sort_values('order_placed_at').groupby('user_id').first().reset_index()
    first_orders = first_orders.merge(
        users_df[['user_id', 'acquisition_channel']], 
        on='user_id', 
        how='left'
    )
    
    channel_results = {}
    
    for channel in first_orders['acquisition_channel'].unique():
        channel_users = first_orders[first_orders['acquisition_channel'] == channel]['user_id'].unique()
        
        # Calculate retention for this channel
        channel_retention = []
        
        for month in range(1, 13):
            active = 0
            for user_id in channel_users:
                user_orders = orders_df[orders_df['user_id'] == user_id]
                first_date = first_orders[first_orders['user_id'] == user_id]['order_placed_at'].iloc[0]
                
                has_order = len(user_orders[
                    (user_orders['order_placed_at'] > first_date) &
                    (user_orders['order_placed_at'] <= first_date + timedelta(days=month*30))
                ]) > 0
                
                if has_order:
                    active += 1
            
            rate = active / len(channel_users) if len(channel_users) > 0 else 0
            channel_retention.append(rate * 100)
        
        channel_results[channel] = channel_retention
    
    return pd.DataFrame(channel_results)

channel_retention = calculate_channel_retention(filtered_orders, users)

# Plot channel retention
fig = go.Figure()

for channel in channel_retention.columns:
    fig.add_trace(go.Scatter(
        x=list(range(1, 13)),
        y=channel_retention[channel],
        mode='lines+markers',
        name=channel,
        line=dict(width=2)
    ))

fig.update_layout(
    height=400,
    title="Retention by Acquisition Channel (12 Months)",
    xaxis_title="Months Since First Order",
    yaxis_title="Retention Rate (%)",
    template='plotly_white',
    hovermode='x unified',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# PREMIUM VS NON-PREMIUM
# ---------------------------------------------------------------------

st.subheader("⭐ Premium vs Non-Premium Retention")

@st.cache_data
def calculate_premium_retention(orders_df, users_df):
    """Calculate retention for premium vs non-premium users"""
    
    first_orders = orders_df.sort_values('order_placed_at').groupby('user_id').first().reset_index()
    first_orders = first_orders.merge(
        users_df[['user_id', 'is_premium_member']], 
        on='user_id', 
        how='left'
    )
    
    premium_retention = {'Premium': [], 'Non-Premium': []}
    
    for is_premium in [True, False]:
        users_in_group = first_orders[first_orders['is_premium_member'] == is_premium]['user_id'].unique()
        
        if len(users_in_group) == 0:
            continue
        
        for month in range(1, 13):
            active = 0
            for user_id in users_in_group:
                user_orders = orders_df[orders_df['user_id'] == user_id]
                first_date = first_orders[first_orders['user_id'] == user_id]['order_placed_at'].iloc[0]
                
                has_order = len(user_orders[
                    (user_orders['order_placed_at'] > first_date) &
                    (user_orders['order_placed_at'] <= first_date + timedelta(days=month*30))
                ]) > 0
                
                if has_order:
                    active += 1
            
            rate = active / len(users_in_group) if len(users_in_group) > 0 else 0
            premium_retention['Premium' if is_premium else 'Non-Premium'].append(rate * 100)
    
    return pd.DataFrame(premium_retention)

premium_retention = calculate_premium_retention(filtered_orders, users)

if len(premium_retention) > 0:
    fig = go.Figure()
    
    for group in premium_retention.columns:
        fig.add_trace(go.Scatter(
            x=list(range(1, 13)),
            y=premium_retention[group],
            mode='lines+markers',
            name=group,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        height=400,
        title="Premium vs Non-Premium Retention",
        xaxis_title="Months Since First Order",
        yaxis_title="Retention Rate (%)",
        template='plotly_white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Insufficient data for premium retention analysis")

# ---------------------------------------------------------------------
# KEY INSIGHTS
# ---------------------------------------------------------------------

with st.expander("💡 Key Insights & Recommendations"):
    st.markdown("""
    **🔍 Key Findings:**
    
    1. **Retention Trends:**
       - The first 3 months are critical for retention
       - Most cohorts show steep drop-off in Month 1-2
       - Retention stabilizes after Month 6
    
    2. **Channel Performance:**
       - Referral users show the best retention
       - Paid channels have lower retention, especially in early months
       - Organic users show steady retention
    
    3. **Premium Impact:**
       - Premium users retain significantly better
       - Premium status is a strong retention signal
       - Premium conversion opportunity for high-engagement users
    
    **🎯 Recommendations:**
    
    1. **Improve Early Retention:**
       - Optimize onboarding experience
       - Second-order incentives within 30 days
       - Early engagement campaigns
    
    2. **Channel Strategy:**
       - Increase investment in referral programs
       - Improve paid channel targeting
       - Focus on organic growth
    
    3. **Premium Membership:**
       - Target high-engagement users for premium
       - Highlight premium benefits early
       - Test premium trial offers
    """)

st.caption(f"📊 Cohort analysis based on {len(filtered_orders):,} orders from {start_date} to {end_date}")