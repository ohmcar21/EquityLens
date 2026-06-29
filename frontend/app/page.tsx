"use client";

import { useEffect, useState, useRef } from "react";
import HoldingsTable from "../components/HoldingsTable";
import SectorAllocationChart from "../components/SectorAllocationChart";
import HealthBreakdown from "../components/HealthBreakdown";
import DiversificationAnalysis from "../components/DiversificationAnalysis";
import AIInsights from "../components/AIInsights"; 
import HistoricalComparison from "../components/HistoricalComparison";


export default function Home() {
  const [health, setHealth] = useState<any>(null);
  const [diversification, setDiversification] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const [sectorAllocation, setSectorAllocation] = useState<any>(null);
  const [sectorLoading, setSectorLoading] = useState<boolean>(false);
  const [sectorError, setSectorError] = useState<string | null>(null);

  const [comparison, setComparison] = useState<any>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Extract fetch functions for reuse
  const fetchHealth = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/analytics/health");
      const data = await res.json();
      setHealth(data);
    } catch (err) {
      console.error("Failed to fetch health:", err);
    }
  };

  const fetchDiversification = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/analytics/diversification");
      const data = await res.json();
      setDiversification(data);
    } catch (err) {
      console.error("Failed to fetch diversification:", err);
    }
  };

  const fetchSectorAllocation = async () => {
    try {
      setSectorLoading(true);
      const res = await fetch("http://127.0.0.1:8000/api/v1/analytics/sector-allocation");
      const data = await res.json();
      setSectorAllocation(data);
      setSectorError(null);
    } catch (err) {
      console.error("Failed to fetch sector allocation:", err);
      setSectorError(err instanceof Error ? err.message : "Failed to load sector allocation");
    } finally {
      setSectorLoading(false);
    }
  };

  const fetchComparison = async () => {
    try {
      const res = await fetch(
        "http://127.0.0.1:8000/api/v1/analytics/history/compare"
      );

      const data = await res.json();
      setComparison(data);
    } catch (err) {
      console.error("Failed to fetch comparison:", err);
    }
  };

  const fetchHoldings = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/portfolio/holdings");
      const data = await res.json();
      setSummary(data);
    } catch (err) {
      console.error("Failed to fetch holdings:", err);
    }
  };

  // Handle file upload - takes file as parameter, not from state
  const handleUpload = async (file: File) => {
    try {
      setUploading(true);

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/portfolio/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();
      console.log("Upload Success:", data);

      // Update selected file state after successful upload
      setSelectedFile(file);

      // Refresh all dashboard data
      await fetchHoldings();
      await fetchHealth();
      await fetchDiversification();
      await fetchSectorAllocation();
      await fetchComparison();

    } catch (error) {
      console.error("Upload Error:", error);
      alert(`Upload failed: ${error instanceof Error ? error.message : "Unknown error"}`);
      setSelectedFile(null);
    } finally {
      setUploading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    fetchDiversification();
    fetchSectorAllocation();
    fetchHoldings();
    fetchComparison();
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

        <div className="flex justify-center mb-4">
         <button
            onClick={() => fileInputRef.current?.click()}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg"
          >
            {uploading
              ? "Uploading..."
              : selectedFile
              ? "Analyze Portfolio"
              : "Upload Portfolio"}
          </button>
 <input
  ref={fileInputRef}
  type="file"
  accept=".csv,.xlsx"
  className="hidden"
  onChange={(e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleUpload(file);
    }
  }}
/>
      </div>

{selectedFile && (
  <p className="text-sm text-gray-600 mb-4">
    Selected: {selectedFile.name}
  </p>
)}

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

        <HistoricalComparison data={comparison} />
        <HoldingsTable holdings={summary?.holdings ?? []} />
        <AIInsights />
      </div>
    </main>
  );
}
