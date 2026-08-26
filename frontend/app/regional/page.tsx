import ComingSoon from "@/components/states/ComingSoon";

export default function RegionalPage() {
  return (
    <ComingSoon
      title="Analisis Regional"
      description="Peringkat kinerja, pertumbuhan, dan perbandingan antarprovinsi."
      items={["Peringkat Regional", "Pertumbuhan", "Perbandingan Antarwilayah"]}
    />
  );
}