export interface OverviewIndicator {
  indicator_key: string;
  indicator_name: string;
  unit: string;
  frequency: string;
  latest_year: number;
  years_available: number;
  region_count: number;
  current_value: number | null;
  yoy_growth: number | null;
  national_value_status?: "available" | "unavailable";
}

export interface OverviewInsight {
  id: string;
  category: string;
  title: string;
  description: string;
  direction: "up" | "down" | "neutral";
  value: string;
}

export interface OverviewApiResponse {
  kpis: OverviewIndicator[];
  trend: TrendPoint[];
  regional: RegionalPoint[];
  insights: OverviewInsight[];
  metadata: IndicatorMetadata | null;
  filters: {
    domain: string | null;
    year: number;
    region: string;
    indicator_key: string;
  };
}

export interface TrendPoint {
  year: number;
  indicator_key: string;
  indicator_name: string;
  unit: string;
  national_value: number;
  previous_value: number | null;
  growth_pct: number | null;
}

export interface EconomicTrendResponse {
  data: TrendPoint[];
}

export interface RegionalPoint {
  year: number;
  region_key: string;
  region_name: string;
  indicator_key: string;
  indicator_name: string;
  value: number;
  regional_rank: number;
  previous_value: number | null;
  growth_pct: number | null;
  growth_status?: string;
}

export interface RegionalResponse {
  data: RegionalPoint[];
}

export interface TradeTrendPoint {
  year: number;
  trade_flow: string;
  total_value_usd: number;
  total_weight_kg: number;
  transaction_count: number;
}

export interface TradeTrendResponse {
  data: TradeTrendPoint[];
}

export interface CommodityPoint {
  year: number;
  trade_flow: string;
  product_code: string;
  product_name: string;
  total_value_usd: number;
  total_weight_kg: number;
  commodity_rank: number;
}

export interface CommodityResponse {
  data: CommodityPoint[];
}

export interface PartnerPoint {
  year: number;
  trade_flow: string;
  country_code: string;
  country_name: string;
  total_value_usd: number;
  partner_rank: number;
}

export interface PartnerResponse {
  data: PartnerPoint[];
}

export interface IndicatorMetadata {
  indicator_key: string;
  indicator_code: string;
  indicator_name: string;
  subject_name: string | null;
  category_name: string | null;
  unit: string | null;
  frequency: string | null;
  concept: string | null;
  definition: string | null;
  classification: string | null;
  measure: string | null;
  data_source: string | null;
  aggregation_method: string | null;
}

export interface IndicatorListResponse {
  indicators: Array<{
    indicator_key: string;
    indicator_code: string;
    indicator_name: string;
    subject_name: string | null;
    category_name: string | null;
    unit: string | null;
    frequency: string | null;
    data_source: string | null;
  }>;
}

export interface OverviewDomainOption {
  key: string;
  subject_candidates: string[];
  matched_subjects: string[];
  available: boolean;
}

export interface OverviewDomainsResponse {
  available_subjects: string[];
  configured_domains: Record<
    string,
    {
      subject_candidates: string[];
      matched_subjects: string[];
    }
  >;
  supported_domains: OverviewDomainOption[];
}

// ===== Filter & API Contract (FastAPI → Neon) =====

export interface FilterOption<T = string> {
  value: T;
  label: string;
}

/**
 * Single source of truth for the Overview global filters.
 * All sections (KPI, trend, regional, metadata) are driven by this state.
 */
export interface OverviewFilters {
  /** Stable API domain key. Empty string means no domain filter is sent. */
  domain: string;
  /** Selected indicator key — drives KPI, historical trend, and regional breakdown. */
  indicatorKey: string;
  /** Selected period; null = latest available year. */
  year: number | null;
  /** Current overview contract only supports the national scope. */
  region: string;
}
