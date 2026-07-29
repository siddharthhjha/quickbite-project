"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: LTV Dashboard
==================================================================
Purpose: Analyze customer lifetime value, LTV:CAC ratios,
and optimize acquisition spending.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.sample_data import create_sample_ltv_data

# Get data from session state
data = st.session_state.data
orders = data['orders']
users = data['users']

# Try to load LTV data
try:
    ltv_data = pd.read_csv('../outputs/cleaned_data/ltv_predictions.csv')
    st.info("✅ Loaded LTV predictions")
except:
    st.info("📊 Using sample LTV data")
    ltv_data = create_sample_ltv_data()

def create_sample_ltv_data():
    """Create sample LTV data"""
    np.random.seed(42)
    n_users = 1000
    
    ltv_data = pd.DataFrame({
        'user_id': range(n_users),
        'lifetime_value': np.random.exponential(2000, n_users) + 100,
        'predicted_ltv': np.random.exponential(2000, n_users) + 100,
        'acquisition_channel': np.random.choice(['organic', 'referral', 'paid_social', 'paid_search'], n_users),
        'is_premium_member': np.random.choice([True, False], n_users, p=[0.2, 0.8]),
        'order_count': np.random.poisson(5, n_users) + 1,
        'segment': np.random.choice(['Champions', 'Loyal', 'At Risk', 'Dormant', 'New'], n_users)
    })
    
    return ltv_data

st.header("💰 LTV Dashboard")
st.markdown("""
Understand customer lifetime value and optimize acquisition strategy.
Track LTV:CAC ratios and identify high-value segments.
""")

# ---------------------------------------------------------------------
# LTV OVERVIEW
# ---------------------------------------------------------------------

st.subheader("📊 LTV Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_ltv = ltv_data['lifetime_value'].mean()
    st.metric("Average LTV", f"₹{avg_ltv:,.0f}")

with col2:
    median_ltv = ltv_data['lifetime_value'].median()
    st.metric("Median LTV", f"₹{median_ltv:,.0f}")

with col3:
    total_ltv = ltv_data['lifetime_value'].sum()
    st.metric("Total LTV", f"₹{total_ltv:,.2f}")

with col4:
    top_10_pct = ltv_data['lifetime_value'].quantile(0.9)
    st.metric("Top 10% LTV", f"₹{top_10_pct:,.0f}")

# ---------------------------------------------------------------------
# LTV DISTRIBUTION
# ---------------------------------------------------------------------

st.subheader("📈 LTV Distribution")

fig = make_subplots(rows=1, cols=2, subplot_titles=('LTV Distribution', 'LTV by Channel'))

# LTV histogram
fig.add_trace(
    go.Histogram(
        x=ltv_data['lifetime_value'],
        nbinsx=50,
        name='LTV',
        marker_color='#3498db',
        opacity=0.7
    ),
    row=1, col=1
)

# LTV by channel
channel_ltv = ltv_data.groupby('acquisition_channel')['lifetime_value'].mean().sort_values(ascending=False)
fig.add_trace(
    go.Bar(
        x=channel_ltv.index,
        y=channel_ltv.values,
        name='Avg LTV',
        marker_color='#2ecc71'
    ),
    row=1, col=2
)

fig.update_layout(
    height=400,
    template='plotly_white',
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# LTV BY SEGMENT
# ---------------------------------------------------------------------

st.subheader("👥 LTV by Segment")

segment_ltv = ltv_data.groupby('segment').agg({
    'lifetime_value': ['mean', 'median', 'std'],
    'user_id': 'count'
}).round(2)

segment_ltv.columns = ['mean', 'median', 'std', 'users']
segment_ltv = segment_ltv.sort_values('mean', ascending=False)

# Display
st.dataframe(
    segment_ltv.style.background_gradient(cmap='RdYlGn', subset=['mean']),
    use_container_width=True
)

# ---------------------------------------------------------------------
# LTV:CAC ANALYSIS
# ---------------------------------------------------------------------

st.subheader("📊 LTV:CAC Analysis")

# Calculate CAC by channel (using signup channel cost)
if 'signup_channel_cost' in users.columns:
    cac_data = users.groupby('acquisition_channel')['signup_channel_cost'].mean()
else:
    # Sample CAC data
    cac_data = pd.Series({
        'organic': 0,
        'referral': 60,
        'paid_social': 180,
        'paid_search': 220
    })

# Merge with LTV
channel_analysis = pd.DataFrame({
    'channel': cac_data.index,
    'cac': cac_data.values,
    'ltv': [ltv_data[ltv_data['acquisition_channel'] == ch]['lifetime_value'].mean() for ch in cac_data.index]
})

channel_analysis['ltv_cac_ratio'] = channel_analysis['ltv'] / (channel_analysis['cac'] + 1)

# Sort
channel_analysis = channel_analysis.sort_values('ltv_cac_ratio', ascending=False)

# Display
st.dataframe(
    channel_analysis.style.background_gradient(cmap='RdYlGn', subset=['ltv_cac_ratio']),
    use_container_width=True
)

# Visualize
fig = px.bar(
    channel_analysis,
    x='channel',
    y='ltv_cac_ratio',
    color='ltv_cac_ratio',
    text='ltv_cac_ratio',
    title="LTV:CAC Ratio by Channel",
    color_continuous_scale='Viridis'
)

fig.add_hline(y=3, line_dash="dash", line_color="green", annotation_text="Good (3x)")
fig.add_hline(y=1, line_dash="dash", line_color="red", annotation_text="Breakeven (1x)")

fig.update_traces(texttemplate='%{text:.1f}x', textposition='outside')
fig.update_layout(
    height=400,
    template='plotly_white',
    xaxis_title="Channel",
    yaxis_title="LTV:CAC Ratio",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# PREDICTED VS ACTUAL
# ---------------------------------------------------------------------

st.subheader("🎯 Predicted vs Actual LTV")

if 'predicted_ltv' in ltv_data.columns:
    # Sample for visualization
    sample = ltv_data.sample(min(500, len(ltv_data)))
    
    fig = px.scatter(
        sample,
        x='lifetime_value',
        y='predicted_ltv',
        color='acquisition_channel',
        title="Predicted vs Actual LTV",
        labels={'lifetime_value': 'Actual LTV (₹)', 'predicted_ltv': 'Predicted LTV (₹)'}
    )
    
    fig.add_trace(go.Scatter(
        x=[0, sample['lifetime_value'].max() * 1.1],
        y=[0, sample['lifetime_value'].max() * 1.1],
        mode='lines',
        name='Perfect Prediction',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# ACQUISITION OPTIMIZATION
# ---------------------------------------------------------------------

st.subheader("💰 Acquisition Optimization")

# Calculate optimal allocation
total_budget = 1000000  # ₹10L
channel_analysis['optimal_allocation'] = (
    channel_analysis['ltv_cac_ratio'] / channel_analysis['ltv_cac_ratio'].sum() * total_budget
)

fig = px.pie(
    channel_analysis,
    values='optimal_allocation',
    names='channel',
    title="Recommended Budget Allocation",
    color='channel'
)

fig.update_traces(textinfo='label+percent+value', textposition='inside')
fig.update_layout(
    height=400,
    template='plotly_white'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# KEY INSIGHTS
# ---------------------------------------------------------------------

with st.expander("💡 Key Insights & Recommendations"):
    best_channel = channel_analysis.iloc[0]['channel'] if len(channel_analysis) > 0 else 'N/A'
    best_ratio = channel_analysis.iloc[0]['ltv_cac_ratio'] if len(channel_analysis) > 0 else 0
    
    st.markdown(f"""
    **🔍 Key Findings:**
    
    1. **LTV Insights:**
       - Average LTV: ₹{avg_ltv:,.0f}
       - Median LTV: ₹{median_ltv:,.0f}
       - Top 10% users drive {(ltv_data[ltv_data['lifetime_value'] > top_10_pct]['lifetime_value'].sum() / total_ltv * 100):.1f}% of LTV
    
    2. **Channel Performance:**
       - Best channel by LTV:CAC: {best_channel} ({best_ratio:.1f}x)
       - Recommended budget allocation optimized for ROI
       - Referral users show highest LTV
    
    3. **Segmentation:**
       - Champions have {segment_ltv.loc['Champions', 'mean'] / segment_ltv['mean'].mean():.1f}x higher LTV
       - Premium users: {ltv_data[ltv_data['is_premium_member'] == True]['lifetime_value'].mean():.0f} vs {ltv_data[ltv_data['is_premium_member'] == False]['lifetime_value'].mean():.0f}
    
    **🎯 Recommendations:**
    
    1. **Optimize Acquisition:**
       - Increase budget for {best_channel}
       - Target users with high LTV potential
       - Improve targeting for underperforming channels
    
    2. **Increase LTV:**
       - Premium membership conversion
       - Cross-selling and upselling
       - Improve retention in first 90 days
    
    3. **Channel Strategy:**
       - Scale referral programs
       - Optimize paid channel targeting
       - A/B test creatives for high-LTV segments
    """)

st.caption(f"📊 LTV analysis based on {len(ltv_data):,} users")