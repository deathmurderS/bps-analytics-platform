import { Construction } from "lucide-react";

interface ComingSoonProps {
  title: string;
  description: string;
  items?: string[];
}

export default function ComingSoon({
  title,
  description,
  items = [],
}: ComingSoonProps) {
  return (
    <div className="space-y-section-gap">
      {/* Page header */}
      <div>
        <h1 className="text-headline-md text-ink">{title}</h1>
        <p className="mt-1 text-body-md text-ink-soft">{description}</p>
      </div>

      {/* Placeholder card */}
      <div className="card flex flex-col items-center justify-center gap-4 px-6 py-16 text-center">
        <span className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-50 text-primary">
          <Construction className="h-6 w-6" strokeWidth={1.75} />
        </span>
        <div>
          <p className="text-headline-sm text-ink">Halaman Segera Hadir</p>
          <p className="mx-auto mt-1 max-w-md text-body-sm leading-5 text-ink-soft">
            Halaman ini sedang diimplementasikan sesuai desain Stitch dan akan
            terhubung ke data BPS melalui FastAPI setelah integrasi backend
            selesai.
          </p>
        </div>

        {items.length > 0 && (
          <div className="mt-2 flex flex-wrap items-center justify-center gap-2">
            {items.map((item) => (
              <span
                key={item}
                className="inline-flex items-center gap-1.5 rounded border border-line bg-slate-50 px-2.5 py-1 text-[11px] font-medium text-ink-soft"
              >
                <span className="h-1 w-1 rounded-full bg-primary" />
                {item}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}