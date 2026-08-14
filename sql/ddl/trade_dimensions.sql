-- BPS Data Warehouse - Foreign Trade Dimensions
-- Multi-domain expansion: Trade domain

-- Dimension: Product (Commodity)
CREATE TABLE IF NOT EXISTS warehouse.dim_product (
    product_key    VARCHAR(50) PRIMARY KEY,
    product_code   VARCHAR(50),
    product_name   TEXT,
    UNIQUE (product_code)
);

-- Dimension: Country (Trading Partner)
CREATE TABLE IF NOT EXISTS warehouse.dim_country (
    country_key    VARCHAR(20) PRIMARY KEY,
    country_code   VARCHAR(20),
    country_name   VARCHAR(150),
    UNIQUE (country_code)
);

-- Dimension: Trade Flow (Export/Import)
CREATE TABLE IF NOT EXISTS warehouse.dim_trade_flow (
    trade_flow     VARCHAR(10) PRIMARY KEY,
    flow_name      VARCHAR(50)
);