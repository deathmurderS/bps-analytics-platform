-- Trend Analysis
-- Identifies trends and patterns in economic indicators

-- 1. Long-term trend by indicator (multi-year average change)
SELECT
    i.indicator_name,
    r.region_name,
    COUNT(*) AS years_observed,
    ROUND(AVG(f.value), 6) AS avg_value,
    ROUND(STDDEV(f.value), 6) AS stddev_value,
    ROUND(
        (MAX(f.value) - MIN(f.value)) / NULLIF(MIN(f.value), 0) * 100,
        2
    ) AS total_change_pct
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
JOIN warehouse.dim_region r
    ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i
    ON f.indicator_key = i.indicator_key
GROUP BY i.indicator_name, r.region_name
ORDER BY i.indicator_name, r.region_name;

-- 2. Indicator trend for the latest 5 years (all regions)
WITH ranked_years AS (
    SELECT DISTINCT d.year
    FROM warehouse.fact_economic f
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
)
SELECT
    d.year,
    i.indicator_name,
    r.region_name,
    f.value
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
JOIN warehouse.dim_region r
    ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i
    ON f.indicator_key = i.indicator_key
WHERE d.year >= (
    SELECT MAX(year) - 4 FROM ranked_years
)
ORDER BY i.indicator_name, d.year, r.region_name;

-- 3. Moving average (3-year) for smoothing trends
SELECT
    d.year,
    r.region_name,
    i.indicator_name,
    f.value,
    ROUND(AVG(f.value) OVER (
        PARTITION BY r.region_name, i.indicator_name
        ORDER BY d.year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 6) AS moving_avg_3y
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
JOIN warehouse.dim_region r
    ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i
    ON f.indicator_key = i.indicator_key
ORDER BY i.indicator_name, r.region_name, d.year;

-- 4. Acceleration of growth (second derivative)
-- Shows if growth is speeding up or slowing down
WITH growth_data AS (
    SELECT
        d.year,
        r.region_name,
        i.indicator_name,
        f.value,
        LAG(f.value) OVER (
            PARTITION BY r.region_name, i.indicator_name
            ORDER BY d.year
        ) AS prev_value,
        LAG(f.value, 2) OVER (
            PARTITION BY r.region_name, i.indicator_name
            ORDER BY d.year
        ) AS prev2_value
    FROM warehouse.fact_economic f
    JOIN warehouse.dim_date d
        ON f.date_key = d.date_key
    JOIN warehouse.dim_region r
        ON f.region_key = r.region_key
    JOIN warehouse.dim_indicator i
        ON f.indicator_key = i.indicator_key
)
SELECT
    year,
    region_name,
    indicator_name,
    value,
    ROUND(
        (value - prev_value) / NULLIF(prev_value, 0) * 100,
        2
    ) AS growth_pct,
    ROUND(
        ((value - prev_value) / NULLIF(prev_value, 0) * 100) -
        ((prev_value - prev2_value) / NULLIF(prev2_value, 0) * 100),
        2
    ) AS acceleration_pct
FROM growth_data
WHERE prev_value IS NOT NULL AND prev2_value IS NOT NULL
ORDER BY indicator_name, region_name, year;

-- 5. Consistency score (coefficient of variation)
-- Lower CV = more stable indicator; higher CV = more volatile
SELECT
    i.indicator_name,
    r.region_name,
    ROUND(AVG(f.value), 6) AS mean_value,
    ROUND(STDDEV(f.value), 6) AS stddev_value,
    ROUND(
        STDDEV(f.value) / NULLIF(AVG(f.value), 0) * 100,
        2
    ) AS coefficient_of_variation
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
JOIN warehouse.dim_region r
    ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i
    ON f.indicator_key = i.indicator_key
GROUP BY i.indicator_name, r.region_name
HAVING COUNT(*) > 1
ORDER BY coefficient_of_variation ASC;