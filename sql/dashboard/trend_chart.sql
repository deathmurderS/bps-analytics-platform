-- Dashboard: Indicator Trend Chart
-- Uses: mart.indicator_trend
-- Provides: time series of national values with growth

SELECT
    year,
    national_value,
    previous_value,
    growth_pct,
    indicator_name,
    unit
FROM mart.indicator_trend
WHERE indicator_key = {{indicator_key}}
ORDER BY year;