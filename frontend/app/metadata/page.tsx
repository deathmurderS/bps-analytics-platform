import ComingSoon from "@/components/states/ComingSoon";

export default function MetadataPage() {
  return (
    <ComingSoon
      title="Metadata Indikator"
      description="Definisi, konsep, unit, frekuensi, sumber data, dan metadata teknis terkait."
      items={[
        "Definisi & Konsep Indikator",
        "Unit & Frekuensi",
        "Sumber Data & Status Metadata",
        "Dataset BPS terkait",
      ]}
    />
  );
}