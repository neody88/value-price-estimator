"use client";

import type { RoeResult, StabilityResult } from "@/lib/api";

interface Props {
  roe: RoeResult;
  stability: StabilityResult | null;
}

const classLabel: Record<string, string> = {
  STABLE: "안정",
  MODERATE: "보통",
  CYCLICAL: "경기민감",
};

const classColor: Record<string, string> = {
  STABLE: "text-green-700 bg-green-100",
  MODERATE: "text-yellow-700 bg-yellow-100",
  CYCLICAL: "text-red-700 bg-red-100",
};

export default function RoeHistory({ roe, stability }: Props) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold text-gray-800">ROE 이력</h3>
        {stability && (
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${classColor[stability.classification] ?? ""}`}>
            {classLabel[stability.classification] ?? stability.classification}
            {stability.spread != null && ` (스프레드 ${stability.spread.toFixed(1)}%p)`}
          </span>
        )}
      </div>

      <div className="mb-3 flex gap-6 text-sm">
        <div>
          <p className="text-gray-500">최근 ROE</p>
          <p className="text-lg font-bold">{roe.latest != null ? `${roe.latest.toFixed(1)}%` : "-"}</p>
        </div>
        <div>
          <p className="text-gray-500">정규화 ROE (중앙값)</p>
          <p className="text-lg font-bold">{roe.normalized != null ? `${roe.normalized.toFixed(1)}%` : "-"}</p>
        </div>
      </div>

      {roe.history.length > 0 && (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 text-left text-gray-500">
              <th className="pb-1 font-medium">연도</th>
              <th className="pb-1 text-right font-medium">ROE</th>
              <th className="pb-1 text-right font-medium">BPS (원)</th>
            </tr>
          </thead>
          <tbody>
            {roe.history.map((r) => (
              <tr key={r.year} className="border-b border-gray-50">
                <td className="py-1 text-gray-700">{r.year}</td>
                <td className={`py-1 text-right font-mono ${r.roe != null && r.roe < 0 ? "text-red-600" : "text-gray-900"}`}>
                  {r.roe != null ? `${r.roe.toFixed(1)}%` : "-"}
                </td>
                <td className="py-1 text-right font-mono text-gray-700">
                  {r.bps != null ? r.bps.toLocaleString("ko-KR") : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {roe.years < 5 && (
        <p className="mt-2 text-xs text-gray-400">
          ※ {roe.years}개 연도 데이터 사용 (yfinance 제한) — 직접 확인 권장
        </p>
      )}
    </div>
  );
}
