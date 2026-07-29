"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Experiments
==================================================================
Purpose: View and analyze A/B test results with statistical
significance testing and business recommendations.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from utils.sample_data import create_sample_experiments

# Get data from session state
data = st.session_state.data

st.header("🧪 A/B Test Experiments")
st.markdown("""
View experiment results with statistical significance testing.
Make data-driven decisions based on test outcomes.
""")

# ---------------------------------------------------------------------
# LOAD EXPERIMENT DATA
# ---------------------------------------------------------------------

# Try to load experiment data
try:
    # Look for experiment files
    import glob
    exp_files = glob.glob('../outputs/cleaned_data/experiment_*.csv')
    
    if exp_files:
        experiment_data = {}
        for file in exp_files:
            exp_name = file.split('_')[-1].replace('.csv', '')
            experiment_data[exp_name] = pd.read_csv(file)
    else:
        # Create sample experiment data for demo
        experiment_data = create_sample_experiments()
        st.info("📊 Using sample experiment data for demonstration")
except:
    # Create sample experiment data
    experiment_data = create_sample_experiments()
    st.info("📊 Using sample experiment data for demonstration")

def create_sample_experiments():
    """Create sample experiment data for demo"""
    
    np.random.seed(42)
    
    experiments = {
        'free_delivery': {
            'name': 'Free Delivery Threshold',
            'control_rate': 0.28,
            'treatment_rate': 0.31,
            'sample_size': 8600,
            'p_value': 0.012,
            'lift': 10.7,
            'status': 'Shipped',
            'guardrails': {'aov': '✅', 'cancellation': '✅'}
        },
        'recommendation': {
            'name': 'Recommendation Algorithm',
            'control_rate': 0.25,
            'treatment_rate': 0.27,
            'sample_size': 20000,
            'p_value': 0.004,
            'lift': 8.0,
            'status': 'Shipped',
            'guardrails': {'session_length': '✅', 'diversity': '⚠️'}
        },
        'coupon_size': {
            'name': 'Coupon Size (Flat vs %)',
            'control_rate': 0.30,
            'treatment_rate': 0.32,
            'sample_size': 12000,
            'p_value': 0.034,
            'lift': 6.7,
            'status': 'Hold',
            'guardrails': {'redemption_rate': '⚠️'}
        },
        'checkout_ui': {
            'name': 'Checkout UI',
            'control_rate': 0.65,
            'treatment_rate': 0.63,
            'sample_size': 6000,
            'p_value': 0.089,
            'lift': -3.1,
            'status': 'Killed',
            'guardrails': {'payment_failure': '✅'}
        },
        'delivery_fee': {
            'name': 'Delivery Fee Structure',
            'control_rate': 0.32,
            'treatment_rate': 0.33,
            'sample_size': 10000,
            'p_value': 0.056,
            'lift': 3.1,
            'status': 'Hold',
            'guardrails': {'long_distance': '⚠️'}
        },
        'restaurant_ranking': {
            'name': 'Restaurant Ranking',
            'control_rate': 0.30,
            'treatment_rate': 0.315,
            'sample_size': 20000,
            'p_value': 0.001,
            'lift': 5.0,
            'status': 'Shipped',
            'guardrails': {'cancellation': '✅'}
        },
        'push_timing': {
            'name': 'Push Notification Timing',
            'control_rate': 0.10,
            'treatment_rate': 0.12,
            'sample_size': 10000,
            'p_value': 0.002,
            'lift': 20.0,
            'status': 'Shipped',
            'guardrails': {'opt_out': '✅'}
        }
    }
    
    return experiments

# ---------------------------------------------------------------------
# EXPERIMENT SUMMARY
# ---------------------------------------------------------------------

st.subheader("📊 Experiment Summary")

# Create experiment summary table
summary_data = []
for exp_key, exp_data in experiment_data.items():
    if isinstance(exp_data, dict):
        # Sample data format
        summary_data.append({
            'Experiment': exp_data['name'],
            'Control Rate': f"{exp_data['control_rate']*100:.1f}%",
            'Treatment Rate': f"{exp_data['treatment_rate']*100:.1f}%",
            'Lift': f"{exp_data['lift']:.1f}%",
            'P-Value': f"{exp_data['p_value']:.4f}",
            'Significant': '✅' if exp_data['p_value'] < 0.05 else '❌',
            'Status': exp_data['status'],
            'Guardrails': '🟢' if all(v == '✅' for v in exp_data['guardrails'].values()) else '🟡'
        })
    else:
        # Real data format
        # Would parse from CSV
        pass

summary_df = pd.DataFrame(summary_data)

# Display summary
st.dataframe(
    summary_df.style.background_gradient(cmap='RdYlGn', subset=['P-Value']),
    use_container_width=True
)

# ---------------------------------------------------------------------
# EXPERIMENT DETAILS
# ---------------------------------------------------------------------

st.subheader("🔬 Experiment Details")

selected_experiment = st.selectbox(
    "Select an experiment to analyze",
    options=list(experiment_data.keys()),
    format_func=lambda x: experiment_data[x]['name'] if isinstance(experiment_data[x], dict) else x
)

if selected_experiment:
    exp = experiment_data[selected_experiment]
    
    if isinstance(exp, dict):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Control Rate",
                value=f"{exp['control_rate']*100:.1f}%"
            )
        
        with col2:
            st.metric(
                label="Treatment Rate",
                value=f"{exp['treatment_rate']*100:.1f}%",
                delta=f"{exp['lift']:.1f}%"
            )
        
        with col3:
            st.metric(
                label="Sample Size",
                value=f"{exp['sample_size']:,}"
            )
        
        with col4:
            st.metric(
                label="P-Value",
                value=f"{exp['p_value']:.4f}",
                delta="✅ Significant" if exp['p_value'] < 0.05 else "❌ Not Significant"
            )
        
        # Confidence interval visualization
        st.subheader("📈 Confidence Interval")
        
        control_rate = exp['control_rate']
        treatment_rate = exp['treatment_rate']
        n = exp['sample_size'] // 2
        
        # Calculate confidence intervals
        se_control = np.sqrt(control_rate * (1 - control_rate) / n)
        se_treatment = np.sqrt(treatment_rate * (1 - treatment_rate) / n)
        
        ci_control_lower = control_rate - 1.96 * se_control
        ci_control_upper = control_rate + 1.96 * se_control
        ci_treatment_lower = treatment_rate - 1.96 * se_treatment
        ci_treatment_upper = treatment_rate + 1.96 * se_treatment
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=['Control', 'Treatment'],
            y=[control_rate, treatment_rate],
            error_y=dict(
                type='data',
                symmetric=False,
                array=[control_rate - ci_control_lower, treatment_rate - ci_treatment_lower],
                arrayminus=[ci_control_upper - control_rate, ci_treatment_upper - treatment_rate]
            ),
            mode='markers',
            marker=dict(size=20, color=['#3498db', '#2ecc71'])
        ))
        
        fig.update_layout(
            height=400,
            title=f"Conversion Rate with 95% CI - {exp['name']}",
            xaxis_title="Variant",
            yaxis_title="Conversion Rate",
            template='plotly_white',
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Guardrail metrics
        st.subheader("🛡️ Guardrail Metrics")
        
        guardrail_df = pd.DataFrame([
            {'Metric': k, 'Status': v} for k, v in exp['guardrails'].items()
        ])
        st.dataframe(guardrail_df, use_container_width=True)
        
        # Decision
        st.subheader("📋 Decision")
        
        if exp['p_value'] < 0.05:
            if exp['lift'] > 0:
                if all(v == '✅' for v in exp['guardrails'].values()):
                    st.success("✅ **SHIP**: Statistically significant positive result with clean guardrails")
                else:
                    st.warning("⚠️ **SHIP WITH CAUTION**: Positive result but guardrail concerns")
            else:
                st.error("❌ **KILL**: Statistically significant negative result")
        else:
            st.info("⏸️ **HOLD**: Not statistically significant - need more data")

# ---------------------------------------------------------------------
# POWER ANALYSIS CALCULATOR
# ---------------------------------------------------------------------

with st.expander("📊 Power Analysis Calculator"):
    st.markdown("""
    Calculate required sample size for your A/B test.
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        baseline_rate = st.slider(
            "Baseline Conversion Rate",
            min_value=0.01,
            max_value=0.50,
            value=0.28,
            step=0.01,
            format="%.0f%%"
        )
    
    with col2:
        mde = st.slider(
            "Minimum Detectable Effect (MDE)",
            min_value=0.005,
            max_value=0.10,
            value=0.02,
            step=0.005,
            format="%.1f%%"
        )
    
    with col3:
        power = st.slider(
            "Statistical Power",
            min_value=0.70,
            max_value=0.95,
            value=0.80,
            step=0.01
        )
    
    # Calculate sample size
    from scipy.stats import norm
    import math
    
    z_alpha = norm.ppf(1 - 0.05/2)
    z_beta = norm.ppf(power)
    p_pooled = baseline_rate + mde / 2
    
    n = (z_alpha * math.sqrt(2 * p_pooled * (1 - p_pooled)) + 
         z_beta * math.sqrt(baseline_rate * (1 - baseline_rate) + 
                            (baseline_rate + mde) * (1 - baseline_rate - mde))) ** 2 / (mde ** 2)
    
    n = int(math.ceil(n))
    total_n = n * 2
    
    st.metric(
        label="Required Sample Size (per group)",
        value=f"{n:,}",
        delta=f"Total: {total_n:,}"
    )
    
    st.caption(f"Based on α=0.05, power={power*100:.0f}%, baseline={baseline_rate*100:.0f}%, MDE={mde*100:.1f}%")

st.caption("📊 Experiment analysis based on A/B test data")