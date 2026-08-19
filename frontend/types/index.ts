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
}

export interface OverviewResponse {
  indicators: OverviewIndicator[];
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