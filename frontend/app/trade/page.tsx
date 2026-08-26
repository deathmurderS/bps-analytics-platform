import ComingSoon from "@/components/states/ComingSoon";

export default function TradePage() {
  return (
    <ComingSoon
      title="Analisis Perdagangan"
      description="Tren ekspor-impor, komoditas unggulan, mitra dagang, dan neraca perdagangan."
      items={[
        "Tren Ekspor & Impor",
        "Komoditas Unggulan",
        "Mitra Dagang & Neraca",
        "Kinerja Pelabuhan / Wilayah",
      ]}
    />
  );
}