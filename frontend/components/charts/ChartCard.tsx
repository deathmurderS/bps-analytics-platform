import { Download } from "lucide-react";
import { FadeIn } from "@/components/motion/Motion";

interface ChartCardProps {
  title: string;
  subtitle?: string;
  timeRange?: string;
  children: React.ReactNode;
  className?: string;
}

export default function ChartCard({
  title,
  subtitle,
  timeRange = "2020 - 2024",
  children,
  className = "",
}: ChartCardProps) {
  return (
    <FadeIn className="h-full">
      <div className={`card flex h-full flex-col ${className}`}>
        <div className="card-header">
          <div>
            <h3 className="text-headline-sm text-ink">{title}</h3>
            {subtitle && (
              <p className="mt-0.5 text-body-sm text-ink-muted">{subtitle}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden items-center rounded border border-line bg-white px-2 py-1 text-[11px] font-medium text-ink-soft sm:inline-flex">
              {timeRange}
            </span>
            <button
              className="btn-ghost"
              title="Unduh / Ekspor"
              aria-label={`Unduh ${title}`}
            >
              <Download className="h-4 w-4" />
            </button>
          </div>
        </div>
        <div className="flex-1">{children}</div>
      </div>
    </FadeIn>
  );
}
