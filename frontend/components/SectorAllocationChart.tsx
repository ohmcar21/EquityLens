import React from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";

type Sector = {
  sector?: string;
  value?: number | string;
  percentage?: number | string;
  holdings_count?: number | string;
};

type Props = {
  sectors: Sector[];
  isLoading: boolean;
};

const COLORS = [
  "#6366f1",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#14b8a6",
  "#f97316",
  "#3b82f6",
];

const safeNumber = (value: any) => {
  if (value === null || value === undefined) return 0;
  if (typeof value === "number") return value;
  const parsed = parseFloat(String(value));
  return Number.isFinite(parsed) ? parsed : 0;
};

const formatPercent = (value: number) => `${value.toFixed(2)}%`;

export default function SectorAllocationChart({ sectors, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="mt-6 p-6 rounded-xl bg-gray-50 border border-gray-200">
        <div className="h-64 flex items-center justify-center text-gray-600">Loading sector allocation...</div>
      </div>
    );
  }

  if (!Array.isArray(sectors) || sectors.length === 0) {
    return (
      <div className="mt-6 p-6 rounded-xl bg-gray-50 border border-gray-200 text-center text-gray-600">
        No sector allocation data available.
      </div>
    );
  }

  const chartData = sectors.map((sector) => ({
    name: sector.sector ?? "Unknown",
    value: safeNumber(sector.value),
    percentage: safeNumber(sector.percentage),
    holdings_count: safeNumber(sector.holdings_count),
  }));

  return (
    <div className="mt-6 rounded-xl bg-gray-50 border border-gray-200 p-6">
      <div className="mb-4 text-left">
        <h3 className="text-lg font-semibold text-black">Sector Allocation</h3>
        <p className="text-sm text-gray-600">Portfolio distribution by sector.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[320px_1fr]">
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                innerRadius={72}
                outerRadius={96}
                paddingAngle={2}
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: any) => [
                  `${safeNumber(value).toFixed(2)}`,
                  "Value",
                ]}
                cursor={{ fill: "rgba(0,0,0,0.05)" }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-3">
          {chartData.map((sector, index) => (
            <div
              key={`${sector.name}-${index}`}
              className="flex items-center justify-between rounded-2xl border border-gray-200 bg-white p-3"
            >
              <div className="flex items-center gap-3">
                <span
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <div>
                  <p className="text-sm font-semibold text-black">{sector.name}</p>
                  <p className="text-xs text-gray-500">{sector.holdings_count} holdings</p>
                </div>
              </div>

              <div className="text-right">
                <p className="text-sm font-semibold text-black">{formatPercent(sector.percentage)}</p>
                <p className="text-xs text-gray-500">Allocation</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
