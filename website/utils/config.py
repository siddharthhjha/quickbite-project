"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Utils: Configuration
==================================================================
Purpose: Centralized configuration for the website.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR.parent / 'outputs' / 'cleaned_data'
MODELS_DIR = BASE_DIR.parent / 'outputs' / 'models'
RAW_DATA_DIR = BASE_DIR.parent / 'data'
ASSETS_DIR = BASE_DIR / 'assets'

# App configuration
APP_CONFIG = {
    'title': 'QuickBite Analytics Platform',
    'icon': '🍔',
    'version': '2.0.0',
    'author': 'Product Analytics Team',
    'year': '2026'
}

# Database configuration
DB_CONFIG = {
    'memory_db': True,
    'tables': [
        'users', 'orders', 'order_items', 'payments',
        'restaurants', 'partners', 'cities', 'rfm',
        'ltv', 'churn', 'daily_metrics', 'segment_metrics',
        'experiment_recommendations', 'association_rules',
        'cross_sell'
    ]
}

# Visualization defaults
VIZ_CONFIG = {
    'color_palette': {
        'primary': '#3498db',
        'secondary': '#2ecc71',
        'danger': '#e74c3c',
        'warning': '#f39c12',
        'purple': '#9b59b6',
        'dark': '#2c3e50'
    },
    'template': 'plotly_white',
    'height': 400,
    'width': '100%'
}

# Metrics configuration
METRICS_CONFIG = {
    'kpis': [
        {'name': 'Orders', 'field': 'orders', 'format': '{:,}', 'icon': '📦'},
        {'name': 'GMV', 'field': 'gmv', 'format': '₹{:,}', 'icon': '💰'},
        {'name': 'AOV', 'field': 'aov', 'format': '₹{:,}', 'icon': '🧾'},
        {'name': 'Users', 'field': 'users', 'format': '{:,}', 'icon': '👤'},
        {'name': 'Retention', 'field': 'retention', 'format': '{:.1f}%', 'icon': '🔄'},
        {'name': 'Cancellation', 'field': 'cancellation', 'format': '{:.1f}%', 'icon': '❌'}
    ]
}