-- Year-over-Year Analysis
-- Computes YoY change for economic indicators

-- 1. Year-over-year comparison for all indicators
SELECT
    d.year,
    r.region_name,
    i.indicator_name,
    f.value,
    LAG(f.value) OVER (
        PARTITION BY r.region_name, i.indicator_name
        ORDER BY d.year
    ) AS previous_year_value,
    ROUND(
        (f.value - LAG(f.value) OVER (
            PARTITION BY r.region_name, i.indicator_name
            ORDER BY d.year
        )) / NULLIF(LAG(f.value) OVER (
            PARTITION BY r.region_name, i.indicator_name
            ORDER BY d.year
        ), 0) * 100,
        2
    ) AS yoy_growth_pct
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
JOIN warehouse.dim_region r
    ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i
    ON f.indicator_key = i.indicator_key
ORDER BY
    i.indicator_name,
    r.region_name,
    d.year;

-- 2. YoY growth by region for a specific indicator
-- Replace :indicator_name with the actual indicator
SELECT
    d.year,
    r.region_name,
    f.value,
    ROUND(
        (f.value - LAG(f.value) OVER (
            PARTITION BY r.region_name
            ORDER BY d.year
        )) / NULLIF(LAG(f.value) OVER (
            PARTITION BY r.region_name
            ORDER BY d.year
        ), 0) * 100,
        2
    ) AS yoy_growth_pct
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
JOIN warehouse.dim_region r
    ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i
    ON f.indicator_key = i.indicator_key
WHERE i.indicator_name = :indicator_name
ORDER BY r.region_name, d.year;

-- 3. National aggregate YoY (no regional breakdown)
SELECT
    d.year,
    i.indicator_name,
    SUM(f.value) AS national_value,
    ROUND(
        (SUM(f.value) - LAG(SUM(f.value)) OVER (
            PARTITION BY i.indicator_name
            ORDER BY d.year
        )) / NULLIF(LAG(SUM(f.value)) OVER (
            PARTITION BY i.indicator_name
            ORDER BY d.year
        ), 0) * 100,
        2
    ) AS yoy_growth_pct
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
JOIN warehouse.dim_indicator i
    ON f.indicator_key = i.indicator_key
GROUP BY d.year, i.indicator_name
ORDER BY i.indicator_name, d.year;