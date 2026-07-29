"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Customer Segments
==================================================================
Purpose: Interactive RFM segmentation analysis with segment
profiling and actionable recommendations.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Get data from session state
data = st.session_state.data

# Extract data with safety checks
orders = data.get('orders') if data else None
users = data.get('users') if data else None
rfm = data.get('rfm') if data else None

# Check if data exists
if rfm is None or len(rfm) == 0:
    st.warning("⚠️ No RFM data available. Please generate data first.")
    st.stop()

st.header("👥 Customer Segments")
st.markdown("""
Understand your user base through RFM segmentation.
Identify high-value segments, at-risk users, and personalization opportunities.
""")

# Apply filters
start_date = st.session_state.start_date
end_date = st.session_state.end_date

# =====================================================================
# SEGMENT OVERVIEW
# =====================================================================

st.subheader("📊 Segment Distribution")

# Get segment counts
segment_counts = rfm['segment'].value_counts().reset_index()
segment_counts.columns = ['Segment', 'Count']
segment_counts['Percentage'] = segment_counts['Count'] / segment_counts['Count'].sum() * 100

# Color mapping
segment_colors = {
    'Champions': '#2ecc71',
    'Loyal Customers': '#27ae60',
    'Big Spenders': '#f1c40f',
    'Potential Loyalists': '#3498db',
    'Recent Users': '#2980b9',
    'New Customers': '#1abc9c',
    'At Risk': '#e67e22',
    'Dormant': '#f39c12',
    'Lost': '#e74c3c',
    'Low Value': '#95a5a6',
    'Other': '#bdc3c7'
}

# Create segment distribution chart
col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(
        segment_counts,
        x='Segment',
        y='Count',
        color='Segment',
        color_discrete_map=segment_colors,
        text='Percentage',
        title='User Segment Distribution'
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        height=400,
        template='plotly_white',
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Segment metrics
    st.metric(
        label="Total Users",
        value=f"{len(rfm):,}"
    )
    st.metric(
        label="Segments",
        value=f"{len(segment_counts)}"
    )
    st.metric(
        label="Largest Segment",
        value=segment_counts.iloc[0]['Segment'],
        delta=f"{segment_counts.iloc[0]['Percentage']:.1f}%"
    )

# =====================================================================
# SEGMENT METRICS
# =====================================================================

st.subheader("📈 Segment Performance Metrics")

# Calculate segment metrics
segment_metrics = rfm.groupby('segment').agg({
    'user_id': 'count',
    'recency': 'mean',
    'frequency': 'mean',
    'monetary': ['mean', 'sum']
}).round(2)

segment_metrics.columns = ['users', 'avg_recency', 'avg_frequency', 'avg_monetary', 'total_monetary']
segment_metrics = segment_metrics.sort_values('avg_monetary', ascending=False)

# Display metrics table
st.dataframe(
    segment_metrics.style.background_gradient(cmap='RdYlGn', subset=['avg_monetary']),
    use_container_width=True
)

# =====================================================================
# KEY INSIGHTS
# =====================================================================

with st.expander("💡 Key Insights & Recommendations"):
    st.markdown("""
    **🔍 Key Findings:**
    
    1. **Revenue Concentration:**
       - Top segments drive majority of revenue
       - Champions have highest retention
       - At Risk + Dormant represent revenue risk
    
    2. **Segment Health:**
       - Champions have highest retention rate
       - Premium users are more likely to be high-value
       - Referral channel creates more Champions
    
    **🎯 Recommendations:**
    
    **P0 (Immediate):**
    - Champions → Referral program with premium rewards
    - At Risk → Targeted win-back campaign
    - New Customers → Improved onboarding
    
    **P1 (Short-term):**
    - Loyal Customers → Early access to new features
    - Recent Users → Subscription conversion
    - Dormant → Re-engagement incentives
    """)

st.caption(f"📊 RFM segmentation based on {len(rfm):,} users")