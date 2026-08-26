import { Lightbulb, Sparkles } from "lucide-react";
import { FadeIn } from "@/components/motion/Motion";

export interface Insight {
  id: string;
  title: string;
  description: string;
  category: string;
  direction: "up" | "down" | "neutral";
  value: string;
}

interface InsightCardProps {
  insight: Insight;
}

export default function InsightCard({ insight }: InsightCardProps) {
  const directionColor =
    insight.direction === "up"
      ? "text-semantic-success"
      : insight.direction === "down"
        ? "text-semantic-danger"
        : "text-ink-muted";

  return (
    <FadeIn className="h-full">
      <div className="flex h-full gap-3 rounded-lg border border-line bg-white p-4 transition-colors hover:border-line-strong">
      <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded bg-primary-50 text-primary">
        <Lightbulb className="h-4 w-4" />
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <p className="label-caps text-ink-muted">{insight.category}</p>
          <span className={`data-tabular font-semibold ${directionColor}`}>
            {insight.value}
          </span>
        </div>
        <h4 className="mt-1 text-body-md font-semibold text-ink">
          {insight.title}
        </h4>
        <p className="mt-0.5 text-body-sm leading-5 text-ink-soft">
          {insight.description}
        </p>
      </div>
      </div>
    </FadeIn>
  );
}

export function InsightHeader() {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-primary" />
        <h2 className="text-headline-sm text-ink">Insight Otomatis</h2>
      </div>
      <span className="text-body-sm text-ink-muted">Diperbarui harian</span>
    </div>
  );
}