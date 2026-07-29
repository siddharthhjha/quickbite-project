"""
QuickBite Synthetic Data Generator
====================================
Generates realistic, business-logic-driven data for the QuickBite
analytics platform and writes CSVs matching sql/01_schema.sql.

DESIGN PRINCIPLE: nothing here is uniform random. Every table encodes
a causal relationship that the analytics layer is meant to discover.
Search for "BUSINESS LOGIC:" comments to see each one.

DEFAULT SCALE (demo-sized, runs in ~1-2 min on a laptop):
    users        : 5,000
    restaurants  : 400
    orders       : 60,000
    events       : ~600,000
To hit portfolio-scale numbers (100K users / 1M orders / 10M events),
change the constants in CONFIG below -- the logic is identical, only
row counts change. At full scale, generate in a proper env (not a
notebook) and load via COPY, not pandas.to_sql.

Usage:
    python generate_synthetic_data.py --out ./data --scale demo
    python generate_synthetic_data.py --out ./data --scale full
"""

import argparse
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

RNG = np.random.default_rng(42)

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
SCALES = {
    "demo": dict(n_users=5_000, n_restaurants=400, n_partners=800,
                 n_orders=60_000, days_history=365),
    "full": dict(n_users=100_000, n_restaurants=6_000, n_partners=15_000,
                 n_orders=1_000_000, days_history=540),
}

CITIES = [
    ("Mumbai", "Maharashtra", "Tier1", "2018-01-15", 205, 7.8),
    ("Delhi", "Delhi", "Tier1", "2018-01-15", 320, 8.2),
    ("Bengaluru", "Karnataka", "Tier1", "2018-03-01", 130, 8.5),
    ("Hyderabad", "Telangana", "Tier1", "2018-06-01", 100, 6.5),
    ("Pune", "Maharashtra", "Tier2", "2019-01-10", 70, 6.0),
    ("Ahmedabad", "Gujarat", "Tier2", "2019-04-15", 80, 5.0),
    ("Jaipur", "Rajasthan", "Tier2", "2020-02-01", 40, 4.5),
    ("Lucknow", "Uttar Pradesh", "Tier2", "2020-08-01", 45, 4.8),
    ("Indore", "Madhya Pradesh", "Tier3", "2021-05-01", 25, 3.5),
    ("Coimbatore", "Tamil Nadu", "Tier3", "2021-09-01", 22, 3.2),
]

CATEGORIES = [
    ("North Indian", False), ("South Indian", False), ("Chinese", False),
    ("Pizza", False), ("Biryani", False), ("Healthy/Salads", True),
    ("Desserts", False), ("Cafe", True), ("Continental", True),
    ("Street Food", False), ("Sushi", True), ("Burgers", False),
]

ACQ_CHANNELS = ["organic", "paid_social", "referral", "paid_search", "push_reactivation"]
# BUSINESS LOGIC: referral & organic users retain better than paid channels
CHANNEL_RETENTION_MULT = {
    "organic": 1.15, "referral": 1.35, "paid_social": 0.80,
    "paid_search": 0.90, "push_reactivation": 0.70,
}
CHANNEL_COST = {  # CAC per user, NULL for organic
    "organic": 0, "paid_social": 180, "referral": 60,
    "paid_search": 220, "push_reactivation": 40,
}

CANCEL_REASONS = ["restaurant_closed", "long_wait", "no_partner_available",
                   "payment_failed", "user_changed_mind", "item_unavailable"]


def daterange_days(start, n):
    return [start + timedelta(days=i) for i in range(n)]


def gen_cities():
    rows = []
    for i, (name, state, tier, launch, pop, traffic) in enumerate(CITIES, start=1):
        rows.append(dict(city_id=i, city_name=name, state=state, tier=tier,
                          launch_date=launch, population_lakhs=pop,
                          avg_traffic_index=traffic))
    return pd.DataFrame(rows)


def gen_categories():
    rows = []
    for i, (name, premium) in enumerate(CATEGORIES, start=1):
        rows.append(dict(category_id=i, category_name=name, is_premium_cuisine=premium))
    return pd.DataFrame(rows)


def gen_users(n_users, cities_df, start_date, days_history):
    end_date = start_date + timedelta(days=days_history)
    rows = []
    for uid in range(1, n_users + 1):
        # BUSINESS LOGIC: signups grow over time (platform growth), not uniform
        t = RNG.random()
        signup_offset = int((t ** 0.6) * days_history)  # skew toward more recent signups
        signup_date = start_date + timedelta(days=signup_offset)

        city = cities_df.sample(1, weights=cities_df["population_lakhs"], random_state=None).iloc[0]
        channel = RNG.choice(ACQ_CHANNELS, p=[0.35, 0.25, 0.15, 0.20, 0.05])
        cost = CHANNEL_COST[channel] * (0.85 + RNG.random() * 0.3) if channel != "organic" else 0

        # BUSINESS LOGIC: premium membership more common among organic/referral,
        # longer-tenured users
        tenure_days = (end_date - signup_date).days
        premium_base_prob = 0.08 + min(tenure_days / days_history, 1) * 0.12
        is_premium = RNG.random() < premium_base_prob * (1.3 if channel in ("organic", "referral") else 0.8)
        premium_start = None
        if is_premium:
            premium_start = signup_date + timedelta(days=int(RNG.integers(5, max(6, tenure_days + 1))))

        rows.append(dict(
            user_id=uid, signup_date=signup_date.date(), city_id=int(city["city_id"]),
            acquisition_channel=channel, referred_by_user_id=None,
            is_premium_member=is_premium,
            premium_start_date=premium_start.date() if premium_start else None,
            age_band=RNG.choice(["18-24", "25-34", "35-44", "45+"], p=[0.30, 0.40, 0.20, 0.10]),
            gender=RNG.choice(["male", "female", "other"], p=[0.55, 0.43, 0.02]),
            device_type=RNG.choice(["Android", "iOS"], p=[0.72, 0.28]),
            signup_channel_cost=round(cost, 2) if cost else None,
            is_churned=False, churned_at=None,
        ))

    df = pd.DataFrame(rows)
    # BUSINESS LOGIC: referral users are referred_by an earlier-signed-up user
    referral_mask = df["acquisition_channel"] == "referral"
    for idx in df[referral_mask].index:
        earlier = df[df["user_id"] < df.loc[idx, "user_id"]]
        if len(earlier) > 0:
            df.loc[idx, "referred_by_user_id"] = int(earlier.sample(1).iloc[0]["user_id"])
    return df


def gen_restaurants(n_restaurants, cities_df, categories_df, start_date, days_history):
    rows = []
    for rid in range(1, n_restaurants + 1):
        city = cities_df.sample(1).iloc[0]
        cat = categories_df.sample(1).iloc[0]
        onboarded = start_date + timedelta(days=int(RNG.integers(0, days_history)))
        # BUSINESS LOGIC: rating is roughly normal around 4.0, premium cuisines
        # skew slightly higher (better packaging/service expectations)
        base = 4.0 + (0.15 if cat["is_premium_cuisine"] else 0)
        rating = float(np.clip(RNG.normal(base, 0.35), 2.5, 5.0))
        prep_time = int(np.clip(RNG.normal(22, 7), 8, 60))
        acceptance = float(np.clip(RNG.normal(0.90, 0.08), 0.5, 0.99))
        rows.append(dict(
            restaurant_id=rid, restaurant_name=f"Restaurant_{rid}",
            city_id=int(city["city_id"]), category_id=int(cat["category_id"]),
            onboarded_date=onboarded.date(), avg_rating=round(rating, 1),
            avg_prep_time_minutes=prep_time, acceptance_rate=round(acceptance, 3),
            price_tier=RNG.choice(["budget", "mid", "premium"], p=[0.4, 0.45, 0.15]),
            is_active=RNG.random() > 0.03,
        ))
    return pd.DataFrame(rows)


def gen_delivery_partners(n_partners, cities_df, start_date, days_history):
    rows = []
    for pid in range(1, n_partners + 1):
        city = cities_df.sample(1).iloc[0]
        joined = start_date + timedelta(days=int(RNG.integers(0, days_history)))
        rows.append(dict(
            partner_id=pid, city_id=int(city["city_id"]), joined_date=joined.date(),
            vehicle_type=RNG.choice(["bike", "scooter", "bicycle"], p=[0.6, 0.35, 0.05]),
            avg_rating=round(float(np.clip(RNG.normal(4.3, 0.3), 3.0, 5.0)), 1),
            is_active=RNG.random() > 0.05,
            shift_type=RNG.choice(["full_time", "part_time", "peak_hours_only"], p=[0.4, 0.35, 0.25]),
        ))
    return pd.DataFrame(rows)


def gen_coupons():
    data = [
        ("WELCOME50", "percentage", 50, 199, "new_user"),
        ("FREEDEL", "free_delivery", 0, 149, "all"),
        ("COMEBACK100", "flat", 100, 299, "churn_risk"),
        ("PLUS20", "percentage", 20, 249, "premium"),
        ("FLAT75", "flat", 75, 249, "all"),
    ]
    rows = []
    for i, (code, dtype, val, minv, seg) in enumerate(data, start=1):
        rows.append(dict(coupon_id=i, coupon_code=code, discount_type=dtype,
                          discount_value=val, min_order_value=minv,
                          valid_from="2023-01-01", valid_to="2026-12-31",
                          target_segment=seg))
    return pd.DataFrame(rows)


def gen_weather_traffic(cities_df, start_date, days_history):
    weather_rows, traffic_rows = [], []
    wid = tid = 1
    for city in cities_df.itertuples():
        for day in daterange_days(start_date, days_history):
            # BUSINESS LOGIC: monsoon months (Jun-Sep) have much higher rain probability
            is_monsoon = day.month in (6, 7, 8, 9)
            rain_prob = 0.35 if is_monsoon else 0.08
            for hour in [12, 19]:  # lunch & dinner peak snapshot per day, keeps table size sane
                condition = RNG.choice(
                    ["clear", "rain", "heavy_rain", "heatwave"],
                    p=[1 - rain_prob - 0.05, rain_prob * 0.7, rain_prob * 0.3, 0.05]
                )
                weather_rows.append(dict(weather_id=wid, city_id=city.city_id, date=day.date(),
                                          hour=hour, condition=condition,
                                          temperature_c=round(float(RNG.normal(30, 5)), 1)))
                wid += 1
                # BUSINESS LOGIC: traffic higher on weekdays at peak hours, and
                # scales with the city's base traffic index
                weekday_mult = 1.2 if day.weekday() < 5 else 0.9
                traffic_idx = float(np.clip(RNG.normal(city.avg_traffic_index * weekday_mult, 1.0), 0, 10))
                traffic_rows.append(dict(traffic_id=tid, city_id=city.city_id, date=day.date(),
                                          hour=hour, traffic_index=round(traffic_idx, 2)))
                tid += 1
    return pd.DataFrame(weather_rows), pd.DataFrame(traffic_rows)


def gen_orders_and_related(n_orders, users_df, restaurants_df, partners_df,
                            coupons_df, weather_df, traffic_df, start_date, days_history):
    end_date = start_date + timedelta(days=days_history)
    weather_lookup = weather_df.set_index(["city_id", "date"])["condition"].to_dict()
    traffic_lookup = traffic_df.set_index(["city_id", "date"])["traffic_index"].to_dict()

    users_df = users_df.copy()
    users_df["signup_date"] = pd.to_datetime(users_df["signup_date"])
    restaurants_by_city = {cid: g for cid, g in restaurants_df.groupby("city_id")}
    partners_by_city = {cid: g for cid, g in partners_df.groupby("city_id")}

    orders, items, payments, first_order_seen = [], [], [], set()
    oid = pid_item = pay_id = 1

    # BUSINESS LOGIC: order volume per user is NOT uniform. Premium members
    # and referral-acquired users order more often (retention effect).
    # We sample "how many orders this user places" then distribute dates.
    user_order_counts = {}
    for u in users_df.itertuples():
        tenure = max((end_date - u.signup_date).days, 1)
        base_rate = 0.9  # orders per active month, base
        mult = 1.0
        mult *= 1.6 if u.is_premium_member else 1.0
        mult *= CHANNEL_RETENTION_MULT[u.acquisition_channel]
        expected_orders = max(1, np.random.poisson(base_rate * mult * (tenure / 30)))
        user_order_counts[u.user_id] = min(expected_orders, 250)

    total_target = n_orders
    scale_factor = total_target / max(sum(user_order_counts.values()), 1)

    for _, u in users_df.set_index("user_id").iterrows():
        pass  # placeholder to keep structure explicit; loop below does real work

    for u in users_df.itertuples():
        n_this_user = max(0, int(round(user_order_counts[u.user_id] * scale_factor)))
        if n_this_user == 0:
            continue
        city_restaurants = restaurants_by_city.get(u.city_id)
        city_partners = partners_by_city.get(u.city_id)
        if city_restaurants is None or len(city_restaurants) == 0:
            continue
        if city_partners is None or len(city_partners) == 0:
            continue

        tenure_days = max((end_date - u.signup_date).days, 1)
        for k in range(n_this_user):
            # BUSINESS LOGIC: weekend demand is higher -> bias order date sampling
            order_offset = int(RNG.integers(0, tenure_days))
            order_date = u.signup_date + timedelta(days=order_offset)
            if order_date.weekday() >= 5 and RNG.random() < 0.35:
                order_offset = int(min(order_offset + RNG.integers(0, 2), tenure_days - 1))
                order_date = u.signup_date + timedelta(days=order_offset)
            hour = int(RNG.choice([12, 13, 19, 20, 21], p=[0.2, 0.15, 0.25, 0.25, 0.15]))
            order_ts = datetime.combine(order_date.date(), datetime.min.time()) + timedelta(hours=hour, minutes=int(RNG.integers(0, 60)))

            restaurant = city_restaurants.sample(1, weights=city_restaurants["avg_rating"]).iloc[0]
            partner = city_partners.sample(1).iloc[0]

            weather_cond = weather_lookup.get((u.city_id, order_date.date()), "clear")
            traffic_idx = traffic_lookup.get((u.city_id, order_date.date()), 5.0)

            is_first = u.user_id not in first_order_seen
            if is_first:
                first_order_seen.add(u.user_id)

            # BUSINESS LOGIC: coupon usage more likely on first order or for churn-risk win-back
            coupon = None
            if is_first and RNG.random() < 0.55:
                coupon = coupons_df[coupons_df["target_segment"] == "new_user"].iloc[0]
            elif RNG.random() < 0.12:
                coupon = coupons_df.sample(1).iloc[0]

            # BUSINESS LOGIC: premium members spend more per order
            base_subtotal = RNG.normal(320, 90) * (1.25 if u.is_premium_member else 1.0)
            base_subtotal = float(np.clip(base_subtotal, 99, 1800))
            delivery_fee = 0 if (coupon is not None and coupon.get("discount_type") == "free_delivery") else round(float(np.clip(RNG.normal(30, 8), 0, 80)), 2)
            discount = 0.0
            if coupon is not None:
                if coupon["discount_type"] == "percentage":
                    discount = round(base_subtotal * (coupon["discount_value"] / 100), 2)
                elif coupon["discount_type"] == "flat":
                    discount = float(coupon["discount_value"])
            total = round(base_subtotal + delivery_fee - discount, 2)

            # BUSINESS LOGIC: cancellation probability rises with bad weather,
            # high traffic, low restaurant acceptance rate, and long implied wait
            weather_penalty = {"clear": 0.0, "rain": 0.04, "heavy_rain": 0.10, "heatwave": 0.02}[weather_cond]
            traffic_penalty = max(0, (traffic_idx - 5)) * 0.015
            accept_penalty = max(0, 0.95 - restaurant["acceptance_rate"]) * 0.5
            cancel_prob = min(0.35, 0.03 + weather_penalty + traffic_penalty + accept_penalty)
            is_cancelled = RNG.random() < cancel_prob

            distance_km = float(np.clip(RNG.normal(4.5, 2.2), 0.5, 18))
            prep_time = int(restaurant["avg_prep_time_minutes"]) + (5 if weather_cond in ("rain", "heavy_rain") else 0)
            # BUSINESS LOGIC: delivery time driven by distance, traffic, weather
            delivery_minutes = (
                prep_time
                + distance_km * (2.2 + traffic_penalty * 20)
                + (10 if weather_cond == "heavy_rain" else (5 if weather_cond == "rain" else 0))
                + RNG.normal(0, 4)
            )
            delivery_minutes = float(np.clip(delivery_minutes, 12, 120))

            order_status = "cancelled" if is_cancelled else "delivered"
            cancel_reason = None
            cancelled_by = None
            delivered_at = None
            accepted_at = order_ts + timedelta(minutes=2)
            food_ready_at = accepted_at + timedelta(minutes=prep_time)
            assigned_at = accepted_at + timedelta(minutes=3)
            picked_up_at = food_ready_at + timedelta(minutes=2)

            if is_cancelled:
                cancel_reason = str(RNG.choice(CANCEL_REASONS,
                    p=[0.25, 0.30, 0.15, 0.10, 0.10, 0.10]))
                cancelled_by = "restaurant" if cancel_reason in ("restaurant_closed", "item_unavailable") else \
                                ("system" if cancel_reason == "no_partner_available" else "user")
            else:
                delivered_at = picked_up_at + timedelta(minutes=delivery_minutes - prep_time if delivery_minutes > prep_time else 5)

            orders.append(dict(
                order_id=oid, user_id=u.user_id, restaurant_id=int(restaurant["restaurant_id"]),
                delivery_partner_id=int(partner["partner_id"]) if not is_cancelled else None,
                city_id=u.city_id, coupon_id=int(coupon["coupon_id"]) if coupon is not None else None,
                order_placed_at=order_ts, order_accepted_at=accepted_at if not is_cancelled else None,
                food_ready_at=food_ready_at if not is_cancelled else None,
                delivery_partner_assigned_at=assigned_at if not is_cancelled else None,
                picked_up_at=picked_up_at if not is_cancelled else None,
                delivered_at=delivered_at,
                order_status=order_status, cancellation_reason=cancel_reason,
                cancelled_by=cancelled_by,
                subtotal_amount=round(base_subtotal, 2), delivery_fee=delivery_fee,
                discount_amount=discount, total_amount=total,
                payment_method=str(RNG.choice(["upi", "card", "wallet", "cod"], p=[0.55, 0.20, 0.20, 0.05])),
                distance_km=round(distance_km, 2), weather_condition=weather_cond,
                traffic_index_at_order=round(traffic_idx, 2), is_first_order=is_first,
            ))

            n_items = int(RNG.integers(1, 5))
            for _ in range(n_items):
                unit_price = round(float(np.clip(RNG.normal(base_subtotal / n_items, 30), 30, 900)), 2)
                qty = int(RNG.integers(1, 3))
                items.append(dict(order_item_id=pid_item, order_id=oid,
                                   item_name=f"Item_{RNG.integers(1, 500)}",
                                   category_id=int(restaurant["category_id"]),
                                   unit_price=unit_price, quantity=qty,
                                   line_total=round(unit_price * qty, 2)))
                pid_item += 1

            pay_status = "failed" if (not is_cancelled and RNG.random() < 0.02) else \
                         ("refunded" if is_cancelled and RNG.random() < 0.6 else "success")
            payments.append(dict(payment_id=pay_id, order_id=oid,
                                  payment_method=orders[-1]["payment_method"], amount=total,
                                  payment_status=pay_status,
                                  failure_reason="bank_decline" if pay_status == "failed" else None,
                                  processed_at=order_ts + timedelta(seconds=int(RNG.integers(5, 60)))))
            pay_id += 1
            oid += 1

    return (pd.DataFrame(orders), pd.DataFrame(items), pd.DataFrame(payments))

# In generate_synthetic_data.py, add events generation
def gen_events(orders_df, users_df):
    """Generate realistic events data"""
    events = []
    
    for _, order in orders_df.iterrows():
        user_id = order['user_id']
        order_time = order['order_placed_at']
        
        # Create event sequence
        events.append({'user_id': user_id, 'event_name': 'app_open', 'event_timestamp': order_time - timedelta(minutes=30)})
        events.append({'user_id': user_id, 'event_name': 'search', 'event_timestamp': order_time - timedelta(minutes=25)})
        events.append({'user_id': user_id, 'event_name': 'view_restaurant', 'event_timestamp': order_time - timedelta(minutes=20)})
        events.append({'user_id': user_id, 'event_name': 'view_menu', 'event_timestamp': order_time - timedelta(minutes=15)})
        events.append({'user_id': user_id, 'event_name': 'add_to_cart', 'event_timestamp': order_time - timedelta(minutes=10)})
        events.append({'user_id': user_id, 'event_name': 'checkout_start', 'event_timestamp': order_time - timedelta(minutes=5)})
        events.append({'user_id': user_id, 'event_name': 'payment_start', 'event_timestamp': order_time - timedelta(minutes=2)})
        events.append({'user_id': user_id, 'event_name': 'order_placed', 'event_timestamp': order_time})
    
    return pd.DataFrame(events)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="./data")
    ap.add_argument("--scale", choices=["demo", "full"], default="demo")
    args = ap.parse_args()

    cfg = SCALES[args.scale]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    start_date = datetime(2024, 1, 1)

    print(f"Generating QuickBite synthetic data [{args.scale}] ...")
    cities_df = gen_cities()
    categories_df = gen_categories()
    users_df = gen_users(cfg["n_users"], cities_df, start_date, cfg["days_history"])
    restaurants_df = gen_restaurants(cfg["n_restaurants"], cities_df, categories_df, start_date, cfg["days_history"])
    partners_df = gen_delivery_partners(cfg["n_partners"], cities_df, start_date, cfg["days_history"])
    coupons_df = gen_coupons()
    weather_df, traffic_df = gen_weather_traffic(cities_df, start_date, cfg["days_history"])
    orders_df, items_df, payments_df = gen_orders_and_related(
        cfg["n_orders"], users_df, restaurants_df, partners_df,
        coupons_df, weather_df, traffic_df, start_date, cfg["days_history"]
    )

    tables = {
        "cities": cities_df, "restaurant_categories": categories_df,
        "users": users_df, "restaurants": restaurants_df,
        "delivery_partners": partners_df, "coupons": coupons_df,
        "weather": weather_df, "traffic": traffic_df,
        "orders": orders_df, "order_items": items_df, "payments": payments_df,
    }
    for name, df in tables.items():
        path = out_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"  {name:25s} {len(df):>10,} rows -> {path}")

    print("\nDone. Load these CSVs with COPY / \\copy into the schema in sql/01_schema.sql,")
    print("or read directly with pandas for the Python notebooks.")


if __name__ == "__main__":
    main()
