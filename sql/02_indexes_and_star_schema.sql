-- =====================================================================
-- 02: INDEXES (on the OLTP schema)
-- =====================================================================
CREATE INDEX idx_orders_user_id          ON orders(user_id);
CREATE INDEX idx_orders_restaurant_id     ON orders(restaurant_id);
CREATE INDEX idx_orders_placed_at          ON orders(order_placed_at);
CREATE INDEX idx_orders_status              ON orders(order_status);
CREATE INDEX idx_orders_city_date            ON orders(city_id, order_placed_at);

CREATE INDEX idx_events_user_id               ON events(user_id);
CREATE INDEX idx_events_session_id             ON events(session_id);
CREATE INDEX idx_events_name_ts                 ON events(event_name, event_timestamp);

CREATE INDEX idx_sessions_user_id                ON sessions(user_id);
CREATE INDEX idx_sessions_start                   ON sessions(session_start);

CREATE INDEX idx_users_city                         ON users(city_id);
CREATE INDEX idx_users_signup_date                   ON users(signup_date);
CREATE INDEX idx_users_channel                        ON users(acquisition_channel);

CREATE INDEX idx_restaurants_city_category             ON restaurants(city_id, category_id);
CREATE INDEX idx_support_tickets_user_id                 ON support_tickets(user_id);
CREATE INDEX idx_notifications_user_type                  ON notifications(user_id, notification_type);

-- =====================================================================
-- STAR SCHEMA / DATA WAREHOUSE LAYER
-- This is how a company like Zomato would model this for BI tools
-- (Looker/Mode/Metabase) sitting on top of a warehouse (BigQuery/Snowflake).
-- Grain of the primary fact table: one row per order.
-- =====================================================================

-- ---------------- DIMENSION TABLES ----------------

CREATE TABLE dim_date (
    date_key         INT PRIMARY KEY,        -- yyyymmdd
    full_date          DATE NOT NULL,
    day_of_week          VARCHAR(10),
    is_weekend             BOOLEAN,
    month_name               VARCHAR(10),
    quarter                    SMALLINT,
    year                          SMALLINT,
    is_festival_day                 BOOLEAN   -- Diwali, New Year etc. -- demand spikes
);

CREATE TABLE dim_user (
    user_key            BIGSERIAL PRIMARY KEY, -- surrogate key (supports SCD type 2)
    user_id                BIGINT NOT NULL,      -- natural key back to OLTP
    signup_date               DATE,
    city_name                    VARCHAR(100),
    tier                           VARCHAR(10),
    acquisition_channel               VARCHAR(30),
    is_premium_member                   BOOLEAN,
    age_band                              VARCHAR(10),
    gender                                  VARCHAR(15),
    valid_from                                DATE,
    valid_to                                    DATE,        -- NULL = current row
    is_current                                    BOOLEAN
);

CREATE TABLE dim_restaurant (
    restaurant_key       BIGSERIAL PRIMARY KEY,
    restaurant_id            BIGINT NOT NULL,
    restaurant_name             VARCHAR(150),
    city_name                     VARCHAR(100),
    category_name                   VARCHAR(50),
    price_tier                        VARCHAR(10),
    avg_rating_bucket                   VARCHAR(10) -- '4.5+','4.0-4.5','<4.0'
);

CREATE TABLE dim_delivery_partner (
    partner_key           BIGSERIAL PRIMARY KEY,
    partner_id                BIGINT NOT NULL,
    city_name                    VARCHAR(100),
    vehicle_type                    VARCHAR(15),
    tenure_bucket                     VARCHAR(15)  -- '<3mo','3-12mo','1yr+'
);

CREATE TABLE dim_coupon (
    coupon_key             BIGSERIAL PRIMARY KEY,
    coupon_id                  INT NOT NULL,
    discount_type                  VARCHAR(15),
    target_segment                     VARCHAR(30)
);

-- ---------------- FACT TABLES ----------------

-- Grain: one row per order (the primary fact table for the platform)
CREATE TABLE fact_orders (
    order_key             BIGSERIAL PRIMARY KEY,
    order_id                  BIGINT NOT NULL,
    date_key                     INT NOT NULL REFERENCES dim_date(date_key),
    user_key                       BIGINT NOT NULL REFERENCES dim_user(user_key),
    restaurant_key                    BIGINT NOT NULL REFERENCES dim_restaurant(restaurant_key),
    partner_key                          BIGINT REFERENCES dim_delivery_partner(partner_key),
    coupon_key                              BIGINT REFERENCES dim_coupon(coupon_key),
    order_status                               VARCHAR(15),
    is_first_order                                BOOLEAN,
    -- measures
    subtotal_amount                                 NUMERIC(9,2),
    delivery_fee                                       NUMERIC(7,2),
    discount_amount                                       NUMERIC(7,2),
    total_amount                                             NUMERIC(9,2),
    delivery_time_minutes                                       NUMERIC(6,2),
    prep_time_minutes                                              NUMERIC(6,2),
    distance_km                                                       NUMERIC(5,2)
);

-- Grain: one row per user per day (pre-aggregated activity fact --
-- makes DAU/WAU/MAU and retention queries fast without scanning events)
CREATE TABLE fact_user_activity_daily (
    activity_key         BIGSERIAL PRIMARY KEY,
    date_key                 INT NOT NULL REFERENCES dim_date(date_key),
    user_key                    BIGINT NOT NULL REFERENCES dim_user(user_key),
    sessions_count                  INT,
    total_session_seconds              INT,
    orders_placed                        INT,
    gmv                                     NUMERIC(9,2),
    app_opened                                BOOLEAN
);

-- Grain: one row per funnel-step event per session (used for funnel queries)
CREATE TABLE fact_funnel_events (
    funnel_event_key      BIGSERIAL PRIMARY KEY,
    date_key                  INT NOT NULL REFERENCES dim_date(date_key),
    user_key                     BIGINT NOT NULL REFERENCES dim_user(user_key),
    session_id                      BIGINT,
    funnel_step                        VARCHAR(30),  -- 'view_restaurant','add_to_cart','checkout_start','payment','order_success'
    step_order                            SMALLINT,
    event_timestamp                          TIMESTAMP
);

-- =====================================================================
-- HOW ZOMATO-SCALE COMPANIES ORGANIZE THIS (design notes)
-- =====================================================================
-- 1. OLTP (Postgres/MySQL, sharded by city_id or user_id) -> CDC via
--    Debezium/Kafka -> raw landing zone in the warehouse (BigQuery/
--    Snowflake), untouched, append-only.
-- 2. dbt (or equivalent) builds staging models (1:1 cleaned OLTP
--    tables) -> intermediate models (dedup, SCD2 for dim_user) ->
--    marts (the star schema above). Every model has a primary-key
--    test, not-null tests, and referential-integrity tests.
-- 3. fact_orders is partitioned by date_key and clustered by city_key
--    for query performance at 100M+ row scale.
-- 4. A separate "activity/event" pipeline (Kafka -> Flink/Spark
--    Streaming -> fact_user_activity_daily) pre-aggregates clickstream
--    so DAU/retention dashboards don't scan raw events at query time.
-- 5. Metrics themselves are defined once in a semantic layer (dbt
--    metrics / LookML) so "repeat purchase rate" means the same thing
--    on every dashboard -- this is the difference between a "student
--    dashboard" and a real analytics platform.
-- =====================================================================
