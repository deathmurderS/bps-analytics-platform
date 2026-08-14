-- BPS Data Warehouse - Schema Definitions
-- Creates the layered schemas: raw, staging, warehouse, mart

-- Raw layer: stores original API responses (if loaded into DB)
CREATE SCHEMA IF NOT EXISTS raw;

-- Staging layer: tabular representation of API responses
CREATE SCHEMA IF NOT EXISTS staging;

-- Warehouse layer: dimensional model (dimensions + facts)
CREATE SCHEMA IF NOT EXISTS warehouse;

-- Mart layer: aggregated views for analytics and dashboards
CREATE SCHEMA IF NOT EXISTS mart;