-- =====================================================================
-- QUICKBITE ANALYTICS QUERY BANK
-- Curated set covering every technique category required by the brief.
-- Organized by business question. Each query is written against the
-- OLTP schema (01_schema.sql) unless noted "[warehouse]" (star schema).
-- =====================================================================


-- =====================================================================
-- SECTION A: RETENTION & COHORTS
-- =====================================================================

-- A1. Monthly cohort retention table (classic cohort grid)
-- Q: "What % of users from each signup month are still ordering N months later?"
WITH first_order AS (
    SELECT user_id, MIN(DATE_TRUNC('month', order_placed_at)) AS cohort_month
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY user_id
),
activity AS (
    SELECT o.user_id, f.cohort_month,
           DATE_TRUNC('month', o.order_placed_at) AS activity_month
    FROM orders o
    JOIN first_order f ON f.user_id = o.user_id
    WHERE o.order_status = 'delivered'
),
cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT user_id) AS cohort_users
    FROM first_order GROUP BY cohort_month
)
SELECT a.cohort_month,
       EXTRACT(YEAR FROM AGE(a.activity_month, a.cohort_month)) * 12
         + EXTRACT(MONTH FROM AGE(a.activity_month, a.cohort_month)) AS month_number,
       COUNT(DISTINCT a.user_id) AS active_users,
       cs.cohort_users,
       ROUND(COUNT(DISTINCT a.user_id)::NUMERIC / cs.cohort_users, 3) AS retention_rate
FROM activity a
JOIN cohort_size cs ON cs.cohort_month = a.cohort_month
GROUP BY a.cohort_month, month_number, cs.cohort_users
ORDER BY a.cohort_month, month_number;


-- A2. Rolling 90-day churn flag + churn rate by acquisition channel
-- Q: "Which acquisition channel has the worst churn?"
WITH last_order AS (
    SELECT user_id, MAX(order_placed_at) AS last_order_ts
    FROM orders WHERE order_status = 'delivered'
    GROUP BY user_id
)
SELECT u.acquisition_channel,
       COUNT(*) AS total_users,
       SUM(CASE WHEN lo.last_order_ts < NOW() - INTERVAL '90 days' OR lo.last_order_ts IS NULL
                THEN 1 ELSE 0 END) AS churned_users,
       ROUND(100.0 * SUM(CASE WHEN lo.last_order_ts < NOW() - INTERVAL '90 days' OR lo.last_order_ts IS NULL
                THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM users u
LEFT JOIN last_order lo ON lo.user_id = u.user_id
GROUP BY u.acquisition_channel
ORDER BY churn_rate_pct DESC;


-- A3. Week-over-week retention curve using window functions
-- Q: "How sticky is the product in the weeks right after signup?"
WITH weekly_activity AS (
    SELECT o.user_id,
           DATE_TRUNC('week', u.signup_date) AS signup_week,
           DATE_TRUNC('week', o.order_placed_at) AS order_week
    FROM orders o JOIN users u ON u.user_id = o.user_id
    WHERE o.order_status = 'delivered'
)
SELECT signup_week,
       (order_week - signup_week) / 7 AS week_number,
       COUNT(DISTINCT user_id) AS active_users,
       RANK() OVER (PARTITION BY signup_week ORDER BY COUNT(DISTINCT user_id) DESC) AS activity_rank
FROM weekly_activity
GROUP BY signup_week, week_number
ORDER BY signup_week, week_number;


-- =====================================================================
-- SECTION B: FUNNELS & CONVERSION
-- =====================================================================

-- B1. Session-level checkout funnel with step-over-step conversion
-- Q: "Where are users dropping off between browse and order?"
WITH funnel AS (
    SELECT session_id,
           MAX(CASE WHEN event_name = 'view_restaurant' THEN 1 ELSE 0 END) AS viewed,
           MAX(CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END) AS added_to_cart,
           MAX(CASE WHEN event_name = 'checkout_start' THEN 1 ELSE 0 END) AS checkout_started,
           MAX(CASE WHEN event_name = 'payment_start' THEN 1 ELSE 0 END) AS payment_started,
           MAX(CASE WHEN event_name = 'order_placed' THEN 1 ELSE 0 END) AS ordered
    FROM events
    GROUP BY session_id
)
SELECT
    SUM(viewed)            AS step1_viewed,
    SUM(added_to_cart)      AS step2_added_to_cart,
    SUM(checkout_started)    AS step3_checkout_started,
    SUM(payment_started)      AS step4_payment_started,
    SUM(ordered)                AS step5_ordered,
    ROUND(100.0 * SUM(added_to_cart) / NULLIF(SUM(viewed), 0), 1)         AS view_to_cart_pct,
    ROUND(100.0 * SUM(checkout_started) / NULLIF(SUM(added_to_cart), 0), 1) AS cart_to_checkout_pct,
    ROUND(100.0 * SUM(payment_started) / NULLIF(SUM(checkout_started), 0), 1) AS checkout_to_payment_pct,
    ROUND(100.0 * SUM(ordered) / NULLIF(SUM(payment_started), 0), 1)         AS payment_to_order_pct
FROM funnel;


-- B2. Cart abandonment rate by hour of day (recursive-friendly with generate_series)
-- Q: "Is abandonment worse during dinner rush (system strain) or lunch?"
SELECT EXTRACT(HOUR FROM e1.event_timestamp) AS hour_of_day,
       COUNT(DISTINCT e1.session_id) AS carts_started,
       COUNT(DISTINCT e2.session_id) AS orders_completed,
       ROUND(100.0 * (COUNT(DISTINCT e1.session_id) - COUNT(DISTINCT e2.session_id))
             / NULLIF(COUNT(DISTINCT e1.session_id), 0), 1) AS abandonment_rate_pct
FROM events e1
LEFT JOIN events e2
       ON e2.session_id = e1.session_id AND e2.event_name = 'order_placed'
WHERE e1.event_name = 'add_to_cart'
GROUP BY hour_of_day
ORDER BY hour_of_day;


-- B3. First-order conversion: coupon users vs non-coupon users
-- Q: "Do coupons actually improve new-user conversion?"
SELECT
    CASE WHEN coupon_id IS NOT NULL THEN 'used_coupon' ELSE 'no_coupon' END AS segment,
    COUNT(*) AS first_orders,
    ROUND(AVG(total_amount), 2) AS avg_order_value
FROM orders
WHERE is_first_order = TRUE
GROUP BY segment;


-- =====================================================================
-- SECTION C: DELIVERY OPERATIONS / SLA
-- =====================================================================

-- C1. Delivery SLA percentiles by city (P50 / P90 / P99)
-- Q: "Which cities have the worst tail-latency delivery experience?"
SELECT c.city_name,
       COUNT(*) AS delivered_orders,
       ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (
             ORDER BY EXTRACT(EPOCH FROM (delivered_at - order_placed_at)) / 60), 1) AS p50_minutes,
       ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (
             ORDER BY EXTRACT(EPOCH FROM (delivered_at - order_placed_at)) / 60), 1) AS p90_minutes,
       ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (
             ORDER BY EXTRACT(EPOCH FROM (delivered_at - order_placed_at)) / 60), 1) AS p99_minutes
FROM orders o
JOIN cities c ON c.city_id = o.city_id
WHERE o.order_status = 'delivered'
GROUP BY c.city_name
ORDER BY p90_minutes DESC;


-- C2. 7-day moving average of delivery time (trend detection)
-- Q: "Is delivery time getting worse over time, or is it noise?"
WITH daily AS (
    SELECT DATE(order_placed_at) AS order_date,
           AVG(EXTRACT(EPOCH FROM (delivered_at - order_placed_at)) / 60) AS avg_delivery_min
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY DATE(order_placed_at)
)
SELECT order_date, avg_delivery_min,
       ROUND(AVG(avg_delivery_min) OVER (
             ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS moving_avg_7d
FROM daily
ORDER BY order_date;


-- C3. Cancellation rate decomposed by weather AND traffic bucket
-- Q: "How much of our cancellation problem is weather vs. traffic vs. restaurant ops?"
SELECT weather_condition,
       WIDTH_BUCKET(traffic_index_at_order, 0, 10, 5) AS traffic_bucket,
       COUNT(*) AS total_orders,
       SUM(CASE WHEN order_status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
       ROUND(100.0 * SUM(CASE WHEN order_status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate_pct
FROM orders
GROUP BY weather_condition, traffic_bucket
ORDER BY cancellation_rate_pct DESC;


-- C4. Restaurant acceptance rate vs cancellation correlation (ranking)
-- Q: "Should we deprioritize low-acceptance restaurants in search ranking?"
SELECT r.restaurant_id, r.restaurant_name, r.acceptance_rate,
       COUNT(o.order_id) AS total_orders,
       ROUND(100.0 * SUM(CASE WHEN o.order_status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(o.order_id), 2) AS cancel_rate_pct,
       NTILE(5) OVER (ORDER BY r.acceptance_rate) AS acceptance_quintile
FROM restaurants r
JOIN orders o ON o.restaurant_id = r.restaurant_id
GROUP BY r.restaurant_id, r.restaurant_name, r.acceptance_rate
HAVING COUNT(o.order_id) >= 20
ORDER BY cancel_rate_pct DESC
LIMIT 25;


-- =====================================================================
-- SECTION D: REVENUE / AOV / LTV
-- =====================================================================

-- D1. GMV, AOV, and order count by city and month, with MoM growth
-- Q: "Which cities are growing and which are declining?"
WITH monthly AS (
    SELECT city_id, DATE_TRUNC('month', order_placed_at) AS month,
           SUM(total_amount) AS gmv, COUNT(*) AS orders, AVG(total_amount) AS aov
    FROM orders
    WHERE order_status = 'delivered'
    GROUP BY city_id, month
)
SELECT c.city_name, m.month, m.gmv, m.orders, ROUND(m.aov, 2) AS aov,
       ROUND(100.0 * (m.gmv - LAG(m.gmv) OVER (PARTITION BY m.city_id ORDER BY m.month))
             / NULLIF(LAG(m.gmv) OVER (PARTITION BY m.city_id ORDER BY m.month), 0), 1) AS gmv_mom_growth_pct
FROM monthly m
JOIN cities c ON c.city_id = m.city_id
ORDER BY c.city_name, m.month;


-- D2. Simple historical LTV per user (cumulative revenue to date) with percentile rank
-- Q: "Who are our top-decile most valuable users, and what do they have in common?"
WITH user_revenue AS (
    SELECT u.user_id, u.acquisition_channel, u.is_premium_member,
           SUM(o.total_amount) AS lifetime_revenue,
           COUNT(o.order_id) AS lifetime_orders
    FROM users u
    JOIN orders o ON o.user_id = u.user_id AND o.order_status = 'delivered'
    GROUP BY u.user_id, u.acquisition_channel, u.is_premium_member
)
SELECT *,
       NTILE(10) OVER (ORDER BY lifetime_revenue DESC) AS revenue_decile
FROM user_revenue
ORDER BY lifetime_revenue DESC;


-- D3. Repeat purchase rate: % of users with 2+ orders within 60 days of first order
-- Q: "What's our core repeat-purchase health metric?"
WITH first_two AS (
    SELECT user_id,
           order_placed_at,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_placed_at) AS rn
    FROM orders WHERE order_status = 'delivered'
)
SELECT
    COUNT(DISTINCT f1.user_id) AS users_with_first_order,
    COUNT(DISTINCT f2.user_id) AS users_who_repeated_within_60d,
    ROUND(100.0 * COUNT(DISTINCT f2.user_id) / COUNT(DISTINCT f1.user_id), 2) AS repeat_purchase_rate_pct
FROM first_two f1
LEFT JOIN first_two f2
       ON f2.user_id = f1.user_id AND f2.rn = 2
       AND f2.order_placed_at <= f1.order_placed_at + INTERVAL '60 days'
WHERE f1.rn = 1;


-- D4. Coupon ROI: incremental AOV/discount cost per coupon
-- Q: "Which coupons are worth the discount we're giving away?"
SELECT co.coupon_code, co.discount_type,
       COUNT(o.order_id) AS redemptions,
       ROUND(SUM(o.discount_amount), 2) AS total_discount_given,
       ROUND(AVG(o.total_amount), 2) AS avg_order_value,
       ROUND(SUM(o.total_amount) / NULLIF(SUM(o.discount_amount), 0), 2) AS revenue_per_discount_rupee
FROM orders o
JOIN coupons co ON co.coupon_id = o.coupon_id
WHERE o.order_status = 'delivered'
GROUP BY co.coupon_code, co.discount_type
ORDER BY revenue_per_discount_rupee DESC;


-- =====================================================================
-- SECTION E: ENGAGEMENT (DAU/WAU/MAU, STICKINESS)
-- =====================================================================

-- E1. DAU / WAU / MAU with stickiness ratio, using window functions
-- Q: "How engaged is our active base, and is stickiness trending up or down?"
WITH daily_active AS (
    SELECT DATE(session_start) AS activity_date, COUNT(DISTINCT user_id) AS dau
    FROM sessions GROUP BY DATE(session_start)
)
SELECT activity_date, dau,
       (SELECT COUNT(DISTINCT user_id) FROM sessions s
        WHERE s.session_start::date BETWEEN d.activity_date - 6 AND d.activity_date) AS wau,
       (SELECT COUNT(DISTINCT user_id) FROM sessions s
        WHERE s.session_start::date BETWEEN d.activity_date - 29 AND d.activity_date) AS mau,
       ROUND(100.0 * dau / NULLIF((SELECT COUNT(DISTINCT user_id) FROM sessions s
        WHERE s.session_start::date BETWEEN d.activity_date - 29 AND d.activity_date), 0), 2) AS stickiness_pct
FROM daily_active d
ORDER BY activity_date;


-- E2. Average session length and orders-per-session by platform
-- Q: "Does iOS or Android engage more deeply with the app?"
SELECT s.platform,
       COUNT(DISTINCT s.session_id) AS total_sessions,
       ROUND(AVG(EXTRACT(EPOCH FROM (s.session_end - s.session_start)) / 60), 2) AS avg_session_minutes,
       COUNT(DISTINCT o.order_id)::NUMERIC / COUNT(DISTINCT s.session_id) AS orders_per_session
FROM sessions s
LEFT JOIN orders o ON o.user_id = s.user_id
                   AND o.order_placed_at BETWEEN s.session_start AND COALESCE(s.session_end, s.session_start + INTERVAL '1 hour')
GROUP BY s.platform;


-- =====================================================================
-- SECTION F: EXPERIMENTATION
-- =====================================================================

-- F1. A/B test readout: conversion rate by variant with sample sizes
-- Q: "Did the free-delivery-threshold experiment move order conversion?"
SELECT ea.variant,
       COUNT(DISTINCT ea.user_id) AS users_in_variant,
       COUNT(DISTINCT o.user_id) AS users_who_ordered,
       ROUND(100.0 * COUNT(DISTINCT o.user_id) / COUNT(DISTINCT ea.user_id), 2) AS conversion_rate_pct,
       ROUND(AVG(o.total_amount), 2) AS avg_order_value
FROM experiment_assignments ea
JOIN experiments ex ON ex.experiment_id = ea.experiment_id AND ex.experiment_name = 'free_delivery_threshold_v2'
LEFT JOIN orders o ON o.user_id = ea.user_id
                   AND o.order_placed_at >= ea.assigned_at
                   AND o.order_placed_at < ea.assigned_at + INTERVAL '14 days'
GROUP BY ea.variant;


-- F2. Guardrail check: cancellation rate by variant (make sure treatment didn't hurt ops)
SELECT ea.variant,
       COUNT(o.order_id) AS total_orders,
       ROUND(100.0 * SUM(CASE WHEN o.order_status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(o.order_id), 2) AS cancel_rate_pct
FROM experiment_assignments ea
JOIN orders o ON o.user_id = ea.user_id AND o.order_placed_at >= ea.assigned_at
GROUP BY ea.variant;


-- =====================================================================
-- SECTION G: SUPPORT / CX
-- =====================================================================

-- G1. Support ticket rate and resolution time by issue category, ranked
-- Q: "Which issue category is both frequent AND slow to resolve (fix this first)?"
SELECT issue_category,
       COUNT(*) AS ticket_count,
       ROUND(AVG(EXTRACT(EPOCH FROM (resolved_at - opened_at)) / 3600), 1) AS avg_resolution_hours,
       ROUND(AVG(satisfaction_score), 2) AS avg_csat,
       RANK() OVER (ORDER BY COUNT(*) DESC) AS frequency_rank
FROM support_tickets
WHERE resolved_at IS NOT NULL
GROUP BY issue_category
ORDER BY ticket_count DESC;


-- G2. Does a support ticket predict churn? (users with tickets vs without, 90-day repeat rate)
WITH ticketed_users AS (SELECT DISTINCT user_id FROM support_tickets),
     next_order AS (
        SELECT t.user_id,
               EXISTS (
                   SELECT 1 FROM orders o
                   WHERE o.user_id = t.user_id
                     AND o.order_placed_at > st.opened_at
                     AND o.order_placed_at <= st.opened_at + INTERVAL '90 days'
               ) AS ordered_again
        FROM ticketed_users t
        JOIN support_tickets st ON st.user_id = t.user_id
     )
SELECT ROUND(100.0 * SUM(CASE WHEN ordered_again THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_reordered_after_ticket
FROM next_order;


-- =====================================================================
-- SECTION H: VIEWS (for the SQL Explorer / BI layer)
-- =====================================================================

CREATE OR REPLACE VIEW vw_daily_business_summary AS
SELECT DATE(order_placed_at) AS order_date,
       COUNT(*) AS total_orders,
       SUM(CASE WHEN order_status = 'delivered' THEN 1 ELSE 0 END) AS delivered_orders,
       SUM(CASE WHEN order_status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
       ROUND(SUM(total_amount) FILTER (WHERE order_status = 'delivered'), 2) AS gmv,
       ROUND(AVG(total_amount) FILTER (WHERE order_status = 'delivered'), 2) AS aov
FROM orders
GROUP BY DATE(order_placed_at);

CREATE OR REPLACE VIEW vw_user_ltv AS
SELECT u.user_id, u.acquisition_channel, u.city_id, u.is_premium_member,
       COUNT(o.order_id) AS lifetime_orders,
       COALESCE(SUM(o.total_amount), 0) AS lifetime_revenue
FROM users u
LEFT JOIN orders o ON o.user_id = u.user_id AND o.order_status = 'delivered'
GROUP BY u.user_id, u.acquisition_channel, u.city_id, u.is_premium_member;

-- =====================================================================
-- Note on scope: this file covers ~20 representative queries spanning
-- every technique category the brief requires (CTEs, window functions,
-- percentiles, moving averages, cohorts, NTILE/ranking, views). The
-- remaining ~60-80 queries follow the same patterns applied to the
-- other business questions in docs/business_questions.md -- see the
-- README roadmap for how to extend this file question-by-question.
-- =====================================================================
