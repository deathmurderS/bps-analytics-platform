"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { RegionalResponse } from "@/types";

export default function RegionalPage() {
  const [data, setData] = useState<RegionalResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getRegionalRanking(undefined, undefined, 50)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Analisis Regional</h1>
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

  if (!data || data.data.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h1 className="text-xl font-bold text-yellow-700 mb-2">Data Tidak Tersedia</h1>
        <p className="text-yellow-600">Belum ada data regional.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Analisis Regional</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Peringkat Regional</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Rank
                </th>
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
              {data.data.map((row, idx) => (
                <tr key={idx} className={row.regional_rank <= 3 ? "bg-blue-50" : ""}>
                  <td className="px-4 py-2 text-sm font-medium">
                    {row.regional_rank}
                  </td>
                  <td className="px-4 py-2 text-sm">{row.region_name}</td>
                  <td className="px-4 py-2 text-sm text-right">
                    {row.value.toLocaleString("id-ID")}
                  </td>
                  <td className="px-4 py-2 text-sm text-right">
                    {row.growth_pct !== null ? (
                      <span
                        className={
                          row.growth_pct >= 0 ? "text-green-600" : "text-red-600"
                        }
                      >
                        {row.growth_pct >= 0 ? "+" : ""}
                        {row.growth_pct.toFixed(2)}%
                      </span>
                    ) : (
                      "N/A"
                    )}
                  </td>
                  <td className="px-4 py-2 text-sm text-right">{row.year}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}