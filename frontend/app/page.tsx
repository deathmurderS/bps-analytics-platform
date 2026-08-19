"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { OverviewResponse } from "@/types";

export default function OverviewPage() {
  const [data, setData] = useState<OverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getOverview()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Overview</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-8 bg-gray-200 rounded"></div>
            </div>
          ))}
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

  if (!data || data.indicators.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h1 className="text-xl font-bold text-yellow-700 mb-2">Data Tidak Tersedia</h1>
        <p className="text-yellow-600">
          Belum ada data ekonomi yang dimuat. Jalankan ETL pipeline terlebih dahulu.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Overview Ekonomi</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {data.indicators.map((ind) => (
          <div key={ind.indicator_key} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              {ind.indicator_name}
            </h3>
            <p className="text-2xl font-bold text-gray-900">
              {ind.current_value !== null
                ? ind.current_value.toLocaleString("id-ID")
                : "N/A"}
              {ind.unit ? ` ${ind.unit}` : ""}
            </p>
            <div className="mt-2 text-sm">
              {ind.yoy_growth !== null && (
                <span
                  className={
                    ind.yoy_growth >= 0
                      ? "text-green-600"
                      : "text-red-600"
                  }
                >
                  {ind.yoy_growth >= 0 ? "▲" : "▼"} {Math.abs(ind.yoy_growth).toFixed(2)}%
                </span>
              )}
              <span className="text-gray-500 ml-2">
                Tahun {ind.latest_year}
              </span>
            </div>
            <div className="mt-2 text-xs text-gray-500">
              {ind.region_count} region · {ind.years_available} tahun data
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Ringkasan</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                  Indikator
                </th>
                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                  Nilai Terbaru
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
              {data.indicators.map((ind) => (
                <tr key={ind.indicator_key}>
                  <td className="px-4 py-2 text-sm">{ind.indicator_name}</td>
                  <td className="px-4 py-2 text-sm text-right">
                    {ind.current_value !== null
                      ? ind.current_value.toLocaleString("id-ID")
                      : "N/A"}
                  </td>
                  <td className="px-4 py-2 text-sm text-right">
                    {ind.yoy_growth !== null
                      ? `${ind.yoy_growth >= 0 ? "+" : ""}${ind.yoy_growth.toFixed(2)}%`
                      : "N/A"}
                  </td>
                  <td className="px-4 py-2 text-sm text-right">{ind.latest_year}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}