"""Tests for the BPS API extractor modules."""

import pytest

from src.extract.bps_api import BPSAPIClient, BPSAPIError
from src.extract.domain import DomainExtractor
from src.extract.dynamic_data import DynamicDataExtractor
from src.extract.glossary import GlossaryExtractor
from src.extract.simdasi import SIMDASIExtractor


class TestBPSAPIClient:
    """Test the base API client."""

    def test_init_requires_api_key(self, monkeypatch):
        """Client should raise error if no API key is provided."""
        monkeypatch.setenv("BPS_API_KEY", "")
        with pytest.raises(ValueError, match="API key"):
            BPSAPIClient(api_key="")

    def test_init_with_api_key(self):
        """Client should initialize with a provided API key."""
        client = BPSAPIClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://webapi.bps.go.id/v1/api"


class TestDomainExtractor:
    """Test the domain extractor."""

    def test_parse_domain_list(self):
        """Should parse domain response into region records."""
        response = {
            "status": "200",
            "data": [
                {"kode": "1100", "nama": "ACEH"},
                {"kode": "1200", "nama": "SUMATERA UTARA"},
            ],
        }
        extractor = DomainExtractor(client=None)  # type: ignore
        records = extractor.parse_domain_list(response)

        assert len(records) == 2
        assert records[0] == {
            "region_code": "1100",
            "region_name": "ACEH",
        }
        assert records[1] == {
            "region_code": "1200",
            "region_name": "SUMATERA UTARA",
        }

    def test_parse_domain_list_empty(self):
        """Should handle empty data."""
        extractor = DomainExtractor(client=None)  # type: ignore
        records = extractor.parse_domain_list({"data": []})
        assert records == []


class TestDynamicDataExtractor:
    """Test the dynamic data extractor."""

    def test_parse_variables(self):
        """Should parse variable definitions."""
        response = {
            "variable": [
                {"id": "145", "label": "PDRB", "description": "PDRB ADHK"},
                {"id": "146", "label": "PDRB Per Kapita", "description": "PDRB per kapita"},
            ]
        }
        records = DynamicDataExtractor.parse_variables(response)

        assert len(records) == 2
        assert records[0] == {
            "variable_id": "145",
            "variable_name": "PDRB",
            "variable_description": "PDRB ADHK",
        }

    def test_parse_vertical_variables(self):
        """Should parse vertical variable definitions."""
        response = {
            "vervar": [
                {"id": "1", "label": "Laki-laki", "description": "Male", "unit": "orang"},
            ]
        }
        records = DynamicDataExtractor.parse_vertical_variables(response)

        assert len(records) == 1
        assert records[0] == {
            "vervar_id": "1",
            "vervar_name": "Laki-laki",
            "vervar_description": "Male",
            "vervar_unit": "orang",
        }

    def test_parse_datacontent(self):
        """Should parse data content into records."""
        response = {
            "datacontent": [
                ["2023", "100.5", "200.3"],
                ["2024", "110.2", "210.1"],
            ],
            "infotabel": {"tabel": {"nama": "Test Table"}},
        }
        records = DynamicDataExtractor.parse_datacontent(response)

        assert len(records) == 2
        assert records[0]["year"] == "2023"
        assert records[0]["values"] == ["100.5", "200.3"]


class TestSIMDASIExtractor:
    """Test the SIMDASI extractor."""

    def test_parse_table_metadata(self):
        """Should extract table metadata."""
        response = {
            "data": [
                {
                    "id": "123",
                    "kode": "T-001",
                    "judul": "PDRB Provinsi",
                    "subjek": "Ekonomi",
                    "satuan": "Miliar Rupiah",
                    "periode": "Tahunan",
                }
            ]
        }
        metadata = SIMDASIExtractor.parse_table_metadata(response)

        assert metadata["table_id"] == "123"
        assert metadata["table_code"] == "T-001"
        assert metadata["title"] == "PDRB Provinsi"
        assert metadata["subject"] == "Ekonomi"
        assert metadata["unit"] == "Miliar Rupiah"
        assert metadata["frequency"] == "Tahunan"

    def test_parse_table_metadata_empty(self):
        """Should handle empty data."""
        metadata = SIMDASIExtractor.parse_table_metadata({"data": []})
        assert metadata == {}


class TestGlossaryExtractor:
    """Test the glossary extractor."""

    def test_parse_glossary(self):
        """Should parse glossary records."""
        response = {
            "data": [
                {
                    "id": "1",
                    "nama_indikator": "PDRB",
                    "konsep": "Produk Domestik Regional Bruto",
                    "definisi": "Nilai tambah barang dan jasa",
                    "klasifikasi": "Ekonomi",
                    "ukuran": "Nilai",
                    "satuan": "Miliar Rupiah",
                    "sumber_data": "BPS",
                }
            ]
        }
        records = GlossaryExtractor.parse_glossary(response)

        assert len(records) == 1
        assert records[0]["glossary_id"] == "1"
        assert records[0]["indicator_name"] == "PDRB"
        assert records[0]["concept"] == "Produk Domestik Regional Bruto"
        assert records[0]["unit"] == "Miliar Rupiah"