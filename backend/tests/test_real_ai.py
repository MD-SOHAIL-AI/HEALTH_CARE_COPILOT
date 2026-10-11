"""Standalone provider tests: run pytest -q backend/tests/test_real_ai.py with backend on PYTHONPATH."""
from pathlib import Path
from app.models.entities import DocumentType
from app.services.ai.real import RealOCRProvider, RealExtractionProvider, RealSummaryProvider

def test_lab_values_are_from_actual_text(tmp_path: Path):
    f=tmp_path/"sample.txt"
    f.write_text("Date: 2026-10-01\nHemoglobin: 11.2 g/dL (12.0-16.0)\n",encoding="utf8")
    ocr=RealOCRProvider().extract_text(str(f),"text/plain")
    facts=RealExtractionProvider().extract(ocr.text,DocumentType.lab_report)
    assert facts.observations
    assert facts.observations[0].value==11.2
    assert facts.observations[0].test_name=="Hemoglobin"
    assert facts.record_date.isoformat()=="2026-10-01"
    assert "11.2" in RealSummaryProvider().summarize(facts,"en").plain_text

def test_unrecognized_text_does_not_generate_medical_facts():
    facts=RealExtractionProvider().extract("Just a note without any clinical values",DocumentType.lab_report)
    assert not facts.observations
    assert not facts.medications
    assert not facts.conditions

def test_prescription_only_parses_explicit_dose():
    facts=RealExtractionProvider().extract("Tab Metformin 500 mg twice daily",DocumentType.prescription)
    assert len(facts.medications)==1
    assert facts.medications[0].name=="Metformin"
    assert facts.medications[0].strength=="500 mg"

def test_bad_pdf_is_rejected(tmp_path: Path):
    import pytest
    f=tmp_path/"fake.pdf"
    f.write_bytes(b"not a PDF")
    with pytest.raises(ValueError):
        RealOCRProvider().extract_text(str(f),"application/pdf")
