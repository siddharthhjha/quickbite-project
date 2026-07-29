"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Recommendations
==================================================================
Purpose: Consolidated product recommendations with business impact
analysis and prioritization.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.header("💡 Product Recommendations")
st.markdown("""
Data-driven recommendations to improve key business metrics.
Each recommendation includes expected impact and priority.
""")

# ---------------------------------------------------------------------
# RECOMMENDATIONS DATA
# ---------------------------------------------------------------------

recommendations = [
    {
        'id': 1,
        'title': 'Launch Referral Program for Champions',
        'category': 'Retention',
        'description': 'Target Champions with premium referral rewards to drive organic growth',
        'impact_revenue': 1500000,
        'impact_retention': 15,
        'effort': 'Medium',
        'priority': 'P0',
        'roi': 'High'
    },
    {
        'id': 2,
        'title': 'Win-Back Campaign for At-Risk Users',
        'category': 'Retention',
        'description': 'Urgent re-engagement with time-limited offers for users showing disengagement',
        'impact_revenue': 800000,
        'impact_retention': 25,
        'effort': 'Low',
        'priority': 'P0',
        'roi': 'High'
    },
    {
        'id': 3,
        'title': 'Optimize Checkout Flow',
        'category': 'Conversion',
        'description': 'Reduce friction at checkout with single-page UI and fewer clicks',
        'impact_revenue': 2000000,
        'impact_retention': 10,
        'effort': 'High',
        'priority': 'P0',
        'roi': 'Medium'
    },
    {
        'id': 4,
        'title': 'Implement Cross-Selling at Checkout',
        'category': 'Monetization',
        'description': 'Recommend complementary items based on purchase history and market basket',
        'impact_revenue': 1200000,
        'impact_retention': 5,
        'effort': 'Medium',
        'priority': 'P1',
        'roi': 'High'
    },
    {
        'id': 5,
        'title': 'Premium Membership Upsell',
        'category': 'Monetization',
        'description': 'Target high-engagement users with premium membership offers',
        'impact_revenue': 900000,
        'impact_retention': 20,
        'effort': 'Low',
        'priority': 'P1',
        'roi': 'High'
    },
    {
        'id': 6,
        'title': 'Optimize Delivery Experience',
        'category': 'Operations',
        'description': 'Improve delivery times and reduce cancellations through partner optimization',
        'impact_revenue': 600000,
        'impact_retention': 30,
        'effort': 'High',
        'priority': 'P1',
        'roi': 'Medium'
    },
    {
        'id': 7,
        'title': 'Personalized Search Results',
        'category': 'Product',
        'description': 'Use collaborative filtering to recommend relevant restaurants',
        'impact_revenue': 1000000,
        'impact_retention': 15,
        'effort': 'High',
        'priority': 'P2',
        'roi': 'Medium'
    },
    {
        'id': 8,
        'title': 'Payment Success Rate Improvement',
        'category': 'Conversion',
        'description': 'Reduce payment failures through better error handling and retries',
        'impact_revenue': 700000,
        'impact_retention': 12,
        'effort': 'Medium',
        'priority': 'P1',
        'roi': 'High'
    }
]

rec_df = pd.DataFrame(recommendations)

# ---------------------------------------------------------------------
# RECOMMENDATIONS OVERVIEW
# ---------------------------------------------------------------------

st.subheader("📊 Recommendations Overview")

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue_impact = rec_df['impact_revenue'].sum()
    st.metric("Total Revenue Impact", f"₹{total_revenue_impact:,.0f}")

with col2:
    avg_retention_impact = rec_df['impact_retention'].mean()
    st.metric("Avg Retention Impact", f"{avg_retention_impact:.0f}%")

with col3:
    p0_count = len(rec_df[rec_df['priority'] == 'P0'])
    st.metric("P0 Recommendations", p0_count)

with col4:
    high_roi = len(rec_df[rec_df['roi'] == 'High'])
    st.metric("High ROI", high_roi)

# ---------------------------------------------------------------------
# RECOMMENDATION DETAILS
# ---------------------------------------------------------------------

st.subheader("📋 All Recommendations")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    category_filter = st.multiselect(
        "Category",
        options=rec_df['category'].unique(),
        default=rec_df['category'].unique()
    )

with col2:
    priority_filter = st.multiselect(
        "Priority",
        options=['P0', 'P1', 'P2'],
        default=['P0', 'P1', 'P2']
    )

with col3:
    roi_filter = st.multiselect(
        "ROI",
        options=['High', 'Medium', 'Low'],
        default=['High', 'Medium', 'Low']
    )

# Apply filters
filtered_recs = rec_df[
    (rec_df['category'].isin(category_filter)) &
    (rec_df['priority'].isin(priority_filter)) &
    (rec_df['roi'].isin(roi_filter))
]

# Sort by priority
priority_order = {'P0': 0, 'P1': 1, 'P2': 2}
filtered_recs['priority_order'] = filtered_recs['priority'].map(priority_order)
filtered_recs = filtered_recs.sort_values(['priority_order', 'impact_revenue'], ascending=[True, False])

# Display cards
for _, rec in filtered_recs.iterrows():
    with st.expander(f"**{rec['priority']}** - {rec['title']}"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Description:** {rec['description']}")
            st.markdown(f"**Category:** {rec['category']}")
            st.markdown(f"**Effort:** {rec['effort']}")
        
        with col2:
            st.metric("Revenue Impact", f"₹{rec['impact_revenue']:,.0f}")
            st.metric("Retention Impact", f"+{rec['impact_retention']}%")
            st.metric("ROI", rec['roi'])

# ---------------------------------------------------------------------
# IMPACT VISUALIZATION
# ---------------------------------------------------------------------

st.subheader("📊 Impact Analysis")

# Revenue vs Retention scatter
fig = px.scatter(
    filtered_recs,
    x='impact_revenue',
    y='impact_retention',
    color='priority',
    size='impact_revenue',
    hover_data=['title'],
    title="Revenue Impact vs Retention Impact",
    labels={'impact_revenue': 'Revenue Impact (₹)', 'impact_retention': 'Retention Impact (%)'}
)

fig.update_layout(
    height=500,
    template='plotly_white'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# PRIORITIZATION MATRIX
# ---------------------------------------------------------------------

st.subheader("🎯 Prioritization Matrix")

# Create effort-impact matrix
effort_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
filtered_recs['effort_score'] = filtered_recs['effort'].map(effort_mapping)
filtered_recs['impact_score'] = (filtered_recs['impact_revenue'] / filtered_recs['impact_revenue'].max()) * 100

fig = px.scatter(
    filtered_recs,
    x='effort_score',
    y='impact_score',
    color='priority',
    size='impact_revenue',
    hover_data=['title'],
    title="Effort vs Impact Matrix",
    labels={'effort_score': 'Effort (Low→High)', 'impact_score': 'Relative Impact (%)'}
)

# Add quadrant lines
fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
fig.add_vline(x=2, line_dash="dash", line_color="gray", opacity=0.5)

fig.update_layout(
    height=500,
    template='plotly_white'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# IMPLEMENTATION ROADMAP
# ---------------------------------------------------------------------

st.subheader("🗓️ Implementation Roadmap")

# Group by priority
for priority in ['P0', 'P1', 'P2']:
    priority_recs = filtered_recs[filtered_recs['priority'] == priority]
    if len(priority_recs) > 0:
        with st.expander(f"**{priority}** - {len(priority_recs)} recommendations"):
            for _, rec in priority_recs.iterrows():
                st.markdown(f"""
                **{rec['title']}**
                - Revenue: ₹{rec['impact_revenue']:,.0f} | Retention: +{rec['impact_retention']}%
                - Effort: {rec['effort']} | ROI: {rec['roi']}
                - *{rec['description']}*
                ---
                """)

st.caption(f"📊 {len(filtered_recs)} recommendations shown")