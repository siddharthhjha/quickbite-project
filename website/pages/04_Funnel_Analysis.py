"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Funnel Analysis
==================================================================
Purpose: Interactive funnel visualization using real events data
when available.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Get data from session state
data = st.session_state.data

# Extract data
orders = data.get('orders') if data else None
users = data.get('users') if data else None

st.header("🎯 Funnel Analysis")
st.markdown("""
Visualize the user journey from app open to order completion.
Identify where users drop off and optimize the conversion path.
""")

# =====================================================================
# LOAD EVENTS DATA
# =====================================================================

events = None
events_loaded = False

# Try multiple paths
event_paths = [
    Path('../data/events.csv'),
    Path('./data/events.csv'),
    Path('../outputs/cleaned_data/events.csv'),
    Path('./outputs/cleaned_data/events.csv'),
    Path('D:/PA-Project/data/events.csv'),
]

for path in event_paths:
    if path.exists():
        try:
            events = pd.read_csv(path)
            events['event_timestamp'] = pd.to_datetime(events['event_timestamp'])
            st.success(f"✅ Loaded {len(events):,} events from {path.name}")
            events_loaded = True
            break
        except Exception as e:
            st.warning(f"⚠️ Error loading events from {path}: {e}")

# =====================================================================
# FUNNEL DEFINITION
# =====================================================================

funnel_steps = ['app_open', 'search', 'view_restaurant', 'view_menu', 
                'add_to_cart', 'checkout_start', 'payment_start', 'order_placed']
funnel_labels = ['App Open', 'Search', 'View Restaurant', 'View Menu', 
                 'Add to Cart', 'Checkout Start', 'Payment Start', 'Order Placed']

# =====================================================================
# CALCULATE FUNNEL
# =====================================================================

if events_loaded and events is not None and len(events) > 0:
    # Use REAL events data
    with st.spinner("Calculating funnel from events data..."):
        funnel_data = []
        for i, step in enumerate(funnel_steps):
            users_at_step = events[events['event_name'] == step]['user_id'].nunique()
            funnel_data.append({'step': funnel_labels[i], 'users': users_at_step})
        
        funnel_df = pd.DataFrame(funnel_data)
        st.info("📊 Using real events data for funnel")
else:
    # Use SYNTHETIC funnel from orders
    st.info("📊 Using synthetic funnel based on orders data")
    
    if orders is None or len(orders) == 0:
        st.warning("⚠️ No orders data available.")
        st.stop()
    
    delivered_orders = orders[orders['order_status'] == 'delivered']
    
    # Calculate from real orders
    total_users = len(users) if users is not None else 1000
    users_with_orders = len(delivered_orders['user_id'].unique()) if len(delivered_orders) > 0 else 0
    
    # Distribute users across steps (realistic estimates)
    funnel_data = [
        {'step': 'App Open', 'users': total_users},
        {'step': 'Search', 'users': int(total_users * 0.85)},
        {'step': 'View Restaurant', 'users': int(total_users * 0.70)},
        {'step': 'View Menu', 'users': int(total_users * 0.60)},
        {'step': 'Add to Cart', 'users': int(total_users * 0.45)},
        {'step': 'Checkout Start', 'users': int(total_users * 0.32)},
        {'step': 'Payment Start', 'users': int(total_users * 0.27)},
        {'step': 'Order Placed', 'users': users_with_orders}
    ]
    
    funnel_df = pd.DataFrame(funnel_data)

# =====================================================================
# ENSURE FUNNEL IS LOGICAL
# =====================================================================

# Fix: Order Placed should not exceed Checkout Start
if len(funnel_df) > 1:
    order_idx = len(funnel_df) - 1
    checkout_idx = len(funnel_df) - 3  # Checkout Start is 3 from end
    
    if funnel_df.iloc[order_idx]['users'] > funnel_df.iloc[checkout_idx]['users']:
        # Set Order Placed to 80% of Checkout Start
        funnel_df.iloc[order_idx, funnel_df.columns.get_loc('users')] = int(funnel_df.iloc[checkout_idx]['users'] * 0.8)
        st.warning("⚠️ Adjusted funnel: Order Placed capped at 80% of Checkout Start")

# =====================================================================
# CALCULATE CONVERSION METRICS
# =====================================================================

funnel_df['conversion_from_start'] = funnel_df['users'] / funnel_df['users'].iloc[0] * 100
funnel_df['conversion_from_previous'] = 100.0
if len(funnel_df) > 1:
    for i in range(1, len(funnel_df)):
        prev = funnel_df.iloc[i-1]['users']
        curr = funnel_df.iloc[i]['users']
        funnel_df.iloc[i, funnel_df.columns.get_loc('conversion_from_previous')] = (curr / prev * 100) if prev > 0 else 0

funnel_df['drop_off'] = 100 - funnel_df['conversion_from_previous']
funnel_df.iloc[0, funnel_df.columns.get_loc('drop_off')] = 0

# =====================================================================
# VISUALIZE FUNNEL
# =====================================================================

st.subheader("📊 Conversion Funnel")

fig = go.Figure()

fig.add_trace(go.Funnel(
    name="User Journey",
    y=funnel_df['step'],
    x=funnel_df['users'],
    textinfo="value+percent initial",
    textposition="inside",
    marker=dict(
        color=['#2ecc71', '#2ecc71', '#2ecc71', '#f1c40f', 
               '#f39c12', '#e67e22', '#e74c3c', '#e74c3c'],
        line=dict(width=2)
    ),
    connector=dict(line=dict(color="royalblue", width=2))
))

fig.update_layout(
    height=500,
    title="End-to-End Conversion Funnel",
    template='plotly_white',
    margin=dict(l=0, r=0, t=50, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# CONVERSION METRICS
# =====================================================================

st.subheader("📈 Conversion Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    overall_conversion = funnel_df['conversion_from_start'].iloc[-1]
    st.metric(
        label="Overall Conversion",
        value=f"{overall_conversion:.1f}%",
        delta="App Open → Order"
    )

with col2:
    cart_to_order = funnel_df['conversion_from_previous'].iloc[-1]
    st.metric(
        label="Cart → Order",
        value=f"{cart_to_order:.1f}%",
        delta="Cart to order"
    )

with col3:
    checkout_to_payment = funnel_df['conversion_from_previous'].iloc[-2] if len(funnel_df) > 1 else 0
    st.metric(
        label="Checkout → Payment",
        value=f"{checkout_to_payment:.1f}%",
        delta="Checkout to payment"
    )

with col4:
    biggest_drop = funnel_df.loc[funnel_df['drop_off'].idxmax(), 'step'] if len(funnel_df) > 1 else "N/A"
    st.metric(
        label="Biggest Drop-off",
        value=biggest_drop,
        delta=f"{funnel_df['drop_off'].max():.1f}% drop"
    )

# =====================================================================
# DROP-OFF ANALYSIS
# =====================================================================

st.subheader("📉 Drop-off Analysis")

drop_off_df = funnel_df[funnel_df['drop_off'] > 0].copy()
drop_off_df = drop_off_df.sort_values('drop_off', ascending=True)

fig = go.Figure()

fig.add_trace(go.Bar(
    x=drop_off_df['drop_off'],
    y=drop_off_df['step'],
    orientation='h',
    marker=dict(
        color=['#e74c3c' if x > 30 else '#f39c12' if x > 15 else '#2ecc71' 
               for x in drop_off_df['drop_off']],
        line=dict(width=1)
    ),
    text=drop_off_df['drop_off'].round(1).astype(str) + '%',
    textposition='outside'
))

fig.update_layout(
    height=400,
    title="Step-by-Step Drop-off Rate",
    xaxis_title="Drop-off Rate (%)",
    yaxis_title="Funnel Step",
    template='plotly_white',
    xaxis=dict(range=[0, 100])
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# KEY INSIGHTS
# =====================================================================

with st.expander("💡 Key Insights & Recommendations"):
    drop_off_1 = funnel_df.iloc[1]['drop_off'] if len(funnel_df) > 1 else 0
    drop_off_2 = funnel_df.iloc[2]['drop_off'] if len(funnel_df) > 2 else 0
    drop_off_3 = funnel_df.iloc[3]['drop_off'] if len(funnel_df) > 3 else 0
    
    st.markdown(f"""
    **🔍 Key Findings:**
    
    1. **Biggest Drop-off Points:**
       - {funnel_df.iloc[1]['step']}: {drop_off_1:.1f}% drop-off
       - {funnel_df.iloc[2]['step']}: {drop_off_2:.1f}% drop-off
       - {funnel_df.iloc[3]['step']}: {drop_off_3:.1f}% drop-off
    
    2. **Overall Health:**
       - Overall Conversion: {overall_conversion:.1f}%
       - {'✅' if overall_conversion > 20 else '⚠️'} Industry benchmark: 15-25%
       - {'✅' if cart_to_order > 30 else '⚠️'} Cart to Order: {cart_to_order:.1f}%
    
    **🎯 Recommendations:**
    
    1. **Fix Top Drop-off Points:**
       - Search → View: Improve search relevance
       - View → Add to Cart: Better menu UX
       - Add to Cart → Checkout: Lower delivery fees
    
    2. **Quick Wins:**
       - Cart abandonment emails
       - Payment process optimization
       - Better restaurant recommendations
    """)

st.caption(f"📊 Funnel analysis from {'events' if events_loaded else 'orders'} data")