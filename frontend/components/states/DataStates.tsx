import { AlertTriangle, Inbox, Loader2 } from "lucide-react";

export function LoadingState({ label = "Memuat data..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-line bg-white px-6 py-12">
      <Loader2 className="h-6 w-6 animate-spin text-primary" />
      <p className="text-body-sm text-ink-muted">{label}</p>
    </div>
  );
}

export function EmptyState({
  title = "Data Tidak Tersedia",
  description = "Belum ada data untuk ditampilkan. Jalankan ETL pipeline terlebih dahulu.",
}: {
  title?: string;
  description?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-line bg-white px-6 py-12 text-center">
      <Inbox className="h-8 w-8 text-ink-faint" />
      <p className="text-body-md font-semibold text-ink">{title}</p>
      <p className="max-w-sm text-body-sm text-ink-muted">{description}</p>
    </div>
  );
}

export function ErrorState({
  message = "Terjadi kesalahan saat memuat data.",
}: {
  message?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-6 py-12 text-center">
      <AlertTriangle className="h-8 w-8 text-semantic-danger" />
      <p className="text-body-md font-semibold text-rose-700">Error</p>
      <p className="max-w-sm text-body-sm text-rose-600">{message}</p>
    </div>
  );
}