"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Utils: Metrics Calculations
==================================================================
Purpose: Centralized metric calculations used across the platform.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_retention(orders_df, days=30):
    """
    Calculate retention rate for a given period
    """
    if len(orders_df) == 0:
        return 0
    
    # Get first and last orders for each user
    first_orders = orders_df.sort_values('order_placed_at').groupby('user_id').first().reset_index()
    last_orders = orders_df.groupby('user_id')['order_placed_at'].max().reset_index()
    
    # Calculate retention
    cutoff_date = datetime.now() - timedelta(days=days)
    retained = last_orders[last_orders['order_placed_at'] >= cutoff_date]['user_id'].nunique()
    total = first_orders['user_id'].nunique()
    
    return retained / total * 100 if total > 0 else 0

def calculate_churn_rate(orders_df, days=90):
    """
    Calculate churn rate for a given period
    """
    if len(orders_df) == 0:
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Get users who haven't ordered in the period
    last_orders = orders_df.groupby('user_id')['order_placed_at'].max().reset_index()
    churned = last_orders[last_orders['order_placed_at'] < cutoff_date]['user_id'].nunique()
    total = len(last_orders)
    
    return churned / total * 100 if total > 0 else 0

def calculate_ltv(orders_df, users_df=None):
    """
    Calculate average lifetime value
    """
    if len(orders_df) == 0:
        return 0
    
    gmv = orders_df[orders_df['order_status'] == 'delivered']['total_amount'].sum()
    total_users = orders_df['user_id'].nunique()
    
    return gmv / total_users if total_users > 0 else 0

def calculate_aov(orders_df):
    """
    Calculate average order value
    """
    delivered = orders_df[orders_df['order_status'] == 'delivered']
    if len(delivered) == 0:
        return 0
    
    return delivered['total_amount'].mean()

def calculate_cancellation_rate(orders_df):
    """
    Calculate cancellation rate
    """
    if len(orders_df) == 0:
        return 0
    
    cancelled = len(orders_df[orders_df['order_status'] == 'cancelled'])
    total = len(orders_df)
    
    return cancelled / total * 100 if total > 0 else 0

def calculate_gmv(orders_df):
    """
    Calculate Gross Merchandise Value
    """
    delivered = orders_df[orders_df['order_status'] == 'delivered']
    return delivered['total_amount'].sum()

def calculate_repeat_rate(orders_df, days=60):
    """
    Calculate repeat purchase rate
    """
    if len(orders_df) == 0:
        return 0
    
    # Get first order for each user
    first_orders = orders_df.sort_values('order_placed_at').groupby('user_id').first().reset_index()
    
    # Count users with 2+ orders within window
    repeat_users = 0
    for _, row in first_orders.iterrows():
        user_orders = orders_df[orders_df['user_id'] == row['user_id']]
        repeat_orders = user_orders[
            (user_orders['order_placed_at'] > row['order_placed_at']) &
            (user_orders['order_placed_at'] <= row['order_placed_at'] + timedelta(days=days))
        ]
        if len(repeat_orders) > 0:
            repeat_users += 1
    
    return repeat_users / len(first_orders) * 100 if len(first_orders) > 0 else 0

def get_daily_metrics(orders_df):
    """
    Calculate daily metrics
    """
    if len(orders_df) == 0:
        return pd.DataFrame()
    
    daily = orders_df.groupby(orders_df['order_placed_at'].dt.date).agg({
        'order_id': 'count',
        'total_amount': 'sum',
        'user_id': 'nunique',
        'order_status': lambda x: (x == 'cancelled').sum() / len(x) * 100
    }).reset_index()
    
    daily.columns = ['date', 'orders', 'gmv', 'active_users', 'cancellation_rate']
    
    # Add AOV
    delivered = orders_df[orders_df['order_status'] == 'delivered']
    daily_aov = delivered.groupby(delivered['order_placed_at'].dt.date)['total_amount'].mean().reset_index()
    daily_aov.columns = ['date', 'aov']
    daily = daily.merge(daily_aov, on='date', how='left')
    daily['aov'] = daily['aov'].fillna(0)
    
    return daily

def get_channel_metrics(orders_df, users_df):
    """
    Calculate channel performance metrics
    """
    if len(orders_df) == 0 or len(users_df) == 0:
        return pd.DataFrame()
    
    # Merge orders with users
    merged = orders_df[orders_df['order_status'] == 'delivered'].merge(
        users_df[['user_id', 'acquisition_channel']],
        on='user_id'
    )
    
    channel_metrics = merged.groupby('acquisition_channel').agg({
        'order_id': 'count',
        'total_amount': ['sum', 'mean'],
        'user_id': 'nunique'
    }).reset_index()
    
    channel_metrics.columns = ['channel', 'orders', 'gmv', 'aov', 'users']
    channel_metrics['gmv_per_user'] = channel_metrics['gmv'] / channel_metrics['users']
    channel_metrics['orders_per_user'] = channel_metrics['orders'] / channel_metrics['users']
    
    return channel_metrics

def get_city_metrics(orders_df, cities_df):
    """
    Calculate city performance metrics
    """
    if len(orders_df) == 0 or len(cities_df) == 0:
        return pd.DataFrame()
    
    city_metrics = orders_df[orders_df['order_status'] == 'delivered'].groupby('city_id').agg({
        'order_id': 'count',
        'total_amount': ['sum', 'mean'],
        'user_id': 'nunique'
    }).reset_index()
    
    city_metrics.columns = ['city_id', 'orders', 'gmv', 'aov', 'users']
    city_metrics = city_metrics.merge(cities_df[['city_id', 'city_name', 'tier']], on='city_id')
    
    return city_metrics