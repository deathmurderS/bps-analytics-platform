-- BPS Data Warehouse - Fact Tables

-- Fact: Economic Indicators
-- Grain: one row = one indicator × one region × one period
CREATE TABLE IF NOT EXISTS warehouse.fact_economic (
    fact_key       BIGSERIAL PRIMARY KEY,
    date_key       INTEGER NOT NULL REFERENCES warehouse.dim_date (date_key),
    region_key     VARCHAR(20) NOT NULL REFERENCES warehouse.dim_region (region_key),
    indicator_key  VARCHAR(50) NOT NULL REFERENCES warehouse.dim_indicator (indicator_key),
    value          NUMERIC(20, 6),
    source_key     INTEGER,
    loaded_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (date_key, region_key, indicator_key)
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_fact_economic_date ON warehouse.fact_economic (date_key);
CREATE INDEX IF NOT EXISTS idx_fact_economic_region ON warehouse.fact_economic (region_key);
CREATE INDEX IF NOT EXISTS idx_fact_economic_indicator ON warehouse.fact_economic (indicator_key);

-- Fact: Foreign Trade (future expansion - Phase 4)
-- Grain: one row = one product × one country × one port × one period
CREATE TABLE IF NOT EXISTS warehouse.fact_trade (
    trade_key       BIGSERIAL PRIMARY KEY,
    date_key        INTEGER REFERENCES warehouse.dim_date (date_key),
    product_key     VARCHAR(50),
    country_key     VARCHAR(20),
    port_key        VARCHAR(20),
    trade_type      VARCHAR(10),
    value_usd       NUMERIC(20, 2),
    net_weight_kg   NUMERIC(20, 2),
    loaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (date_key, product_key, country_key, port_key, trade_type)
);

CREATE INDEX IF NOT EXISTS idx_fact_trade_date ON warehouse.fact_trade (date_key);
CREATE INDEX IF NOT EXISTS idx_fact_trade_product ON warehouse.fact_trade (product_key);
CREATE INDEX IF NOT EXISTS idx_fact_trade_country ON warehouse.fact_trade (country_key);