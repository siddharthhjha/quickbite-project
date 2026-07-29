"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: SQL Explorer
==================================================================
Purpose: Interactive SQL query execution with results visualization
and query library.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime
import tempfile
import os
import traceback

# Get data from session state
data = st.session_state.data

st.header("🔍 SQL Explorer")
st.markdown("""
Run custom SQL queries against the QuickBite database. 
[View the query library](#query-library) for examples.
""")

# =====================================================================
# CREATE SQLITE DATABASE - THREAD-SAFE
# =====================================================================

def create_sqlite_db():
    """Create a thread-safe SQLite connection"""
    
    # Use a temporary file for thread safety
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    conn = sqlite3.connect(temp_db.name, check_same_thread=False)
    
    # Load all tables from data
    for table_name, df in data.items():
        if isinstance(df, pd.DataFrame) and df is not None and len(df) > 0:
            # Clean column names for SQLite compatibility
            df_clean = df.copy()
            df_clean.columns = [col.replace(' ', '_').replace('-', '_') for col in df_clean.columns]
            
            # Save to SQLite
            df_clean.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"   ✅ Loaded table: {table_name} ({len(df_clean):,} rows)")
    
    conn.commit()
    
    # Store connection info in session state
    st.session_state.db_path = temp_db.name
    st.session_state.db_created = True
    
    return conn

# =====================================================================
# GET OR CREATE DB CONNECTION
# =====================================================================

@st.cache_resource
def get_db_connection():
    """Get or create SQLite connection (thread-safe)"""
    
    if not hasattr(st.session_state, 'db_created'):
        st.session_state.db_created = False
    
    if not st.session_state.db_created:
        conn = create_sqlite_db()
        return conn
    
    # Reconnect to existing database
    try:
        conn = sqlite3.connect(st.session_state.db_path, check_same_thread=False)
        return conn
    except:
        # If connection fails, recreate
        conn = create_sqlite_db()
        return conn

# =====================================================================
# QUERY EXECUTION FUNCTION
# =====================================================================

def execute_query(conn, query):
    """Execute query and return results"""
    
    # Get a cursor
    cursor = conn.cursor()
    
    try:
        # Execute query
        cursor.execute(query)
        
        # Check if SELECT query
        if query.strip().upper().startswith('SELECT'):
            # Fetch results
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            if results:
                df = pd.DataFrame(results, columns=columns)
                return {'success': True, 'data': df, 'rows': len(df)}
            else:
                return {'success': True, 'data': pd.DataFrame(columns=columns), 'rows': 0}
        else:
            # For INSERT/UPDATE/DELETE
            conn.commit()
            rows_affected = cursor.rowcount
            return {'success': True, 'data': None, 'rows_affected': rows_affected, 'message': f'Query executed successfully. {rows_affected} rows affected.'}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

# =====================================================================
# QUERY PRESETS
# =====================================================================

query_presets = {
    "Select all orders": "SELECT * FROM orders LIMIT 100",
    "Daily order volume": """
        SELECT 
            DATE(order_placed_at) as order_date,
            COUNT(*) as orders,
            SUM(total_amount) as gmv
        FROM orders
        WHERE order_status = 'delivered'
        GROUP BY DATE(order_placed_at)
        ORDER BY order_date DESC
    """,
    "Top cities by orders": """
        SELECT 
            c.city_name,
            COUNT(o.order_id) as orders,
            SUM(o.total_amount) as gmv
        FROM orders o
        JOIN cities c ON o.city_id = c.city_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.city_name
        ORDER BY orders DESC
    """,
    "Churn rate by channel": """
        WITH last_order AS (
            SELECT 
                user_id,
                MAX(DATE(order_placed_at)) as last_order_date
            FROM orders
            WHERE order_status = 'delivered'
            GROUP BY user_id
        )
        SELECT 
            u.acquisition_channel,
            COUNT(*) as total_users,
            SUM(CASE 
                WHEN lo.last_order_date < DATE('now', '-90 days') 
                OR lo.last_order_date IS NULL 
                THEN 1 ELSE 0 
            END) as churned_users,
            ROUND(100.0 * SUM(CASE 
                WHEN lo.last_order_date < DATE('now', '-90 days') 
                OR lo.last_order_date IS NULL 
                THEN 1 ELSE 0 
            END) / COUNT(*), 2) as churn_rate
        FROM users u
        LEFT JOIN last_order lo ON u.user_id = lo.user_id
        GROUP BY u.acquisition_channel
        ORDER BY churn_rate DESC
    """,
    "Funnel conversion": """
        WITH session_funnel AS (
            SELECT 
                session_id,
                MAX(CASE WHEN event_name = 'view_restaurant' THEN 1 ELSE 0 END) as viewed,
                MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) as added,
                MAX(CASE WHEN event_name = 'checkout_start' THEN 1 ELSE 0 END) as checkout,
                MAX(CASE WHEN event_name = 'payment_start' THEN 1 ELSE 0 END) as payment,
                MAX(CASE WHEN event_name = 'order_placed' THEN 1 ELSE 0 END) as ordered
            FROM events
            GROUP BY session_id
        )
        SELECT 
            COUNT(*) as total_sessions,
            SUM(viewed) as step1_viewed,
            SUM(added) as step2_added,
            SUM(checkout) as step3_checkout,
            SUM(payment) as step4_payment,
            SUM(ordered) as step5_ordered,
            ROUND(100.0 * SUM(added) / NULLIF(SUM(viewed), 0), 1) as view_to_cart,
            ROUND(100.0 * SUM(checkout) / NULLIF(SUM(added), 0), 1) as cart_to_checkout,
            ROUND(100.0 * SUM(payment) / NULLIF(SUM(checkout), 0), 1) as checkout_to_payment,
            ROUND(100.0 * SUM(ordered) / NULLIF(SUM(payment), 0), 1) as payment_to_order
        FROM session_funnel
    """
}

# =====================================================================
# MAIN UI
# =====================================================================

# Query mode
query_mode = st.radio("Query Mode", ["Write your own", "Use preset"], horizontal=True)

if query_mode == "Use preset":
    preset_name = st.selectbox("Select a preset query", list(query_presets.keys()))
    query = query_presets[preset_name]
    st.code(query, language='sql')
else:
    query = st.text_area(
        "Enter your SQL query",
        value="SELECT * FROM orders LIMIT 10",
        height=200
    )

# Execute button
col1, col2 = st.columns([1, 3])
with col1:
    execute = st.button("▶️ Execute Query", type="primary", use_container_width=True)

if execute and query.strip():
    with st.spinner("Executing query..."):
        try:
            # Get database connection
            conn = get_db_connection()
            
            # Execute query
            result = execute_query(conn, query)
            
            if result['success']:
                if 'data' in result and result['data'] is not None:
                    # Display results
                    df = result['data']
                    st.subheader(f"📊 Results ({result['rows']} rows)")
                    
                    # Data preview
                    st.dataframe(df, use_container_width=True)
                    
                    # Download buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        # Create Excel file
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False, sheet_name='Query Results')
                        excel_data = output.getvalue()
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_data,
                            file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    # Basic statistics
                    with st.expander("📈 Basic Statistics"):
                        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                        if len(numeric_cols) > 0:
                            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                    
                    # Visualization option
                    with st.expander("📊 Quick Visualization"):
                        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                        categorical_cols = df.select_dtypes(include=['object']).columns
                        
                        if len(numeric_cols) > 0 and len(categorical_cols) > 0:
                            import plotly.express as px
                            viz_type = st.selectbox("Select visualization type", ["Bar Chart", "Line Chart", "Scatter Plot"])
                            x_col = st.selectbox("X Axis", categorical_cols.tolist() + numeric_cols.tolist())
                            y_col = st.selectbox("Y Axis", numeric_cols.tolist())
                            
                            if viz_type == "Bar Chart":
                                fig = px.bar(df, x=x_col, y=y_col)
                            elif viz_type == "Line Chart":
                                fig = px.line(df, x=x_col, y=y_col)
                            else:
                                fig = px.scatter(df, x=x_col, y=y_col)
                            
                            st.plotly_chart(fig, use_container_width=True)
                    
                elif 'message' in result:
                    st.success(result['message'])
                else:
                    st.info("Query executed successfully but returned no results.")
            else:
                st.error(f"❌ Query execution failed: {result['error']}")
                st.code(query, language='sql')
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.code(traceback.format_exc())

# =====================================================================
# QUERY LIBRARY
# =====================================================================

st.markdown("---")
st.subheader("📚 Query Library")

with st.expander("View all preset queries"):
    for name, sql in query_presets.items():
        st.markdown(f"**{name}**")
        st.code(sql, language='sql')
        st.markdown("---")

# =====================================================================
# TABLE SCHEMA EXPLORER
# =====================================================================

st.subheader("🗂️ Database Schema")

with st.expander("📋 View table schemas"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get table list
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            schema = cursor.fetchall()
            
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            st.markdown(f"**{table_name}** ({len(schema)} columns, {row_count:,} rows)")
            
            schema_df = pd.DataFrame(schema, columns=['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk'])
            schema_df = schema_df[['name', 'type', 'notnull', 'pk']]
            schema_df['notnull'] = schema_df['notnull'].map({0: '❌', 1: '✅'})
            schema_df['pk'] = schema_df['pk'].map({0: '', 1: '🔑'})
            
            st.dataframe(schema_df, use_container_width=True)
            st.markdown("---")
            
    except Exception as e:
        st.error(f"Error loading schema: {str(e)}")

st.caption("🛡️ Read-only mode. All data is loaded in-memory from CSV files.")