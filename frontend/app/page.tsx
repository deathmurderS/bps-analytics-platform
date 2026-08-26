"use client";

import { useEffect, useMemo, useState } from "react";
import GlobalFilters from "@/components/filters/GlobalFilters";
import KPICard, { KPICardData } from "@/components/cards/KPICard";
import ChartCard from "@/components/charts/ChartCard";
import EconomicTrendChart, {
  TrendDatum,
} from "@/components/charts/EconomicTrendChart";
import RegionalPerformanceTable, {
  RegionalRow,
} from "@/components/tables/RegionalPerformanceTable";
import InsightCard, {
  Insight,
  InsightHeader,
} from "@/components/insights/InsightCard";
import MetadataPreview, {
  MetadataItem,
} from "@/components/metadata/MetadataPreview";
import { LoadingState, EmptyState, ErrorState } from "@/components/states/DataStates";
import { ApiError, api } from "@/lib/api";
import type {
  OverviewApiResponse,
  OverviewDomainsResponse,
  IndicatorListResponse,
  OverviewFilters,
} from "@/types";

interface IndicatorOption {
  indicator_key: string;
  indicator_name: string;
  unit: string | null;
  frequency: string | null;
  subject_name: string | null;
}

export default function OverviewPage() {
  const [indicators, setIndicators] = useState<IndicatorListResponse | null>(
    null
  );
  const [domains, setDomains] = useState<OverviewDomainsResponse | null>(null);
  const [overview, setOverview] = useState<OverviewApiResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [domainNotice, setDomainNotice] = useState<string | null>(null);

  // Single source of truth for filters — drives KPI, trend, regional, metadata.
  const [filters, setFilters] = useState<OverviewFilters>({
    domain: "",
    indicatorKey: "",
    year: null,
    region: "national",
  });

  // Indicator options for the filter dropdown (from dim_indicator)
  const indicatorOptions: IndicatorOption[] = useMemo(() => {
    return (indicators?.indicators ?? []).map((ind) => ({
      indicator_key: ind.indicator_key,
      indicator_name: ind.indicator_name,
      unit: ind.unit,
      frequency: ind.frequency,
      subject_name: ind.subject_name,
    }));
  }, [indicators]);

  // Years available from KPI latest_year (for period filter)
  const availableYears: number[] = useMemo(() => {
    const years = new Set<number>();
    (overview?.kpis ?? []).forEach((kpi) => years.add(kpi.latest_year));
    return Array.from(years).sort((a, b) => a - b);
  }, [overview]);

  // Initialize filters once indicators + domain contract are loaded.
  useEffect(() => {
    if (!indicatorOptions.length || !domains || filters.indicatorKey) return;

    const availableDomains = domains.supported_domains.filter((domain) => domain.available);
    const preferredDomain =
      availableDomains.find((domain) => domain.key === "poverty") ??
      availableDomains.find((domain) => domain.key === "economic") ??
      null;

    const matchedSubjects = new Set(preferredDomain?.matched_subjects ?? []);
    const firstMatchingIndicator = preferredDomain
      ? indicatorOptions.find((indicator) => {
          const subject = indicator.subject_name?.trim().toLowerCase();
          return subject ? matchedSubjects.has(subject) : false;
        })
      : null;

    const first = firstMatchingIndicator ?? indicatorOptions[0];
    setFilters((prev) => ({
      ...prev,
      domain: preferredDomain?.key ?? "",
      indicatorKey: first.indicator_key,
    }));
  }, [domains, indicatorOptions, filters.indicatorKey]);

  // Load indicator list + domain contract once (for filter options)
  useEffect(() => {
    let cancelled = false;

    Promise.all([api.getIndicators(), api.getOverviewDomains()])
      .then(([meta, domainMeta]) => {
        if (cancelled) return;
        setIndicators(meta);
        setDomains(domainMeta);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // Combined overview — single request driven by filter state
  useEffect(() => {
    if (!filters.indicatorKey) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    setDomainNotice(null);

    api
      .getOverview({
        indicator_key: filters.indicatorKey,
        year: filters.year ?? undefined,
        region: filters.region,
        domain: filters.domain || undefined,
      })
      .then((data) => {
        if (cancelled) return;
        setOverview(data);
      })
      .catch((err: unknown) => {
        if (cancelled) return;

        if (err instanceof ApiError && err.status === 404 && filters.domain) {
          const selectedDomain = domains?.supported_domains.find(
            (domain) => domain.key === filters.domain
          );
          const label = selectedDomain?.key ?? filters.domain;
          setOverview(null);
          setDomainNotice(
            `Domain ${label} belum tersedia di warehouse untuk indikator yang dipilih.`
          );
          return;
        }

        setError(err instanceof Error ? err.message : "Terjadi kesalahan saat memuat data.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [domains, filters.indicatorKey, filters.year, filters.region, filters.domain]);

  const selectedIndicator = indicatorOptions.find(
    (ind) => ind.indicator_key === filters.indicatorKey
  );

  const selectedDomain = domains?.supported_domains.find(
    (domain) => domain.key === filters.domain
  );

  const pageCopy = useMemo(() => {
    switch (filters.domain) {
      case "poverty":
        return {
          title: "Overview Kemiskinan Indonesia",
          subtitle: "Indikator kemiskinan BPS dari warehouse nasional dan regional.",
          trendAriaLabel: "Tren kemiskinan",
        };
      case "economic":
        return {
          title: "Overview Ekonomi Indonesia",
          subtitle: selectedDomain?.available
            ? "Indikator utama makroekonomi dari data BPS."
            : "Domain ekonomi sudah disiapkan, tetapi belum tersedia di warehouse saat ini.",
          trendAriaLabel: "Tren ekonomi",
        };
      default:
        return {
          title: "Overview Statistik Indonesia",
          subtitle: "Ringkasan indikator utama BPS dari FastAPI dan Neon.",
          trendAriaLabel: "Tren indikator nasional",
        };
    }
  }, [filters.domain, selectedDomain?.available]);

  // Selected period label — single source from filters or backend-resolved year
  const selectedPeriod =
    filters.year ?? overview?.filters?.year ?? null;

  // KPI grid — one card per indicator (live data from mart.economic_overview)
  const kpiGrid: KPICardData[] = useMemo(() => {
    return (overview?.kpis ?? []).map((kpi) => ({
      key: kpi.indicator_key,
      title: kpi.indicator_name,
      value: kpi.current_value,
      unit: kpi.unit ?? undefined,
      yoy: kpi.yoy_growth ?? undefined,
      period: kpi.latest_year ? String(kpi.latest_year) : undefined,
      footnote: kpi.frequency ?? undefined,
      status: kpi.national_value_status,
    }));
  }, [overview]);

  // Trend data for the chart (historical, all years)
  const trendData: TrendDatum[] = useMemo(() => {
    return (overview?.trend ?? [])
      .slice()
      .sort((a, b) => a.year - b.year)
      .map((d) => ({ year: d.year, value: d.national_value }));
  }, [overview]);

  const trendSubtitle = useMemo(() => {
    const unit = overview?.metadata?.unit;
    if (!selectedIndicator?.indicator_name) return unit ?? "";
    return unit
      ? `${selectedIndicator.indicator_name} · ${unit}`
      : selectedIndicator.indicator_name;
  }, [overview?.metadata?.unit, selectedIndicator?.indicator_name]);

  // Regional rows for the table (latest year, top 8)
  const regionalRows: RegionalRow[] = useMemo(() => {
    const data = overview?.regional ?? [];
    if (!data.length) return [];
    const maxYear = Math.max(...data.map((d) => d.year));
    return data
      .filter((d) => d.year === maxYear)
      .sort((a, b) => (a.regional_rank ?? 0) - (b.regional_rank ?? 0))
      .slice(0, 8)
      .map((d) => ({
        rank: d.regional_rank,
        region_name: d.region_name,
        value: d.value,
        growth_pct: d.growth_pct,
        year: d.year,
      }));
  }, [overview]);

  // Insights — computed server-side, rendered directly
  const insights: Insight[] = useMemo(() => {
    return overview?.insights ?? [];
  }, [overview]);

  // Metadata items for the preview panel
  const metadataItems: MetadataItem[] = useMemo(() => {
    const md = overview?.metadata;
    if (!md) return [];
    return [
      {
        indicator_key: md.indicator_key,
        indicator_name: md.indicator_name,
        indicator_code: md.indicator_code,
        subject_name: md.subject_name,
        unit: md.unit,
        frequency: md.frequency,
        data_source: md.data_source,
      },
    ];
  }, [overview]);

  if (loading && !overview) {
    return <LoadingState label="Memuat data dari FastAPI → Neon..." />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (domainNotice) {
    return (
      <div className="space-y-section-gap">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-headline-md text-ink">{pageCopy.title}</h1>
            <p className="mt-1 text-body-md text-ink-soft">{pageCopy.subtitle}</p>
          </div>
          <p className="text-body-sm text-ink-muted">
            Periode: {selectedPeriod ?? "—"} · Wilayah: Nasional
          </p>
        </div>

        <GlobalFilters
          filters={filters}
          indicators={indicatorOptions}
          domains={domains?.supported_domains ?? []}
          years={availableYears}
          onChange={setFilters}
        />

        <EmptyState
          title="Domain Belum Tersedia"
          description={domainNotice}
        />
      </div>
    );
  }

  if (!overview || overview.kpis.length === 0) {
    return (
      <EmptyState description="Belum ada data indikator di warehouse. Jalankan ETL pipeline terlebih dahulu." />
    );
  }

  return (
    <div className="space-y-section-gap">
      {/* Page header */}
      <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-headline-md text-ink">{pageCopy.title}</h1>
          <p className="mt-1 text-body-md text-ink-soft">{pageCopy.subtitle}</p>
        </div>
        <p className="text-body-sm text-ink-muted">
          Periode: {selectedPeriod ?? "—"} · Wilayah: Nasional
        </p>
      </div>

      {/* Global filters — single state drives all sections */}
      <GlobalFilters
        filters={filters}
        indicators={indicatorOptions}
        domains={domains?.supported_domains ?? []}
        years={availableYears}
        onChange={setFilters}
      />

      {/* KPI Grid — live indicators */}
      <section aria-label="Indikator utama">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {kpiGrid.map((kpi) => (
            <KPICard key={kpi.key} data={kpi} />
          ))}
        </div>
      </section>

      {/* Economic Trend + Regional Performance */}
      <section
        className="grid grid-cols-1 gap-6 xl:grid-cols-3"
        aria-label={pageCopy.trendAriaLabel}
      >
        <div className="xl:col-span-2">
          <ChartCard
            title="Tren Indikator Nasional"
            subtitle={trendSubtitle}
            timeRange={
              filters.year ? `Tahun ${filters.year}` : "Data historis"
            }
          >
            {trendData.length > 0 ? (
              <EconomicTrendChart data={trendData} height={340} />
            ) : (
              <div className="chart-body">
                <EmptyState description="Belum ada data tren untuk indikator ini." />
              </div>
            )}
          </ChartCard>
        </div>
        <RegionalPerformanceTable
          rows={regionalRows}
          unit={overview?.metadata?.unit}
          title="Kinerja Regional"
          subtitle={selectedPeriod ? `Peringkat tahun ${selectedPeriod}` : "Peringkat tahun berjalan"}
        />
      </section>

      {/* Automated Insights */}
      <section aria-label="Insight otomatis">
        <div className="mb-4">
          <InsightHeader />
        </div>
        {insights.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {insights.map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </div>
        ) : (
          <EmptyState description="Insight akan tersedia setelah data tren dan regional dimuat." />
        )}
      </section>

      {/* Metadata Preview */}
      <section aria-label="Metadata indikator">
        <MetadataPreview items={metadataItems} />
      </section>
    </div>
  );
}
