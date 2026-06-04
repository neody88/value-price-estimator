"use client";

import { useState } from "react";
import type { EstimateResult } from "@/lib/api";
import { fetchEstimate } from "@/lib/api";
import ResultCard from "@/components/ResultCard";

const EXAMPLES = ["005930", "035720", "000660", "051910"];

export default function Home() {
  const [ticker, setTicker] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EstimateResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  function validate(value: string): string | null {
    if (!value) return "종목코드를 입력해주세요.";
    if (!/^\d{6}$/.test(value.trim())) return "종목코드는 6자리 숫자여야 합니다. (예: 005930)";
    return null;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = ticker.trim();
    const validationError = validate(trimmed);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await fetchEstimate(trimmed);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  function handleExample(code: string) {
    setTicker(code);
    setError(null);
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-10">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900">주식 가치 평가기</h1>
        <p className="mt-2 text-gray-500">
          서준식 ROE 기반 10년 주가 예측 · 매수 추천가 계산
        </p>
      </div>

      {/* Search form */}
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={ticker}
            onChange={(e) => {
              setTicker(e.target.value);
              setError(null);
            }}
            placeholder="종목코드 6자리 입력 (예: 005930)"
            maxLength={6}
            className={`flex-1 rounded-lg border px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 ${
              error ? "border-red-400 focus:ring-red-400" : "border-gray-300"
            }`}
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "조회중…" : "조회"}
          </button>
        </div>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </form>

      {/* Examples */}
      <div className="mb-8 flex flex-wrap gap-2">
        <span className="text-sm text-gray-400">예시:</span>
        {EXAMPLES.map((code) => (
          <button
            key={code}
            onClick={() => handleExample(code)}
            className="rounded border border-gray-200 px-3 py-1 text-sm text-gray-600 hover:bg-gray-100"
          >
            {code}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="py-16 text-center text-gray-500">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p>데이터를 불러오는 중입니다…</p>
        </div>
      )}

      {/* Result */}
      {!loading && result && <ResultCard result={result} />}
    </main>
  );
}
