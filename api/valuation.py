from __future__ import annotations

import statistics
from typing import Optional

try:
    from ._models import (
        BuyPriceEntry,
        EstimateResult,
        ProjectionResult,
        RoeResult,
        StabilityResult,
        StockData,
    )
except ImportError:
    from _models import (  # type: ignore[no-redef]
        BuyPriceEntry,
        EstimateResult,
        ProjectionResult,
        RoeResult,
        StabilityResult,
        StockData,
    )

_RETENTION = 0.7
_YEARS = 10
_TARGETS = (8, 10, 12, 15)
_NEAR_ZERO_EPS = 0.5  # ROE mean below this → CV undefined


def normalize_roe(roe_history: list[float]) -> dict:
    """Returns {latest, normalized (median), n}."""
    valid = [r for r in roe_history if r is not None]
    if not valid:
        return {"latest": None, "normalized": None, "n": 0}
    return {
        "latest": valid[0],
        "normalized": statistics.median(valid),
        "n": len(valid),
    }


def roe_stability(roe_history: list[float]) -> dict:
    """CV-based stability classification. Guards against near-zero mean."""
    valid = [r for r in roe_history if r is not None]
    if not valid:
        return {"cv": None, "spread": None, "classification": "CYCLICAL", "is_cyclical": True}

    spread = max(valid) - min(valid)
    has_negative = any(r < 0 for r in valid)

    if has_negative or spread > 8:
        return {
            "cv": None,
            "spread": round(spread, 2),
            "classification": "CYCLICAL",
            "is_cyclical": True,
        }

    mean = statistics.mean(valid)
    if abs(mean) < _NEAR_ZERO_EPS:
        return {
            "cv": None,
            "spread": round(spread, 2),
            "classification": "CYCLICAL",
            "is_cyclical": True,
            "note": "CV 미정의 (ROE 평균 ≈ 0)",
        }

    stdev = statistics.stdev(valid) if len(valid) > 1 else 0.0
    cv = stdev / abs(mean)
    classification = "STABLE" if cv < 0.25 else "MODERATE"
    return {
        "cv": round(cv, 3),
        "spread": round(spread, 2),
        "classification": classification,
        "is_cyclical": False,
    }


def calc_future_bps(
    bps: float,
    roe: float,
    *,
    retention: float = _RETENTION,
    years: int = _YEARS,
) -> float:
    """future_bps = bps × (1 + roe × retention)^years. roe is a decimal (e.g. 0.094)."""
    return bps * (1 + roe * retention) ** years


def project(
    bps: float,
    roe: float,
    *,
    current_pbr: Optional[float],
    current_price: Optional[float] = None,
    retention: float = _RETENTION,
    years: int = _YEARS,
) -> dict:
    """Project fair value from BPS + normalized ROE. roe is a decimal."""
    fbps = calc_future_bps(bps, roe, retention=retention, years=years)
    exit_pbr_neutral = min(current_pbr, 1.5) if current_pbr and current_pbr > 0 else 1.0
    fv_conservative = fbps * 1.0
    fv_neutral = fbps * exit_pbr_neutral

    implied_conservative = implied_neutral = None
    if current_price and current_price > 0:
        implied_conservative = round(((fv_conservative / current_price) ** (1 / years) - 1) * 100, 2)
        implied_neutral = round(((fv_neutral / current_price) ** (1 / years) - 1) * 100, 2)

    return {
        "years": years,
        "future_bps": round(fbps),
        "exit_pbr_neutral": round(exit_pbr_neutral, 2),
        "fair_value_conservative": round(fv_conservative),
        "fair_value_neutral": round(fv_neutral),
        "implied_return_conservative": implied_conservative,
        "implied_return_neutral": implied_neutral,
    }


def calc_buy_prices(
    fair_value_conservative: float,
    fair_value_neutral: float,
    *,
    targets: tuple = _TARGETS,
    years: int = _YEARS,
) -> list[dict]:
    """Entry price P such that compounding P at target r for years reaches fair_value."""
    result = []
    for t in targets:
        r = t / 100
        divisor = (1 + r) ** years
        result.append({
            "target": t,
            "price_conservative": round(fair_value_conservative / divisor),
            "price_neutral": round(fair_value_neutral / divisor),
        })
    return result


def estimate(data: StockData) -> EstimateResult:
    roe_values = [m.roe for m in data.roe_history if m.roe is not None]

    roe_norm = normalize_roe(roe_values)
    stab = roe_stability(roe_values)

    roe_out: Optional[RoeResult] = None
    if roe_values:
        roe_out = RoeResult(
            latest=roe_norm["latest"],
            normalized=round(roe_norm["normalized"], 2) if roe_norm["normalized"] is not None else None,
            years=roe_norm["n"],
            history=[{"year": m.year, "roe": m.roe, "bps": m.bps} for m in data.roe_history],
        )

    stability_out = StabilityResult(
        cv=stab.get("cv"),
        spread=stab.get("spread"),
        classification=stab["classification"],
        is_cyclical=stab["is_cyclical"],
    )

    warning = (
        "ROE 변동성이 큽니다 — 경기민감주(시클리컬)로 이 전략에 부적합할 수 있습니다."
        if stability_out.is_cyclical
        else None
    )

    projection_out: Optional[ProjectionResult] = None
    buy_prices_out: list[BuyPriceEntry] = []
    notes = list(data.notes)

    if data.bps and roe_out and roe_out.normalized:
        proj = project(
            data.bps,
            roe_out.normalized / 100,  # percentage → decimal
            current_pbr=data.pbr,
            current_price=data.price,
        )
        projection_out = ProjectionResult(**proj)
        buy_prices_out = [
            BuyPriceEntry(**bp)
            for bp in calc_buy_prices(
                proj["fair_value_conservative"],
                proj["fair_value_neutral"],
            )
        ]
    elif not data.bps:
        notes.append("BPS 데이터가 없어 예측을 계산할 수 없습니다.")

    return EstimateResult(
        ticker=data.ticker,
        name=data.name,
        price=data.price,
        pbr=data.pbr,
        per=data.per,
        bps=data.bps,
        roe=roe_out,
        stability=stability_out,
        projection=projection_out,
        buy_prices=buy_prices_out,
        warning=warning,
        notes=notes,
        disclaimer="본 결과는 추정치이며 투자 권유가 아닙니다.",
    )
