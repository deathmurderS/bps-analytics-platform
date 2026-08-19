"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { api } from "@/lib/api";
import type { EconomicTrendResponse, RegionalResponse } from "@/types";

export default function EconomicPage() {
  const [trendData, setTrendData] = useState<EconomicTrendResponse | null>(null);
  const [regionalData, setRegionalData] = useState<RegionalResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.getEconomicTrend(), api.getEconomicRegional()])
      .then(([trend, regional]) => {
        setTrendData(trend);
        setRegionalData(regional);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Analisis Ekonomi</h1>
        <div className="bg-white rounded-lg shadow p-6 animate-pulse">
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h1 className="text-xl font-bold text-red-700 mb-2">Error</h1>
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  const chartData = trendData?.data.map((d) => ({
    year: d.year,
    value: d.national_value,
    growth: d.growth_pct,
  }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Analisis Ekonomi</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Tren Nasional</h2>
        {chartData && chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                name="Nilai Nasional"
                stroke="#2563eb"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-500">Tidak ada data tren.</p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Perbandingan Regional</h2>
        {regionalData && regionalData.data.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Region
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                    Nilai
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                    Pertumbuhan
                  </th>
                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                    Tahun
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {regionalData.data.slice(0, 20).map((row, idx) => (
                  <tr key={idx}>
                    <td className="px-4 py-2 text-sm">{row.region_name}</td>
                    <td className="px-4 py-2 text-sm text-right">
                      {row.value.toLocaleString("id-ID")}
                    </td>
                    <td className="px-4 py-2 text-sm text-right">
                      {row.growth_pct !== null
                        ? `${row.growth_pct >= 0 ? "+" : ""}${row.growth_pct.toFixed(2)}%`
                        : "N/A"}
                    </td>
                    <td className="px-4 py-2 text-sm text-right">{row.year}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">Tidak ada data regional.</p>
        )}
      </div>
    </div>
  );
}