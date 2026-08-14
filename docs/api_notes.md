# BPS WebAPI Notes

Technical documentation and exploration notes for the BPS WebAPI.

---

## Overview

- **Documentation:** https://webapi.bps.go.id/documentation/
- **Base URL:** `https://webapi.bps.go.id/v1/api`
- **Authentication:** API key (`key` parameter)
- **Format:** JSON

All requests must include the `key` parameter:
```
https://webapi.bps.go.id/v1/api/domain?type=prov&key=YOUR_API_KEY
```

---

## API Endpoints

### 1. Domain

Returns a list of regions at a specified administrative level.

```
GET /v1/api/domain?type={level}&key={key}
```

| Parameter | Description | Example |
|-----------|-------------|---------|
| `type` | Region level | `prov`, `kab`, `kec`, `desa` |

**Response structure:**
```json
{
    "status": "200",
    "data-availability": "available",
    "data": [
        {
            "kode": "1100",
            "nama": "ACEH"
        }
    ]
}
```

### 2. Dynamic Data

Returns data content for specified variables, domains, and periods.

```
GET /v1/api/list?model={model}&domain={domain}&var={var}&th={period}&key={key}
```

| Parameter | Description | Example |
|-----------|-------------|---------|
| `model` | API model | `data` |
| `domain` | Domain code | `1100` (province), `0000` (national) |
| `var` | Variable ID(s) | `145` or `145,146` |
| `th` | Period(s) | `2023` or `2020,2021,2022` |
| `vervar` | Vertical variable ID | e.g., gender breakdown |

**Response structure (simplified):**
```json
{
    "status": "200",
    "data-availability": "available",
    "variable": [
        {
            "id": "145",
            "label": "PDRB",
            "description": "..."
        }
    ],
    "vervar": [...],
    "infotabel": {
        "tabel": {
            "id": "...",
            "kode": "...",
            "nama": "..."
        }
    },
    "datacontent": [
        ["2023", "100.5", "200.3", "300.1"],
        ["2024", "110.2", "210.1", "310.5"]
    ]
}
```

**datacontent format:**
- Each row: `[year, value1, value2, ..., valueN]`
- The number of values per row = `len(variables)` or `len(variables) * len(vervars)`
- Values map to regions in the order of the domain list

### 3. SIMDASI

Returns table metadata.

```
GET /v1/api/simdasi?id={table_id}&key={key}
```

| Parameter | Description |
|-----------|-------------|
| `id` | Table ID |

**Response structure:**
```json
{
    "data": [
        {
            "id": "...",
            "kode": "...",
            "judul": "...",
            "subjek": "...",
            "satuan": "...",
            "periode": "..."
        }
    ]
}
```

### 4. Glosarium

Returns glossary/indicator definitions.

```
GET /v1/api/glosarium?key={key}
```

**Response structure:**
```json
{
    "data": [
        {
            "id": "...",
            "nama_indikator": "...",
            "konsep": "...",
            "definisi": "...",
            "klasifikasi": "...",
            "ukuran": "...",
            "satuan": "...",
            "sumber_data": "..."
        }
    ]
}
```

---

## API Key Setup

1. Register at https://webapi.bps.go.id
2. Obtain your API key
3. Set it in `.env`:

```bash
BPS_API_KEY=your_api_key_here
```

⚠️ **Never commit your API key to Git.**

---

## Error Handling

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad request (missing/invalid params) |
| `401` | Invalid API key |
| `404` | Resource not found |

Common issues:
- Missing `key` parameter → authentication error
- Invalid `var` or `domain` → empty `datacontent`
- Unsupported `th` format → empty response

---

## Discoverability Workflow

To find data for a specific indicator:

1. **Get the domain list** — find region codes
2. **Query a table** — use SIMDASI to understand available tables
3. **Find variable IDs** — look at dynamic data variable definitions
4. **Fetch data** — get the actual data content
5. **Map to glossary** — get the definition and unit

---

## Example Queries

### Get all provinces

```bash
curl "https://webapi.bps.go.id/v1/api/domain?type=prov&key=YOUR_KEY"
```

### Get PDRB for all regions (national, variable 145)

```bash
curl "https://webapi.bps.go.id/v1/api/list?model=data&domain=0000&var=145&th=2023&key=YOUR_KEY"
```

### Get PDRB for ACEH province

```bash
curl "https://webapi.bps.go.id/v1/api/list?model=data&domain=1100&var=145&th=2023&key=YOUR_KEY"
```

### Get data for multiple years

```bash
curl "https://webapi.bps.go.id/v1/api/list?model=data&domain=1100&var=145&th=2020,2021,2022,2023&key=YOUR_KEY"
```

---

## References

- Official documentation: https://webapi.bps.go.id/documentation/
- BPS Website: https://www.bps.go.id
- API base URL: https://webapi.bps.go.id/v1/api