# Example Insights

> ⚠️ **IMPORTANT DISCLAIMER**
>
> The insights in this document are derived from the project's **test fixture** (`tests/fixtures/bps_dynamic_response.json`) and are intended to **demonstrate analytical capabilities** of the platform. They are **NOT official BPS statistical findings** and should not be presented as real economic data.
>
> For insights from actual BPS API extraction, see [real_insights.md](real_insights.md).

---

## Purpose

This document demonstrates the analytical value of the BPS Data Warehouse using the realistic fixture data. These are the types of insights you can extract from the dashboard.

---

## Dataset Used

**Indicator:** PDRB Atas Dasar Harga Konstan (GDP at Constant Prices)
**Unit:** Miliar Rupiah (Billion Rupiah)
**Frequency:** Tahunan (Annual)
**Regions:** ACEH (1100), SUMATERA UTARA (1200), SUMATERA BARAT (1300), RIAU (1400)
**Period:** 2020–2022

---

## Insight 1: National Trend

> PDRB nasional (4 provinsi) tumbuh dari **669.14** miliar rupiah (2020) menjadi **705.25** miliar rupiah (2022), dengan pertumbuhan **+2.00%** (2021) dan **+3.33%** (2022).

| Year | National Value | Growth |
|------|---------------|--------|
| 2020 | 669.14 | — |
| 2021 | 682.50 | +2.00% |
| 2022 | 705.25 | +3.33% |

**Interpretation:** Ekonomi menunjukkan akselerasi pertumbuhan dari 2021 ke 2022, mengindikasikan pemulihan yang semakin kuat.

---

## Insight 2: Regional Ranking

> **SUMATERA UTARA** mendominasi dengan nilai tertinggi (508.83 miliar rupiah pada 2020), sementara **RIAU** memiliki nilai terendah (1.05 miliar rupiah).

| Rank | Region | Value (2020) |
|------|--------|-------------|
| 1 | SUMATERA UTARA | 508.83 |
| 2 | ACEH | 126.51 |
| 3 | SUMATERA BARAT | 32.75 |
| 4 | RIAU | 1.05 |

**Interpretation:** SUMATERA UTARA menyumbang **76%** dari total PDRB keempat provinsi, menjadikannya pusat ekonomi dominan di wilayah tersebut.

---

## Insight 3: Regional Growth

> **SUMATERA UTARA** tumbuh paling cepat (+2.01%), diikuti **ACEH** (+1.92%) dan **RIAU** (+1.90%).

| Region | 2020 | 2021 | Growth |
|--------|------|------|--------|
| SUMATERA UTARA | 508.83 | 519.07 | +2.01% |
| ACEH | 126.51 | 128.94 | +1.92% |
| RIAU | 1.05 | 1.07 | +1.90% |

**Interpretation:** Pertumbuhan relatif merata di semua provinsi, dengan SUMATERA UTARA memimpin baik dari sisi nilai maupun pertumbuhan.

---

## Insight 4: National vs Regional

> Pertumbuhan nasional (+2.00%) sejalan dengan pertumbuhan regional, dengan semua provinsi tumbuh dalam kisaran 1.90%–2.01%.

| Year | National Growth | Top Region Growth | Bottom Region Growth |
|------|----------------|-------------------|---------------------|
| 2021 | +2.00% | +2.01% (SUMUT) | +1.90% (RIAU) |

**Interpretation:** Tidak ada divergensi signifikan antara pertumbuhan nasional dan regional — indikasi pertumbuhan ekonomi yang inklusif di keempat provinsi.

---

## Insight 5: Metadata Context

> Setiap angka di dashboard dapat ditelusuri ke definisi resmi BPS.

```
Indicator: PDRB Atas Dasar Harga Konstan
Concept:   Produk Domestik Regional Bruto
Unit:      Miliar Rupiah
Frequency: Tahunan
Source:    BPS
Dataset:   PDRB Atas Dasar Harga Konstan Menurut Provinsi (T-001)
```

---

## How to Reproduce These Insights

```bash
# 1. Run the pipeline with the fixture data
python -m src.pipeline --domain 0000 --var 145 --th 2020,2021,2022

# 2. Query the Data Marts
# mart.indicator_trend → Insight 1
# mart.regional_performance → Insights 2 & 3
# mart.economic_overview → Insight 4
# warehouse.dim_indicator → Insight 5

# 3. View in Metabase
python scripts/metabase_setup.py
```

---

## Data Lineage for These Insights

```
Insight: "PDRB nasional tumbuh +2.00% pada 2021"
    ↓
mart.indicator_trend
    ↓
fact_economic (SUM of values by year)
    ↓
staging.dynamic_data (region_id, year, value)
    ↓
Raw JSON response (datacontent)
    ↓
BPS WebAPI (var=145, domain=0000, th=2020,2021,2022)