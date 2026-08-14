# Business Questions & Analytical Framework

This document defines the analytical questions that drive the Data Mart design. Each mart is built to answer specific business questions, not just to display data.

---

## Framework

```
Business Questions
       ↓
Data Mart Design
       ↓
SQL Analytics
       ↓
Dashboard
```

---

## Q1 — Indicator Trend

> Bagaimana perkembangan indikator dari tahun ke tahun?

**Purpose:** Understand the historical trajectory of key economic indicators.

**Output:**
```
Year    Value    Previous    Growth %
2020    126.51    -          -
2021    128.94    126.51     1.92%
2022    133.45    128.94     3.50%
```

**Mart:** `mart.indicator_trend`

---

## Q2 — Regional Performance

> Provinsi mana yang memiliki nilai tertinggi dan terendah?

**Purpose:** Compare regions side-by-side for a given indicator and year.

**Output:**
```
Rank    Province        Value
1       SUMATERA UTARA  508.83
2       ACEH            126.51
3       SUMATERA BARAT  32.75
4       RIAU            1.05
```

**Mart:** `mart.regional_performance`

---

## Q3 — Regional Growth

> Provinsi mana yang mengalami pertumbuhan paling tinggi?

**Purpose:** Identify which regions are growing fastest (or declining).

**Output:**
```
Province        2020    2021    Growth %
RIAU            1.05    1.07    1.90%
ACEH            126.51  128.94  1.92%
SUMATERA UTARA  508.83  519.07  2.01%
```

**Mart:** `mart.regional_performance` (with growth columns)

---

## Q4 — National vs Regional

> Apakah perubahan indikator nasional sejalan dengan perubahan di tingkat provinsi?

**Purpose:** Compare national trends against regional trends to identify divergence.

**Output:**
```
Year    National    National Growth    Top Region Growth    Bottom Region Growth
2021    128.94      1.92%              2.01%               1.90%
```

**Mart:** `mart.economic_overview`

---

## Q5 — Indicator Metadata

> Apa definisi, unit, dan sumber dari indikator ini?

**Purpose:** Provide semantic context for every number shown in the dashboard.

**Output:**
```
Indicator: PDRB Atas Dasar Harga Konstan
Concept:   Produk Domestik Regional Bruto
Unit:      Miliar Rupiah
Frequency: Tahunan
Source:    BPS
```

**Source:** `warehouse.dim_indicator` (enriched with glossary)

---

## Data Mart Design

### `mart.indicator_trend`

Answers Q1. Provides year-over-year trend for each indicator.

```sql
CREATE MATERIALIZED VIEW mart.indicator_trend AS
SELECT
    d.year,
    i.indicator_key,
    i.indicator_name,
    i.unit,
    i.frequency,
    SUM(f.value) AS national_value,
    LAG(SUM(f.value)) OVER (
        PARTITION BY i.indicator_key
        ORDER BY d.year
    ) AS previous_value,
    ROUND(
        (SUM(f.value) - LAG(SUM(f.value)) OVER (
            PARTITION BY i.indicator_key
            ORDER BY d.year
        )) / NULLIF(LAG(SUM(f.value)) OVER (
            PARTITION BY i.indicator_key
            ORDER BY d.year
        ), 0) * 100,
        2
    ) AS growth_pct
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_indicator i ON f.indicator_key = i.indicator_key
GROUP BY d.year, i.indicator_key, i.indicator_name, i.unit, i.frequency;
```

### `mart.regional_performance`

Answers Q2 and Q3. Provides regional comparison with ranking and growth.

```sql
CREATE MATERIALIZED VIEW mart.regional_performance AS
SELECT
    d.year,
    r.region_key,
    r.region_name,
    i.indicator_key,
    i.indicator_name,
    f.value,
    RANK() OVER (
        PARTITION BY d.year, i.indicator_key
        ORDER BY f.value DESC
    ) AS regional_rank,
    LAG(f.value) OVER (
        PARTITION BY r.region_key, i.indicator_key
        ORDER BY d.year
    ) AS previous_value,
    ROUND(
        (f.value - LAG(f.value) OVER (
            PARTITION BY r.region_key, i.indicator_key
            ORDER BY d.year
        )) / NULLIF(LAG(f.value) OVER (
            PARTITION BY r.region_key, i.indicator_key
            ORDER BY d.year
        ), 0) * 100,
        2
    ) AS growth_pct
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_region r ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i ON f.indicator_key = i.indicator_key;
```

### `mart.economic_overview`

Answers Q4. Provides national aggregate with regional context.

```sql
CREATE MATERIALIZED VIEW mart.economic_overview AS
SELECT
    d.year,
    i.indicator_key,
    i.indicator_name,
    i.unit,
    i.frequency,
    i.concept,
    i.definition,
    i.data_source,
    SUM(f.value) AS national_value,
    LAG(SUM(f.value)) OVER (
        PARTITION BY i.indicator_key
        ORDER BY d.year
    ) AS previous_national_value,
    ROUND(
        (SUM(f.value) - LAG(SUM(f.value)) OVER (
            PARTITION BY i.indicator_key
            ORDER BY d.year
        )) / NULLIF(LAG(SUM(f.value)) OVER (
            PARTITION BY i.indicator_key
            ORDER BY d.year
        ), 0) * 100,
        2
    ) AS national_growth_pct,
    COUNT(DISTINCT r.region_key) AS region_count
FROM warehouse.fact_economic f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
JOIN warehouse.dim_region r ON f.region_key = r.region_key
JOIN warehouse.dim_indicator i ON f.indicator_key = i.indicator_key
GROUP BY d.year, i.indicator_key, i.indicator_name, i.unit, i.frequency,
         i.concept, i.definition, i.data_source;
```

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│              BPS ECONOMIC OVERVIEW                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  KPI 1          KPI 2          KPI 3        KPI 4  │
│  Latest Value   YoY Growth     Top Region   Region  │
│                                 Count               │
├─────────────────────────────────────────────────────┤
│                                                     │
│         INDICATOR TREND (Q1)                        │
│         ────────────────────────                    │
│                                                     │
├──────────────────────┬──────────────────────────────┤
│                      │                              │
│ REGIONAL COMPARISON  │ REGIONAL RANKING (Q2)        │
│ (Q2)                 │                              │
│                      │                              │
├──────────────────────┴──────────────────────────────┤
│                                                     │
│ REGIONAL GROWTH (Q3)                                │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ INDICATOR METADATA (Q5)                             │
│ Definition / Concept / Unit / Source                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Data Lineage

```
BPS API
  │
  ▼
Dataset (SIMDASI)
  │
  ├── Table
  │
  └── Indicator
        │
        ├── Definition (Glosarium)
        ├── Unit
        └── Source
              │
              ▼
         Raw Response
              │
              ▼
           Staging
              │
              ▼
       Data Quality
              │
              ▼
       fact_economic
              │
              ▼
        Data Mart
        ├── indicator_trend
        ├── regional_performance
        └── economic_overview
              │
              ▼
          Dashboard