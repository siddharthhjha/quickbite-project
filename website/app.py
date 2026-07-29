"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Main Application - Streamlit Implementation
==================================================================
Purpose: Main entry point for the analytics platform with navigation
and shared configurations.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import traceback

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="QuickBite Analytics Platform",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def ensure_datetime(df, column):
    """Safely convert column to datetime"""
    if column in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df[column]):
            try:
                df[column] = pd.to_datetime(df[column])
                print(f"   ✅ Converted {column} to datetime")
            except Exception as e:
                print(f"   ⚠️ Could not convert {column}: {e}")
    return df

def safe_date_min(df, column):
    """Safely get min date from column"""
    df = ensure_datetime(df, column)
    if column in df.columns and len(df) > 0:
        try:
            return df[column].min().date()
        except:
            return datetime.now().date() - timedelta(days=30)
    return datetime.now().date() - timedelta(days=30)

def safe_date_max(df, column):
    """Safely get max date from column"""
    df = ensure_datetime(df, column)
    if column in df.columns and len(df) > 0:
        try:
            return df[column].max().date()
        except:
            return datetime.now().date()
    return datetime.now().date()

# =====================================================================
# SESSION STATE INITIALIZATION
# =====================================================================

def initialize_session_state():
    """Initialize all session state variables"""
    
    # Data loading flags
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'data' not in st.session_state:
        st.session_state.data = None
    
    if 'models' not in st.session_state:
        st.session_state.models = None
    
    # Date filters
    if 'start_date' not in st.session_state:
        st.session_state.start_date = None
    
    if 'end_date' not in st.session_state:
        st.session_state.end_date = None
    
    # City and segment filters
    if 'selected_cities' not in st.session_state:
        st.session_state.selected_cities = []
    
    if 'selected_segments' not in st.session_state:
        st.session_state.selected_segments = []
    
    # Error state
    if 'load_error' not in st.session_state:
        st.session_state.load_error = None

# Initialize session state
initialize_session_state()

# =====================================================================
# LOAD CUSTOM CSS
# =====================================================================

def load_css():
    """Load custom CSS styles"""
    css_path = 'assets/css/style.css'
    if os.path.exists(css_path):
        try:
            with open(css_path) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except:
            pass
    else:
        # Fallback minimal styling
        st.markdown("""
            <style>
            .main { padding: 0px 20px; }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            .stMetric { background: #f8f9fa; padding: 10px; border-radius: 5px; }
            </style>
        """, unsafe_allow_html=True)

load_css()

# =====================================================================
# DATA LOADING FUNCTION
# =====================================================================

@st.cache_data(ttl=3600)
def load_data():
    """Load all data with error handling"""
    try:
        from utils.data_loader import load_all_data
        from pathlib import Path
        
        # Try multiple paths
        possible_paths = [
            Path('../data'),
            Path('./data'),
            Path('../outputs/cleaned_data'),
            Path('./outputs/cleaned_data'),
            Path('D:/PA-Project/data'),
        ]
        
        data = None
        for path in possible_paths:
            if path.exists() and any(path.glob('*.csv')):
                print(f"🔍 Found data at: {path}")
                data = load_all_data(data_path=str(path))
                if data is not None and any(v is not None for v in data.values()):
                    break
        
        if data is None or all(v is None for v in data.values()):
            return None
        
        # Ensure date columns are properly converted
        if 'orders' in data and data['orders'] is not None:
            data['orders'] = ensure_datetime(data['orders'], 'order_placed_at')
        
        if 'users' in data and data['users'] is not None:
            data['users'] = ensure_datetime(data['users'], 'signup_date')
            data['users'] = ensure_datetime(data['users'], 'premium_start_date')
            data['users'] = ensure_datetime(data['users'], 'churned_at')
        
        if 'restaurants' in data and data['restaurants'] is not None:
            data['restaurants'] = ensure_datetime(data['restaurants'], 'onboarded_date')
        
        if 'payments' in data and data['payments'] is not None:
            data['payments'] = ensure_datetime(data['payments'], 'processed_at')
        
        return data
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return None

@st.cache_resource
def load_models_cached():
    """Load models with caching"""
    try:
        from utils.data_loader import load_models
        return load_models()
    except Exception as e:
        print(f"⚠️ Could not load models: {str(e)}")
        return {}

# =====================================================================
# LOAD DATA
# =====================================================================

# Load data if not already loaded
if not st.session_state.data_loaded:
    with st.spinner("🔄 Loading data..."):
        try:
            st.session_state.data = load_data()
            st.session_state.models = load_models_cached()
            st.session_state.data_loaded = True
            
            if st.session_state.data is None or all(v is None for v in st.session_state.data.values()):
                st.session_state.load_error = "No data loaded. Please check data directory."
            else:
                st.session_state.load_error = None
        except Exception as e:
            st.session_state.load_error = str(e)
            st.session_state.data_loaded = True

# =====================================================================
# SIDEBAR - NAVIGATION AND FILTERS
# =====================================================================

# Logo/Header
st.sidebar.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <h1 style='font-size: 28px; margin: 0;'>🍔 QuickBite</h1>
        <p style='color: #7f8c8d; font-size: 12px; margin: 0;'>Analytics Platform</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation
pages = {
    "📊 Executive Dashboard": "01_Executive_Dashboard",
    "🔍 SQL Explorer": "02_SQL_Explorer",
    "📈 Cohort Analysis": "03_Cohort_Analysis",
    "🎯 Funnel Analysis": "04_Funnel_Analysis",
    "👥 Customer Segments": "05_Customer_Segments",
    "🔄 Retention Dashboard": "06_Retention_Dashboard",
    "🧪 Experiments": "07_Experiments",
    "⚠️ Churn Predictor": "08_Churn_Predictor",
    "🛒 Market Basket": "09_Market_Basket",
    "💰 LTV Dashboard": "10_LTV_Dashboard",
    "🚨 Anomaly Detector": "11_Anomaly_Detector",
    "💡 Recommendations": "12_Recommendations",
    "📚 Data Dictionary": "13_Data_Dictionary",
    "🔗 ER Diagram": "14_ER_Diagram",
    "📖 Methodology": "15_Methodology",
    "💡 Recommendations Dashboard": "16_Recommendations_Dashboard",
    "📈 Business Impact": "17_Business_Impact"
}

selection = st.sidebar.radio("Navigation", list(pages.keys()))

# =====================================================================
# FILTERS - Only if data is loaded
# =====================================================================

data = st.session_state.data

# Check if data is loaded properly
data_loaded = False
if data is not None:
    # Check if we have actual data (not all None)
    has_data = False
    for key, value in data.items():
        if value is not None and isinstance(value, pd.DataFrame) and len(value) > 0:
            has_data = True
            break
    data_loaded = has_data

if data_loaded:
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Date Range")
    
    orders_df = data.get('orders')
    
    if orders_df is not None and len(orders_df) > 0:
        # Ensure order_placed_at is datetime
        orders_df = ensure_datetime(orders_df, 'order_placed_at')
        
        try:
            min_date = orders_df['order_placed_at'].min().date()
            max_date = orders_df['order_placed_at'].max().date()
        except:
            # Fallback if date conversion fails
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
        
        # Segment filter
        rfm_df = data.get('rfm')
        if rfm_df is not None and len(rfm_df) > 0:
            segments = rfm_df['segment'].unique().tolist()
            default_segments = segments[:5] if len(segments) > 5 else segments
            st.session_state.selected_segments = st.sidebar.multiselect(
                "Select Segments",
                options=segments,
                default=default_segments
            )
    else:
        st.sidebar.warning("⚠️ No orders data available")
else:
    st.sidebar.warning("⚠️ Data not loaded. Please check data files.")

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
        <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
""", unsafe_allow_html=True)

# =====================================================================
# MAIN CONTENT
# =====================================================================

st.title("🍔 QuickBite Product Analytics Platform")

# Check for data load errors
if st.session_state.load_error:
    st.error(f"❌ Error loading data: {st.session_state.load_error}")
    st.info("💡 Please ensure data files exist. Run the data generator first:")
    st.code("""
    # From project root:
    python python/generate_synthetic_data.py --out ./data --scale demo
    """)
    st.stop()

# Check if data is available
if not data_loaded:
    st.warning("⚠️ No data available. Please run the data generator first.")
    st.info("""
    **To generate data:**
    1. Navigate to the project root: `cd D:\\PA-Project`
    2. Run: `python python/generate_synthetic_data.py --out ./data --scale demo`
    3. Wait for data generation to complete
    4. Refresh this page
    """)
    
    # Show data directory contents for debugging
    import os
    from pathlib import Path
    st.subheader("🔍 Debug: Checking Data Directories")
    
    paths_to_check = [
        Path('../data'),
        Path('./data'),
        Path('../outputs/cleaned_data'),
        Path('./outputs/cleaned_data'),
        Path('D:/PA-Project/data'),
    ]
    
    for path in paths_to_check:
        if path.exists():
            csv_files = list(path.glob('*.csv'))
            st.write(f"📁 {path}: {len(csv_files)} CSV files")
            if csv_files:
                st.write(f"   Files: {', '.join([f.name for f in csv_files[:5]])}")
        else:
            st.write(f"❌ {path}: Directory not found")
    
    st.stop()

# Display summary
if st.session_state.start_date and st.session_state.end_date:
    st.markdown(f"""
        <div style='background: #f8f9fa; padding: 10px 20px; border-radius: 5px; margin-bottom: 20px;'>
            <span style='font-weight: 600;'>📊 Data Range:</span> 
            {st.session_state.start_date} to {st.session_state.end_date} &nbsp;|&nbsp;
            <span style='font-weight: 600;'>🏙️ Cities:</span> 
            {len(st.session_state.selected_cities)} selected &nbsp;|&nbsp;
            <span style='font-weight: 600;'>👥 Segments:</span> 
            {len(st.session_state.selected_segments)} selected
        </div>
    """, unsafe_allow_html=True)

# =====================================================================
# LOAD AND EXECUTE THE SELECTED PAGE
# =====================================================================

page_file = f"pages/{pages[selection]}.py"

if os.path.exists(page_file):
    try:
        # Read with utf-8 encoding
        with open(page_file, 'r', encoding='utf-8-sig') as f:
            page_code = f.read()
        
        # Execute the page
        exec_globals = {
            'st': st,
            'pd': pd,
            'np': np,
            'px': px,
            'go': go,
            'datetime': datetime,
            'timedelta': timedelta,
            'data': data if data_loaded else {},
            'st_session_state': st.session_state
        }
        exec(page_code, exec_globals, {})
        
    except UnicodeDecodeError:
        # If utf-8 fails, try reading as binary and decoding with different encodings
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(page_file, 'r', encoding=encoding) as f:
                    page_code = f.read()
                exec(page_code, exec_globals, {})
                break
            except:
                continue
        else:
            st.error("❌ Could not read page file due to encoding issues")
            st.info("💡 Try running: python fix_encoding.py")
            
    except Exception as e:
        st.error(f"❌ Error loading page: {str(e)}")
        st.code(traceback.format_exc())
else:
    st.warning(f"⚠️ Page '{selection}' is under construction.")
    st.info("""
    **Coming Soon!**
    This page is being developed. Check back later.
    """)

# =====================================================================
# FOOTER
# =====================================================================

st.markdown("---")
st.caption(f"🛡️ Data as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | QuickBite Analytics Platform v2.0")