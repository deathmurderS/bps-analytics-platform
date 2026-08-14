-- BPS Data Warehouse - Dimension Tables
-- Dimensional model for economic indicators

-- Dimension: Region
CREATE TABLE IF NOT EXISTS warehouse.dim_region (
    region_key        VARCHAR(20) PRIMARY KEY,
    region_code       VARCHAR(20) NOT NULL,
    region_name       VARCHAR(150) NOT NULL,
    province_name     VARCHAR(150),
    regency_name      VARCHAR(150),
    district_name     VARCHAR(150),
    UNIQUE (region_code)
);

-- Dimension: Indicator
-- Enriched with glossary definitions (concept, definition, etc.)
-- aggregation_method defines how the indicator should be aggregated
-- (SUM, AVG, N/A) — part of the semantic layer.
CREATE TABLE IF NOT EXISTS warehouse.dim_indicator (
    indicator_key       VARCHAR(50) PRIMARY KEY,
    indicator_code      VARCHAR(50),
    indicator_name      TEXT NOT NULL,
    subject_name        TEXT,
    category_name       TEXT,
    unit                VARCHAR(100),
    frequency           VARCHAR(50),
    concept             TEXT,
    definition          TEXT,
    classification      TEXT,
    measure             TEXT,
    data_source         TEXT,
    aggregation_method  VARCHAR(10) DEFAULT 'SUM',
    UNIQUE (indicator_code, indicator_name)
);

-- Dimension: Date
-- For annual data, date_key represents the reference period
-- (e.g., 20200101 for year 2020). period_type documents the
-- frequency of the data (YEAR, QUARTER, MONTH).
CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key      INTEGER PRIMARY KEY,
    full_date     DATE NOT NULL,
    year          INTEGER NOT NULL,
    quarter       INTEGER,
    month         INTEGER,
    month_name    VARCHAR(20),
    period_type   VARCHAR(10) DEFAULT 'YEAR'
);

-- Dimension: Dataset (SIMDASI metadata)
CREATE TABLE IF NOT EXISTS warehouse.dim_dataset (
    dataset_key      SERIAL PRIMARY KEY,
    table_id         VARCHAR(50),
    table_code       VARCHAR(50),
    title            TEXT,
    subject          TEXT,
    available_years  VARCHAR(255),
    source_system    VARCHAR(50) DEFAULT 'BPS'
);

-- Dimension: Glossary
CREATE TABLE IF NOT EXISTS warehouse.dim_glossary (
    glossary_key    SERIAL PRIMARY KEY,
    glossary_id     VARCHAR(50),
    indicator_name  TEXT,
    concept         TEXT,
    definition      TEXT,
    classification  TEXT,
    measure         TEXT,
    unit            VARCHAR(100),
    data_source     TEXT,
    endpoint        VARCHAR(255)
);