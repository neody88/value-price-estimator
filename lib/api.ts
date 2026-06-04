export interface YearMetric {
  year: number;
  roe: number | null;
  bps: number | null;
}

export interface RoeResult {
  latest: number | null;
  normalized: number | null;
  years: number;
  history: YearMetric[];
}

export interface StabilityResult {
  cv: number | null;
  spread: number | null;
  classification: "STABLE" | "MODERATE" | "CYCLICAL";
  is_cyclical: boolean;
}

export interface ProjectionResult {
  years: number;
  future_bps: number;
  exit_pbr_neutral: number;
  fair_value_conservative: number;
  fair_value_neutral: number;
  implied_return_conservative: number | null;
  implied_return_neutral: number | null;
}

export interface BuyPriceEntry {
  target: number;
  price_conservative: number;
  price_neutral: number;
}

export interface EstimateResult {
  ticker: string;
  name: string | null;
  price: number | null;
  pbr: number | null;
  per: number | null;
  bps: number | null;
  roe: RoeResult | null;
  stability: StabilityResult | null;
  projection: ProjectionResult | null;
  buy_prices: BuyPriceEntry[];
  warning: string | null;
  notes: string[];
  disclaimer: string;
}

export interface ApiError {
  error: string;
  ticker: string;
}

export async function fetchEstimate(ticker: string): Promise<EstimateResult> {
  const res = await fetch(`/api/estimate?ticker=${encodeURIComponent(ticker)}`);
  const data = await res.json();
  if (!res.ok) {
    throw new Error((data as ApiError).error ?? `HTTP ${res.status}`);
  }
  return data as EstimateResult;
}

export function formatKRW(value: number | null | undefined): string {
  if (value == null) return "-";
  return `${value.toLocaleString("ko-KR")}원`;
}

export function formatPct(value: number | null | undefined): string {
  if (value == null) return "-";
  return `${value.toFixed(1)}%`;
}
