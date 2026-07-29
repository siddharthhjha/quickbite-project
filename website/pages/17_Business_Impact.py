"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Business Impact Simulation
==================================================================
Purpose: Simulate the business impact of implementing
recommendations with interactive what-if analysis.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Business Impact - QuickBite",
    page_icon="📈",
    layout="wide"
)

st.header("📈 Business Impact Simulation")
st.markdown("""
Interactive what-if analysis to simulate the business impact
of implementing product recommendations.
""")

# ---------------------------------------------------------------------
# CURRENT STATE
# ---------------------------------------------------------------------

# Current business metrics
current_metrics = {
    'GMV': 45000000,
    'Orders': 132456,
    'Active Users': 8456,
    'AOV': 340,
    'Retention Rate': 34.5,
    'Churn Rate': 12.3,
    'Cancellation Rate': 8.7,
    'LTV': 2456,
    'CAC': 200,
    'LTV:CAC': 12.3
}

st.subheader("📊 Current Business State")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("GMV", f"₹{current_metrics['GMV']:,.0f}")
with col2:
    st.metric("Orders", f"{current_metrics['Orders']:,}")
with col3:
    st.metric("Active Users", f"{current_metrics['Active Users']:,}")
with col4:
    st.metric("AOV", f"₹{current_metrics['AOV']}")
with col5:
    st.metric("Retention", f"{current_metrics['Retention Rate']}%")

# ---------------------------------------------------------------------
# IMPACT SIMULATION
# ---------------------------------------------------------------------

st.subheader("🎯 Impact Simulation")

# Select recommendations to simulate
recommendations = {
    'Referral Program': {
        'gmv_impact': 0.05,
        'retention_impact': 0.08,
        'users_impact': 0.15,
        'aov_impact': 0.02
    },
    'Win-Back Campaign': {
        'gmv_impact': 0.04,
        'retention_impact': 0.12,
        'users_impact': 0.08,
        'aov_impact': 0.01
    },
    'Checkout Optimization': {
        'gmv_impact': 0.08,
        'retention_impact': 0.05,
        'users_impact': 0.03,
        'aov_impact': 0.05
    },
    'Cross-Selling': {
        'gmv_impact': 0.06,
        'retention_impact': 0.03,
        'users_impact': 0.02,
        'aov_impact': 0.08
    },
    'Premium Upsell': {
        'gmv_impact': 0.03,
        'retention_impact': 0.10,
        'users_impact': 0.02,
        'aov_impact': 0.04
    },
    'Delivery Optimization': {
        'gmv_impact': 0.02,
        'retention_impact': 0.15,
        'users_impact': 0.05,
        'aov_impact': 0.01
    },
    'Personalized Search': {
        'gmv_impact': 0.04,
        'retention_impact': 0.06,
        'users_impact': 0.04,
        'aov_impact': 0.03
    },
    'Payment Optimization': {
        'gmv_impact': 0.03,
        'retention_impact': 0.04,
        'users_impact': 0.02,
        'aov_impact': 0.02
    }
}

# Multi-select
selected_recs = st.multiselect(
    "Select recommendations to simulate",
    options=list(recommendations.keys()),
    default=['Referral Program', 'Win-Back Campaign', 'Checkout Optimization']
)

if selected_recs:
    # Calculate combined impact
    combined_impact = {
        'gmv_impact': 0,
        'retention_impact': 0,
        'users_impact': 0,
        'aov_impact': 0
    }
    
    # Apply diminishing returns (synergy effect)
    synergy_factor = 0.8  # 80% of sum due to overlap
    
    for rec in selected_recs:
        for metric in combined_impact.keys():
            combined_impact[metric] += recommendations[rec][metric]
    
    # Apply synergy
    for metric in combined_impact.keys():
        combined_impact[metric] = combined_impact[metric] * synergy_factor
    
    # Calculate projected metrics
    projected = {
        'GMV': current_metrics['GMV'] * (1 + combined_impact['gmv_impact']),
        'Orders': current_metrics['Orders'] * (1 + combined_impact['gmv_impact'] * 0.8),
        'Active Users': current_metrics['Active Users'] * (1 + combined_impact['users_impact']),
        'AOV': current_metrics['AOV'] * (1 + combined_impact['aov_impact']),
        'Retention Rate': current_metrics['Retention Rate'] * (1 + combined_impact['retention_impact']),
        'Churn Rate': current_metrics['Churn Rate'] * (1 - combined_impact['retention_impact'] * 0.5)
    }
    
    # Display projected metrics
    st.subheader("📈 Projected Impact")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Projected GMV",
            f"₹{projected['GMV']:,.0f}",
            f"+{(projected['GMV']/current_metrics['GMV']-1)*100:.1f}%"
        )
    with col2:
        st.metric(
            "Projected Orders",
            f"{projected['Orders']:,.0f}",
            f"+{(projected['Orders']/current_metrics['Orders']-1)*100:.1f}%"
        )
    with col3:
        st.metric(
            "Projected Users",
            f"{projected['Active Users']:,.0f}",
            f"+{(projected['Active Users']/current_metrics['Active Users']-1)*100:.1f}%"
        )
    with col4:
        st.metric(
            "Projected AOV",
            f"₹{projected['AOV']:,.0f}",
            f"+{(projected['AOV']/current_metrics['AOV']-1)*100:.1f}%"
        )
    with col5:
        st.metric(
            "Projected Retention",
            f"{projected['Retention Rate']:.1f}%",
            f"+{(projected['Retention Rate']/current_metrics['Retention Rate']-1)*100:.1f}%"
        )
    
    # Visualize impact
    fig = go.Figure()
    
    # Current vs Projected
    metrics = ['GMV', 'Orders', 'Active Users', 'AOV', 'Retention Rate']
    current_values = [current_metrics[m] for m in metrics]
    projected_values = [projected[m] for m in metrics]
    
    # Normalize for visualization
    max_val = max(max(current_values), max(projected_values))
    current_norm = [v/max_val*100 for v in current_values]
    projected_norm = [v/max_val*100 for v in projected_values]
    
    fig.add_trace(go.Bar(
        x=metrics,
        y=current_norm,
        name='Current',
        marker_color='#3498db'
    ))
    
    fig.add_trace(go.Bar(
        x=metrics,
        y=projected_norm,
        name='Projected',
        marker_color='#2ecc71'
    ))
    
    fig.update_layout(
        height=400,
        title="Current vs Projected Performance",
        xaxis_title="Metric",
        yaxis_title="Normalized Value (%)",
        template='plotly_white',
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ROI Calculation
    st.subheader("💰 ROI Analysis")
    
    total_investment = len(selected_recs) * 1000000  # Assume ₹10L per recommendation
    total_revenue_impact = projected['GMV'] - current_metrics['GMV']
    roi = (total_revenue_impact - total_investment) / total_investment * 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Investment", f"₹{total_investment:,.0f}")
    with col2:
        st.metric("Revenue Impact", f"₹{total_revenue_impact:,.0f}")
    with col3:
        st.metric("ROI", f"{roi:.0f}%")
    
    # Break-even analysis
    months_to_breakeven = total_investment / (total_revenue_impact / 12)
    
    st.info(f"""
    **📊 Break-even Analysis:**
    
    - Monthly Revenue Increase: ₹{total_revenue_impact/12:,.0f}
    - Time to Break-even: {months_to_breakeven:.1f} months
    - 1-Year ROI: {(total_revenue_impact - total_investment) / total_investment * 100:.0f}%
    """)

# ---------------------------------------------------------------------
# SENSITIVITY ANALYSIS
# ---------------------------------------------------------------------

with st.expander("🎯 Sensitivity Analysis"):
    st.markdown("""
    Adjust the expected impact of each recommendation to see how 
    changes affect overall business performance.
    """)
    
    sensitivity_rec = st.selectbox(
        "Select recommendation for sensitivity analysis",
        options=list(recommendations.keys())
    )
    
    if sensitivity_rec:
        impact_range = st.slider(
            "Impact Multiplier",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        # Calculate impact with sensitivity
        base_impact = recommendations[sensitivity_rec]['gmv_impact']
        adjusted_impact = base_impact * impact_range
        
        sensitivity_gmv = current_metrics['GMV'] * (1 + adjusted_impact)
        
        st.metric(
            f"Projected GMV with {sensitivity_rec}",
            f"₹{sensitivity_gmv:,.0f}",
            f"+{(sensitivity_gmv/current_metrics['GMV']-1)*100:.1f}%"
        )
        
        # Create sensitivity chart
        impacts = [base_impact * m for m in np.linspace(0.5, 2.0, 10)]
        gmvs = [current_metrics['GMV'] * (1 + i) for i in impacts]
        
        fig = px.line(
            x=np.linspace(0.5, 2.0, 10),
            y=gmvs,
            title=f"Sensitivity Analysis: {sensitivity_rec}",
            labels={'x': 'Impact Multiplier', 'y': 'Projected GMV (₹)'}
        )
        
        fig.add_hline(y=current_metrics['GMV'], line_dash="dash", line_color="red", annotation_text="Current")
        fig.update_layout(template='plotly_white')
        
        st.plotly_chart(fig, use_container_width=True)

st.caption("📊 Business Impact Simulation - Interactive Decision Support")