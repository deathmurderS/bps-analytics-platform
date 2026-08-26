"use client";

import { SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type {
  FilterOption,
  OverviewDomainOption,
  OverviewFilters,
} from "@/types";

interface GlobalFiltersProps {
  filters: OverviewFilters;
  /** Indicator options from the live metadata API. */
  indicators: Array<{
    indicator_key: string;
    indicator_name: string;
    unit: string | null;
    frequency: string | null;
    subject_name: string | null;
  }>;
  domains: OverviewDomainOption[];
  /** Available periods from the live data (e.g. trend years). */
  years: number[];
  onChange: (next: OverviewFilters) => void;
}

export default function GlobalFilters({
  filters,
  indicators,
  domains,
  years,
  onChange,
}: GlobalFiltersProps) {
  const [draft, setDraft] = useState<OverviewFilters>(filters);

  useEffect(() => {
    setDraft(filters);
  }, [filters]);

  const domainOptions: FilterOption[] = useMemo(
    () => [
      { value: "", label: "Semua domain" },
      ...domains.map((domain) => ({
        value: domain.key,
        label: `${domain.key}${domain.available ? "" : " (belum tersedia)"}`,
      })),
    ],
    [domains]
  );

  const indicatorOptions: FilterOption[] = useMemo(() => {
    if (!filters.domain) {
      return indicators.map((ind) => ({
        value: ind.indicator_key,
        label: ind.indicator_name,
      }));
    }

    const selectedDomain = domains.find((domain) => domain.key === filters.domain);
    const matchedSubjects = new Set(selectedDomain?.matched_subjects ?? []);

    const filtered = indicators.filter((ind) => {
      const subject = ind.subject_name?.trim().toLowerCase();
      return subject ? matchedSubjects.has(subject) : false;
    });

    const source = filtered.length > 0 ? filtered : indicators;
    return source.map((ind) => ({
      value: ind.indicator_key,
      label: ind.indicator_name,
    }));
  }, [domains, filters.domain, indicators]);

  // Period options derived from data
  const yearOptions: FilterOption<number>[] = useMemo(
    () => [...years].sort((a, b) => b - a).map((y) => ({ value: y, label: String(y) })),
    [years]
  );

  // Region options — national only until backend exposes region dimension
  const regionOptions: FilterOption[] = useMemo(
    () => [{ value: "national", label: "Nasional" }],
    []
  );

  // Keep draft in sync when parent filters change
  const isDirty =
    draft.domain !== filters.domain ||
    draft.indicatorKey !== filters.indicatorKey ||
    draft.year !== filters.year ||
    draft.region !== filters.region;

  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border border-line bg-white px-4 py-3">
      <span className="flex items-center gap-1.5 text-label-caps text-ink-muted">
        <SlidersHorizontal className="h-3.5 w-3.5" />
        Filter
      </span>

      <span className="h-5 w-px bg-line" />

      {/* Domain filter */}
      <label className="flex items-center gap-1.5">
        <span className="text-[11px] font-medium text-ink-muted">Domain</span>
        <select
          className="input h-8 w-auto max-w-[180px] py-0 pr-7 text-xs"
          value={draft.domain}
          onChange={(e) =>
            setDraft((d) => {
              const nextDomain = e.target.value;
              const selectedDomain = domains.find((domain) => domain.key === nextDomain);
              const matchedSubjects = new Set(selectedDomain?.matched_subjects ?? []);
              const filteredIndicators = !nextDomain
                ? indicators
                : indicators.filter((ind) => {
                    const subject = ind.subject_name?.trim().toLowerCase();
                    return subject ? matchedSubjects.has(subject) : false;
                  });

              return {
                ...d,
                domain: nextDomain,
                indicatorKey: filteredIndicators[0]?.indicator_key ?? d.indicatorKey,
              };
            })
          }
        >
          {domainOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>

      {/* Indicator filter */}
      <label className="flex items-center gap-1.5">
        <span className="text-[11px] font-medium text-ink-muted">Indikator</span>
        <select
          className="input h-8 w-auto max-w-[220px] py-0 pr-7 text-xs"
          value={draft.indicatorKey}
          onChange={(e) =>
            setDraft((d) => ({ ...d, indicatorKey: e.target.value }))
          }
        >
          {indicatorOptions.length === 0 && <option value="">Tidak ada</option>}
          {indicatorOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>

      {/* Period filter */}
      <label className="flex items-center gap-1.5">
        <span className="text-[11px] font-medium text-ink-muted">Periode</span>
        <select
          className="input h-8 w-auto py-0 pr-7 text-xs"
          value={draft.year ?? ""}
          onChange={(e) =>
            setDraft((d) => ({
              ...d,
              year: e.target.value ? Number(e.target.value) : null,
            }))
          }
        >
          <option value="">Terbaru</option>
          {yearOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>

      {/* Region filter */}
      <label className="flex items-center gap-1.5">
        <span className="text-[11px] font-medium text-ink-muted">Wilayah</span>
        <select
          className="input h-8 w-auto py-0 pr-7 text-xs"
          value={draft.region}
          onChange={(e) => setDraft((d) => ({ ...d, region: e.target.value }))}
        >
          {regionOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>

      <div className="flex-1" />

      <button
        className="btn-secondary h-8 px-3 py-0 text-xs"
        disabled={!isDirty}
        onClick={() => onChange(draft)}
      >
        Terapkan
      </button>
    </div>
  );
}