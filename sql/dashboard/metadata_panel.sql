-- Dashboard: Indicator Metadata Panel
-- Uses: warehouse.dim_indicator (enriched with glossary)
-- Provides: semantic context for the selected indicator

SELECT
    indicator_name,
    unit,
    frequency,
    subject_name,
    category_name,
    concept,
    definition,
    classification,
    measure,
    data_source,
    aggregation_method
FROM warehouse.dim_indicator
WHERE indicator_key = {{indicator_key}};

-- ============================================================
-- Dataset Context (from SIMDASI metadata)
-- ============================================================
SELECT
    ds.table_id,
    ds.table_code,
    ds.title,
    ds.subject AS dataset_subject,
    ds.available_years,
    ds.source_system
FROM warehouse.dim_dataset ds
LIMIT 1;