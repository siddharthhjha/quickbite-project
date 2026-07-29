"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Utils: Data Loader - FIXED with Date Conversion
==================================================================
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import os

def load_all_data(data_path=None):
    """
    Load all cleaned data files with auto-detection
    """
    data = {}
    
    # If no path provided, try to find data
    if data_path is None:
        possible_paths = [
            Path('../data'),
            Path('./data'),
            Path('../outputs/cleaned_data'),
            Path('./outputs/cleaned_data'),
            Path('D:/PA-Project/data'),
        ]
        
        data_path = None
        for path in possible_paths:
            if path.exists() and any(path.glob('*.csv')):
                data_path = path
                print(f"✅ Found data at: {data_path}")
                break
        
        if data_path is None:
            print("❌ No data directory found.")
            return None
    
    # Define files to load
    files = {
        'users': ['users_cleaned.csv', 'users.csv'],
        'orders': ['orders_cleaned.csv', 'orders.csv'],
        'order_items': ['order_items_cleaned.csv', 'order_items.csv'],
        'payments': ['payments_cleaned.csv', 'payments.csv'],
        'restaurants': ['restaurants_cleaned.csv', 'restaurants.csv'],
        'partners': ['delivery_partners_cleaned.csv', 'delivery_partners.csv'],
        'cities': ['cities_cleaned.csv', 'cities.csv'],
        'rfm': ['rfm_segments_cleaned.csv', 'rfm_segments.csv'],
        'ltv': ['ltv_predictions_cleaned.csv', 'ltv_predictions.csv'],
        'churn': ['churn_predictions_cleaned.csv', 'churn_predictions.csv'],
        'daily_metrics': ['daily_metrics_with_anomalies_cleaned.csv', 'daily_metrics_with_anomalies.csv'],
        'segment_metrics': ['segment_metrics_cleaned.csv', 'segment_metrics.csv'],
        'experiment_recommendations': ['experiment_recommendations_cleaned.csv', 'experiment_recommendations.csv'],
        'association_rules': ['association_rules_items_cleaned.csv', 'association_rules_items.csv'],
        'cross_sell': ['cross_sell_opportunities_cleaned.csv', 'cross_sell_opportunities.csv']
    }
    
    # Column name variations for date columns
    date_columns = ['date', 'created_at', 'updated_at', 'signup_date', 'premium_start_date', 
                    'churned_at', 'order_placed_at', 'order_accepted_at', 'food_ready_at',
                    'delivery_partner_assigned_at', 'picked_up_at', 'delivered_at',
                    'onboarded_date', 'joined_date', 'launch_date', 'valid_from', 'valid_to',
                    'processed_at', 'opened_at', 'resolved_at', 'sent_at', 'assigned_at',
                    'start_date', 'end_date']
    
    # Load each file
    for name, file_list in files.items():
        loaded = False
        for file in file_list:
            file_path = Path(data_path) / file
            if file_path.exists():
                try:
                    # Read CSV
                    df = pd.read_csv(file_path)
                    
                    # Convert date columns
                    for col in df.columns:
                        # Check if column is a date column
                        is_date_col = False
                        for date_pattern in date_columns:
                            if date_pattern in col.lower():
                                is_date_col = True
                                break
                        
                        if is_date_col:
                            try:
                                df[col] = pd.to_datetime(df[col], errors='coerce')
                                print(f"   ✅ Converted {col} to datetime")
                            except Exception as e:
                                print(f"   ⚠️ Could not convert {col}: {e}")
                    
                    data[name] = df
                    print(f"✅ Loaded {name}: {len(df):,} rows")
                    loaded = True
                    break
                except Exception as e:
                    print(f"⚠️ Error loading {name}: {e}")
                    continue
        
        if not loaded:
            print(f"⚠️ File not found: {name}")
            data[name] = None
    
    return data

def load_models(models_path=None):
    """Load pre-trained models"""
    models = {}
    
    if models_path is None:
        possible_paths = [
            Path('../outputs/models'),
            Path('./outputs/models'),
            Path('../models'),
            Path('./models')
        ]
        
        models_path = None
        for path in possible_paths:
            if path.exists():
                models_path = path
                break
    
    if models_path is None:
        return models
    
    model_files = ['churn_model.pkl', 'scaler.pkl', 'ltv_model.pkl']
    
    for model_file in model_files:
        file_path = Path(models_path) / model_file
        if file_path.exists():
            try:
                with open(file_path, 'rb') as f:
                    models[model_file.replace('.pkl', '')] = pickle.load(f)
                print(f"✅ Loaded model: {model_file}")
            except:
                pass
    
    return models

def get_filtered_data(data, start_date=None, end_date=None, cities=None, segments=None):
    """Apply filters to dataframes"""
    filtered = data.copy()
    
    if start_date and end_date and 'orders' in filtered and filtered['orders'] is not None:
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(filtered['orders']['order_placed_at']):
            filtered['orders']['order_placed_at'] = pd.to_datetime(filtered['orders']['order_placed_at'])
        
        mask = (filtered['orders']['order_placed_at'].dt.date >= start_date) & \
               (filtered['orders']['order_placed_at'].dt.date <= end_date)
        filtered['orders'] = filtered['orders'][mask]
    
    if cities and 'orders' in filtered and filtered['orders'] is not None and 'cities' in filtered and filtered['cities'] is not None:
        city_ids = filtered['cities'][filtered['cities']['city_name'].isin(cities)]['city_id'].tolist()
        filtered['orders'] = filtered['orders'][filtered['orders']['city_id'].isin(city_ids)]
    
    if segments and 'rfm' in filtered and filtered['rfm'] is not None:
        filtered['rfm'] = filtered['rfm'][filtered['rfm']['segment'].isin(segments)]
    
    return filtered