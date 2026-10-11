from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

from app.models.entities import DocumentType


@dataclass
class OCRResult:
    text: str
    language: str = "en"
    confidence: float = 0.9


@dataclass
class ExtractedMedication:
    name: str
    strength: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    route: str | None = None
    duration: str | None = None
    instructions: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    confidence: float = 0.9


@dataclass
class ExtractedObservation:
    test_name: str
    value: float | None = None
    value_text: str | None = None
    unit: str | None = None
    ref_low: float | None = None
    ref_high: float | None = None
    loinc_code: str | None = None
    effective_date: date | None = None
    confidence: float = 0.9


@dataclass
class ExtractedCondition:
    name: str
    icd10_code: str | None = None
    clinical_status: str = "active"
    onset_date: date | None = None
    confidence: float = 0.9


@dataclass
class ExtractedEncounter:
    facility: str | None = None
    admit_date: date | None = None
    discharge_date: date | None = None
    reason: str | None = None
    confidence: float = 0.9


@dataclass
class ExtractionResult:
    medications: list[ExtractedMedication] = field(default_factory=list)
    observations: list[ExtractedObservation] = field(default_factory=list)
    conditions: list[ExtractedCondition] = field(default_factory=list)
    encounters: list[ExtractedEncounter] = field(default_factory=list)
    record_date: date | None = None
    source_facility: str | None = None
    doc_type_hint: DocumentType | None = None


@dataclass
class SummaryResult:
    plain_text: str
    abnormal_explanations: list[dict]
    language: str = "en"
    provider: str = "mock"
    disclaimer: str = "Not a diagnosis; consult your doctor."


class OCRProvider(Protocol):
    def extract_text(self, file_path: str, mime: str) -> OCRResult: ...


class ExtractionProvider(Protocol):
    def extract(self, text: str, doc_type: DocumentType) -> ExtractionResult: ...


class SummaryProvider(Protocol):
    def summarize(self, extraction: ExtractionResult, lang: str) -> SummaryResult: ...
