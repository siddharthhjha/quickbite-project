"""
QUICKBITE PRODUCT ANALYTICS PLATFORM
Page: Data Dictionary
==================================================================
Purpose: Complete documentation of all tables, columns, and
business logic used in the analytics platform.

Author: Senior Product Analytics Team
Date: 2026-07-28
"""

import streamlit as st
import pandas as pd

st.header("📚 Data Dictionary")
st.markdown("""
Complete documentation of all data tables, columns, and business logic.
Use this as a reference for understanding the data model.
""")

# ---------------------------------------------------------------------
# TABLE DEFINITIONS
# ---------------------------------------------------------------------

tables = {
    'users': {
        'description': 'Platform users with demographic and acquisition data',
        'columns': {
            'user_id': 'Primary key, unique user identifier',
            'signup_date': 'Date user created account',
            'city_id': 'Foreign key to cities table',
            'acquisition_channel': 'How user was acquired (organic, paid_social, referral, paid_search, push_reactivation)',
            'referred_by_user_id': 'Self-referential foreign key for referral tracking',
            'is_premium_member': 'QuickBite Plus subscription status',
            'premium_start_date': 'Date of premium subscription start',
            'age_band': 'User age range (18-24, 25-34, 35-44, 45+)',
            'gender': 'User gender',
            'device_type': 'Primary device (iOS, Android)',
            'signup_channel_cost': 'Customer acquisition cost for non-organic channels',
            'is_churned': 'Flag for users inactive for 90+ days',
            'churned_at': 'Date user was flagged as churned'
        }
    },
    'orders': {
        'description': 'Core transaction table containing all order details',
        'columns': {
            'order_id': 'Primary key, unique order identifier',
            'user_id': 'Foreign key to users table',
            'restaurant_id': 'Foreign key to restaurants table',
            'delivery_partner_id': 'Foreign key to delivery_partners table',
            'city_id': 'Foreign key to cities table',
            'coupon_id': 'Foreign key to coupons table',
            'order_placed_at': 'Timestamp of order placement',
            'order_accepted_at': 'Timestamp of restaurant acceptance',
            'food_ready_at': 'Timestamp when food is ready for pickup',
            'delivery_partner_assigned_at': 'Timestamp of partner assignment',
            'picked_up_at': 'Timestamp of food pickup',
            'delivered_at': 'Timestamp of delivery completion',
            'order_status': 'delivered, cancelled, failed',
            'cancellation_reason': 'Reason for cancellation if applicable',
            'cancelled_by': 'user, restaurant, system',
            'subtotal_amount': 'Order subtotal before fees and discounts',
            'delivery_fee': 'Delivery charge',
            'discount_amount': 'Total discount applied',
            'total_amount': 'Final order total',
            'payment_method': 'upi, card, wallet, cod',
            'distance_km': 'Delivery distance in kilometers',
            'weather_condition': 'Weather at order time (denormalized)',
            'traffic_index_at_order': 'Traffic index at order time (0-10)',
            'is_first_order': 'Flag for user\'s first order'
        }
    },
    'restaurants': {
        'description': 'Restaurant information and performance metrics',
        'columns': {
            'restaurant_id': 'Primary key',
            'restaurant_name': 'Restaurant display name',
            'city_id': 'Foreign key to cities',
            'category_id': 'Foreign key to restaurant_categories',
            'onboarded_date': 'Date restaurant joined platform',
            'avg_rating': 'Average user rating (1.0-5.0)',
            'avg_prep_time_minutes': 'Average food preparation time',
            'acceptance_rate': 'Rate of order acceptance',
            'price_tier': 'budget, mid, premium',
            'is_active': 'Whether restaurant is currently active'
        }
    },
    'cities': {
        'description': 'City metadata and market characteristics',
        'columns': {
            'city_id': 'Primary key',
            'city_name': 'City name',
            'state': 'State/region name',
            'tier': 'Tier1, Tier2, Tier3 city classification',
            'launch_date': 'Date QuickBite launched in this city',
            'population_lakhs': 'City population in lakhs',
            'avg_traffic_index': 'Average traffic congestion (0-10)'
        }
    },
    'delivery_partners': {
        'description': 'Delivery partner information and performance',
        'columns': {
            'partner_id': 'Primary key',
            'city_id': 'Foreign key to cities',
            'joined_date': 'Date partner joined platform',
            'vehicle_type': 'bike, bicycle, scooter',
            'avg_rating': 'Average delivery partner rating (1.0-5.0)',
            'is_active': 'Whether partner is currently active',
            'shift_type': 'full_time, part_time, peak_hours_only'
        }
    },
    'coupons': {
        'description': 'Promotional coupon definitions',
        'columns': {
            'coupon_id': 'Primary key',
            'coupon_code': 'Unique coupon code',
            'discount_type': 'flat, percentage, free_delivery',
            'discount_value': 'Discount amount or percentage',
            'min_order_value': 'Minimum order value to apply coupon',
            'valid_from': 'Coupon validity start date',
            'valid_to': 'Coupon validity end date',
            'target_segment': 'new_user, churn_risk, premium, all'
        }
    },
    'order_items': {
        'description': 'Item-level details for each order',
        'columns': {
            'order_item_id': 'Primary key',
            'order_id': 'Foreign key to orders',
            'item_name': 'Name of the item',
            'category_id': 'Foreign key to restaurant_categories',
            'unit_price': 'Price per unit',
            'quantity': 'Number of units ordered',
            'line_total': 'Total price for this item (unit_price × quantity)'
        }
    },
    'payments': {
        'description': 'Payment transaction details',
        'columns': {
            'payment_id': 'Primary key',
            'order_id': 'Foreign key to orders',
            'payment_method': 'upi, card, wallet, cod',
            'amount': 'Payment amount',
            'payment_status': 'success, failed, refunded',
            'failure_reason': 'Reason for payment failure if applicable',
            'processed_at': 'Timestamp of payment processing'
        }
    },
    'events': {
        'description': 'User clickstream and app interaction events',
        'columns': {
            'event_id': 'Primary key',
            'session_id': 'Foreign key to sessions',
            'user_id': 'Foreign key to users',
            'event_name': 'app_open, search, view_restaurant, add_to_cart, checkout_start, apply_coupon, payment_start, order_placed, order_cancelled',
            'event_timestamp': 'Timestamp of event',
            'restaurant_id': 'Foreign key to restaurants (contextual)',
            'metadata': 'JSONB field for additional event data'
        }
    },
    'sessions': {
        'description': 'User app sessions for engagement analysis',
        'columns': {
            'session_id': 'Primary key',
            'user_id': 'Foreign key to users',
            'session_start': 'Session start timestamp',
            'session_end': 'Session end timestamp',
            'platform': 'iOS, Android, Web',
            'app_version': 'App version number',
            'entry_source': 'push, organic_open, deep_link, referral_link'
        }
    },
    'restaurant_categories': {
        'description': 'Cuisine categories for restaurants',
        'columns': {
            'category_id': 'Primary key',
            'category_name': 'Category display name (North Indian, Chinese, Pizza, etc.)',
            'is_premium_cuisine': 'Flag for premium cuisine categories'
        }
    },
    'weather': {
        'description': 'Weather data by city and hour',
        'columns': {
            'weather_id': 'Primary key',
            'city_id': 'Foreign key to cities',
            'date': 'Date of weather record',
            'hour': 'Hour of day (0-23)',
            'condition': 'clear, rain, heavy_rain, heatwave',
            'temperature_c': 'Temperature in Celsius'
        }
    },
    'traffic': {
        'description': 'Traffic congestion data by city and hour',
        'columns': {
            'traffic_id': 'Primary key',
            'city_id': 'Foreign key to cities',
            'date': 'Date of traffic record',
            'hour': 'Hour of day (0-23)',
            'traffic_index': 'Traffic congestion index (0-10)'
        }
    },
    'experiments': {
        'description': 'A/B test experiment definitions',
        'columns': {
            'experiment_id': 'Primary key',
            'experiment_name': 'Name of the experiment',
            'hypothesis': 'Test hypothesis description',
            'primary_metric': 'Primary success metric',
            'start_date': 'Experiment start date',
            'end_date': 'Experiment end date',
            'status': 'running, concluded, shipped, rolled_back'
        }
    },
    'experiment_assignments': {
        'description': 'User assignments to experiment variants',
        'columns': {
            'assignment_id': 'Primary key',
            'experiment_id': 'Foreign key to experiments',
            'user_id': 'Foreign key to users',
            'variant': 'control, treatment_a, treatment_b',
            'assigned_at': 'Timestamp of assignment'
        }
    },
    'support_tickets': {
        'description': 'Customer support interactions',
        'columns': {
            'ticket_id': 'Primary key',
            'user_id': 'Foreign key to users',
            'order_id': 'Foreign key to orders',
            'issue_category': 'missing_item, late_delivery, refund, app_bug',
            'opened_at': 'Ticket creation timestamp',
            'resolved_at': 'Ticket resolution timestamp',
            'resolution_type': 'refund, replacement, apology_credit, no_action',
            'satisfaction_score': 'Post-resolution satisfaction score (1-5)'
        }
    },
    'notifications': {
        'description': 'Push notifications and user engagement',
        'columns': {
            'notification_id': 'Primary key',
            'user_id': 'Foreign key to users',
            'notification_type': 'cart_abandon, win_back, promo, order_update',
            'sent_at': 'Notification send timestamp',
            'opened_at': 'Notification open timestamp',
            'clicked_at': 'Notification click timestamp',
            'channel': 'push, sms, email, whatsapp'
        }
    }
}

# ---------------------------------------------------------------------
# DISPLAY TABLES
# ---------------------------------------------------------------------

# Search/Filter
search_term = st.text_input("🔍 Search tables or columns", placeholder="Type to filter...")

# Display tables
for table_name, table_info in tables.items():
    # Filter by search term
    if search_term:
        if search_term.lower() not in table_name.lower() and \
           search_term.lower() not in table_info['description'].lower() and \
           not any(search_term.lower() in col.lower() or search_term.lower() in desc.lower() 
                   for col, desc in table_info['columns'].items()):
            continue
    
    with st.expander(f"📊 **{table_name}** - {table_info['description']}"):
        # Create column dataframe
        col_df = pd.DataFrame([
            {'Column': col, 'Description': desc} 
            for col, desc in table_info['columns'].items()
        ])
        
        # Highlight search term
        if search_term:
            col_df['Column'] = col_df['Column'].apply(
                lambda x: f"**{x}**" if search_term.lower() in x.lower() else x
            )
            col_df['Description'] = col_df['Description'].apply(
                lambda x: x.replace(search_term, f"**{search_term}**") 
                if search_term.lower() in x.lower() else x
            )
        
        st.dataframe(col_df, use_container_width=True)
        
        # Count columns
        st.caption(f"📋 {len(table_info['columns'])} columns")

# ---------------------------------------------------------------------
# TABLE RELATIONSHIPS
# ---------------------------------------------------------------------

st.subheader("🔗 Table Relationships")

# Complete relationships
relationship_text = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                        QUICKBITE DATABASE RELATIONSHIPS                     │
└─────────────────────────────────────────────────────────────────────────────┘

MASTER RELATIONSHIPS:
═══════════════════════════════════════════════════════════════════════════════

1. users.user_id → orders.user_id
   └── One-to-Many: Each user can have multiple orders

2. users.city_id → cities.city_id
   └── Many-to-One: Multiple users belong to one city

3. users.referred_by_user_id → users.user_id
   └── Self-referential: One user refers another

4. orders.restaurant_id → restaurants.restaurant_id
   └── Many-to-One: Multiple orders to one restaurant

5. orders.delivery_partner_id → delivery_partners.partner_id
   └── Many-to-One: Multiple orders delivered by one partner

6. orders.city_id → cities.city_id
   └── Many-to-One: Multiple orders in one city

7. orders.coupon_id → coupons.coupon_id
   └── Many-to-One: Multiple orders using one coupon

8. orders.order_id → order_items.order_id
   └── One-to-Many: Each order has multiple items

9. orders.order_id → payments.order_id
   └── One-to-One: Each order has one payment

10. restaurants.city_id → cities.city_id
    └── Many-to-One: Multiple restaurants in one city

11. restaurants.category_id → restaurant_categories.category_id
    └── Many-to-One: Multiple restaurants in one category

12. delivery_partners.city_id → cities.city_id
    └── Many-to-One: Multiple partners in one city

13. events.session_id → sessions.session_id
    └── Many-to-One: Multiple events in one session

14. events.user_id → users.user_id
    └── Many-to-One: Multiple events by one user

15. events.restaurant_id → restaurants.restaurant_id
    └── Many-to-One: Multiple events for one restaurant

16. experiment_assignments.experiment_id → experiments.experiment_id
    └── Many-to-One: Multiple assignments to one experiment

17. experiment_assignments.user_id → users.user_id
    └── Many-to-One: Multiple assignments for one user

18. support_tickets.user_id → users.user_id
    └── Many-to-One: Multiple tickets by one user

19. support_tickets.order_id → orders.order_id
    └── Many-to-One: Multiple tickets for one order

20. notifications.user_id → users.user_id
    └── Many-to-One: Multiple notifications for one user

21. weather.city_id → cities.city_id
    └── Many-to-One: Multiple weather records for one city

22. traffic.city_id → cities.city_id
    └── Many-to-One: Multiple traffic records for one city

FOREIGN KEY SUMMARY:
═══════════════════════════════════════════════════════════════════════════════

Table: users
├── city_id → cities.city_id
└── referred_by_user_id → users.user_id

Table: orders
├── user_id → users.user_id
├── restaurant_id → restaurants.restaurant_id
├── delivery_partner_id → delivery_partners.partner_id
├── city_id → cities.city_id
└── coupon_id → coupons.coupon_id

Table: restaurants
├── city_id → cities.city_id
└── category_id → restaurant_categories.category_id

Table: delivery_partners
└── city_id → cities.city_id

Table: order_items
└── order_id → orders.order_id

Table: payments
└── order_id → orders.order_id

Table: events
├── session_id → sessions.session_id
├── user_id → users.user_id
└── restaurant_id → restaurants.restaurant_id

Table: experiment_assignments
├── experiment_id → experiments.experiment_id
└── user_id → users.user_id

Table: support_tickets
├── user_id → users.user_id
└── order_id → orders.order_id

Table: notifications
└── user_id → users.user_id

Table: weather
└── city_id → cities.city_id

Table: traffic
└── city_id → cities.city_id
"""

st.code(relationship_text, language='text')

# ---------------------------------------------------------------------
# TABLE SUMMARY
# ---------------------------------------------------------------------

st.subheader("📊 Table Summary")

# Create summary dataframe
summary_data = []
for table_name, table_info in tables.items():
    # Count relationships
    rel_count = 0
    for rel in relationship_text.split('\n'):
        if f'{table_name}.' in rel and '→' in rel:
            rel_count += 1
    
    summary_data.append({
        'Table': table_name,
        'Description': table_info['description'],
        'Columns': len(table_info['columns']),
        'Relationships': rel_count
    })

summary_df = pd.DataFrame(summary_data)
summary_df = summary_df.sort_values('Columns', ascending=False)

st.dataframe(
    summary_df.style.background_gradient(cmap='Blues', subset=['Columns', 'Relationships']),
    use_container_width=True
)

# ---------------------------------------------------------------------
# BUSINESS LOGIC
# ---------------------------------------------------------------------

st.subheader("🧠 Business Logic & Definitions")

business_logic = {
    'Churn Definition': 'Users with no order in trailing 90 days are considered churned. This is updated by a batch job.',
    'Retention Definition': 'Users who place at least one order in the specified period (30/60/90 days).',
    'LTV Calculation': 'Sum of all delivered order amounts per user to date (historical LTV).',
    'CAC Calculation': 'Total channel spend / number of users acquired through that channel.',
    'LTV:CAC Ratio': 'LTV / CAC. Healthy ratio is >3:1, <1:1 means the business loses money on every user.',
    'Delivery SLA': 'P90 and P99 delivery times used to monitor tail latency. P50 for median performance.',
    'Cancellation Attribution': 'Categorized as user-initiated, restaurant-initiated, or system-initiated for root cause analysis.',
    'Premium Status': 'Users with active QuickBite Plus subscription. Shows correlation with retention and spend.',
    'Repeat Purchase Rate': 'Users with 2+ orders within 60 days of first order / total first-order users.',
    'Stickiness': 'DAU / MAU ratio. Food delivery benchmarks are typically 15-25%.',
    'Coupon Redemption': 'Orders with coupon applied / orders eligible for that coupon.',
    'NPS': '% Promoters (9-10) − % Detractors (0-6) from post-delivery surveys.'
}

for logic, description in business_logic.items():
    st.markdown(f"**{logic}**")
    st.markdown(f"*{description}*")
    st.markdown("---")

# ---------------------------------------------------------------------
# DATA GENERATION LOGIC
# ---------------------------------------------------------------------

st.subheader("⚙️ Data Generation Logic")

st.markdown("""
The synthetic data generator encodes real business relationships:

| Relationship | Logic |
|--------------|-------|
| Weather → Cancellations | Rain increases cancellations by 2x, heavy rain by 3x |
| Premium → Spend | Premium members spend 25% more per order |
| Referral → Retention | Referral users order 30% more than paid-acquired users |
| Traffic → Delivery Time | 1 point increase in traffic index = 15% longer delivery |
| Ratings → Order Probability | Restaurants with higher ratings get more orders |
| First Order → Coupon | 55% of first orders use a welcome coupon |
| Weekend → Demand | Weekend order volume is 35% higher |
| City Tier → Growth | Tier 1 cities have 2x higher user growth rate |
| Premium → Premium Users | Premium membership more common among organic/referral users |
| Acquisition Channel → CAC | Paid channels have higher CAC, referral has lower |

### Verification of Business Logic:
- Cancellation rate by weather: clear 10.1% → heavy_rain 21.0%
- Avg order value: non-premium ₹332 → premium ₹413
- Orders per user by channel: push_reactivation 8.2 → referral 16.3
""")

# ---------------------------------------------------------------------
# METRICS DEFINITIONS
# ---------------------------------------------------------------------

st.subheader("📊 Metrics Definitions")

metrics = {
    'DAU': 'Distinct users with at least one session in a day',
    'WAU': 'Distinct users with at least one session in trailing 7 days',
    'MAU': 'Distinct users with at least one session in trailing 30 days',
    'GMV': 'Sum of total_amount for delivered orders',
    'AOV': 'GMV / delivered_orders',
    'Conversion Rate': 'orders placed / sessions with a restaurant view × 100',
    'Cart Abandonment': '1 - (orders completed / carts started) × 100',
    'Cancellation Rate': 'cancelled orders / total orders × 100',
    'Restaurant Acceptance Rate': 'orders accepted / orders sent to restaurant × 100',
    'Coupon Redemption Rate': 'orders with coupon applied / orders eligible × 100',
    'Feature Adoption': 'users who used feature X / active users × 100',
    'Session Length': 'AVG(session_end - session_start) in minutes',
    'NPS': '% Promoters (9-10) − % Detractors (0-6)',
    'CSAT': 'AVG(satisfaction_score) from support_tickets (1-5)'
}

for metric, definition in metrics.items():
    st.markdown(f"**{metric}**: {definition}")

# ---------------------------------------------------------------------
# DENORMALIZED FIELDS
# ---------------------------------------------------------------------

st.subheader("📌 Denormalized Fields")

st.markdown("""
The following fields are denormalized in the orders table for performance:

| Field | Source | Purpose |
|-------|--------|---------|
| `weather_condition` | weather table | Snapshot at order time for operational analysis |
| `traffic_index_at_order` | traffic table | Snapshot at order time for SLA analysis |
| `city_id` | cities table | Direct city reference (also in users) |
| `is_first_order` | Derived | Flag for new user conversion analysis |

**Why denormalized?**
- Avoids joins for common queries
- Preserves historical context (weather/traffic changes over time)
- Enables faster analytics queries
""")

st.caption("📚 Data Dictionary v2.0 - Complete Reference")