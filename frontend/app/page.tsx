"use client";

import { useEffect, useState } from "react";
import HoldingsTable from "../components/HoldingsTable";
import SectorAllocationChart from "../components/SectorAllocationChart";
import HealthBreakdown from "../components/HealthBreakdown";
import DiversificationAnalysis from "../components/DiversificationAnalysis";
import AIInsights from "../components/AIInsights";


export default function Home() {
  const [health, setHealth] = useState<any>(null);
  const [diversification, setDiversification] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [sectorAllocation, setSectorAllocation] = useState<any>(null);
  const [sectorLoading, setSectorLoading] = useState<boolean>(false);
  const [sectorError, setSectorError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/v1/analytics/health")
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch((err) => console.error(err));

    setSectorLoading(true);
    fetch("http://127.0.0.1:8000/api/v1/analytics/sector-allocation")
      .then((res) => res.json())
      .then((data) => setSectorAllocation(data))
      .catch((err) => {
        console.error(err);
        setSectorError(err.message || "Failed to load sector allocation");
      })
      .finally(() => setSectorLoading(false));

    fetch("http://127.0.0.1:8000/api/v1/portfolio/holdings")
      .then((res) => res.json())
      .then((data) => setSummary(data))
      .catch((err) => console.error(err));

    fetch("http://127.0.0.1:8000/api/v1/analytics/diversification")
      .then((res) => res.json())
      .then((data) => setDiversification(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-100">
      <div className="text-center mb-8">
  <h1 className="text-4xl font-bold text-black">
    EquityLens
  </h1>

  <p className="text-gray-600 mt-2">
    AI-Powered Portfolio Intelligence Platform
  </p>
</div>

      <div className="bg-white p-8 rounded-xl shadow-md text-center min-w-[400px]">
        <h2 className="text-2xl font-semibold mb-4 text-black">
          Portfolio Dashboard
        </h2>

        {summary && (
  <div className="grid grid-cols-2 gap-4 mb-6">
    <div className="bg-green-100 p-4 rounded-lg">
      <p className="text-sm text-gray-600">Portfolio Value</p>
      <p className="text-xl font-bold text-black">
        ₹{summary.total_current_value}
      </p>
    </div>

    <div className="bg-blue-100 p-4 rounded-lg">
      <p className="text-sm text-black">Invested Value</p>
      <p className="text-xl font-bold text-black">
        ₹{summary.total_invested}
      </p>
    </div>

    <div className="bg-yellow-100 p-4 rounded-lg">
      <p className="text-sm text-black">PnL</p>
      <p className="text-sm text-black">
        ₹{summary.total_pnl}
      </p>
    </div>

    <div className="bg-purple-100 p-4 rounded-lg">
      <p className="text-sm text-black">Health Score</p>
      <p className="text-sm text-black">
        {health?.overall_score}
      </p>
    </div>
  </div>
)}

        {health ? (
          <>
            <p className="text-3xl font-bold text-green-600">
              Score: {health.overall_score}
            </p>

            <p className="text-xl mt-2 text-black">
              Grade: {health.grade}
            </p>

            <p className="text-lg mt-2 text-black">
              Status: {health.status}
            </p>

            {summary && (
              <>
                <p className="text-black mt-4">
                  Holdings Count: {summary.holdings_count}
                </p>

                <p className="text-black">
                  Total PnL: ₹{summary.total_pnl}
                </p>
              </>
            )}
          </>
        ) : (
          <p>Loading...</p>
        )}

        <HealthBreakdown health={health} />

        <DiversificationAnalysis diversification={diversification} />

        <SectorAllocationChart
          sectors={sectorAllocation?.sectors ?? []}
          isLoading={sectorLoading}
        />

        {/* Holdings Table placed below the summary */}
        <HoldingsTable holdings={summary?.holdings ?? []} />
        <AIInsights />
      </div>
    </main>
  );
}