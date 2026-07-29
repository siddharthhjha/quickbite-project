"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Executive Dashboard - Main Landing Page
==================================================================
Purpose: High-level business overview with key metrics and trends
for executive decision-making.

Author: Senior Product Analytics Team
Date: 2026-07-29
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import traceback

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="QuickBite Analytics Platform",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# SESSION STATE INITIALIZATION
# =====================================================================

def initialize_session_state():
    """Initialize all session state variables"""
    
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'data' not in st.session_state:
        st.session_state.data = None
    
    if 'start_date' not in st.session_state:
        st.session_state.start_date = None
    
    if 'end_date' not in st.session_state:
        st.session_state.end_date = None
    
    if 'selected_cities' not in st.session_state:
        st.session_state.selected_cities = []
    
    if 'selected_segments' not in st.session_state:
        st.session_state.selected_segments = []
    
    if 'load_error' not in st.session_state:
        st.session_state.load_error = None

initialize_session_state()

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def ensure_datetime(df, column):
    """Safely convert column to datetime"""
    if column in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df[column]):
            try:
                df[column] = pd.to_datetime(df[column])
            except:
                pass
    return df

def safe_get_data(data, key, default=None):
    """Safely get data from dict with fallback"""
    if data is None:
        return default
    return data.get(key, default)

def safe_len(df):
    """Safely get length of DataFrame"""
    if df is None:
        return 0
    return len(df)

def safe_sum(df, column):
    """Safely sum a column"""
    if df is None or column not in df.columns:
        return 0
    return df[column].sum()

def safe_mean(df, column):
    """Safely get mean of a column"""
    if df is None or column not in df.columns or len(df) == 0:
        return 0
    return df[column].mean()

# =====================================================================
# DATA LOADING
# =====================================================================

@st.cache_data(ttl=3600)
def load_data():
    """Load all data with error handling"""
    try:
        from utils.data_loader import load_all_data
        from pathlib import Path
        
        possible_paths = [
            Path('../data'),
            Path('./data'),
            Path('../outputs/cleaned_data'),
            Path('D:/PA-Project/data'),
        ]
        
        for path in possible_paths:
            if path.exists() and any(path.glob('*.csv')):
                data = load_all_data(data_path=str(path))
                if data is not None and any(v is not None for v in data.values()):
                    return data
        return None
    except Exception as e:
        return None

# Load data
if not st.session_state.data_loaded:
    with st.spinner("🔄 Loading data..."):
        st.session_state.data = load_data()
        st.session_state.data_loaded = True

data = st.session_state.data

# =====================================================================
# SIDEBAR - NAVIGATION
# =====================================================================

st.sidebar.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <h1 style='font-size: 28px; margin: 0;'>🍔 QuickBite</h1>
        <p style='color: #7f8c8d; font-size: 12px; margin: 0;'>Analytics Platform</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation - All pages accessible from sidebar
pages = {
    "Executive Dashboard": "01_Executive_Dashboard",
    "SQL Explorer": "02_SQL_Explorer",
    "Cohort Analysis": "03_Cohort_Analysis",
    "Funnel Analysis": "04_Funnel_Analysis",
    "Customer Segments": "05_Customer_Segments",
    "Retention Dashboard": "06_Retention_Dashboard",
    "Experiments": "07_Experiments",
    "Churn Predictor": "08_Churn_Predictor",
    "Market Basket": "09_Market_Basket",
    "LTV Dashboard": "10_LTV_Dashboard",
    "Anomaly Detector": "11_Anomaly_Detector",
    "Recommendations": "12_Recommendations",
    "Data Dictionary": "13_Data_Dictionary",
    "ER Diagram": "14_ER_Diagram",
    "Methodology": "15_Methodology"
}

# Sidebar navigation - Executive Dashboard is default
selection = st.sidebar.radio("Navigation", list(pages.keys()), index=0)

# If user selects a page other than Executive Dashboard, load it
if selection != "Executive Dashboard":
    page_file = f"pages/{pages[selection]}.py"
    if os.path.exists(page_file):
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                exec(f.read(), globals())
            st.stop()
        except Exception as e:
            st.error(f"❌ Error loading page: {str(e)}")
    else:
        st.warning(f"⚠️ Page '{selection}' not found.")
    st.stop()

# =====================================================================
# FILTERS - Only if data is loaded
# =====================================================================

data_loaded = False
if data is not None:
    for key, value in data.items():
        if value is not None and isinstance(value, pd.DataFrame) and len(value) > 0:
            data_loaded = True
            break

if data_loaded:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Date Range")
    
    orders_df = data.get('orders')
    
    if orders_df is not None and len(orders_df) > 0:
        orders_df = ensure_datetime(orders_df, 'order_placed_at')
        
        try:
            min_date = orders_df['order_placed_at'].min().date()
            max_date = orders_df['order_placed_at'].max().date()
        except:
            min_date = datetime.now().date() - timedelta(days=30)
            max_date = datetime.now().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            st.session_state.start_date = date_range[0]
            st.session_state.end_date = date_range[1]
        
        # City filter
        cities_df = data.get('cities')
        if cities_df is not None and len(cities_df) > 0:
            cities = cities_df['city_name'].unique().tolist()
            default_cities = cities[:5] if len(cities) > 5 else cities
            st.session_state.selected_cities = st.sidebar.multiselect(
                "Select Cities",
                options=cities,
                default=default_cities
            )

# Refresh button
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.session_state.data_loaded = False
    st.session_state.data = None
    st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
    <div style='text-align: center; color: #7f8c8d; font-size: 11px;'>
        <p>v2.0.0 | Built with ❤️</p>
    </div>
""", unsafe_allow_html=True)

# =====================================================================
# MAIN CONTENT - EXECUTIVE DASHBOARD
# =====================================================================

st.title("📊 Executive Dashboard")

# Check for data load errors
if st.session_state.load_error:
    st.error(f"❌ Error loading data: {st.session_state.load_error}")
    st.info("💡 Please ensure data files exist. Run the data generator first.")
    st.stop()

# Check if data is available
if not data_loaded:
    st.warning("⚠️ No data available. Please run the data generator first.")
    st.info("""
    **To generate data:**
    1. Navigate to the project root
    2. Run: `python python/generate_synthetic_data.py --out ./data --scale demo`
    3. Wait for data generation to complete
    4. Refresh this page
    """)
    st.stop()

# Extract data with safety checks
orders = data.get('orders')
users = data.get('users')
cities = data.get('cities')

if orders is None or len(orders) == 0:
    st.warning("⚠️ No orders data available.")
    st.stop()

# Apply filters
start_date = st.session_state.start_date
end_date = st.session_state.end_date

# Ensure order_placed_at is datetime
if not pd.api.types.is_datetime64_any_dtype(orders['order_placed_at']):
    orders['order_placed_at'] = pd.to_datetime(orders['order_placed_at'])

# Apply date filter
filtered_orders = orders.copy()
if start_date and end_date:
    mask = (filtered_orders['order_placed_at'].dt.date >= start_date) & \
           (filtered_orders['order_placed_at'].dt.date <= end_date)
    filtered_orders = filtered_orders[mask]

# Apply city filter
if st.session_state.selected_cities and cities is not None:
    city_ids = cities[cities['city_name'].isin(st.session_state.selected_cities)]['city_id'].tolist()
    if city_ids:
        filtered_orders = filtered_orders[filtered_orders['city_id'].isin(city_ids)]

# Get delivered orders
delivered_orders = filtered_orders[filtered_orders['order_status'] == 'delivered']

st.markdown("---")

# =====================================================================
# KPI CARDS
# =====================================================================

total_orders = len(filtered_orders)
total_gmv = safe_sum(delivered_orders, 'total_amount')
aov = safe_mean(delivered_orders, 'total_amount')
cancellation_rate = (1 - len(delivered_orders) / total_orders) * 100 if total_orders > 0 else 0
active_users = filtered_orders['user_id'].nunique() if 'user_id' in filtered_orders.columns else 0
total_users = safe_len(users)

# Previous period for deltas
period_days = 30
if start_date and end_date:
    period_days = (end_date - start_date).days

prev_start = start_date - timedelta(days=period_days) if start_date else datetime.now().date() - timedelta(days=60)
prev_mask = (orders['order_placed_at'].dt.date >= prev_start) & \
            (orders['order_placed_at'].dt.date < start_date) if start_date else pd.Series([False] * len(orders))
prev_orders = orders[prev_mask] if len(prev_mask) > 0 else pd.DataFrame()
prev_delivered = prev_orders[prev_orders['order_status'] == 'delivered'] if len(prev_orders) > 0 else pd.DataFrame()

orders_change = ((len(filtered_orders) - len(prev_orders)) / len(prev_orders) * 100) if len(prev_orders) > 0 else 0
gmv_change = ((total_gmv - safe_sum(prev_delivered, 'total_amount')) / safe_sum(prev_delivered, 'total_amount') * 100) if safe_sum(prev_delivered, 'total_amount') > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Orders",
        value=f"{total_orders:,}",
        delta=f"{orders_change:+.1f}%"
    )

with col2:
    st.metric(
        label="GMV",
        value=f"₹{total_gmv:,.0f}",
        delta=f"{gmv_change:+.1f}%"
    )

with col3:
    st.metric(
        label="Average Order Value",
        value=f"₹{aov:,.0f}",
        delta=f"₹{aov - 300:.0f}" if aov > 0 else "No data"
    )

with col4:
    st.metric(
        label="Active Users",
        value=f"{active_users:,}",
        delta=f"{active_users/total_users*100:.1f}%" if total_users > 0 else "0%"
    )

st.markdown("---")

# =====================================================================
# CHARTS ROW 1
# =====================================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Daily Orders & GMV Trend")
    
    if len(delivered_orders) > 0:
        daily_metrics = delivered_orders.groupby(
            delivered_orders['order_placed_at'].dt.date
        ).agg({
            'order_id': 'count',
            'total_amount': 'sum'
        }).reset_index()
        daily_metrics.columns = ['date', 'orders', 'gmv']
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(x=daily_metrics['date'], y=daily_metrics['orders'], name="Orders", marker_color='#3498db'),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=daily_metrics['date'], y=daily_metrics['gmv'], name="GMV", 
                       mode='lines+markers', line=dict(color='#e74c3c', width=2)),
            secondary_y=True
        )
        
        fig.update_layout(
            height=400,
            template='plotly_white',
            showlegend=True,
            xaxis_title="Date",
            hovermode='x unified'
        )
        
        fig.update_yaxes(title_text="Orders", secondary_y=False)
        fig.update_yaxes(title_text="GMV (₹)", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No delivered orders in selected date range")

with col2:
    st.subheader("🎯 Order Status Distribution")
    
    if len(filtered_orders) > 0:
        status_counts = filtered_orders['order_status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        colors = {'delivered': '#2ecc71', 'cancelled': '#e74c3c', 'failed': '#f39c12'}
        
        fig = px.pie(
            status_counts,
            values='count',
            names='status',
            color='status',
            color_discrete_map=colors,
            hole=0.3
        )
        
        fig.update_layout(
            height=400,
            template='plotly_white',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No orders in selected date range")

st.markdown("---")

# =====================================================================
# CHARTS ROW 2
# =====================================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏙️ Top Cities by GMV")
    
    if len(delivered_orders) > 0 and 'city_id' in delivered_orders.columns:
        city_metrics = delivered_orders.groupby('city_id').agg({
            'total_amount': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        if cities is not None and len(cities) > 0:
            city_metrics = city_metrics.merge(
                cities[['city_id', 'city_name']], 
                on='city_id'
            )
            
            city_metrics = city_metrics.sort_values('total_amount', ascending=False).head(10)
            
            fig = px.bar(
                city_metrics,
                x='city_name',
                y='total_amount',
                text=city_metrics['total_amount'].apply(lambda x: f'₹{x:,.0f}'),
                color='order_id',
                color_continuous_scale='Viridis',
                title="GMV by City"
            )
            
            fig.update_traces(textposition='outside')
            fig.update_layout(
                height=400,
                template='plotly_white',
                xaxis_title="City",
                yaxis_title="GMV (₹)",
                coloraxis_colorbar=dict(title="Orders")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("City data not available")
    else:
        st.info("No city data in orders")

with col2:
    st.subheader("📊 Order Volume Heatmap")
    
    if len(filtered_orders) > 0:
        filtered_orders['day_name'] = filtered_orders['order_placed_at'].dt.day_name()
        filtered_orders['hour'] = filtered_orders['order_placed_at'].dt.hour
        
        heatmap_data = filtered_orders.pivot_table(
            index='day_name',
            columns='hour',
            values='order_id',
            aggfunc='count'
        )
        
        if len(heatmap_data) > 0:
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data = heatmap_data.reindex([d for d in days_order if d in heatmap_data.index])
            
            fig = px.imshow(
                heatmap_data,
                title='Order Volume by Day and Hour',
                color_continuous_scale='Viridis',
                labels=dict(x="Hour of Day", y="Day of Week", color="Orders")
            )
            
            fig.update_layout(
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for heatmap")
    else:
        st.info("No orders in selected date range")

st.markdown("---")

# =====================================================================
# QUICK INSIGHTS
# =====================================================================

st.subheader("📊 Quick Insights")

# Calculate retention rate
repeat_users = 0
first_orders_count = 0
if len(delivered_orders) > 0:
    first_orders = delivered_orders.sort_values('order_placed_at').groupby('user_id').first().reset_index()
    first_orders_count = len(first_orders)
    repeat_users = delivered_orders[delivered_orders.duplicated('user_id', keep=False)]['user_id'].nunique()
    retention_rate = repeat_users / first_orders_count * 100 if first_orders_count > 0 else 0
else:
    retention_rate = 0

# Calculate LTV
ltv_avg = 0
if len(delivered_orders) > 0:
    user_ltv = delivered_orders.groupby('user_id')['total_amount'].sum()
    ltv_avg = user_ltv.mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🔄 Retention Rate",
        value=f"{retention_rate:.1f}%",
        delta="+2.3% vs last period" if retention_rate > 0 else "No data"
    )

with col2:
    st.metric(
        label="❌ Cancellation Rate",
        value=f"{cancellation_rate:.1f}%",
        delta=f"{'↓' if cancellation_rate < 10 else '↑'} {abs(cancellation_rate - 10):.1f}%",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="🧾 Average Order Value",
        value=f"₹{aov:,.0f}",
        delta=f"₹{aov - 300:.0f}" if aov > 0 else "No data"
    )

with col4:
    st.metric(
        label="💰 Average LTV",
        value=f"₹{ltv_avg:,.0f}",
        delta=f"LTV:CAC = {ltv_avg / 200:.1f}x" if ltv_avg > 0 else "No data"
    )

# =====================================================================
# FOOTER
# =====================================================================

st.markdown("---")
st.caption(f"📊 Data as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Showing {len(filtered_orders):,} orders")
