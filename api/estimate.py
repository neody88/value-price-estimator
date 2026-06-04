from __future__ import annotations

import json
import math
import os
import re
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Ensure sibling modules are importable (Vercel runs with project root as cwd)
_API_DIR = os.path.dirname(__file__)
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from datasource import fetch
from valuation import estimate as compute_estimate


class _SafeEncoder(json.JSONEncoder):
    """Converts NaN/Inf floats to null so the response is always valid JSON."""
    def iterencode(self, o: object, _one_shot: bool = False):  # type: ignore[override]
        return super().iterencode(self._clean(o), _one_shot)

    def _clean(self, obj: object) -> object:
        if isinstance(obj, float):
            return None if (math.isnan(obj) or math.isinf(obj)) else obj
        if isinstance(obj, dict):
            return {k: self._clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._clean(v) for v in obj]
        return obj


def _json_response(body: dict, status: int = 200) -> tuple[int, bytes]:
    return status, json.dumps(body, ensure_ascii=False, cls=_SafeEncoder).encode("utf-8")


def _handle(ticker: str) -> tuple[int, bytes]:
    if not re.fullmatch(r"\d{6}", ticker):
        return _json_response({"error": "종목코드는 6자리 숫자여야 합니다.", "ticker": ticker}, 400)

    try:
        stock_data = fetch(ticker)
    except Exception as exc:
        return _json_response({"error": f"데이터 조회 실패: {exc}", "ticker": ticker}, 502)

    if not stock_data.price and not stock_data.roe_history:
        return _json_response({"error": "모든 데이터 소스에서 데이터를 가져올 수 없습니다.", "ticker": ticker}, 502)

    result = compute_estimate(stock_data)
    return _json_response(result.model_dump())


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        ticker = (params.get("ticker") or [""])[0].strip()

        status, body = _handle(ticker)

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "s-maxage=21600, stale-while-revalidate=3600")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass  # suppress default access logs in serverless
