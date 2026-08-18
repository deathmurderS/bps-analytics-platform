# BPS Statistical & Economic Data Warehouse

End-to-end Data Warehouse project using official **Badan Pusat Statistik (BPS)** data via their WebAPI. This project demonstrates the complete data engineering pipeline: **API → Raw → Staging → Data Quality → Warehouse → Data Mart → Analytics**.

Built as a portfolio project for Data Analyst/Data Engineer roles.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Getting Started](#getting-started)
5. [Pipeline Usage](#pipeline-usage)
6. [Data Warehouse Design](#data-warehouse-design)
7. [SQL Analytics](#sql-analytics)
8. [Dashboard](#dashboard)
9. [Testing](#testing)
10. [Roadmap](#roadmap)
11. [Important Notes](#important-notes)

---

## Overview

This project is an **end-to-end analytical data platform** built on official **Badan Pusat Statistik (BPS)** data. It demonstrates the complete journey from raw API data to business-ready dashboards:

```
API → Raw → Staging → Quality → Warehouse → Mart → Analytics → Dashboard
```

It's designed as a **Data Analyst / Data Engineer portfolio project** showing:
- **Data engineering**: ETL pipeline, dimensional modeling, idempotent loading
- **Data governance**: Data quality checks, metadata layer, data lineage
- **Data analytics**: Business-driven Data Marts, SQL analytics, BI dashboards

### Key Features

- **Real data, not dummy data** — Uses actual BPS API responses
- **Raw layer preservation** — Original JSON responses saved for reprocessing
- **Layered architecture** — Raw → Staging → Warehouse → Mart
- **Data quality validation** — Automated checks before loading
- **Dimensional modeling** — Star schema with fact and dimension tables
- **Idempotent pipeline** — UPSERT logic prevents duplicate data on re-runs
- **Full dimension loading** — dim_region, dim_indicator, dim_date all populated
- **Metadata layer** — SIMDASI + Glosarium enrich indicators with definitions
- **Business-driven Data Marts** — Marts designed to answer specific analytical questions
- **Region mapping** — Values correctly mapped to regions via Domain API
- **Integration tests** — Realistic BPS response fixture validates the pipeline
- **SQL analytics** — YoY, regional, and trend analysis
- **Containerized** — Docker Compose for PostgreSQL + Metabase

### Data Sources

| Service | Description |
|---------|-------------|
| Domain | Region metadata (province, regency, district, village) |
| Dynamic Data | Main data content (indicators by region and period) |
| SIMDASI | Table metadata and MFD region information |
| Glosarium | Indicator definitions, concepts, classifications, units |
| Foreign Trade | Trade data (future Phase 4 expansion) |

---

## Architecture

```
                         BPS WEB API
                              |
          +-------------------+-------------------+
          |                   |                   |
        Domain          Dynamic Data          SIMDASI
          |                   |                   |
          |                   v                   v
          |              Economic Data        Metadata
          |                   |                   |
          +-------------------+-------------------+
                              |
                       Python Extractor
                              |
                              v
                         RAW LAYER
                         Original JSON
                              |
                              v
                          STAGING
                              |
                              v
                 Data Quality + Transform
                              |
                              v
                    DATA WAREHOUSE
                        PostgreSQL
                              |
             +----------------+----------------+
             |                |                |
       Fact Economic     Dimensions        Metadata
             |                |                |
             +----------------+----------------+
                              |
                         DATA MART
                    /        |        \
             Economic     Regional     Trend
                              |
                              v
                    Dashboard / SQL / BI

Future: Foreign Trade API -> Fact Trade -> Trade Mart
```

---

## Project Structure

```
bps-data-warehouse/
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
│
├── src/
│   ├── config/
│   │   └── settings.py          # Config from .env
│   ├── extract/
│   │   ├── bps_api.py           # Base API client
│   │   ├── domain.py            # Domain extractor
│   │   ├── dynamic_data.py      # Dynamic data extractor
│   │   ├── foreign_trade.py     # Foreign Trade extractor
│   │   ├── simdasi.py           # SIMDASI extractor
│   │   └── glossary.py          # Glosarium extractor
│   ├── raw/
│   │   └── storage.py           # Raw JSON storage
│   ├── staging/
│   │   └── dynamic_transform.py # JSON -> tabular staging
│   ├── quality/
│   │   └── validators.py        # Data quality checks
│   ├── transform/
│   │   ├── economic.py          # Economic dimensional model builder
│   │   ├── trade.py             # Trade dimensional model builder
│   │   └── metadata.py          # Metadata dimension builder
│   ├── load/
│   │   └── postgres.py          # PostgreSQL loader
│   └── pipeline.py              # Orchestrated ETL pipeline
│
├── sql/
│   ├── ddl/
│   │   ├── schemas.sql          # raw, staging, warehouse, mart schemas
│   │   ├── dimensions.sql       # dim_region, dim_indicator, dim_date
│   │   ├── trade_dimensions.sql # dim_product, dim_country, dim_trade_flow
│   │   └── facts.sql            # fact_economic, fact_trade
│   ├── staging/
│   │   └── staging_tables.sql   # Staging layer tables
│   ├── mart/
│   │   ├── marts.sql            # Economic Data Mart materialized views
│   │   └── trade_marts.sql      # Trade Data Mart materialized views
│   ├── dashboard/
│   │   ├── overview_kpis.sql    # KPI cards
│   │   ├── trend_chart.sql      # Trend line chart
│   │   ├── regional_performance.sql  # Regional comparison
│   │   └── metadata_panel.sql   # Indicator metadata
│   └── analytics/
│       ├── yoy.sql              # Year-over-year analysis
│       ├── regional.sql         # Regional comparisons
│       └── trends.sql           # Trend analysis
│
├── scripts/
│   ├── metabase_setup.py        # Automated Metabase dashboard setup
│   └── extract_real_data.py     # Real BPS data extraction for insights
│
├── data/
│   └── raw/                     # Raw API responses
│
├── tests/
│   ├── fixtures/
│   │   ├── bps_dynamic_response.json  # Realistic BPS API fixture
│   │   └── bps_trade_response.json    # Foreign Trade API fixture
│   ├── test_extractor.py        # Extractor tests
│   ├── test_quality.py          # Quality validator tests
│   ├── test_transform.py        # Transform & storage tests
│   ├── test_metadata.py         # Metadata transformer tests
│   ├── test_integration.py      # Integration tests with BPS fixture
│   ├── test_analytics.py        # Analytical validation (Phase 4A)
│   └── test_trade.py            # Foreign Trade tests (Phase 5)
│
└── docs/
    ├── data_dictionary.md
    ├── api_notes.md
    ├── business_questions.md    # Analytical framework & Data Mart design
    ├── example_insights.md      # Insights from test fixture (with disclaimer)
    └── real_insights.md         # Insights from actual BPS API data
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- BPS API key (free registration at https://webapi.bps.go.id)

### 1. Obtain a BPS API Key

Register and obtain an API key from: https://webapi.bps.go.id

### 2. Clone and Set Up

```bash
# Clone the repository
git clone <your-repo-url>
cd bps-data-warehouse

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your BPS_API_KEY and PostgreSQL credentials
```

### 3. Start PostgreSQL and Metabase

```bash
docker-compose up -d
```

This starts:
- **PostgreSQL** on port `5432`
- **Metabase** on port `3000` (visit http://localhost:3000)

### 4. Initialize Database Schemas

```bash
docker exec -i bps_dw_postgres psql -U postgres -d bps_dw < sql/ddl/schemas.sql
docker exec -i bps_dw_postgres psql -U postgres -d bps_dw < sql/ddl/dimensions.sql
docker exec -i bps_dw_postgres psql -U postgres -d bps_dw < sql/ddl/facts.sql
docker exec -i bps_dw_postgres psql -U postgres -d bps_dw < sql/staging/staging_tables.sql
```

(Or run the pipeline which auto-creates tables.)

---

## Pipeline Usage

### Run the Full ETL Pipeline

```bash
# Extract a specific variable for a domain and period
python -m src.pipeline \
    --domain 1100 \
    --var 145 \
    --th 2020,2021,2022,2023 \
    --dataset pdrb_aceh
```

**Arguments:**

| Flag | Description |
|------|-------------|
| `--domain` | BPS domain code (e.g., `1100` for ACEH province) |
| `--var` | BPS variable ID (e.g., `145`) |
| `--th` | Period(s), comma-separated (e.g., `2020,2021,2022`) |
| `--dataset` | Dataset name for raw storage (optional) |
| `--api-key` | Override API key from .env (optional) |

### Example: Explore the API Manually

```bash
# Using the Python client
python -c "
from src.extract.bps_api import BPSAPIClient
from src.extract.domain import DomainExtractor

client = BPSAPIClient()
extractor = DomainExtractor(client)
provinces = extractor.fetch_provinces()
records = extractor.parse_domain_list(provinces)
for r in records[:5]:
    print(r)
"
```

---

## Data Warehouse Design

### Schemas

| Schema | Purpose |
|--------|---------|
| `raw` | Original API responses |
| `staging` | Tabular representation of API data |
| `warehouse` | Dimensional model |
| `mart` | Aggregated views for analytics |

### Dimension Tables

**`warehouse.dim_region`**

| Column | Type | Description |
|--------|------|-------------|
| region_key | VARCHAR(20) PK | Surrogate key |
| region_code | VARCHAR(20) | BPS region code |
| region_name | VARCHAR(150) | Region name |
| province_name | VARCHAR(150) | Province (for regency-level data) |
| regency_name | VARCHAR(150) | Regency/city |
| district_name | VARCHAR(150) | District |

**`warehouse.dim_indicator`**

| Column | Type | Description |
|--------|------|-------------|
| indicator_key | VARCHAR(50) PK | Surrogate key |
| indicator_code | VARCHAR(50) | BPS variable ID |
| indicator_name | TEXT | Indicator name |
| subject_name | TEXT | Subject/domain |
| category_name | TEXT | Category |
| unit | VARCHAR(100) | Unit of measure |
| frequency | VARCHAR(50) | Frequency (e.g., annual) |

**`warehouse.dim_date`**

| Column | Type | Description |
|--------|------|-------------|
| date_key | INTEGER PK | e.g., YYYY0101 |
| full_date | DATE | Full date |
| year | INTEGER | Year |
| quarter | INTEGER | Quarter |
| month | INTEGER | Month |
| month_name | VARCHAR(20) | Month name |

### Fact Table

**`warehouse.fact_economic`**
Grain: **one row = one indicator × one region × one period**

| Column | Type | Description |
|--------|------|-------------|
| fact_key | BIGSERIAL PK | Surrogate key |
| date_key | INTEGER FK | Reference to dim_date |
| region_key | VARCHAR(20) FK | Reference to dim_region |
| indicator_key | VARCHAR(50) FK | Reference to dim_indicator |
| value | NUMERIC(20,6) | Indicator value |
| source_key | INTEGER | Source reference |
| loaded_at | TIMESTAMP | Load timestamp |

### Data Mart

The `mart` schema contains materialized views for dashboard consumption:

```sql
CREATE MATERIALIZED VIEW mart.economic_summary AS
SELECT
    d.year,
    r.region_name,
    i.indicator_name,
    AVG(f.value) AS avg_value
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_region r ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i ON f.indicator_key = i.indicator_key
GROUP BY d.year, r.region_name, i.indicator_name;
```

---

## SQL Analytics

### Year-over-Year (YoY) Analysis

```sql
-- From: sql/analytics/yoy.sql
SELECT
    d.year,
    r.region_name,
    i.indicator_name,
    f.value,
    LAG(f.value) OVER (
        PARTITION BY r.region_name, i.indicator_name
        ORDER BY d.year
    ) AS previous_year_value,
    ROUND(
        (f.value - LAG(f.value) OVER (
            PARTITION BY r.region_name, i.indicator_name
            ORDER BY d.year
        )) / NULLIF(LAG(f.value) OVER (
            PARTITION BY r.region_name, i.indicator_name
            ORDER BY d.year
        ), 0) * 100,
        2
    ) AS yoy_growth_pct
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_region r ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i ON f.indicator_key = i.indicator_key
ORDER BY i.indicator_name, r.region_name, d.year;
```

### Regional Comparison

```sql
-- From: sql/analytics/regional.sql
-- Rank regions for the latest year
WITH latest_year AS (
    SELECT MAX(d.year) AS max_year
    FROM warehouse.fact_economic f
    JOIN warehouse.dim_date d ON f.date_key = d.date_key
)
SELECT
    d.year,
    r.region_name,
    i.indicator_name,
    f.value,
    RANK() OVER (
        PARTITION BY i.indicator_name
        ORDER BY f.value DESC
    ) AS regional_rank
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_region r ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i ON f.indicator_key = i.indicator_key
CROSS JOIN latest_year ly
WHERE d.year = ly.max_year;
```

### Trend Analysis

```sql
-- From: sql/analytics/trends.sql
-- 3-year moving average
SELECT
    d.year,
    r.region_name,
    i.indicator_name,
    f.value,
    ROUND(AVG(f.value) OVER (
        PARTITION BY r.region_name, i.indicator_name
        ORDER BY d.year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 6) AS moving_avg_3y
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_region r ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i ON f.indicator_key = i.indicator_key;
```

---

## Dashboard

### Metabase

Metabase runs on http://localhost:3000 after `docker-compose up -d`.

### Automated Dashboard Setup

After the pipeline has loaded data, run the automated setup script to create the dashboard:

```bash
python scripts/metabase_setup.py
```

This script:
1. Waits for Metabase to be ready
2. Creates the admin user (first-time setup)
3. Connects to the `bps_dw` PostgreSQL database
4. Creates dashboard cards from `sql/dashboard/*.sql`
5. Creates the **BPS Economic Intelligence** dashboard

### Dashboard Components

The dashboard has 4 areas, each backed by Data Mart views:

#### 1. Overview KPIs (`sql/dashboard/overview_kpis.sql`)
- Current Value (latest year)
- YoY Growth
- Region Count
- Latest Period / Years Available
- **Source:** `mart.economic_overview`

#### 2. Indicator Trend (`sql/dashboard/trend_chart.sql`)
- Line chart of national values over time
- Growth percentage per year
- **Source:** `mart.indicator_trend`

#### 3. Regional Performance (`sql/dashboard/regional_performance.sql`)
- Regional ranking table
- Regional growth with status (Positive/Negative/Stable)
- Region filter list
- **Source:** `mart.regional_performance`

#### 4. Indicator Metadata (`sql/dashboard/metadata_panel.sql`)
- Indicator name, unit, frequency
- Concept and definition (from Glosarium)
- Data source
- Dataset context (from SIMDASI)
- **Source:** `warehouse.dim_indicator` + `warehouse.dim_dataset`

### Manual Metabase Setup

If you prefer manual setup:
1. Open http://localhost:3000
2. Complete initial setup
3. Connect to PostgreSQL:
   - Host: `localhost` (or `postgres` if running inside Docker network)
   - Port: `5432`
   - Database: `bps_dw`
   - Username: `postgres`
   - Password: (from your .env)
4. Create questions using the SQL in `sql/dashboard/`

---

## Data Lineage

Every number in the dashboard can be traced back to its source:

```
Dashboard
    ↓
Data Mart (mart.*)
    ↓
Fact Table (warehouse.fact_economic)
    ↓
Staging (staging.dynamic_data)
    ↓
Raw JSON (data/raw/)
    ↓
BPS WebAPI
```

Each layer has automated tests ensuring data integrity:
- **Extraction tests** — API response parsing correctness
- **Quality tests** — Data validation before loading
- **Reconciliation tests** — Source → warehouse → mart consistency
- **Analytical tests** — Data Mart calculation correctness

---

## Example Insights

The project distinguishes between **fixture insights** (for demonstration) and **real BPS insights** (from actual API extraction):

### Fixture Insights (Demonstration)

See [docs/example_insights.md](docs/example_insights.md) — these use the test fixture to demonstrate analytical capabilities.

> ⚠️ These are **NOT official BPS statistical findings**.

### Real BPS Insights

See [docs/real_insights.md](docs/real_insights.md) — populated after running real BPS data extraction:

```bash
python scripts/extract_real_data.py --domain 0000 --var 145 --th 2020,2021,2022,2023,2024 --dataset pdrb_nasional
```

This script:
1. Fetches actual BPS API data
2. Runs quality checks
3. Saves the raw response
4. Outputs summary statistics (national values, regional values)
5. Provides data for populating `real_insights.md`

### Example from Fixture Data

Using the fixture data (PDRB, 4 provinces, 2020–2022):

| Insight | Finding |
|---------|---------|
| National Trend | PDRB grew from 669.14 → 705.25 (+3.33% in 2022) |
| Regional Ranking | SUMATERA UTARA dominates with 76% of total |
| Regional Growth | SUMUT fastest at +2.01%, RIAU slowest at +1.90% |
| National vs Regional | Growth is inclusive — all regions 1.90%–2.01% |
| Metadata Context | Every number traceable to BPS definition |

---

## Testing

```bash
# Run the full test suite
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Test Coverage

- `test_extractor.py` — API client and extractor parsing
- `test_quality.py` — Data quality validators
- `test_transform.py` — Dimensional model transforms and raw storage
- `test_metadata.py` — Metadata transformer (SIMDASI + Glosarium)
- `test_integration.py` — Full pipeline with realistic BPS response fixture
  - Verifies metadata extraction
  - Verifies value-to-region mapping
  - Verifies vervar (vertical variable) mapping
  - Verifies fact and dimension building
  - Verifies data quality on realistic BPS structure
- `test_analytics.py` — Analytical validation (Phase 4A)
  - Verifies Data Mart calculations (national value, growth rate, regional rank)
  - Verifies reconciliation (source → warehouse → mart consistency)
  - Verifies grain uniqueness and data lineage integrity
- `test_trade.py` — Foreign Trade domain (Phase 5)
  - Verifies trade extractor parsing
  - Verifies fact_trade building and period conversion
  - Verifies trade dimensions (product, country, trade flow)
  - Verifies trade mart calculations (export/import trend, commodity ranking, trade balance)

---

## Roadmap

### Phase 1: Core DWH ✅
- [x] API exploration
- [x] Raw layer storage
- [x] Staging + Data Quality
- [x] Dimensional model (dimensions + fact)
- [x] Idempotent UPSERT loading
- [x] Integration tests with BPS fixture

### Phase 2: Metadata Layer ✅
- [x] SIMDASI metadata extraction
- [x] Glosarium extraction
- [x] dim_dataset / dim_glossary tables
- [x] dim_indicator enriched with glossary definitions
- [x] Metadata transformer tests

### Phase 3: Analytical Data Marts ✅
- [x] Business questions framework (docs/business_questions.md)
- [x] mart.indicator_trend — Q1: indicator trajectory
- [x] mart.regional_performance — Q2/Q3: regional comparison & growth
- [x] mart.economic_overview — Q4: national vs regional
- [x] Mart building in pipeline

### Phase 4A: Analytical Validation ✅
- [x] Data Mart calculation tests (national value, growth rate, regional rank)
- [x] Reconciliation tests (source → warehouse → mart consistency)
- [x] Grain uniqueness and data lineage integrity
- [x] Semantic layer: aggregation_method in dim_indicator

### Phase 4B: Dashboard ✅
- [x] Dashboard SQL queries (KPI, Trend, Regional, Metadata)
- [x] Automated Metabase setup script (scripts/metabase_setup.py)
- [x] Dashboard backed by Data Mart views
- [x] Indicator metadata panel with semantic context

### Phase 4C: Portfolio Hardening ✅
- [x] Example insights document (docs/example_insights.md)
- [x] Data lineage documentation
- [x] Portfolio narrative in README
- [x] Complete project structure documentation

### Phase 4D: Real Data Validation & Insights ✅
- [x] Disclaimer added to example_insights.md
- [x] Real insights template (docs/real_insights.md)
- [x] Real data extraction script (scripts/extract_real_data.py)
- [x] Fixture vs real insight distinction in README

### Phase 5: Foreign Trade ✅
- [x] ForeignTradeExtractor (src/extract/foreign_trade.py)
- [x] TradeTransformer (src/transform/trade.py)
- [x] Trade dimensions (dim_product, dim_country, dim_trade_flow)
- [x] Trade Data Marts (trend, regional, commodity, partner)
- [x] Cross-domain economic_trade_bridge mart
- [x] Trade fixture + 12 tests

### Phase 6: Deployment & Monitoring ✅
- [x] GitHub Actions scheduled ETL (setiap Senin 02:00 UTC)
- [x] Neon PostgreSQL cloud database
- [x] Data quality verification gate setelah ETL
- [x] Monitoring via GitHub Actions status

### Phase 7: Advanced
- [ ] Forecasting / ML
- [ ] Data lineage visualization
- [ ] Online dashboard (Metabase/Streamlit)

---

## Deployment & Monitoring

### Arsitektur Deployment

```
             BPS WebAPI
                 ↓
          GitHub Actions
                 ↓
          ETL + Data Quality
                 ↓
        ┌─────────────────┐
        │ Neon PostgreSQL │
        │   Data Warehouse│
        └────────┬────────┘
                 ↓
            Data Mart
                 ↓
             Dashboard
                 ↓
       Portfolio / Recruiter
```

### GitHub Actions Workflow

Workflow `.github/workflows/etl.yml` berjalan secara:

1. **Manual** — via `workflow_dispatch` (tombol "Run workflow" di Actions tab)
2. **Scheduled** — setiap **Senin jam 02:00 UTC (09:00 WIB)** via cron

### Alur Workflow

```
1. Checkout repository
2. Setup Python 3.11
3. Install dependencies
4. Run tests (pytest)
5. Run BPS ETL pipeline
6. Verify data quality in warehouse
   - fact_economic: harus > 0 rows
   - dim_date: harus > 0 rows
   - dim_region: harus > 0 rows
   - dim_indicator: harus > 0 rows
```

### Monitoring

GitHub Actions berfungsi sebagai **monitoring dasar pipeline**:

- ✅ **Hijau** = ETL sukses, data quality pass
- ❌ **Merah** = ETL gagal atau data quality fail
- 📅 **Scheduled** = Pipeline otomatis jalan setiap minggu

### Setup Secrets

Tambahkan secrets di **GitHub → Settings → Secrets and variables → Actions**:

| Secret | Deskripsi |
|--------|-----------|
| `BPS_API_KEY` | API key BPS WebAPI |
| `DATABASE_URL` | Full Neon PostgreSQL connection string |

---

## Important Notes

1. **Grain first** — Do not finalize fact tables before understanding the actual dataset grain from real BPS responses.
2. **No dummy data** — The pipeline must use real BPS API responses to validate the architecture.
3. **Save raw responses** — Always keep raw JSON for reprocessing when transforms change.
4. **Environment security** — API keys and passwords go in `.env`, which is git-ignored.
5. **Start small** — Begin with one clear dataset (e.g., one variable, one domain, a few years).
6. **ID values are illustrative** — Variable IDs, domain codes, and schemas in this document are examples. Actual IDs must come from the real BPS API documentation/responses.

---

## References

- BPS WebAPI Documentation: https://webapi.bps.go.id/documentation/
- BPS Website: https://www.bps.go.id
- Metabase: https://www.metabase.com
- PostgreSQL: https://www.postgresql.org