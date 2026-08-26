import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { FadeIn } from "@/components/motion/Motion";

export interface RegionalRow {
  rank: number;
  region_name: string;
  value: number;
  growth_pct: number | null;
  year: number;
}

interface RegionalPerformanceTableProps {
  rows: RegionalRow[];
  unit?: string | null;
  title?: string;
  subtitle?: string;
}

export default function RegionalPerformanceTable({
  rows,
  unit,
  title = "Kinerja Regional",
  subtitle = "Peringkat tahun berjalan",
}: RegionalPerformanceTableProps) {
  return (
    <FadeIn className="h-full">
      <div className="card flex h-full flex-col">
        <div className="card-header">
          <h3 className="text-headline-sm text-ink">{title}</h3>
          <span className="text-body-sm text-ink-muted">{subtitle}</span>
        </div>
        <div className="flex-1 overflow-x-auto">
          <table className="min-w-full divide-y divide-line">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-5 py-2.5 text-left label-caps">Rank</th>
                <th className="px-5 py-2.5 text-left label-caps">Provinsi</th>
                <th className="px-5 py-2.5 text-right label-caps">Nilai</th>
                <th className="px-5 py-2.5 text-right label-caps">
                  Pertumbuhan YoY
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {rows.slice(0, 8).map((row) => (
                <tr
                  key={row.region_name}
                  className="transition-colors hover:bg-slate-50/60"
                >
                  <td className="px-5 py-2.5">
                    <span
                      className={`inline-flex h-6 w-6 items-center justify-center rounded text-[11px] font-semibold ${
                        row.rank <= 3
                          ? "bg-primary-50 text-primary"
                          : "text-ink-muted"
                      }`}
                    >
                      {row.rank}
                    </span>
                  </td>
                  <td className="px-5 py-2.5 text-body-md font-medium text-ink">
                    {row.region_name}
                  </td>
                  <td className="px-5 py-2.5 text-right data-tabular text-ink">
                    {row.value.toLocaleString("id-ID", {
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 2,
                    })}
                    {unit ? <span className="ml-1 text-[11px] text-ink-muted">{unit}</span> : null}
                  </td>
                  <td className="px-5 py-2.5 text-right">
                    {row.growth_pct !== null ? (
                      <span
                        className={
                          row.growth_pct >= 0
                            ? "yoy-positive"
                            : "yoy-negative"
                        }
                      >
                        {row.growth_pct >= 0 ? (
                          <ArrowUpRight className="h-3.5 w-3.5" />
                        ) : (
                          <ArrowDownRight className="h-3.5 w-3.5" />
                        )}
                        {row.growth_pct >= 0 ? "+" : ""}
                        {row.growth_pct.toFixed(2)}%
                      </span>
                    ) : (
                      <span className="text-ink-faint">N/A</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </FadeIn>
  );
}