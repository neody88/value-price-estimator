"""Unit tests for valuation.py — Phase 3 acceptance criteria."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from valuation import (
    calc_future_bps,
    calc_buy_prices,
    normalize_roe,
    project,
    roe_stability,
)


def approx(a: float, b: float, tol: float = 0.01) -> bool:
    """True if a is within tol (1%) of b."""
    return abs(a - b) / abs(b) <= tol


# ── normalize_roe ──────────────────────────────────────────────────────────────

def test_normalize_roe_median():
    result = normalize_roe([13.9, 8.9, 6.1, 12.2])
    # sorted: [6.1, 8.9, 12.2, 13.9] → median = (8.9+12.2)/2 = 10.55
    assert result["normalized"] == 10.55, f"Expected 10.55, got {result['normalized']}"
    assert result["latest"] == 13.9
    assert result["n"] == 4


def test_normalize_roe_empty():
    r = normalize_roe([])
    assert r["normalized"] is None
    assert r["n"] == 0


def test_normalize_roe_single():
    r = normalize_roe([8.5])
    assert r["normalized"] == 8.5
    assert r["latest"] == 8.5


# ── roe_stability ──────────────────────────────────────────────────────────────

def test_roe_stability_stable():
    r = roe_stability([10.0, 11.0, 10.5, 10.8])
    assert r["classification"] == "STABLE"
    assert not r["is_cyclical"]
    assert r["spread"] is not None and r["spread"] <= 8


def test_roe_stability_cyclical_spread():
    r = roe_stability([3.0, 12.0, 1.0, 14.0])  # spread=13 > 8
    assert r["classification"] == "CYCLICAL"
    assert r["is_cyclical"]


def test_roe_stability_cyclical_negative():
    r = roe_stability([8.0, -2.0, 9.0])
    assert r["classification"] == "CYCLICAL"
    assert r["is_cyclical"]


def test_roe_stability_near_zero_mean():
    r = roe_stability([0.1, -0.1, 0.2])  # mean ≈ 0.07, spread=0.3 but has negative
    assert r["classification"] == "CYCLICAL"
    assert r["is_cyclical"]


def test_roe_stability_no_zero_division():
    # mean=0 exactly — must not raise
    try:
        r = roe_stability([0.0, 0.0, 0.0])
        assert r["is_cyclical"]
    except ZeroDivisionError:
        raise AssertionError("roe_stability raised ZeroDivisionError on zero mean")


# ── calc_future_bps ────────────────────────────────────────────────────────────

def test_future_bps_samsung():
    fbps = calc_future_bps(bps=63997, roe=0.094, retention=0.7, years=10)
    # exact ≈ 121,037
    assert approx(fbps, 121037), f"Expected ~121037, got {fbps}"


def test_future_bps_zero_roe():
    fbps = calc_future_bps(bps=50000, roe=0.0, retention=0.7, years=10)
    assert fbps == 50000.0


# ── project ───────────────────────────────────────────────────────────────────

def test_project_fair_value_neutral():
    proj = project(bps=63997, roe=0.094, current_pbr=5.63, current_price=360500)
    # exit_pbr_neutral = min(5.63, 1.5) = 1.5
    assert proj["exit_pbr_neutral"] == 1.5
    # fair_value_neutral ≈ 121037 × 1.5 = 181556
    assert approx(proj["fair_value_neutral"], 181556), f"Expected ~181556, got {proj['fair_value_neutral']}"
    # fair_value_conservative ≈ 121037
    assert approx(proj["fair_value_conservative"], 121037)
    # implied return should be negative (current price >> conservative fair value)
    assert proj["implied_return_conservative"] is not None
    assert proj["implied_return_conservative"] < 0


def test_project_low_pbr_uses_one():
    proj = project(bps=50000, roe=0.10, current_pbr=0.8, current_price=40000)
    # min(0.8, 1.5) = 0.8, not floored (plan intentionally allows <1.0)
    assert proj["exit_pbr_neutral"] == 0.8


# ── calc_buy_prices ────────────────────────────────────────────────────────────

def test_buy_prices_10pct_conservative():
    bps_out = calc_future_bps(bps=63997, roe=0.094, retention=0.7, years=10)
    prices = calc_buy_prices(bps_out, bps_out * 1.5)
    entry_10 = next(p for p in prices if p["target"] == 10)
    # buy_price(10%) = 121037 / (1.10)^10 ≈ 46677
    assert approx(entry_10["price_conservative"], 46677), f"Expected ~46677, got {entry_10['price_conservative']}"


def test_buy_prices_monotone():
    prices = calc_buy_prices(100000, 150000)
    conserv = [p["price_conservative"] for p in prices]
    assert conserv == sorted(conserv, reverse=True), "Buy prices should decrease as target return increases"


def test_buy_prices_round_trip():
    fv = 121037.0
    prices = calc_buy_prices(fv, fv)
    for p in prices:
        r = p["target"] / 100
        reconstructed = p["price_conservative"] * (1 + r) ** 10
        assert approx(reconstructed, fv), f"Round-trip failed for target={p['target']}%"


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for fn in tests:
        try:
            fn()
            print(f"  ✓ {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {fn.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
