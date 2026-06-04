from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class YearMetric(BaseModel):
    year: int
    roe: Optional[float] = None
    bps: Optional[float] = None
    net_income: Optional[float] = None
    equity: Optional[float] = None


class StockData(BaseModel):
    ticker: str
    symbol: str
    exchange: str
    name: Optional[str] = None
    price: Optional[float] = None
    shares_outstanding: Optional[float] = None
    bps: Optional[float] = None
    pbr: Optional[float] = None
    per: Optional[float] = None
    eps: Optional[float] = None
    roe_history: list[YearMetric] = []
    notes: list[str] = []


class StabilityResult(BaseModel):
    cv: Optional[float] = None
    spread: Optional[float] = None
    classification: str  # STABLE | MODERATE | CYCLICAL
    is_cyclical: bool


class ProjectionResult(BaseModel):
    years: int = 10
    future_bps: float
    exit_pbr_neutral: float
    fair_value_conservative: float
    fair_value_neutral: float
    implied_return_conservative: Optional[float] = None
    implied_return_neutral: Optional[float] = None


class BuyPriceEntry(BaseModel):
    target: int
    price_conservative: float
    price_neutral: float


class RoeResult(BaseModel):
    latest: Optional[float] = None
    normalized: Optional[float] = None
    years: int = 0
    history: list[dict] = []


class EstimateResult(BaseModel):
    ticker: str
    name: Optional[str] = None
    price: Optional[float] = None
    pbr: Optional[float] = None
    per: Optional[float] = None
    bps: Optional[float] = None
    roe: Optional[RoeResult] = None
    stability: Optional[StabilityResult] = None
    projection: Optional[ProjectionResult] = None
    buy_prices: list[BuyPriceEntry] = []
    warning: Optional[str] = None
    notes: list[str] = []
    disclaimer: str = "본 결과는 추정치이며 투자 권유가 아닙니다."
