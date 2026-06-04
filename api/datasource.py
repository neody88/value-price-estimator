from __future__ import annotations

import math
import re
import sys
import os
from datetime import datetime, timedelta
from typing import Optional

# Guard: no module-level disk writes
# cache is an in-process LRU — safe to import at module level
sys.path.insert(0, os.path.dirname(__file__))
from cache import cache
from _models import StockData, YearMetric

# yfinance column names documented from Phase 0 spike (005930.KS, 2026-06-05)
_NI_KEY = "Net Income From Continuing Operation Net Minority Interest"
_EQ_KEY = "Stockholders Equity"
def _parse_float(v: object) -> Optional[float]:
    """Port of _parse_float from fund_manager seo_valuation.py:6."""
    if v is None:
        return None
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (ValueError, TypeError):
        pass
    s = str(v).replace(",", "").strip()
    if s in ("-", "N/A", "", "nan", "None", "NaN"):
        return None
    try:
        f = float(re.sub(r"[^\d.\-+]", "", s))
        return None if (math.isnan(f) or math.isinf(f)) else f
    except (ValueError, TypeError):
        return None


def fetch(ticker: str) -> StockData:
    """Fetch StockData for a 6-digit Korean ticker. Never raises — degrades to notes."""
    ticker = ticker.strip()
    cached = cache.get(f"stock:{ticker}")
    if cached is not None:
        return cached

    notes: list[str] = []
    exchange_suffix = ".KS"
    name: Optional[str] = None
    price: Optional[float] = None
    shares: Optional[float] = None
    roe_history: list[YearMetric] = []

    # 1. Exchange detection + company name via FDR
    try:
        import FinanceDataReader as fdr
        import pandas as pd

        listing = fdr.StockListing("KRX")
        row = listing[listing["Code"] == ticker]
        if not row.empty:
            market = str(row.iloc[0].get("Market", ""))
            exchange_suffix = ".KS" if "KOSPI" in market.upper() else ".KQ"
            name = str(row.iloc[0].get("Name", "")) or None
            stocks_val = row.iloc[0].get("Stocks")
            if stocks_val and str(stocks_val) not in ("nan", "None", ""):
                shares = float(stocks_val)
        else:
            notes.append(f"종목코드 {ticker}를 KRX 목록에서 찾을 수 없습니다.")
    except Exception as exc:
        notes.append(f"FDR 거래소 감지 오류: {exc}")

    symbol = f"{ticker}{exchange_suffix}"

    # 2. Current price + historical financials via yfinance
    try:
        import yfinance as yf

        t = yf.Ticker(symbol)

        # Current price via fast_info
        try:
            fi = t.fast_info
            price = _parse_float(fi.get("last_price")) or _parse_float(fi.get("regular_market_price"))
        except Exception:
            pass

        # Shares outstanding from yfinance info (more accurate than FDR Stocks)
        try:
            info = t.info
            yf_shares = info.get("sharesOutstanding")
            if yf_shares:
                shares = float(yf_shares)
        except Exception:
            pass

        # Historical financials
        try:
            fin = t.financials   # columns = fiscal year-end dates, rows = line items
            bs = t.balance_sheet

            if not fin.empty and not bs.empty and shares and shares > 0:
                for col in fin.columns:
                    year = col.year
                    try:
                        ni_raw = fin.loc[_NI_KEY, col] if _NI_KEY in fin.index else None
                        eq_raw = bs.loc[_EQ_KEY, col] if _EQ_KEY in bs.index else None

                        # Average equity: use adjacent period when available
                        col_list = list(fin.columns)
                        idx = col_list.index(col)
                        eq_curr_parsed = _parse_float(eq_raw)
                        if idx + 1 < len(col_list) and _EQ_KEY in bs.index:
                            eq_prev_parsed = _parse_float(bs.loc[_EQ_KEY, col_list[idx + 1]])
                            eq_avg = (
                                (eq_curr_parsed + eq_prev_parsed) / 2
                                if eq_curr_parsed is not None and eq_prev_parsed is not None
                                else eq_curr_parsed
                            )
                        else:
                            eq_avg = eq_curr_parsed

                        ni = _parse_float(ni_raw)

                        roe = (ni / eq_avg * 100) if ni and eq_avg and eq_avg != 0 else None
                        bps_yr = (eq_curr_parsed / shares) if eq_curr_parsed else None

                        roe_history.append(YearMetric(
                            year=year,
                            roe=round(roe, 2) if roe is not None else None,
                            bps=round(bps_yr) if bps_yr is not None else None,
                            net_income=ni,
                            equity=eq_curr_parsed,
                        ))
                    except Exception:
                        continue
        except Exception as exc:
            notes.append(f"yfinance 재무제표 오류: {exc}")

        # Fallback price via FDR if yfinance fast_info failed
        if price is None:
            try:
                import FinanceDataReader as fdr
                from_d = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")
                price_df = fdr.DataReader(ticker, from_d)
                if not price_df.empty:
                    price = float(price_df["Close"].iloc[-1])
            except Exception as exc:
                notes.append(f"가격 조회 오류: {exc}")

    except Exception as exc:
        notes.append(f"yfinance 오류: {exc}")

    # Sort history newest-first
    roe_history.sort(key=lambda x: x.year, reverse=True)

    if len(roe_history) < 3:
        notes.append(f"ROE 데이터가 {len(roe_history)}개 연도만 확보됨 (yfinance 제한) — 직접 확인 권장.")
    else:
        notes.append("ROE는 약 4개 연도 데이터 기준 (yfinance 제한) — 직접 확인 권장.")

    # Derive current snapshot metrics from latest year
    latest_bps: Optional[float] = roe_history[0].bps if roe_history else None
    latest_ni: Optional[float] = roe_history[0].net_income if roe_history else None
    latest_eps = (latest_ni / shares) if latest_ni and shares and shares > 0 else None
    pbr = (price / latest_bps) if price and latest_bps and latest_bps > 0 else None
    per = (price / latest_eps) if price and latest_eps and latest_eps > 0 else None

    data = StockData(
        ticker=ticker,
        symbol=symbol,
        exchange=exchange_suffix.lstrip("."),
        name=name,
        price=round(price) if price else None,
        shares_outstanding=shares,
        bps=round(latest_bps) if latest_bps else None,
        pbr=round(pbr, 2) if pbr else None,
        per=round(per, 1) if per else None,
        eps=round(latest_eps) if latest_eps else None,
        roe_history=roe_history,
        notes=notes,
    )

    cache.set(f"stock:{ticker}", data)
    return data
