"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: ER Diagram
==================================================================
Purpose: Visual representation of the database schema with
table relationships and key field indicators.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.header("🔗 Entity Relationship Diagram")
st.markdown("""
Visual representation of the database structure showing all
tables, their relationships, and key fields.
""")

# ---------------------------------------------------------------------
# ER DIAGRAM WITH PLOTLY
# ---------------------------------------------------------------------

st.subheader("📊 Database Schema")

# Define tables and their positions
tables = {
    'users': {'x': 0, 'y': 0, 'color': '#3498db'},
    'orders': {'x': 2, 'y': 0, 'color': '#2ecc71'},
    'order_items': {'x': 4, 'y': 0, 'color': '#f39c12'},
    'restaurants': {'x': 0, 'y': -2, 'color': '#e74c3c'},
    'cities': {'x': -2, 'y': 0, 'color': '#9b59b6'},
    'coupons': {'x': -2, 'y': 2, 'color': '#1abc9c'},
    'delivery_partners': {'x': 2, 'y': -2, 'color': '#e67e22'},
    'payments': {'x': 4, 'y': -2, 'color': '#e74c3c'}
}

# Define relationships
relationships = [
    ('users', 'orders', 'user_id'),
    ('users', 'cities', 'city_id'),
    ('users', 'referral', 'user_id'),
    ('orders', 'restaurants', 'restaurant_id'),
    ('orders', 'delivery_partners', 'delivery_partner_id'),
    ('orders', 'cities', 'city_id'),
    ('orders', 'coupons', 'coupon_id'),
    ('orders', 'payments', 'order_id'),
    ('orders', 'order_items', 'order_id'),
    ('restaurants', 'cities', 'city_id'),
    ('delivery_partners', 'cities', 'city_id')
]

# Create figure
fig = go.Figure()

# Add tables as nodes
for table_name, pos in tables.items():
    x, y = pos['x'], pos['y']
    color = pos['color']
    
    fig.add_trace(go.Scatter(
        x=[x],
        y=[y],
        mode='markers+text',
        marker=dict(
            size=50,
            color=color,
            symbol='square',
            line=dict(color='black', width=2)
        ),
        text=table_name,
        textposition='middle center',
        textfont=dict(size=12, color='white'),
        name=table_name,
        hovertext=f"Table: {table_name}",
        hoverinfo='text'
    ))

# Add relationships as lines
for rel in relationships:
    if len(rel) == 3:
        from_table, to_table, key = rel
        if from_table in tables and to_table in tables:
            x0, y0 = tables[from_table]['x'], tables[from_table]['y']
            x1, y1 = tables[to_table]['x'], tables[to_table]['y']
            
            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode='lines',
                line=dict(color='gray', width=1, dash='solid'),
                hovertext=f"{from_table}.{key} → {to_table}.{key}",
                hoverinfo='text',
                showlegend=False
            ))

fig.update_layout(
    height=600,
    title="Entity Relationship Diagram",
    template='plotly_white',
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        range=[-3, 5]
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        range=[-3, 3]
    ),
    hovermode='closest'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------
# TABLE LIST WITH RELATIONSHIPS
# ---------------------------------------------------------------------

st.subheader("📋 Table Relationships Reference")

# Create relationship table
rel_data = []
for rel in relationships:
    if len(rel) == 3:
        from_table, to_table, key = rel
        if from_table != 'referral' and to_table != 'referral':
            rel_data.append({
                'From Table': from_table,
                'To Table': to_table,
                'Foreign Key': key,
                'Relationship': f"One-to-Many" if from_table != to_table else "Self-referential"
            })

rel_df = pd.DataFrame(rel_data)
st.dataframe(rel_df, use_container_width=True)

# ---------------------------------------------------------------------
# TABLE DETAILS
# ---------------------------------------------------------------------

st.subheader("📊 Table Summary")

# Create table summary
table_summary = []
for table_name, pos in tables.items():
    table_summary.append({
        'Table': table_name,
        'Color': pos['color'],
        'X': pos['x'],
        'Y': pos['y'],
        'Relationships': len([r for r in relationships if r[0] == table_name or r[1] == table_name])
    })

summary_df = pd.DataFrame(table_summary)
st.dataframe(
    summary_df.style.background_gradient(cmap='Blues', subset=['Relationships']),
    use_container_width=True
)

# ---------------------------------------------------------------------
# KEY INSIGHTS
# ---------------------------------------------------------------------

with st.expander("💡 Schema Design Notes"):
    st.markdown("""
    **🔍 Schema Design Philosophy:**
    
    1. **OLTP vs Warehouse:**
       - OLTP schema optimized for transaction processing
       - Star schema (in data warehouse) optimized for analytics
    
    2. **Denormalization Strategy:**
       - Weather and traffic denormalized into orders for performance
       - City tier and category names available for easy filtering
    
    3. **Surrogate Keys:**
       - All tables use surrogate primary keys
       - Natural keys preserved for referential integrity
    
    4. **Time-Variant Data:**
       - Timestamps for all events
       - Date-based partitioning strategy
    
    5. **Exogenous Variables:**
       - Weather and traffic tables for operational context
       - Support tickets for customer experience analysis
    """)

st.caption("🔗 ER Diagram showing database relationships")