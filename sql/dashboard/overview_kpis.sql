-- Dashboard: Economic Overview — KPI Cards
-- Uses: mart.economic_overview
-- Provides: Current Value, YoY Growth, Region Count, Latest Period

-- ============================================================
-- KPI 1: Current Value (latest year for selected indicator)
-- ============================================================
SELECT
    indicator_name,
    national_value AS current_value,
    unit,
    year AS latest_period
FROM mart.economic_overview
WHERE year = (
    SELECT MAX(year) FROM mart.economic_overview
)
  AND indicator_key = {{indicator_key}}
ORDER BY year DESC
LIMIT 1;

-- ============================================================
-- KPI 2: YoY Growth (latest year)
-- ============================================================
SELECT
    indicator_name,
    national_growth_pct AS yoy_growth,
    year
FROM mart.economic_overview
WHERE year = (
    SELECT MAX(year) FROM mart.economic_overview
)
  AND indicator_key = {{indicator_key}}
LIMIT 1;

-- ============================================================
-- KPI 3: Region Count (regions with data)
-- ============================================================
SELECT
    region_count,
    indicator_name
FROM mart.economic_overview
WHERE year = (
    SELECT MAX(year) FROM mart.economic_overview
)
  AND indicator_key = {{indicator_key}}
LIMIT 1;

-- ============================================================
-- KPI 4: Latest Period
-- ============================================================
SELECT
    MAX(year) AS latest_year,
    COUNT(DISTINCT year) AS years_available
FROM mart.economic_overview
WHERE indicator_key = {{indicator_key}};