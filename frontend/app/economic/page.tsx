import ComingSoon from "@/components/states/ComingSoon";

export default function EconomicPage() {
  return (
    <ComingSoon
      title="Analisis Ekonomi"
      description="Tren indikator ekonomi makro, perbandingan regional, dan analisis pertumbuhan."
      items={["Tren Ekonomi", "Kinerja Regional", "Perbandingan Pertumbuhan"]}
    />
  );
}