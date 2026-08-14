# Data Dictionary

## BPS Data Warehouse

This document describes all tables in each layer of the data warehouse.

---

## Layer: Raw

The raw layer stores original API responses as JSON files in `data/raw/`. These files are not loaded into the database but serve as the source of truth for reprocessing.

### Raw File Layout

```
data/raw/
└── bps/
    └── {source}/
        └── {dataset}/
            └── {YYYY}/
                └── {MM}/
                    └── {DD}/
                        └── response.json
```

| Path Element | Description |
|-------------|-------------|
| `{source}` | API endpoint (e.g., `domain`, `dynamic_data`, `simdasi`, `glosarium`) |
| `{dataset}` | Dataset identifier (e.g., `pdrb`, `var145`) |
| `{YYYY}/{MM}/{DD}` | Date of retrieval |

---

## Layer: Staging

### `staging.dynamic_data`

Tabular representation of dynamic data API responses.

| Column | Type | Description |
|--------|------|-------------|
| staging_key | BIGSERIAL PK | Auto-increment ID |
| variable_id | VARCHAR(50) | BPS variable ID |
| vervar_id | VARCHAR(50) | Vertical variable ID |
| region_id | VARCHAR(20) | Region code |
| year | INTEGER | Reference year |
| value | NUMERIC(20,6) | Indicator value |
| table_id | VARCHAR(50) | Source table ID |
| loaded_at | TIMESTAMP | Load timestamp |

### `staging.domain_regions`

Region metadata from the Domain API.

| Column | Type | Description |
|--------|------|-------------|
| staging_key | BIGSERIAL PK | Auto-increment ID |
| region_code | VARCHAR(20) | BPS region code |
| region_name | VARCHAR(150) | Region name |
| level | VARCHAR(10) | Region level (prov/kab/kec/desa) |
| loaded_at | TIMESTAMP | Load timestamp |

### `staging.variables`

Variable definitions from the API response.

| Column | Type | Description |
|--------|------|-------------|
| staging_key | BIGSERIAL PK | Auto-increment ID |
| variable_id | VARCHAR(50) | BPS variable ID |
| variable_name | TEXT | Variable label |
| variable_description | TEXT | Variable description |
| table_id | VARCHAR(50) | Source table ID |
| loaded_at | TIMESTAMP | Load timestamp |

### `staging.glossary`

Glossary entries from the Glosarium API.

| Column | Type | Description |
|--------|------|-------------|
| staging_key | BIGSERIAL PK | Auto-increment ID |
| glossary_id | VARCHAR(50) | Glossary entry ID |
| indicator_name | TEXT | Indicator name |
| concept | TEXT | Concept name |
| definition | TEXT | Formal definition |
| classification | TEXT | Classification |
| measure | TEXT | Measure unit |
| unit | VARCHAR(100) | Unit of measure |
| data_source | TEXT | Data source |
| loaded_at | TIMESTAMP | Load timestamp |

---

## Layer: Warehouse

### `warehouse.dim_region`

Geographic region dimension.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| region_key | VARCHAR(20) PK | Surrogate key | `1100` |
| region_code | VARCHAR(20) | BPS region code | `1100` |
| region_name | VARCHAR(150) | Region name | `ACEH` |
| province_name | VARCHAR(150) | Province name | `ACEH` |
| regency_name | VARCHAR(150) | Regency/city | `KOTA BANDA ACEH` |
| district_name | VARCHAR(150) | District | `BAITURRAHMAN` |

### `warehouse.dim_indicator`

Indicator dimension.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| indicator_key | VARCHAR(50) PK | Surrogate key | `145` |
| indicator_code | VARCHAR(50) | BPS variable ID | `145` |
| indicator_name | TEXT | Indicator name | `PDRB Atas Dasar Harga Konstan` |
| subject_name | TEXT | Subject/domain | `Ekonomi` |
| category_name | TEXT | Category | `Produk Domestik Regional Bruto` |
| unit | VARCHAR(100) | Unit of measure | `Miliar Rupiah` |
| frequency | VARCHAR(50) | Frequency | `Tahunan` |

### `warehouse.dim_date`

Time dimension.

For annual data, `date_key` represents the **reference period** (e.g., `20200101` for year 2020), not an actual observation date. The `period_type` column documents this.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| date_key | INTEGER PK | Surrogate key (reference period) | `20230101` |
| full_date | DATE | Reference date | `2023-01-01` |
| year | INTEGER | Year | `2023` |
| quarter | INTEGER | Quarter | `1` |
| month | INTEGER | Month | `1` |
| month_name | VARCHAR(20) | Month name | `January` |
| period_type | VARCHAR(10) | Frequency (YEAR, QUARTER, MONTH) | `YEAR` |

### `warehouse.dim_dataset`

Dataset metadata from SIMDASI.

| Column | Type | Description |
|--------|------|-------------|
| dataset_key | SERIAL PK | Auto-increment ID |
| table_id | VARCHAR(50) | BPS table ID |
| table_code | VARCHAR(50) | BPS table code |
| title | TEXT | Table title |
| subject | TEXT | Subject |
| available_years | VARCHAR(255) | Available years |
| source_system | VARCHAR(50) | Source system (default `BPS`) |

### `warehouse.dim_glossary`

Glossary dimension for indicator definitions.

| Column | Type | Description |
|--------|------|-------------|
| glossary_key | SERIAL PK | Auto-increment ID |
| glossary_id | VARCHAR(50) | Glossary entry ID |
| indicator_name | TEXT | Indicator name |
| concept | TEXT | Concept |
| definition | TEXT | Formal definition |
| classification | TEXT | Classification |
| measure | TEXT | Measure |
| unit | VARCHAR(100) | Unit |
| data_source | TEXT | Data source |
| endpoint | VARCHAR(255) | API endpoint |

### `warehouse.fact_economic`

**Grain:** One row = one indicator × one region × one period.

| Column | Type | Description |
|--------|------|-------------|
| fact_key | BIGSERIAL PK | Auto-increment ID |
| date_key | INTEGER FK | Reference to `dim_date` |
| region_key | VARCHAR(20) FK | Reference to `dim_region` |
| indicator_key | VARCHAR(50) FK | Reference to `dim_indicator` |
| value | NUMERIC(20,6) | Indicator value |
| source_key | INTEGER | Source reference |
| loaded_at | TIMESTAMP | Load timestamp |

### `warehouse.fact_trade`

**Grain:** One row = one product × one country × one port × one period.

| Column | Type | Description |
|--------|------|-------------|
| trade_key | BIGSERIAL PK | Auto-increment ID |
| date_key | INTEGER FK | Reference to `dim_date` |
| product_key | VARCHAR(50) | Product code |
| country_key | VARCHAR(20) | Country code |
| port_key | VARCHAR(20) | Port code |
| trade_type | VARCHAR(10) | `EXPORT` or `IMPORT` |
| value_usd | NUMERIC(20,2) | Value in USD |
| net_weight_kg | NUMERIC(20,2) | Net weight in kg |
| loaded_at | TIMESTAMP | Load timestamp |

---

## Layer: Mart

### `mart.economic_summary` (Materialized View)

Aggregated economic summary for dashboard consumption.

| Column | Type | Description |
|--------|------|-------------|
| year | INTEGER | Year |
| region_name | VARCHAR(150) | Region name |
| indicator_name | TEXT | Indicator name |
| avg_value | NUMERIC | Average value |

---

## Data Lineage

```
BPS API ──→ Raw JSON ──→ Staging ──→ Quality Check ──→ Warehouse ──→ Mart
                                                     │              │
                                          dim_region  │       economic_summary
                                          dim_indicator│              │
                                          dim_date     │              ▼
                                          fact_economic        Dashboard