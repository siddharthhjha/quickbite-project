"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Utils: Sample Data Generator
==================================================================
Purpose: Generate sample data for pages when real data is not available.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import pandas as pd
import numpy as np

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

def create_sample_churn_data():
    """Create sample churn prediction data"""
    np.random.seed(42)
    n_users = 1000
    
    churn_data = pd.DataFrame({
        'user_id': range(n_users),
        'churn_probability': np.random.beta(2, 5, n_users),
        'churned': np.random.choice([0, 1], n_users, p=[0.7, 0.3]),
        'segment': np.random.choice(['Champions', 'Loyal', 'At Risk', 'Dormant', 'New'], n_users),
        'acquisition_channel': np.random.choice(['organic', 'referral', 'paid_social', 'paid_search'], n_users),
        'is_premium_member': np.random.choice([True, False], n_users, p=[0.2, 0.8])
    })
    
    return churn_data

def create_sample_ltv_data():
    """Create sample LTV data"""
    np.random.seed(42)
    n_users = 1000
    
    ltv_data = pd.DataFrame({
        'user_id': range(n_users),
        'lifetime_value': np.random.exponential(2000, n_users) + 100,
        'predicted_ltv': np.random.exponential(2000, n_users) + 100,
        'acquisition_channel': np.random.choice(['organic', 'referral', 'paid_social', 'paid_search'], n_users),
        'is_premium_member': np.random.choice([True, False], n_users, p=[0.2, 0.8]),
        'order_count': np.random.poisson(5, n_users) + 1,
        'segment': np.random.choice(['Champions', 'Loyal', 'At Risk', 'Dormant', 'New'], n_users)
    })
    
    return ltv_data

def create_sample_daily_metrics(orders_df):
    """Create sample daily metrics with anomalies"""
    
    if orders_df is not None and len(orders_df) > 0:
        # Use real data if available
        daily = orders_df.groupby(orders_df['order_placed_at'].dt.date).agg({
            'order_id': 'count',
            'total_amount': 'sum'
        }).reset_index()
        daily.columns = ['date', 'orders', 'gmv']
        daily['date'] = pd.to_datetime(daily['date'])
        daily['aov'] = daily['gmv'] / daily['orders']
        daily['cancellation_rate'] = np.random.uniform(5, 15, len(daily))
        
        # Add anomalies (random spikes)
        np.random.seed(42)
        daily['is_anomaly'] = np.random.choice([0, 1], len(daily), p=[0.95, 0.05])
        daily['anomaly_score'] = np.random.normal(0, 1, len(daily))
        daily.loc[daily['is_anomaly'] == 1, 'anomaly_score'] = np.random.uniform(2, 4, daily['is_anomaly'].sum())
    else:
        # Create synthetic data
        dates = pd.date_range(start='2024-01-01', periods=180, freq='D')
        np.random.seed(42)
        
        daily = pd.DataFrame({
            'date': dates,
            'orders': np.random.poisson(200, 180) + 100,
            'gmv': np.random.normal(70000, 15000, 180),
            'aov': np.random.normal(350, 50, 180),
            'cancellation_rate': np.random.uniform(5, 15, 180)
        })
        
        # Add anomalies
        daily['is_anomaly'] = np.random.choice([0, 1], 180, p=[0.95, 0.05])
        daily['anomaly_score'] = np.random.normal(0, 1, 180)
        daily.loc[daily['is_anomaly'] == 1, 'anomaly_score'] = np.random.uniform(2, 4, daily['is_anomaly'].sum())
        daily['orders'] = daily['orders'].astype(int)
    
    return daily

def create_sample_rules():
    """Create sample association rules"""
    items = ['Burger', 'Fries', 'Pizza', 'Pasta', 'Garlic Bread', 
             'Biryani', 'Raita', 'Coffee', 'Dessert', 'Salad']
    
    np.random.seed(42)
    rules = []
    
    for i in range(30):
        antecedents = np.random.choice(items, size=np.random.randint(1, 3), replace=False)
        consequents = np.random.choice([item for item in items if item not in antecedents], 
                                       size=np.random.randint(1, 2), replace=False)
        
        rules.append({
            'antecedents': list(antecedents),
            'consequents': list(consequents),
            'support': np.random.uniform(0.01, 0.05),
            'confidence': np.random.uniform(0.3, 0.8),
            'lift': np.random.uniform(1.2, 3.0)
        })
    
    return pd.DataFrame(rules)