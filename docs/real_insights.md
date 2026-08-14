# Real BPS Data Insights

> 📊 **This document contains insights from ACTUAL BPS API extraction.**
>
> The data here comes from running the pipeline against the real BPS WebAPI. These are genuine statistical findings that can be presented as real economic observations.

---

## How to Generate These Insights

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env and set BPS_API_KEY

# 2. Run the pipeline with actual BPS data
python -m src.pipeline \
    --domain 0000 \
    --var 145 \
    --th 2020,2021,2022,2023,2024 \
    --dataset pdrb_nasional

# 3. Generate dashboard
python scripts/metabase_setup.py
```

---

## Template

### Dataset Used

| Field | Value |
|-------|-------|
| Indicator | *[indicator name from BPS]* |
| Variable ID | *[BPS variable ID]* |
| Unit | *[unit]* |
| Frequency | *[frequency]* |
| Period | *[years covered]* |
| Regions | *[regions covered]* |

### Insight 1: [Title]

> *[Insight statement with actual numbers]*

| Year | Value | Growth |
|------|-------|--------|
| *[year]* | *[value]* | *[growth]* |

**Interpretation:** *[Analytical interpretation]*

### Insight 2: [Title]

> *[Insight statement]*

**Source:** `mart.*` → `warehouse.fact_economic` → `staging.dynamic_data` → Raw JSON → BPS API

---

## Data Lineage

Every insight in this document can be traced:

```
Insight: "..." 
    ↓
Data Mart
    ↓
Fact Table
    ↓
Staging
    ↓
Raw JSON (data/raw/bps/dynamic_data/*/)
    ↓
BPS WebAPI (request parameters documented in raw metadata)