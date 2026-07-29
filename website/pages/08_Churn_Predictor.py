"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Churn Predictor
==================================================================
Purpose: Predict and analyze user churn with machine learning.
Identify at-risk users and recommend interventions.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from utils.sample_data import create_sample_churn_data

# Get data from session state
data = st.session_state.data
orders = data['orders']
users = data['users']

# Try to load churn data
try:
    churn_data = pd.read_csv('../outputs/cleaned_data/churn_predictions.csv')
    st.info("✅ Loaded churn prediction model results")
except:
    # Create sample churn data
    st.info("📊 Using sample churn prediction data")
    churn_data = create_sample_churn_data()

def create_sample_churn_data():
    """Create sample churn prediction data"""
    np.random.seed(42)
    n_users = 1000
    
    churn_data = pd.DataFrame({
        'user_id': range(n_users),
        'churn_probability': np.random.beta(2, 5, n_users),
        'churned': np.random.choice([0, 1], n_users, p=[0.7, 0.3]),
        'segment': np.random.choice(['Champions', 'Loyal', 'At Risk', 'Dormant', 'New'], n_users),
        'acquisition_channel': np.random.choice(['organic', 'referral', 'paid_social', 'paid_search'], n_users),
        'is_premium_member': np.random.choice([True, False], n_users, p=[0.2, 0.8])
    })
    
    return churn_data

st.header("⚠️ Churn Predictor")
st.markdown("""
Predict which users are at risk of churning and take proactive action.
Identify key drivers of churn and prioritize interventions.
""")

# ---------------------------------------------------------------------
# CHURN OVERVIEW
# ---------------------------------------------------------------------

st.subheader("📊 Churn Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_users = len(churn_data)
    st.metric("Total Users", f"{total_users:,}")

with col2:
    churned = churn_data['churned'].sum()
    st.metric("Churned Users", f"{churned:,}", f"{churned/total_users*100:.1f}%")

with col3:
    avg_prob = churn_data['churn_probability'].mean()
    st.metric("Avg Churn Probability", f"{avg_prob*100:.1f}%")

with col4:
    high_risk = len(churn_data[churn_data['churn_probability'] > 0.5])
    st.metric("High Risk Users", f"{high_risk:,}", f"{high_risk/total_users*100:.1f}%")

# ---------------------------------------------------------------------
# CHURN RISK DISTRIBUTION
# ---------------------------------------------------------------------

st.subheader("📈 Churn Risk Distribution")

# Create risk buckets
churn_data['risk_bucket'] = pd.cut(
    churn_data['churn_probability'],
    bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
    labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
)

risk_counts = churn_data['risk_bucket'].value_counts().sort_index()

fig = px.bar(
    x=risk_counts.index,
    y=risk_counts.values,
    color=risk_counts.index,
    text=risk_counts.values,
    title="Churn Risk Distribution"
)

fig.update_traces(textposition='outside')
fig.update_layout(
    height=400,
    template='plotly_white',
    xaxis_title="Risk Level",
    yaxis_title="Number of Users",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# CHURN BY SEGMENT
# ---------------------------------------------------------------------

st.subheader("👥 Churn by Segment")

churn_by_segment = churn_data.groupby('segment').agg({
    'user_id': 'count',
    'churn_probability': 'mean',
    'churned': 'mean'
}).reset_index()

churn_by_segment.columns = ['segment', 'users', 'avg_probability', 'churn_rate']
churn_by_segment['churn_rate'] = churn_by_segment['churn_rate'] * 100
churn_by_segment['avg_probability'] = churn_by_segment['avg_probability'] * 100

fig = go.Figure()

fig.add_trace(go.Bar(
    x=churn_by_segment['segment'],
    y=churn_by_segment['churn_rate'],
    name='Churn Rate',
    marker_color='#e74c3c',
    text=churn_by_segment['churn_rate'].round(1).astype(str) + '%',
    textposition='outside'
))

fig.add_trace(go.Scatter(
    x=churn_by_segment['segment'],
    y=churn_by_segment['avg_probability'],
    name='Avg Probability',
    mode='lines+markers',
    line=dict(color='#3498db', width=2),
    yaxis='y2'
))

fig.update_layout(
    height=400,
    title="Churn Rate vs Risk Probability by Segment",
    xaxis_title="Segment",
    yaxis_title="Churn Rate (%)",
    yaxis2=dict(
        title="Avg Risk Probability (%)",
        overlaying='y',
        side='right'
    ),
    template='plotly_white',
    xaxis_tickangle=-45,
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# FEATURE IMPORTANCE
# ---------------------------------------------------------------------

st.subheader("🔑 Key Churn Drivers")

# Try to load feature importance
try:
    feature_importance = pd.read_csv('../outputs/cleaned_data/feature_importance.csv')
    top_features = feature_importance.head(15)
    
    fig = px.bar(
        top_features,
        x='importance',
        y='feature',
        orientation='h',
        color='importance',
        color_continuous_scale='Viridis',
        title="Top 15 Churn Predictors"
    )
    
    fig.update_layout(
        height=500,
        template='plotly_white',
        xaxis_title="Importance Score",
        yaxis_title="Feature",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
except:
    st.info("Feature importance data not available")
    
    # Show sample feature importance
    features = [
        'Days Since Last Order',
        'Order Frequency',
        'Average Order Value',
        'Avg Days Between Orders',
        'Cancellation Rate',
        'Payment Success Rate',
        'Premium Status',
        'Acquisition Channel',
        'Age Band',
        'Device Type'
    ]
    
    importance = np.random.rand(len(features))
    importance = importance / importance.sum()
    
    sample_importance = pd.DataFrame({
        'feature': features,
        'importance': importance
    }).sort_values('importance', ascending=True)
    
    fig = px.bar(
        sample_importance,
        x='importance',
        y='feature',
        orientation='h',
        title="Sample Feature Importance (Demo Data)"
    )
    
    fig.update_layout(
        height=400,
        template='plotly_white',
        xaxis_title="Importance",
        yaxis_title="Feature",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# HIGH RISK USERS
# ---------------------------------------------------------------------

st.subheader("🚨 High Risk Users")

# Display high risk users
high_risk_users = churn_data[churn_data['churn_probability'] > 0.5].sort_values('churn_probability', ascending=False)

if len(high_risk_users) > 0:
    st.dataframe(
        high_risk_users[['user_id', 'churn_probability', 'segment', 'acquisition_channel']].head(20),
        use_container_width=True
    )
    
    # Intervention recommendations
    st.subheader("💡 Intervention Recommendations")
    
    for risk_level in ['Very High', 'High']:
        risk_users = churn_data[churn_data['risk_bucket'] == risk_level]
        if len(risk_users) > 0:
            with st.expander(f"**{risk_level} Risk Users** ({len(risk_users)} users)"):
                st.markdown(f"""
                **Characteristics:**
                - Premium members: {risk_users['is_premium_member'].mean()*100:.1f}%
                - Top channels: {', '.join(risk_users['acquisition_channel'].value_counts().head(3).index)}
                - Top segments: {', '.join(risk_users['segment'].value_counts().head(3).index)}
                
                **Recommendations:**
                - ⚡ Immediate win-back campaign
                - 💰 Personalized offers
                - 📞 Priority support outreach
                - 🎯 Targeted re-engagement
                """)

# ---------------------------------------------------------------------
# PREDICT CHURN FOR NEW USER
# ---------------------------------------------------------------------

with st.expander("🔮 Predict Churn for a User"):
    st.markdown("""
    Enter user metrics to predict churn probability
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days_since_order = st.slider("Days Since Last Order", 0, 365, 30)
        order_frequency = st.slider("Order Frequency (per month)", 0, 10, 2)
    
    with col2:
        cancellation_rate = st.slider("Cancellation Rate (%)", 0, 100, 10)
        payment_success = st.slider("Payment Success Rate (%)", 0, 100, 95)
    
    with col3:
        is_premium = st.checkbox("Premium Member")
        channel = st.selectbox("Acquisition Channel", ['organic', 'referral', 'paid_social', 'paid_search'])
    
    # Simple prediction (demo)
    base_prob = 0.3
    prob = base_prob
    
    prob += min(0.3, days_since_order / 365 * 0.3)
    prob -= min(0.15, order_frequency / 10 * 0.15)
    prob += min(0.1, cancellation_rate / 100 * 0.1)
    prob -= min(0.1, payment_success / 100 * 0.1)
    if is_premium:
        prob -= 0.05
    if channel == 'referral':
        prob -= 0.05
    
    prob = np.clip(prob, 0.01, 0.99)
    
    # Display result
    st.metric(
        label="Predicted Churn Probability",
        value=f"{prob*100:.1f}%",
        delta="High Risk" if prob > 0.5 else "Low Risk",
        delta_color="inverse" if prob > 0.5 else "normal"
    )

st.caption(f"📊 Churn prediction based on {len(churn_data):,} users")