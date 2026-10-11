from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.entities import DocumentStatus, DocumentType, Interpretation, TimelineKind


class MedicationOut(BaseModel):
    id: int
    fhir_id: str
    document_id: int | None
    name: str
    strength: str | None
    dosage: str | None
    frequency: str | None
    route: str | None
    duration: str | None
    instructions: str | None
    start_date: date | None
    end_date: date | None
    is_active: bool
    confidence: float
    verified: bool

    model_config = {"from_attributes": True}


class MedicationUpdate(BaseModel):
    name: str | None = None
    strength: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    route: str | None = None
    duration: str | None = None
    instructions: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class ObservationOut(BaseModel):
    id: int
    fhir_id: str
    document_id: int | None
    test_name: str
    loinc_code: str | None
    value: float | None
    value_text: str | None
    unit: str | None
    ref_low: float | None
    ref_high: float | None
    interpretation: Interpretation
    effective_date: date | None
    confidence: float
    verified: bool

    model_config = {"from_attributes": True}


class ObservationUpdate(BaseModel):
    test_name: str | None = None
    value: float | None = None
    value_text: str | None = None
    unit: str | None = None
    ref_low: float | None = None
    ref_high: float | None = None
    interpretation: Interpretation | None = None
    effective_date: date | None = None


class ConditionOut(BaseModel):
    id: int
    fhir_id: str
    document_id: int | None
    name: str
    icd10_code: str | None
    clinical_status: str
    onset_date: date | None
    confidence: float
    verified: bool

    model_config = {"from_attributes": True}


class ConditionUpdate(BaseModel):
    name: str | None = None
    icd10_code: str | None = None
    clinical_status: str | None = None
    onset_date: date | None = None


class EncounterOut(BaseModel):
    id: int
    fhir_id: str
    document_id: int | None
    facility: str | None
    admit_date: date | None
    discharge_date: date | None
    reason: str | None
    confidence: float
    verified: bool

    model_config = {"from_attributes": True}


class SummaryOut(BaseModel):
    id: int
    document_id: int
    language: str
    plain_text: str
    abnormal_explanations: dict | list | None
    provider: str
    disclaimer: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TimelineEventOut(BaseModel):
    id: int
    event_date: date
    kind: TimelineKind
    title: str
    description: str | None
    ref_type: str
    ref_id: int
    document_id: int | None

    model_config = {"from_attributes": True}


class DocumentOut(BaseModel):
    id: int
    fhir_id: str
    doc_type: DocumentType
    original_filename: str
    mime_type: str
    status: DocumentStatus
    record_date: date | None
    source_facility: str | None
    ocr_text: str | None
    ocr_confidence: float | None
    ocr_language: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    medications: list[MedicationOut] = []
    observations: list[ObservationOut] = []
    conditions: list[ConditionOut] = []
    encounters: list[EncounterOut] = []
    summaries: list[SummaryOut] = []

    model_config = {"from_attributes": True}


class DocumentUpdate(BaseModel):
    doc_type: DocumentType | None = None
    record_date: date | None = None
    source_facility: str | None = None


class DocumentConfirmRequest(BaseModel):
    medications: list[MedicationUpdate] = Field(default_factory=list)
    observations: list[ObservationUpdate] = Field(default_factory=list)
    conditions: list[ConditionUpdate] = Field(default_factory=list)


class DashboardOut(BaseModel):
    patient: dict
    active_medications: list[MedicationOut]
    recent_abnormal: list[ObservationOut]
    latest_summary: SummaryOut | None
    recent_documents: list[DocumentOut]
    document_counts: dict[str, int]


class LabTrendPoint(BaseModel):
    effective_date: date | None
    value: float | None
    unit: str | None
    interpretation: Interpretation
    document_id: int | None


class LabTrendOut(BaseModel):
    test_name: str
    unit: str | None
    ref_low: float | None
    ref_high: float | None
    points: list[LabTrendPoint]
