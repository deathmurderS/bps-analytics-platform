"""Tests for the metadata transformer (SIMDASI + Glosarium)."""

import pandas as pd
import pytest

from src.transform.metadata import MetadataTransformer


class TestMetadataTransformer:
    """Test the metadata transformer."""

    def _make_simdasi_records(self):
        """Create sample SIMDASI records."""
        return [
            {
                "table_id": "1234",
                "table_code": "T-001",
                "title": "PDRB Atas Dasar Harga Konstan Menurut Provinsi",
                "subject": "Ekonomi",
                "unit": "Miliar Rupiah",
                "frequency": "Tahunan",
                "available_years": "2020,2021,2022",
            }
        ]

    def _make_glossary_records(self):
        """Create sample glossary records."""
        return [
            {
                "glossary_id": "1",
                "indicator_name": "PDRB Atas Dasar Harga Konstan",
                "concept": "Produk Domestik Regional Bruto",
                "definition": "Nilai tambah barang dan jasa dihitung dengan harga konstan",
                "classification": "Ekonomi",
                "measure": "Nilai",
                "unit": "Miliar Rupiah",
                "data_source": "BPS",
            }
        ]

    def test_build_dim_dataset(self):
        """Should build the dataset dimension from SIMDASI records."""
        transformer = MetadataTransformer()
        records = self._make_simdasi_records()
        dim_dataset = transformer.build_dim_dataset(records)

        assert len(dim_dataset) == 1
        assert dim_dataset.iloc[0]["dataset_key"] == 1
        assert dim_dataset.iloc[0]["table_id"] == "1234"
        assert dim_dataset.iloc[0]["table_code"] == "T-001"
        assert dim_dataset.iloc[0]["title"] == (
            "PDRB Atas Dasar Harga Konstan Menurut Provinsi"
        )
        assert dim_dataset.iloc[0]["subject"] == "Ekonomi"
        assert dim_dataset.iloc[0]["available_years"] == "2020,2021,2022"
        assert dim_dataset.iloc[0]["source_system"] == "BPS"

    def test_build_dim_dataset_empty(self):
        """Should handle empty SIMDASI records."""
        transformer = MetadataTransformer()
        dim_dataset = transformer.build_dim_dataset([])

        assert dim_dataset.empty

    def test_build_dim_glossary(self):
        """Should build the glossary dimension from glossary records."""
        transformer = MetadataTransformer()
        records = self._make_glossary_records()
        dim_glossary = transformer.build_dim_glossary(records)

        assert len(dim_glossary) == 1
        assert dim_glossary.iloc[0]["glossary_key"] == 1
        assert dim_glossary.iloc[0]["glossary_id"] == "1"
        assert dim_glossary.iloc[0]["indicator_name"] == (
            "PDRB Atas Dasar Harga Konstan"
        )
        assert dim_glossary.iloc[0]["concept"] == "Produk Domestik Regional Bruto"
        assert dim_glossary.iloc[0]["definition"] == (
            "Nilai tambah barang dan jasa dihitung dengan harga konstan"
        )
        assert dim_glossary.iloc[0]["classification"] == "Ekonomi"
        assert dim_glossary.iloc[0]["measure"] == "Nilai"
        assert dim_glossary.iloc[0]["unit"] == "Miliar Rupiah"
        assert dim_glossary.iloc[0]["data_source"] == "BPS"
        assert dim_glossary.iloc[0]["endpoint"] == "glosarium"

    def test_build_dim_glossary_empty(self):
        """Should handle empty glossary records."""
        transformer = MetadataTransformer()
        dim_glossary = transformer.build_dim_glossary([])

        assert dim_glossary.empty

    def test_enrich_indicator_with_glossary(self):
        """Should enrich dim_indicator with glossary definitions."""
        transformer = MetadataTransformer()

        # Create a dim_indicator DataFrame
        dim_indicator = pd.DataFrame(
            [
                {
                    "indicator_key": "145",
                    "indicator_code": "145",
                    "indicator_name": "PDRB Atas Dasar Harga Konstan",
                    "subject_name": "Ekonomi",
                    "category_name": None,
                    "unit": "Miliar Rupiah",
                    "frequency": "Tahunan",
                }
            ]
        )

        glossary_records = self._make_glossary_records()
        enriched = transformer.enrich_indicator_with_glossary(
            dim_indicator,
            glossary_records,
        )

        assert len(enriched) == 1
        assert enriched.iloc[0]["concept"] == "Produk Domestik Regional Bruto"
        assert enriched.iloc[0]["definition"] == (
            "Nilai tambah barang dan jasa dihitung dengan harga konstan"
        )
        assert enriched.iloc[0]["classification"] == "Ekonomi"
        assert enriched.iloc[0]["measure"] == "Nilai"
        assert enriched.iloc[0]["data_source"] == "BPS"

    def test_enrich_indicator_no_match(self):
        """Should leave enrichment columns as None when no match."""
        transformer = MetadataTransformer()

        dim_indicator = pd.DataFrame(
            [
                {
                    "indicator_key": "999",
                    "indicator_code": "999",
                    "indicator_name": "Unknown Indicator",
                    "subject_name": None,
                    "category_name": None,
                    "unit": None,
                    "frequency": None,
                }
            ]
        )

        glossary_records = self._make_glossary_records()
        enriched = transformer.enrich_indicator_with_glossary(
            dim_indicator,
            glossary_records,
        )

        assert len(enriched) == 1
        assert enriched.iloc[0]["concept"] is None
        assert enriched.iloc[0]["definition"] is None
        assert enriched.iloc[0]["classification"] is None
        assert enriched.iloc[0]["measure"] is None
        assert enriched.iloc[0]["data_source"] is None

    def test_enrich_indicator_case_insensitive(self):
        """Should match indicator names case-insensitively."""
        transformer = MetadataTransformer()

        dim_indicator = pd.DataFrame(
            [
                {
                    "indicator_key": "145",
                    "indicator_code": "145",
                    "indicator_name": "pdrb atas dasar harga konstan",
                    "subject_name": None,
                    "category_name": None,
                    "unit": None,
                    "frequency": None,
                }
            ]
        )

        glossary_records = self._make_glossary_records()
        enriched = transformer.enrich_indicator_with_glossary(
            dim_indicator,
            glossary_records,
        )

        assert enriched.iloc[0]["concept"] == "Produk Domestik Regional Bruto"