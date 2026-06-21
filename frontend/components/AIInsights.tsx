"use client";

import { useState } from "react";

interface ReportSection {
  title: string;
  content: string;
  icon: string;
}

const parseReportSections = (report: string): ReportSection[] => {
  const sectionConfig = [
    { title: "Executive Summary", icon: "📋" },
    { title: "Portfolio Health", icon: "💚" },
    { title: "Diversification Analysis", icon: "📊" },
    { title: "Sector Exposure Analysis", icon: "🏢" },
    { title: "Strengths", icon: "⭐" },
    { title: "Risks", icon: "⚠️" },
    { title: "Portfolio Intelligence Summary", icon: "🎯" },
  ];

  const sections: ReportSection[] = [];

  // Create pattern that matches any section header (case-insensitive)
  const sectionHeaders = sectionConfig.map((s) => s.title).join("|");
  const splitRegex = new RegExp(`(${sectionHeaders})[:\\s]*`, "gi");

  // Split report by section headers while keeping the headers
  const parts = report.split(splitRegex);

  // Process pairs: [header, content, header, content, ...]
  for (let i = 1; i < parts.length; i += 2) {
    const headerText = parts[i];
    const content = parts[i + 1];

    if (headerText && content) {
      const config = sectionConfig.find((s) =>
        headerText.toLowerCase().includes(s.title.toLowerCase())
      );
      const cleanContent = content
        .trim()
        .split("\n")
        .filter((line) => line.trim() !== "")
        .join("\n");

      if (config && cleanContent) {
        sections.push({
          title: config.title,
          content: cleanContent,
          icon: config.icon,
        });
      }
    }
  }

  return sections;
};

export default function AIInsights() {
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generateReport = async () => {
    try {
      setLoading(true);
      setError("");
      setReport(""); // Clear previous report

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/ai/report",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log("API Response:", data); // Debug log

      const reportText =
        data.report ||
        data.ai_report ||
        data.content ||
        JSON.stringify(data, null, 2);

      if (!reportText || reportText.trim() === "") {
        throw new Error("Empty report received from backend");
      }

      setReport(reportText);
    } catch (err: any) {
      console.error("Report generation error:", err);
      setError(err.message || "Failed to generate AI report");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8 bg-white p-6 rounded-xl shadow-md border">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold text-black">
          AI Portfolio Insights
        </h2>

        <button
          onClick={generateReport}
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
        >
          {loading ? "Generating..." : "Generate Report"}
        </button>
      </div>

      {error && (
        <div className="text-red-600 mb-4">
          {error}
        </div>
      )}

      {!report && !loading && (
        <p className="text-gray-600">
          Click "Generate Report" to get AI-powered portfolio insights.
        </p>
      )}

      {report && (
        <div className="space-y-4">
          {parseReportSections(report).map((section, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-indigo-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start gap-3 mb-3">
                <span className="text-2xl">{section.icon}</span>
                <h3 className="text-lg font-semibold text-indigo-900">
                  {section.title}
                </h3>
              </div>
              <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                {section.content}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}