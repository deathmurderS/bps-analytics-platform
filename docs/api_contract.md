# API Contract — Next.js → FastAPI → Neon

Dokumen ini mendefinisikan kontrak data antara frontend dashboard (`frontend/`), backend API (`backend/`), dan data warehouse Neon. Tujuannya: **semua data yang tampil di UI berasal dari FastAPI → Neon, tanpa mock/hardcoded di frontend.**

---

## 1. Alur Data

```
BPS API
   ↓
GitHub Actions ETL
   ↓
Neon PostgreSQL (raw → staging → warehouse → mart)
   ↓
FastAPI (backend/app/)
   ↓
Next.js (frontend/lib/api.ts)
   ↓
Komponen UI (KPI, chart, tabel, insight, metadata)
```

Frontend **tidak pernah** terhubung langsung ke Neon. Hanya melalui FastAPI.

---

## 2. Endpoint yang Terlibat (Overview)

| Endpoint | Sumber (Neon) | Dipakai untuk |
|----------|---------------|----------------|
| `GET /api/health` | `SELECT 1` | Health check API + DB |
| `GET /api/overview` | `mart.economic_overview` | KPI cards (nilai terbaru, YoY) |
| `GET /api/economic/trend?indicator_key=&year=` | `mart.indicator_trend` | Line chart tren nasional |
| `GET /api/economic/regional?indicator_key=&year=` | `mart.regional_performance` | Tabel kinerja regional |
| `GET /api/metadata/indicators` | `warehouse.dim_indicator` | Dropdown indikator + metadata preview |

---

## 3. Kontrak Filter (Single Source of Truth)

**Tipe** (`frontend/types/index.ts`):

```ts
interface OverviewFilters {
  domain: string;        // subject_name dari dim_indicator
  indicatorKey: string;  // indicator_key — menggerakkan KPI, tren, regional
  year: number | null;   // null = tahun terbaru tersedia
  region: string;        // "nasional" (reserved untuk provinsi)
}
```

**Prinsip:**
- Satu state `filters` di halaman Overview menggerakkan **semua** section:
  `Selected Indicator → KPI → Historical Trend → Regional Breakdown`.
- Dropdown Domain/Indikator/Periode/Wilayah **di-generate dari data API**, bukan hardcoded.
- Tombol "Terapkan" menyinkronkan draft filter ke parent → memicu refetch API.

---

## 4. Bentuk Respons API (verifikasi 2026-08-20)

### `GET /api/overview`
```json
{
  "indicators": [
    {
      "indicator_key": "192",
      "indicator_name": "Persentase Penduduk Miskin (P0) Menurut Provinsi dan Daerah",
      "unit": "Persen",
      "frequency": null,
      "latest_year": 2026,
      "years_available": 20,
      "region_count": 34,
      "current_value": 275.97,
      "yoy_growth": -3.39
    }
  ]
}
```

### `GET /api/economic/trend?indicator_key=192`
```json
{
  "data": [
    { "year": 2007, "indicator_key": "192", "indicator_name": "...", "unit": "Persen",
      "national_value": 567.42, "previous_value": null, "growth_pct": null },
    { "year": 2008, "...", "national_value": 480.68, "growth_pct": -15.29 }
  ]
}
```

### `GET /api/economic/regional?indicator_key=192`
```json
{
  "data": [
    { "year": 2007, "region_key": "...", "region_name": "Papua",
      "indicator_key": "192", "indicator_name": "...", "value": 50.47,
      "regional_rank": 1, "previous_value": null, "growth_pct": null }
  ]
}
```

### `GET /api/metadata/indicators`
```json
{
  "indicators": [
    { "indicator_key": "192", "indicator_code": "192",
      "indicator_name": "Persentase Penduduk Miskin (P0) Menurut Provinsi dan Daerah",
      "subject_name": "Kemiskinan dan Ketimpangan", "category_name": null,
      "unit": "Persen", "frequency": null, "data_source": null }
  ]
}
```

---

## 5. Temuan Audit (2026-08-20)

1. **Nilai KPI tidak masuk akal** (mis. `Persentase Penduduk Miskin = 275,97%`).
   - Akar masalah: `mart.economic_overview` menyimpan `national_value = SUM(region)` untuk indikator berbasis persentase. Nilai nasional semestinya dihitung ulang (weighted/aggregate yang benar) atau disimpan sebagai nilai nasional dari API BPS — bukan penjumlahan wilayah.
   - **Action:** Perbaiki agregasi di `sql/mart/marts.sql` / transform `mart.economic_overview` agar nilai nasional benar; atau pilih indikator yang memang additive (PDB, ekspor) untuk KPI Overview.
2. **Filter periode tidak konsisten** (header `2026` vs dropdown `2020`).
   - **Sudah diperbaiki:** sekarang semua mengacu pada satu state `OverviewFilters`.
3. **Dropdown hardcoded** (Domain/Periode/Wilayah di-klaim kosmetik).
   - **Sudah diperbaiki:** opsi di-generate dari `dim_indicator` (subject_name) dan tahun dari data mart.
4. **Wilayah** masih `Nasional` saja — backend belum mengekspos daftar region untuk filter.
   - **Next:** tambahkan endpoint `GET /api/regions` (opsional) atau reapakai `warehouse.dim_region`.

---

## 6. Kontrak ke Depan

- KPI Overview hanya menampilkan indikator yang **valid secara agregasi** (additive atau disimpan sebagai nilai nasional).
- Setiap endpoint menerima parameter filter yang sama: `indicator_key`, `year`, (region).
- Metadata preview memakai `dim_indicator` (kode, subjek, unit, frekuensi, sumber data).
- Tidak ada nilai contoh/statis di frontend — semua di-fetch runtime.