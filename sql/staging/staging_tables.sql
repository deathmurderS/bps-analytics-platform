-- BPS Data Warehouse - Staging Tables
-- Tabular representation of API responses before transformation

-- Staging: Dynamic Data
CREATE TABLE IF NOT EXISTS staging.dynamic_data (
    staging_key   BIGSERIAL PRIMARY KEY,
    variable_id   VARCHAR(50),
    vervar_id     VARCHAR(50),
    region_id     VARCHAR(20),
    year          INTEGER,
    value         NUMERIC(20, 6),
    table_id      VARCHAR(50),
    loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging: Domain (Regions)
CREATE TABLE IF NOT EXISTS staging.domain_regions (
    staging_key   BIGSERIAL PRIMARY KEY,
    region_code   VARCHAR(20),
    region_name   VARCHAR(150),
    level         VARCHAR(10),
    loaded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging: Variables
CREATE TABLE IF NOT EXISTS staging.variables (
    staging_key           BIGSERIAL PRIMARY KEY,
    variable_id           VARCHAR(50),
    variable_name         TEXT,
    variable_description  TEXT,
    table_id              VARCHAR(50),
    loaded_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Staging: Glossary
CREATE TABLE IF NOT EXISTS staging.glossary (
    staging_key    BIGSERIAL PRIMARY KEY,
    glossary_id    VARCHAR(50),
    indicator_name TEXT,
    concept        TEXT,
    definition     TEXT,
    classification TEXT,
    measure        TEXT,
    unit           VARCHAR(100),
    data_source    TEXT,
    loaded_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);