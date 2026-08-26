-- BPS Data Warehouse - Data Marts
-- Materialized views designed to answer specific business questions.
-- See docs/business_questions.md for the analytical framework.

-- ============================================================
-- Q1: Indicator Trend
-- "Bagaimana perkembangan indikator dari tahun ke tahun?"
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS mart.indicator_trend CASCADE;

CREATE MATERIALIZED VIEW mart.indicator_trend AS
WITH national_series AS (
    SELECT
        d.year,
        i.indicator_key,
        i.indicator_name,
        i.unit,
        i.frequency,
        i.aggregation_method,
        CASE
            WHEN i.aggregation_method = 'SUM' THEN SUM(f.value)
            WHEN i.aggregation_method = 'AVG' THEN AVG(f.value)
            WHEN i.aggregation_method IN ('WEIGHTED_AVG', 'DIRECT_NATIONAL', 'N/A') THEN NULL
            ELSE NULL
        END AS national_value
    FROM warehouse.fact_economic f
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
    JOIN warehouse.dim_indicator i ON f.indicator_key = i.indicator_key
    GROUP BY d.year, i.indicator_key, i.indicator_name, i.unit, i.frequency, i.aggregation_method
)
SELECT
    year,
    indicator_key,
    indicator_name,
    unit,
    frequency,
    national_value,
    LAG(national_value) OVER (
        PARTITION BY indicator_key
        ORDER BY year
    ) AS previous_value,
    CASE
        WHEN national_value IS NULL THEN NULL
        WHEN LAG(national_value) OVER (PARTITION BY indicator_key ORDER BY year) IS NULL THEN NULL
        ELSE ROUND(
            ((national_value - LAG(national_value) OVER (
                PARTITION BY indicator_key
                ORDER BY year
            )) / NULLIF(LAG(national_value) OVER (
                PARTITION BY indicator_key
                ORDER BY year
            ), 0) * 100)::numeric,
            2
        )
    END AS growth_pct
FROM national_series;

CREATE INDEX IF NOT EXISTS idx_mart_indicator_trend_year
    ON mart.indicator_trend (year);
CREATE INDEX IF NOT EXISTS idx_mart_indicator_trend_indicator
    ON mart.indicator_trend (indicator_key);

-- ============================================================
-- Q2 & Q3: Regional Performance
-- "Provinsi mana yang memiliki nilai tertinggi dan terendah?"
-- "Provinsi mana yang mengalami pertumbuhan paling tinggi?"
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS mart.regional_performance CASCADE;

CREATE MATERIALIZED VIEW mart.regional_performance AS
SELECT
    d.year,
    r.region_key,
    r.region_name,
    i.indicator_key,
    i.indicator_name,
    f.value,
    RANK() OVER (
        PARTITION BY d.year, i.indicator_key
        ORDER BY f.value DESC
    ) AS regional_rank,
    LAG(f.value) OVER (
        PARTITION BY r.region_key, i.indicator_key
        ORDER BY d.year
    ) AS previous_value,
    ROUND(
        ((f.value - LAG(f.value) OVER (
            PARTITION BY r.region_key, i.indicator_key
            ORDER BY d.year
        )) / NULLIF(LAG(f.value) OVER (
            PARTITION BY r.region_key, i.indicator_key
            ORDER BY d.year
        ), 0) * 100)::numeric,
        2
    ) AS growth_pct
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_region r ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i ON f.indicator_key = i.indicator_key;

CREATE INDEX IF NOT EXISTS idx_mart_regional_perf_year
    ON mart.regional_performance (year);
CREATE INDEX IF NOT EXISTS idx_mart_regional_perf_region
    ON mart.regional_performance (region_key);
CREATE INDEX IF NOT EXISTS idx_mart_regional_perf_indicator
    ON mart.regional_performance (indicator_key);

-- ============================================================
-- Q4: Economic Overview
-- "Apakah perubahan indikator nasional sejalan dengan perubahan
--  di tingkat provinsi?"
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS mart.economic_overview CASCADE;

CREATE MATERIALIZED VIEW mart.economic_overview AS
WITH national_series AS (
    SELECT
        d.year,
        i.indicator_key,
        i.indicator_name,
        i.unit,
        i.frequency,
        i.concept,
        i.definition,
        i.data_source,
        i.aggregation_method,
        CASE
            WHEN i.aggregation_method = 'SUM' THEN SUM(f.value)
            WHEN i.aggregation_method = 'AVG' THEN AVG(f.value)
            WHEN i.aggregation_method IN ('WEIGHTED_AVG', 'DIRECT_NATIONAL', 'N/A') THEN NULL
            ELSE NULL
        END AS national_value,
        COUNT(DISTINCT r.region_key) AS region_count
    FROM warehouse.fact_economic f
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
    JOIN warehouse.dim_region r ON f.region_key = r.region_key
    JOIN warehouse.dim_indicator i ON f.indicator_key = i.indicator_key
    GROUP BY d.year, i.indicator_key, i.indicator_name, i.unit, i.frequency,
             i.concept, i.definition, i.data_source, i.aggregation_method
)
SELECT
    year,
    indicator_key,
    indicator_name,
    unit,
    frequency,
    concept,
    definition,
    data_source,
    national_value,
    LAG(national_value) OVER (
        PARTITION BY indicator_key
        ORDER BY year
    ) AS previous_national_value,
    CASE
        WHEN national_value IS NULL THEN NULL
        WHEN LAG(national_value) OVER (PARTITION BY indicator_key ORDER BY year) IS NULL THEN NULL
        ELSE ROUND(
            ((national_value - LAG(national_value) OVER (
                PARTITION BY indicator_key
                ORDER BY year
            )) / NULLIF(LAG(national_value) OVER (
                PARTITION BY indicator_key
                ORDER BY year
            ), 0) * 100)::numeric,
            2
        )
    END AS national_growth_pct,
    region_count
FROM national_series;

CREATE INDEX IF NOT EXISTS idx_mart_econ_overview_year
    ON mart.economic_overview (year);
CREATE INDEX IF NOT EXISTS idx_mart_econ_overview_indicator
    ON mart.economic_overview (indicator_key);