-- =====================================================================
-- QUICKBITE PRODUCT ANALYTICS PLATFORM
-- OLTP Schema (source-of-truth tables, PostgreSQL dialect)
-- =====================================================================
-- Design philosophy: this is what QuickBite's application databases
-- would actually look like. In Part 2 (star_schema.sql) we transform
-- this into an analytics-friendly warehouse (facts + dimensions).
-- =====================================================================

-- ---------------------------------------------------------------------
-- CITIES
-- Why it exists: every retention/ops metric at a food delivery company
-- is city-level before it's national. Tier and launch_date let us
-- explain "why does Jaipur look different from Mumbai" (market maturity).
-- ---------------------------------------------------------------------
CREATE TABLE cities (
    city_id            SERIAL PRIMARY KEY,
    city_name          VARCHAR(100) NOT NULL,
    state              VARCHAR(100) NOT NULL,
    tier                VARCHAR(10)  NOT NULL,        -- 'Tier1','Tier2','Tier3'
    launch_date         DATE NOT NULL,                 -- when QuickBite entered this city
    population_lakhs    NUMERIC(6,2),
    avg_traffic_index   NUMERIC(4,2)                   -- 0-10, used to simulate delivery delays
);

-- ---------------------------------------------------------------------
-- USERS
-- Why it exists: the atomic unit of retention/LTV/CAC analysis.
-- acquisition_channel + referral fields let us answer "which channel
-- brings the highest-LTV users" without joining five tables.
-- ---------------------------------------------------------------------
CREATE TABLE users (
    user_id             BIGSERIAL PRIMARY KEY,
    signup_date          DATE NOT NULL,
    city_id              INT NOT NULL REFERENCES cities(city_id),
    acquisition_channel   VARCHAR(30) NOT NULL,   -- 'organic','paid_social','referral','paid_search','push_reactivation'
    referred_by_user_id   BIGINT REFERENCES users(user_id),
    is_premium_member     BOOLEAN DEFAULT FALSE,   -- "QuickBite Plus" subscription
    premium_start_date    DATE,
    age_band              VARCHAR(10),             -- '18-24','25-34','35-44','45+'
    gender                VARCHAR(15),
    device_type           VARCHAR(10),             -- 'iOS','Android'
    signup_channel_cost    NUMERIC(8,2),            -- CAC contribution, NULL for organic
    is_churned            BOOLEAN DEFAULT FALSE,   -- no order in trailing 90 days, updated by batch job
    churned_at             DATE
);

-- ---------------------------------------------------------------------
-- RESTAURANT_CATEGORIES
-- Why it exists: cuisine-level analysis ("which cuisines drive repeat
-- orders") needs a clean dimension rather than a free-text field.
-- ---------------------------------------------------------------------
CREATE TABLE restaurant_categories (
    category_id       SERIAL PRIMARY KEY,
    category_name      VARCHAR(50) NOT NULL,      -- 'North Indian','Chinese','Pizza','Healthy', etc.
    is_premium_cuisine   BOOLEAN DEFAULT FALSE
);

-- ---------------------------------------------------------------------
-- RESTAURANTS
-- Why it exists: supply-side entity. Rating, acceptance rate, and prep
-- time drive delivery SLA and cancellation analysis.
-- ---------------------------------------------------------------------
CREATE TABLE restaurants (
    restaurant_id        BIGSERIAL PRIMARY KEY,
    restaurant_name        VARCHAR(150) NOT NULL,
    city_id                 INT NOT NULL REFERENCES cities(city_id),
    category_id             INT NOT NULL REFERENCES restaurant_categories(category_id),
    onboarded_date           DATE NOT NULL,
    avg_rating               NUMERIC(2,1),          -- 1.0 - 5.0
    avg_prep_time_minutes     INT,                   -- kitchen prep time
    acceptance_rate           NUMERIC(4,3),          -- % of orders restaurant accepts
    price_tier                VARCHAR(10),           -- 'budget','mid','premium'
    is_active                 BOOLEAN DEFAULT TRUE
);

-- ---------------------------------------------------------------------
-- RESTAURANT_AVAILABILITY
-- Why it exists: restaurants aren't open 24/7; open/close events explain
-- why some orders fail at checkout ("restaurant closed") -- a real
-- cancellation driver, not noise.
-- ---------------------------------------------------------------------
CREATE TABLE restaurant_availability (
    availability_id     BIGSERIAL PRIMARY KEY,
    restaurant_id         BIGINT NOT NULL REFERENCES restaurants(restaurant_id),
    day_of_week            SMALLINT NOT NULL,       -- 0=Mon .. 6=Sun
    open_time               TIME NOT NULL,
    close_time               TIME NOT NULL,
    is_currently_open         BOOLEAN DEFAULT TRUE
);

-- ---------------------------------------------------------------------
-- DELIVERY_PARTNERS
-- Why it exists: delivery time / SLA analysis needs a supply-of-labor
-- entity. Rating and vehicle_type explain variance in delivery speed.
-- ---------------------------------------------------------------------
CREATE TABLE delivery_partners (
    partner_id          BIGSERIAL PRIMARY KEY,
    city_id                INT NOT NULL REFERENCES cities(city_id),
    joined_date             DATE NOT NULL,
    vehicle_type             VARCHAR(15),           -- 'bike','bicycle','scooter'
    avg_rating               NUMERIC(2,1),
    is_active                BOOLEAN DEFAULT TRUE,
    shift_type                VARCHAR(15)            -- 'full_time','part_time','peak_hours_only'
);

-- ---------------------------------------------------------------------
-- COUPONS
-- Why it exists: promo/discount analysis (does a coupon increase
-- first-order conversion, and does that user retain afterward?).
-- ---------------------------------------------------------------------
CREATE TABLE coupons (
    coupon_id           SERIAL PRIMARY KEY,
    coupon_code           VARCHAR(30) UNIQUE NOT NULL,
    discount_type          VARCHAR(15),             -- 'flat','percentage','free_delivery'
    discount_value          NUMERIC(8,2),
    min_order_value          NUMERIC(8,2),
    valid_from                DATE,
    valid_to                   DATE,
    target_segment             VARCHAR(30)           -- 'new_user','churn_risk','all','premium'
);

-- ---------------------------------------------------------------------
-- EXPERIMENTS + EXPERIMENT_ASSIGNMENTS
-- Why it exists: this is what makes the project "product analytics"
-- and not just "reporting". Every A/B test in Part 8 is backed by these.
-- ---------------------------------------------------------------------
CREATE TABLE experiments (
    experiment_id        SERIAL PRIMARY KEY,
    experiment_name         VARCHAR(100) NOT NULL,   -- e.g. 'free_delivery_threshold_v2'
    hypothesis                TEXT,
    primary_metric             VARCHAR(50),
    start_date                  DATE,
    end_date                     DATE,
    status                        VARCHAR(15)          -- 'running','concluded','shipped','rolled_back'
);

CREATE TABLE experiment_assignments (
    assignment_id        BIGSERIAL PRIMARY KEY,
    experiment_id           INT NOT NULL REFERENCES experiments(experiment_id),
    user_id                    BIGINT NOT NULL REFERENCES users(user_id),
    variant                     VARCHAR(20) NOT NULL,  -- 'control','treatment_a','treatment_b'
    assigned_at                  TIMESTAMP NOT NULL
);

-- ---------------------------------------------------------------------
-- SESSIONS
-- Why it exists: app-open to app-close; underlies DAU/WAU/MAU,
-- stickiness, and session-length metrics.
-- ---------------------------------------------------------------------
CREATE TABLE sessions (
    session_id            BIGSERIAL PRIMARY KEY,
    user_id                  BIGINT NOT NULL REFERENCES users(user_id),
    session_start              TIMESTAMP NOT NULL,
    session_end                 TIMESTAMP,
    platform                     VARCHAR(10),         -- 'iOS','Android','Web'
    app_version                   VARCHAR(10),
    entry_source                   VARCHAR(20)          -- 'push','organic_open','deep_link','referral_link'
);

-- ---------------------------------------------------------------------
-- EVENTS
-- Why it exists: the clickstream. Powers funnel analysis
-- (browse -> add_to_cart -> checkout_start -> payment -> order_success).
-- ---------------------------------------------------------------------
CREATE TABLE events (
    event_id               BIGSERIAL PRIMARY KEY,
    session_id                BIGINT NOT NULL REFERENCES sessions(session_id),
    user_id                     BIGINT NOT NULL REFERENCES users(user_id),
    event_name                    VARCHAR(40) NOT NULL, -- 'app_open','search','view_restaurant',
                                                          -- 'add_to_cart','checkout_start','apply_coupon',
                                                          -- 'payment_start','order_placed','order_cancelled'
    event_timestamp                TIMESTAMP NOT NULL,
    restaurant_id                    BIGINT REFERENCES restaurants(restaurant_id),
    metadata                          JSONB              -- flexible: search terms, screen name, etc.
);

-- ---------------------------------------------------------------------
-- ORDERS
-- Why it exists: the core transaction fact. Almost every business
-- question in Part 5 joins through this table.
-- ---------------------------------------------------------------------
CREATE TABLE orders (
    order_id                BIGSERIAL PRIMARY KEY,
    user_id                    BIGINT NOT NULL REFERENCES users(user_id),
    restaurant_id                 BIGINT NOT NULL REFERENCES restaurants(restaurant_id),
    delivery_partner_id             BIGINT REFERENCES delivery_partners(partner_id),
    city_id                          INT NOT NULL REFERENCES cities(city_id),
    coupon_id                         INT REFERENCES coupons(coupon_id),
    order_placed_at                    TIMESTAMP NOT NULL,
    order_accepted_at                    TIMESTAMP,
    food_ready_at                         TIMESTAMP,
    delivery_partner_assigned_at            TIMESTAMP,
    picked_up_at                             TIMESTAMP,
    delivered_at                              TIMESTAMP,
    order_status                               VARCHAR(15) NOT NULL, -- 'delivered','cancelled','failed'
    cancellation_reason                          VARCHAR(50),         -- NULL if delivered
    cancelled_by                                  VARCHAR(15),         -- 'user','restaurant','system'
    subtotal_amount                                NUMERIC(9,2),
    delivery_fee                                    NUMERIC(7,2),
    discount_amount                                  NUMERIC(7,2),
    total_amount                                      NUMERIC(9,2),
    payment_method                                     VARCHAR(15),   -- 'upi','card','wallet','cod'
    distance_km                                         NUMERIC(5,2),
    weather_condition                                    VARCHAR(15), -- denormalized snapshot at order time
    traffic_index_at_order                                NUMERIC(4,2),
    is_first_order                                         BOOLEAN DEFAULT FALSE
);

-- ---------------------------------------------------------------------
-- ORDER_ITEMS
-- Why it exists: item-level detail enables market basket analysis
-- and AOV decomposition (what's actually driving basket size).
-- ---------------------------------------------------------------------
CREATE TABLE order_items (
    order_item_id         BIGSERIAL PRIMARY KEY,
    order_id                  BIGINT NOT NULL REFERENCES orders(order_id),
    item_name                    VARCHAR(150),
    category_id                    INT REFERENCES restaurant_categories(category_id),
    unit_price                       NUMERIC(8,2),
    quantity                          INT,
    line_total                         NUMERIC(9,2)
);

-- ---------------------------------------------------------------------
-- PAYMENTS
-- Why it exists: separates payment lifecycle (auth, capture, failure,
-- refund) from the order itself -- needed for payment-failure funnel
-- analysis and refund-driven churn.
-- ---------------------------------------------------------------------
CREATE TABLE payments (
    payment_id             BIGSERIAL PRIMARY KEY,
    order_id                  BIGINT NOT NULL REFERENCES orders(order_id),
    payment_method                VARCHAR(15),
    amount                           NUMERIC(9,2),
    payment_status                     VARCHAR(15),  -- 'success','failed','refunded'
    failure_reason                        VARCHAR(50),
    processed_at                            TIMESTAMP
);

-- ---------------------------------------------------------------------
-- WEATHER
-- Why it exists: exogenous variable that explains delivery-time and
-- cancellation variance that isn't the platform's "fault".
-- ---------------------------------------------------------------------
CREATE TABLE weather (
    weather_id             BIGSERIAL PRIMARY KEY,
    city_id                   INT NOT NULL REFERENCES cities(city_id),
    date                        DATE NOT NULL,
    hour                          SMALLINT NOT NULL,
    condition                       VARCHAR(15),   -- 'clear','rain','heavy_rain','heatwave'
    temperature_c                    NUMERIC(4,1)
);

-- ---------------------------------------------------------------------
-- TRAFFIC
-- Why it exists: same rationale as weather -- explains delivery SLA
-- variance by city/hour independent of platform performance.
-- ---------------------------------------------------------------------
CREATE TABLE traffic (
    traffic_id              BIGSERIAL PRIMARY KEY,
    city_id                    INT NOT NULL REFERENCES cities(city_id),
    date                          DATE NOT NULL,
    hour                            SMALLINT NOT NULL,
    traffic_index                     NUMERIC(4,2)  -- 0 (empty) - 10 (gridlock)
);

-- ---------------------------------------------------------------------
-- NOTIFICATIONS
-- Why it exists: push/email engagement drives reactivation and is a
-- lever tested in experiments (send-time optimization).
-- ---------------------------------------------------------------------
CREATE TABLE notifications (
    notification_id          BIGSERIAL PRIMARY KEY,
    user_id                     BIGINT NOT NULL REFERENCES users(user_id),
    notification_type              VARCHAR(30),  -- 'cart_abandon','win_back','promo','order_update'
    sent_at                           TIMESTAMP,
    opened_at                           TIMESTAMP,
    clicked_at                            TIMESTAMP,
    channel                                 VARCHAR(15)  -- 'push','sms','email','whatsapp'
);

-- ---------------------------------------------------------------------
-- SUPPORT_TICKETS
-- Why it exists: post-order friction (refund disputes, missing items)
-- is a leading indicator of churn that pure transaction data misses.
-- ---------------------------------------------------------------------
CREATE TABLE support_tickets (
    ticket_id                BIGSERIAL PRIMARY KEY,
    user_id                     BIGINT NOT NULL REFERENCES users(user_id),
    order_id                       BIGINT REFERENCES orders(order_id),
    issue_category                    VARCHAR(30),  -- 'missing_item','late_delivery','refund','app_bug'
    opened_at                            TIMESTAMP,
    resolved_at                             TIMESTAMP,
    resolution_type                            VARCHAR(20), -- 'refund','replacement','apology_credit','no_action'
    satisfaction_score                            SMALLINT   -- 1-5, post-resolution survey
);

-- ---------------------------------------------------------------------
-- Indexes on high-cardinality FK / filter columns
-- (kept in a separate file: 02_indexes.sql, so the schema stays legible)
-- ---------------------------------------------------------------------
