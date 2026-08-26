"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatCompact } from "@/lib/utils";

export interface TrendDatum {
  year: number;
  value: number;
}

interface EconomicTrendChartProps {
  data: TrendDatum[];
  height?: number;
  unit?: string;
}

const axisStyle = {
  fontSize: 11,
  fill: "#64748B",
  fontFamily: "var(--font-inter), sans-serif",
};

const tooltipStyle = {
  backgroundColor: "#0F172A",
  border: "none",
  borderRadius: 6,
  fontSize: 12,
  color: "#E2E8F0",
  padding: "8px 12px",
};

export default function EconomicTrendChart({
  data,
  height = 320,
  unit = "",
}: EconomicTrendChartProps) {
  const formatValue = (v: number) =>
    `${v.toLocaleString("id-ID")}${unit ? ` ${unit}` : ""}`;

  return (
    <div className="chart-body">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 8 }}>
          <CartesianGrid stroke="#E2E8F0" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="year"
            tick={axisStyle}
            tickLine={false}
            axisLine={{ stroke: "#CBD5E1" }}
          />
          <YAxis
            tick={axisStyle}
            tickLine={false}
            axisLine={false}
            width={80}
            tickFormatter={formatCompact}
          />
          <Tooltip
            formatter={(value: number | string) => [
              formatValue(Number(value)),
              "Nilai",
            ]}
            labelFormatter={(label) => `Tahun ${label}`}
            contentStyle={tooltipStyle}
            labelStyle={{ color: "#94A3B8", marginBottom: 4 }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#0284C7"
            strokeWidth={2}
            dot={{ r: 3, fill: "#0284C7", strokeWidth: 0 }}
            activeDot={{ r: 5, fill: "#0369A1" }}
            name="Nilai Nasional"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}