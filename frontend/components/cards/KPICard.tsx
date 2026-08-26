import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { AnimatedNumber, FadeIn } from "@/components/motion/Motion";

export interface KPICardData {
  key: string;
  title: string;
  value: number | null;
  unit?: string;
  yoy?: number | null;
  period?: string;
  footnote?: string;
  status?: "available" | "unavailable";
}

interface KPICardProps {
  data: KPICardData;
}

export default function KPICard({ data }: KPICardProps) {
  const { title, value, unit, yoy, period, footnote, status } = data;
  const positive =
    yoy !== null && yoy !== undefined && yoy >= 0;
  const isUnavailable = status === "unavailable" || value === null;

  return (
    <FadeIn className="h-full">
      <div className="card flex h-full flex-col gap-3 p-5 transition-colors hover:border-line-strong">
      <div className="flex items-start justify-between gap-2">
        <p className="text-body-sm font-medium text-ink-muted">{title}</p>
        {!isUnavailable && yoy !== null && yoy !== undefined && (
          <span
            className={`inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[11px] font-semibold ${
              positive
                ? "bg-emerald-50 text-semantic-success"
                : "bg-rose-50 text-semantic-danger"
            }`}
          >
            {positive ? (
              <ArrowUpRight className="h-3 w-3" />
            ) : (
              <ArrowDownRight className="h-3 w-3" />
            )}
            {Math.abs(yoy).toFixed(1)}%
          </span>
        )}
      </div>

      <div>
        {isUnavailable ? (
          <div className="flex flex-col gap-1">
            <span className="text-display-md font-semibold text-ink-faint">—</span>
            <span className="text-[11px] text-ink-muted font-medium">Nasional tidak tersedia (non-additive)</span>
          </div>
        ) : (
          <>
            <AnimatedNumber
              value={value}
              className="font-mono text-display-lg font-bold text-ink tabular-nums"
            />
            {unit && <p className="mt-0.5 text-body-sm text-ink-soft">{unit}</p>}
          </>
        )}
      </div>

      {(period || footnote) && (
        <div className="mt-auto flex items-center justify-between border-t border-line pt-3">
          {period && (
            <span className="text-body-sm text-ink-muted">{period}</span>
          )}
          {footnote && (
            <span className="text-body-sm text-ink-soft">{footnote}</span>
          )}
        </div>
      )}
      </div>
    </FadeIn>
  );
}
