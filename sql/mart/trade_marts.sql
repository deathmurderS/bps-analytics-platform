-- BPS Data Warehouse - Foreign Trade Data Marts
-- Grain: one row = one product × one country × one port × one period.
-- Source: warehouse.fact_trade

-- ============================================================
-- Trade Trend: Export/Import value by period
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS mart.trade_trend CASCADE;

CREATE MATERIALIZED VIEW mart.trade_trend AS
SELECT
    d.year,
    tf.flow_name AS trade_flow,
    COALESCE(SUM(f.value_usd), 0) AS total_value_usd,
    COALESCE(SUM(f.net_weight_kg), 0) AS total_weight_kg,
    COUNT(*) AS transaction_count
FROM warehouse.fact_trade f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_trade_flow tf ON f.trade_type = tf.trade_flow
GROUP BY d.year, tf.flow_name
ORDER BY d.year, tf.flow_name;

-- ============================================================
-- Regional Performance (by port / region)
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS mart.trade_regional CASCADE;

CREATE MATERIALIZED VIEW mart.trade_regional AS
SELECT
    d.year,
    f.port_key,
    f.trade_type,
    COALESCE(SUM(f.value_usd), 0) AS value_usd,
    COALESCE(SUM(f.net_weight_kg), 0) AS weight_kg,
    COUNT(*) AS record_count
FROM warehouse.fact_trade f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
GROUP BY d.year, f.port_key, f.trade_type
ORDER BY d.year, f.port_key;

-- ============================================================
-- Commodity Ranking (top products by value)
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS mart.trade_commodity CASCADE;

CREATE MATERIALIZED VIEW mart.trade_commodity AS
SELECT
    d.year,
    tf.flow_name AS trade_flow,
    p.product_code,
    p.product_name,
    COALESCE(SUM(f.value_usd), 0) AS total_value_usd,
    COALESCE(SUM(f.net_weight_kg), 0) AS total_weight_kg,
    RANK() OVER (
        PARTITION BY d.year, tf.flow_name
        ORDER BY SUM(f.value_usd) DESC
    ) AS commodity_rank
FROM warehouse.fact_trade f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_trade_flow tf ON f.trade_type = tf.trade_flow
JOIN warehouse.dim_product p ON f.product_key = p.product_key
GROUP BY d.year, tf.flow_name, p.product_code, p.product_name
ORDER BY d.year, tf.flow_name, commodity_rank;

-- ============================================================
-- Trading Partner (country) Analysis
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS mart.trade_partner CASCADE;

CREATE MATERIALIZED VIEW mart.trade_partner AS
SELECT
    d.year,
    tf.flow_name AS trade_flow,
    c.country_code,
    c.country_name,
    COALESCE(SUM(f.value_usd), 0) AS total_value_usd,
    RANK() OVER (
        PARTITION BY d.year, tf.flow_name
        ORDER BY SUM(f.value_usd) DESC
    ) AS partner_rank
FROM warehouse.fact_trade f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_trade_flow tf ON f.trade_type = tf.trade_flow
JOIN warehouse.dim_country c ON f.country_key = c.country_key
GROUP BY d.year, tf.flow_name, c.country_code, c.country_name
ORDER BY d.year, tf.flow_name, partner_rank;

-- ============================================================
-- Cross-Domain: Economic vs Trade Comparison
-- Combines Economic and Trade domains via shared dim_date.
-- Uses economic_overview if it exists, otherwise skip.
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS mart.economic_trade_bridge CASCADE;

CREATE MATERIALIZED VIEW mart.economic_trade_bridge AS
SELECT
    econ.year,
    econ.national_value,
    econ.national_growth_pct,
    COALESCE(trade.export_value_usd, 0) AS export_total_usd,
    COALESCE(trade.import_value_usd, 0) AS import_total_usd,
    COALESCE(trade.balance_usd, 0) AS trade_balance_usd
FROM (
    -- Economic domain: national value and growth per year
    SELECT
        year,
        national_value,
        national_growth_pct
    FROM mart.economic_overview
) econ
FULL OUTER JOIN (
    -- Trade domain: export/import/balance per year
    SELECT
        year,
        SUM(CASE WHEN trade_flow = 'Ekspor' THEN total_value_usd ELSE 0 END) AS export_value_usd,
        SUM(CASE WHEN trade_flow = 'Impor' THEN total_value_usd ELSE 0 END) AS import_value_usd,
        SUM(CASE WHEN trade_flow = 'Ekspor' THEN total_value_usd
                 WHEN trade_flow = 'Impor' THEN -total_value_usd
                 ELSE 0 END) AS balance_usd
    FROM mart.trade_trend
    GROUP BY year
) trade ON econ.year = trade.year
ORDER BY econ.year;
