"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { IndicatorListResponse, IndicatorMetadata } from "@/types";

export default function MetadataPage() {
  const [indicators, setIndicators] = useState<IndicatorListResponse | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<IndicatorMetadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getIndicators()
      .then(setIndicators)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selected) return;
    api
      .getIndicatorMetadata(selected)
      .then(setMetadata)
      .catch((err) => setError(err.message));
  }, [selected]);

  if (loading) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Metadata Explorer</h1>
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

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Metadata Explorer</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Indikator</h2>
          {indicators && indicators.indicators.length > 0 ? (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {indicators.indicators.map((ind) => (
                <button
                  key={ind.indicator_key}
                  onClick={() => setSelected(ind.indicator_key)}
                  className={`w-full text-left px-3 py-2 rounded text-sm ${
                    selected === ind.indicator_key
                      ? "bg-blue-50 text-blue-700"
                      : "hover:bg-gray-50"
                  }`}
                >
                  {ind.indicator_name}
                </button>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">Tidak ada indikator.</p>
          )}
        </div>

        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Detail Metadata</h2>
          {metadata ? (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-500">Nama Indikator</h3>
                <p className="text-lg font-semibold">{metadata.indicator_name}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Kode</h3>
                  <p>{metadata.indicator_code}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Unit</h3>
                  <p>{metadata.unit || "N/A"}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Frekuensi</h3>
                  <p>{metadata.frequency || "N/A"}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Subjek</h3>
                  <p>{metadata.subject_name || "N/A"}</p>
                </div>
              </div>
              {metadata.definition && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Definisi</h3>
                  <p className="text-sm">{metadata.definition}</p>
                </div>
              )}
              {metadata.concept && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Konsep</h3>
                  <p className="text-sm">{metadata.concept}</p>
                </div>
              )}
              {metadata.classification && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Klasifikasi</h3>
                  <p className="text-sm">{metadata.classification}</p>
                </div>
              )}
              {metadata.measure && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Ukuran</h3>
                  <p className="text-sm">{metadata.measure}</p>
                </div>
              )}
              {metadata.data_source && (
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Sumber Data</h3>
                  <p className="text-sm">{metadata.data_source}</p>
                </div>
              )}
              <div>
                <h3 className="text-sm font-medium text-gray-500">Metode Agregasi</h3>
                <p className="text-sm">{metadata.aggregation_method || "N/A"}</p>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">
              Pilih indikator untuk melihat detail metadata.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}