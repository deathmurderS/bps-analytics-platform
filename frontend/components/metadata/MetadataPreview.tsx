import { BookOpenText, ChevronRight } from "lucide-react";
import Link from "next/link";

export interface MetadataItem {
  indicator_key: string;
  indicator_name: string;
  indicator_code: string;
  subject_name?: string | null;
  unit: string | null;
  frequency: string | null;
  data_source: string | null;
}

interface MetadataPreviewProps {
  items: MetadataItem[];
}

export default function MetadataPreview({ items }: MetadataPreviewProps) {
  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-2">
          <BookOpenText className="h-4 w-4 text-primary" />
          <h3 className="text-headline-sm text-ink">Metadata Indikator</h3>
        </div>
        <Link
          href="/metadata"
          className="btn-ghost inline-flex items-center gap-0.5 text-xs"
        >
          Lihat semua <ChevronRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      <div className="divide-y divide-line">
        {items.slice(0, 5).map((item) => (
          <div
            key={item.indicator_key}
            className="flex items-center justify-between gap-4 px-5 py-3"
          >
            <div className="min-w-0">
              <p className="truncate text-body-md font-medium text-ink">
                {item.indicator_name}
              </p>
              <p className="mt-0.5 flex items-center gap-2 text-[11px] text-ink-muted">
                <span className="font-mono">{item.indicator_code}</span>
                {item.unit && (
                  <>
                    <span className="text-line-strong">•</span>
                    <span>{item.unit}</span>
                  </>
                )}
                {item.frequency && (
                  <>
                    <span className="text-line-strong">•</span>
                    <span>{item.frequency}</span>
                  </>
                )}
                {item.subject_name && (
                  <>
                    <span className="text-line-strong">•</span>
                    <span>{item.subject_name}</span>
                  </>
                )}
              </p>
            </div>
            <Link
              href={`/metadata?indicator=${item.indicator_key}`}
              className="shrink-0 rounded p-1.5 text-ink-faint transition-colors hover:bg-slate-100 hover:text-primary"
              aria-label={`Detail ${item.indicator_name}`}
            >
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}