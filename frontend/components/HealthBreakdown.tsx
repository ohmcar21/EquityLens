import React from "react";

type Health = {
  overall_score?: number | string | null;
  grade?: string | null;
  status?: string | null;
  breakdown?: {
    diversification?: number | string | null;
    volatility?: number | string | null;
    drawdown_risk?: number | string | null;
    liquidity?: number | string | null;
    rebalancing_need?: number | string | null;
    [key: string]: any;
  } | null;
  recommendations?: Array<string> | null;
};

function toNumber(value: any): number | null {
  if (value === null || value === undefined || value === "") return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

export default function HealthBreakdown({ health }: { health: Health }) {
  const breakdown = health?.breakdown || {};

  const metrics: Array<{ key: string; label: string }> = [
    { key: "diversification", label: "Diversification" },
    { key: "volatility", label: "Volatility" },
    { key: "drawdown_risk", label: "Drawdown Risk" },
    { key: "liquidity", label: "Liquidity" },
    { key: "rebalancing_need", label: "Rebalancing Need" },
  ];

  return (
    <section className="mt-6 text-left">
      <div className="bg-gray-50 p-4 rounded-lg mb-4">
        <h3 className="text-lg font-semibold text-black mb-2">Health Breakdown</h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {metrics.map((m) => {
            const raw = (breakdown as any)[m.key];
            const num = toNumber(raw);
            const pct = num === null ? 0 : Math.min(Math.max(Math.round(num * 100) / 100, 0), 100);

            return (
              <div key={m.key} className="bg-white p-3 rounded-md shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-700">{m.label}</span>
                  <span className="text-sm font-medium text-black">
                    {num === null ? "—" : `${pct}%`}
                  </span>
                </div>

                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden" role="progressbar" aria-valuenow={num ?? 0} aria-valuemin={0} aria-valuemax={100} aria-label={m.label}>
                  <div
                    className="h-3 bg-gradient-to-r from-green-400 to-blue-500"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {health?.recommendations && health.recommendations.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-semibold text-black mb-1">Recommendations</h4>
            <ul className="list-disc list-inside text-sm text-gray-700">
              {health.recommendations.map((rec, idx) => (
                <li key={idx}>{rec}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
