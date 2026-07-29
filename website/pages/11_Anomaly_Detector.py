"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Anomaly Detector
==================================================================
Purpose: Detect and analyze anomalies in key business metrics
for real-time monitoring and issue identification.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.sample_data import create_sample_daily_metrics

# Get data from session state
data = st.session_state.data
orders = data['orders']

# Try to load daily metrics with anomalies
try:
    daily_metrics = pd.read_csv('../outputs/cleaned_data/daily_metrics_with_anomalies.csv')
    daily_metrics['date'] = pd.to_datetime(daily_metrics['date'])
    st.info("✅ Loaded anomaly detection results")
except:
    st.info("📊 Creating sample anomaly data")
    daily_metrics = create_sample_daily_metrics(orders)

def create_sample_daily_metrics(orders_df):
    """Create sample daily metrics with anomalies"""
    
    # Create daily aggregates
    daily = orders_df.groupby(orders_df['order_placed_at'].dt.date).agg({
        'order_id': 'count',
        'total_amount': 'sum'
    }).reset_index()
    daily.columns = ['date', 'orders', 'gmv']
    daily['date'] = pd.to_datetime(daily['date'])
    daily['aov'] = daily['gmv'] / daily['orders']
    daily['cancellation_rate'] = np.random.uniform(5, 15, len(daily))
    
    # Add anomalies (random spikes)
    np.random.seed(42)
    daily['is_anomaly'] = np.random.choice([0, 1], len(daily), p=[0.95, 0.05])
    daily['anomaly_score'] = np.random.normal(0, 1, len(daily))
    daily.loc[daily['is_anomaly'] == 1, 'anomaly_score'] = np.random.uniform(2, 4, daily['is_anomaly'].sum())
    
    return daily

st.header("🚨 Anomaly Detector")
st.markdown("""
Monitor key metrics for unusual patterns and detect anomalies
in real-time. Identify issues before they impact the business.
""")

# ---------------------------------------------------------------------
# ANOMALY OVERVIEW
# ---------------------------------------------------------------------

st.subheader("📊 Anomaly Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_days = len(daily_metrics)
    st.metric("Total Days", f"{total_days:,}")

with col2:
    anomalies = daily_metrics['is_anomaly'].sum()
    st.metric("Anomalies Detected", f"{anomalies:,}", f"{anomalies/total_days*100:.1f}%")

with col3:
    avg_score = daily_metrics['anomaly_score'].mean()
    st.metric("Avg Anomaly Score", f"{avg_score:.2f}")

with col4:
    max_score = daily_metrics['anomaly_score'].max()
    st.metric("Max Anomaly Score", f"{max_score:.2f}")

# ---------------------------------------------------------------------
# ANOMALY VISUALIZATION
# ---------------------------------------------------------------------

st.subheader("📈 Anomaly Detection Over Time")

# Select metric to visualize
metric_options = ['orders', 'gmv', 'aov', 'cancellation_rate']
selected_metric = st.selectbox("Select Metric", metric_options)

fig = go.Figure()

# Main metric
fig.add_trace(go.Scatter(
    x=daily_metrics['date'],
    y=daily_metrics[selected_metric],
    mode='lines',
    name=selected_metric,
    line=dict(color='#3498db', width=2)
))

# Anomalies
anomaly_data = daily_metrics[daily_metrics['is_anomaly'] == 1]
fig.add_trace(go.Scatter(
    x=anomaly_data['date'],
    y=anomaly_data[selected_metric],
    mode='markers',
    name='Anomalies',
    marker=dict(color='red', size=10, symbol='x')
))

# Add moving average
window = st.slider("Moving Average Window", 3, 30, 7)
ma = daily_metrics[selected_metric].rolling(window=window, center=True).mean()
fig.add_trace(go.Scatter(
    x=daily_metrics['date'],
    y=ma,
    mode='lines',
    name=f'{window}-day MA',
    line=dict(color='#2ecc71', width=1.5, dash='dash')
))

fig.update_layout(
    height=500,
    title=f"{selected_metric.upper()} - Anomaly Detection",
    xaxis_title="Date",
    yaxis_title=selected_metric.upper(),
    template='plotly_white',
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# ANOMALY DETAILS
# ---------------------------------------------------------------------

st.subheader("📋 Anomaly Details")

# Filter anomalies
anomalies_df = daily_metrics[daily_metrics['is_anomaly'] == 1].sort_values('anomaly_score', ascending=False)

if len(anomalies_df) > 0:
    # Display anomaly table
    display_cols = ['date', 'orders', 'gmv', 'aov', 'cancellation_rate', 'anomaly_score']
    st.dataframe(
        anomalies_df[display_cols].style.background_gradient(cmap='RdYlGn', subset=['anomaly_score']),
        use_container_width=True
    )
    
    # Severity distribution
    st.subheader("📊 Anomaly Severity Distribution")
    
    fig = px.histogram(
        anomalies_df,
        x='anomaly_score',
        nbins=20,
        title="Anomaly Score Distribution",
        color_discrete_sequence=['#e74c3c']
    )
    
    fig.update_layout(
        height=300,
        template='plotly_white',
        xaxis_title="Anomaly Score",
        yaxis_title="Count"
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("✅ No anomalies detected in the current period")

# ---------------------------------------------------------------------
# ANOMALY PATTERNS
# ---------------------------------------------------------------------

st.subheader("🔍 Anomaly Patterns")

if len(anomalies_df) > 0:
    # Analyze anomaly patterns
    col1, col2 = st.columns(2)
    
    with col1:
        # Day of week distribution
        anomalies_df['day_of_week'] = anomalies_df['date'].dt.day_name()
        dow_counts = anomalies_df['day_of_week'].value_counts()
        
        fig = px.bar(
            x=dow_counts.index,
            y=dow_counts.values,
            title="Anomalies by Day of Week",
            color=dow_counts.index
        )
        fig.update_layout(
            height=300,
            template='plotly_white',
            xaxis_title="Day",
            yaxis_title="Number of Anomalies",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Weather correlation (if available)
        if 'condition' in daily_metrics.columns:
            weather_counts = anomalies_df['condition'].value_counts()
            
            fig = px.pie(
                values=weather_counts.values,
                names=weather_counts.index,
                title="Anomalies by Weather"
            )
            fig.update_layout(
                height=300,
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Weather data not available for pattern analysis")

# ---------------------------------------------------------------------
# KEY INSIGHTS
# ---------------------------------------------------------------------

with st.expander("💡 Key Insights & Recommendations"):
    if len(anomalies_df) > 0:
        top_anomaly = anomalies_df.iloc[0]
        top_date = top_anomaly['date'].strftime('%Y-%m-%d')
        
        st.markdown(f"""
        **🔍 Key Findings:**
        
        1. **Top Anomalies:**
           - Most severe anomaly: {top_date} (Score: {top_anomaly['anomaly_score']:.2f})
           - {selected_metric} on that day: {top_anomaly[selected_metric]:.0f}
           - Deviation from normal: {(top_anomaly[selected_metric] - daily_metrics[selected_metric].mean()) / daily_metrics[selected_metric].std():.2f}σ
        
        2. **Pattern Insights:**
           - {anomalies_df['day_of_week'].value_counts().index[0]} has the most anomalies
           - Anomalies often cluster around {selected_metric} changes
           - {len(anomalies_df)} total anomalies detected
        
        3. **Business Impact:**
           - Estimated revenue impact: ₹{anomalies_df['gmv'].sum():,.0f}
           - Order impact: {anomalies_df['orders'].sum():,} orders affected
        """)
    
    st.markdown("""
    **🎯 Recommendations:**
    
    1. **Real-time Monitoring:**
       - Set up alerts for anomaly thresholds
       - Configure notification system
       - Define escalation procedures
    
    2. **Root Cause Analysis:**
       - Investigate top anomalies
       - Check for external factors (weather, events)
       - Review operational logs
    
    3. **Prevention:**
       - Implement automated anomaly detection
       - Build proactive monitoring dashboards
       - Develop anomaly response playbook
    """)

st.caption(f"📊 Anomaly detection based on {len(daily_metrics):,} days of data")