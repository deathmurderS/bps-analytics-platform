-- Dashboard: Regional Performance
-- Uses: mart.regional_performance
-- Provides: regional comparison with ranking and growth

-- ============================================================
-- Regional Ranking (latest year, selected indicator)
-- ============================================================
SELECT
    region_name,
    value,
    regional_rank,
    growth_pct,
    year
FROM mart.regional_performance
WHERE indicator_key = {{indicator_key}}
  AND year = {{year}}
ORDER BY regional_rank;

-- ============================================================
-- Regional Growth Table (latest year)
-- ============================================================
SELECT
    region_name,
    value,
    previous_value,
    growth_pct,
    CASE
        WHEN growth_pct > 0 THEN 'Positive'
        WHEN growth_pct < 0 THEN 'Negative'
        ELSE 'Stable'
    END AS growth_status,
    year
FROM mart.regional_performance
WHERE indicator_key = {{indicator_key}}
  AND year = {{year}}
ORDER BY growth_pct DESC;

-- ============================================================
-- Regional Filter List (distinct regions)
-- ============================================================
SELECT DISTINCT
    region_key,
    region_name
FROM mart.regional_performance
WHERE indicator_key = {{indicator_key}}
ORDER BY region_name;