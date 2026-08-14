-- Regional Analysis
-- Compares economic indicators across regions

-- 1. Regional ranking for the latest available year
WITH latest_year AS (
    SELECT MAX(d.year) AS max_year
    FROM warehouse.fact_economic f
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
)
SELECT
    d.year,
    r.region_name,
    i.indicator_name,
    f.value,
    RANK() OVER (
        PARTITION BY i.indicator_name
        ORDER BY f.value DESC
    ) AS regional_rank
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
JOIN warehouse.dim_region r
    ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i
    ON f.indicator_key = i.indicator_key
CROSS JOIN latest_year ly
WHERE d.year = ly.max_year
ORDER BY i.indicator_name, f.value DESC;

-- 2. Regional comparison table (regions as columns)
-- Pivot the data for a single indicator and year
SELECT
    i.indicator_name,
    d.year,
    MAX(CASE WHEN r.region_name = 'ACEH' THEN f.value END) AS aceh,
    MAX(CASE WHEN r.region_name = 'SUMATERA UTARA' THEN f.value END) AS sumatera_utara,
    MAX(CASE WHEN r.region_name = 'JAKARTA' THEN f.value END) AS jakarta,
    MAX(CASE WHEN r.region_name = 'JAWA BARAT' THEN f.value END) AS jawa_barat,
    MAX(CASE WHEN r.region_name = 'JAWA TIMUR' THEN f.value END) AS jawa_timur
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d
    ON f.date_key = d.date_key
JOIN warehouse.dim_region r
    ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i
    ON f.indicator_key = i.indicator_key
WHERE i.indicator_name = :indicator_name
GROUP BY i.indicator_name, d.year
ORDER BY d.year;

-- 3. Top N regions by indicator growth
-- Replace :indicator_name and :limit_value as needed
WITH yoy_data AS (
    SELECT
        d.year,
        r.region_name,
        f.value,
        LAG(f.value) OVER (
            PARTITION BY r.region_name
            ORDER BY d.year
        ) AS prev_value
    FROM warehouse.fact_economic f
    JOIN warehouse.dim_date d
        ON f.date_key = d.date_key
    JOIN warehouse.dim_region r
        ON f.region_key = r.region_key
    JOIN warehouse.dim_indicator i
        ON f.indicator_key = i.indicator_key
    WHERE i.indicator_name = :indicator_name
)
SELECT
    region_name,
    year,
    value,
    prev_value,
    ROUND(
        (value - prev_value) / NULLIF(prev_value, 0) * 100,
        2
    ) AS growth_pct
FROM yoy_data
WHERE prev_value IS NOT NULL
ORDER BY growth_pct DESC
LIMIT :limit_value;

-- 4. Average value by region (all years)
SELECT
    r.region_name,
    i.indicator_name,
    ROUND(AVG(f.value), 6) AS avg_value,
    ROUND(MIN(f.value), 6) AS min_value,
    ROUND(MAX(f.value), 6) AS max_value,
    COUNT(*) AS observation_count
FROM warehouse.fact_economic f
JOIN warehouse.dim_region r
    ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i
    ON f.indicator_key = i.indicator_key
GROUP BY r.region_name, i.indicator_name
ORDER BY i.indicator_name, avg_value DESC;