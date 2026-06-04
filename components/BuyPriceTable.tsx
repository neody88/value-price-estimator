"use client";

import type { BuyPriceEntry, ProjectionResult } from "@/lib/api";
import { formatKRW, formatPct } from "@/lib/api";

interface Props {
  buyPrices: BuyPriceEntry[];
  projection: ProjectionResult;
  currentPrice: number | null;
}

function gap(buyPrice: number, current: number | null): string {
  if (!current) return "-";
  const pct = ((buyPrice - current) / current) * 100;
  return `${pct > 0 ? "+" : ""}${pct.toFixed(1)}%`;
}

function gapColor(buyPrice: number, current: number | null): string {
  if (!current) return "text-gray-500";
  return buyPrice >= current ? "text-green-700" : "text-red-600";
}

function returnColor(ret: number | null): string {
  return ret != null && ret < 0 ? "text-red-600 font-medium" : "text-green-700 font-medium";
}

export default function BuyPriceTable({ buyPrices, projection, currentPrice }: Props) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-1 font-semibold text-gray-800">목표 수익률별 매수 추천가</h3>
      <p className="mb-3 text-xs text-gray-500">
        10년 후 공정가치: 보수 {formatKRW(projection.fair_value_conservative)} / 중립 {formatKRW(projection.fair_value_neutral)}
        {" "}(Exit PBR×{projection.exit_pbr_neutral})
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-gray-500">
              <th className="pb-2 text-left font-medium">목표 수익률</th>
              <th className="pb-2 text-right font-medium">보수적 (PBR×1.0)</th>
              <th className="pb-2 text-right font-medium">중립 (PBR×{projection.exit_pbr_neutral})</th>
            </tr>
          </thead>
          <tbody>
            {buyPrices.map((bp) => (
              <tr key={bp.target} className="border-b border-gray-50">
                <td className="py-2 font-medium text-gray-700">{bp.target}%</td>
                <td className="py-2 text-right">
                  <span className="font-mono">{formatKRW(bp.price_conservative)}</span>
                  <span className={`ml-2 text-xs ${gapColor(bp.price_conservative, currentPrice)}`}>
                    {gap(bp.price_conservative, currentPrice)}
                  </span>
                </td>
                <td className="py-2 text-right">
                  <span className="font-mono">{formatKRW(bp.price_neutral)}</span>
                  <span className={`ml-2 text-xs ${gapColor(bp.price_neutral, currentPrice)}`}>
                    {gap(bp.price_neutral, currentPrice)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {currentPrice && (
        <div className="mt-3 border-t border-gray-100 pt-3 text-xs text-gray-500">
          현재가 {formatKRW(currentPrice)} 기준 예상 연환산 수익률 —
          보수: <span className={returnColor(projection.implied_return_conservative)}>
            {formatPct(projection.implied_return_conservative)}
          </span>
          {" "}/ 중립: <span className={returnColor(projection.implied_return_neutral)}>
            {formatPct(projection.implied_return_neutral)}
          </span>
        </div>
      )}
    </div>
  );
}
