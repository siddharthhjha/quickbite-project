"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Utils: Visualizations
==================================================================
Purpose: Reusable visualization components for all pages.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_metric_card(label, value, delta=None, delta_color='normal', icon=None):
    """
    Create a metric card with consistent styling
    """
    if icon:
        label = f"{icon} {label}"
    
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def create_trend_chart(df, x_col, y_col, title=None, color=None, 
                       show_ma=False, ma_window=7):
    """
    Create a trend chart with optional moving average
    """
    fig = go.Figure()
    
    # Main trend
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines+markers',
        name=y_col,
        line=dict(color=color or '#3498db', width=2),
        marker=dict(size=6)
    ))
    
    # Moving average
    if show_ma and len(df) >= ma_window:
        ma = df[y_col].rolling(window=ma_window, center=True).mean()
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=ma,
            mode='lines',
            name=f'{ma_window}-day MA',
            line=dict(color='#e74c3c', width=2, dash='dash')
        ))
    
    fig.update_layout(
        title=title,
        template='plotly_white',
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_bar_chart(df, x_col, y_col, title=None, color=None,
                     horizontal=False, sort=False):
    """
    Create a bar chart
    """
    if