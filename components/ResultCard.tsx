"use client";

import type { EstimateResult } from "@/lib/api";
import { formatKRW, formatPct } from "@/lib/api";
import BuyPriceTable from "./BuyPriceTable";
import CyclicalWarning from "./CyclicalWarning";
import RoeHistory from "./RoeHistory";

interface Props {
  result: EstimateResult;
}

export default function ResultCard({ result }: Props) {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              {result.name ?? result.ticker}
            </h2>
            <p className="text-sm text-gray-500">{result.ticker}</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-gray-900">{formatKRW(result.price)}</p>
            <p className="text-xs text-gray-400">현재가</p>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-4 border-t border-gray-100 pt-4 text-center text-sm">
          <div>
            <p className="text-gray-500">PBR</p>
            <p className="font-semibold">{result.pbr != null ? `${result.pbr}배` : "-"}</p>
          </div>
          <div>
            <p className="text-gray-500">PER</p>
            <p className="font-semibold">{result.per != null ? `${result.per}배` : "-"}</p>
          </div>
          <div>
            <p className="text-gray-500">BPS</p>
            <p className="font-semibold">{formatKRW(result.bps)}</p>
          </div>
        </div>
      </div>

      {/* Cyclical warning */}
      {result.warning && <CyclicalWarning warning={result.warning} />}

      {/* ROE history */}
      {result.roe && (
        <RoeHistory roe={result.roe} stability={result.stability} />
      )}

      {/* Buy price table */}
      {result.projection && result.buy_prices.length > 0 && (
        <BuyPriceTable
          buyPrices={result.buy_prices}
          projection={result.projection}
          currentPrice={result.price}
        />
      )}

      {/* Notes */}
      {result.notes.length > 0 && (
        <ul className="space-y-1 text-xs text-gray-500">
          {result.notes.map((note, i) => (
            <li key={i}>※ {note}</li>
          ))}
        </ul>
      )}

      {/* Disclaimer */}
      <p className="text-center text-xs text-gray-400">{result.disclaimer}</p>
    </div>
  );
}
