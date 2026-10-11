import logging
from datetime import date

from sqlalchemy.orm import Session

from app.models.entities import (
    Condition,
    Document,
    DocumentStatus,
    Encounter,
    Medication,
    Observation,
    Summary,
    TimelineEvent,
    TimelineKind,
)
from app.services.ai import get_extraction_provider, get_ocr_provider, get_summary_provider
from app.services.reference_ranges import enrich_observation, interpretation_for

logger = logging.getLogger(__name__)


def process_document(db: Session, document_id: int) -> None:
    doc = db.get(Document, document_id)
    if not doc:
        return

    doc.status = DocumentStatus.processing
    db.commit()

    try:
        ocr = get_ocr_provider().extract_text(doc.file_path, doc.mime_type)
        doc.ocr_text = ocr.text
        doc.ocr_confidence = ocr.confidence
        doc.ocr_language = ocr.language

        extraction = get_extraction_provider().extract(ocr.text, doc.doc_type)
        if extraction.record_date and not doc.record_date:
            doc.record_date = extraction.record_date
        if extraction.source_facility and not doc.source_facility:
            doc.source_facility = extraction.source_facility

        # Clear previous draft clinical rows for reprocessing
        for coll in (doc.medications, doc.observations, doc.conditions, doc.encounters):
            for row in list(coll):
                db.delete(row)
        for s in list(doc.summaries):
            db.delete(s)
        db.flush()

        for m in extraction.medications:
            db.add(
                Medication(
                    patient_id=doc.patient_id,
                    document_id=doc.id,
                    name=m.name,
                    strength=m.strength,
                    dosage=m.dosage,
                    frequency=m.frequency,
                    route=m.route,
                    duration=m.duration,
                    instructions=m.instructions,
                    start_date=m.start_date,
                    end_date=m.end_date,
                    is_active=True,
                    confidence=m.confidence,
                    verified=False,
                )
            )

        for o in extraction.observations:
            enriched = enrich_observation(o)
            interp = interpretation_for(enriched)
            db.add(
                Observation(
                    patient_id=doc.patient_id,
                    document_id=doc.id,
                    test_name=enriched.test_name,
                    loinc_code=enriched.loinc_code,
                    value=enriched.value,
                    value_text=enriched.value_text,
                    unit=enriched.unit,
                    ref_low=enriched.ref_low,
                    ref_high=enriched.ref_high,
                    interpretation=interp,
                    effective_date=enriched.effective_date or doc.record_date,
                    confidence=enriched.confidence,
                    verified=False,
                )
            )

        for c in extraction.conditions:
            db.add(
                Condition(
                    patient_id=doc.patient_id,
                    document_id=doc.id,
                    name=c.name,
                    icd10_code=c.icd10_code,
                    clinical_status=c.clinical_status,
                    onset_date=c.onset_date,
                    confidence=c.confidence,
                    verified=False,
                )
            )

        for e in extraction.encounters:
            db.add(
                Encounter(
                    patient_id=doc.patient_id,
                    document_id=doc.id,
                    facility=e.facility,
                    admit_date=e.admit_date,
                    discharge_date=e.discharge_date,
                    reason=e.reason,
                    confidence=e.confidence,
                    verified=False,
                )
            )

        summarizer = get_summary_provider()
        for lang in ("en", "hi"):
            summary = summarizer.summarize(extraction, lang)
            db.add(
                Summary(
                    patient_id=doc.patient_id,
                    document_id=doc.id,
                    language=summary.language,
                    plain_text=summary.plain_text,
                    abnormal_explanations=summary.abnormal_explanations,
                    provider=summary.provider,
                    disclaimer=summary.disclaimer,
                )
            )

        doc.status = DocumentStatus.needs_review
        db.commit()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Document %s processing failed", document_id)
        db.rollback()
        doc = db.get(Document, document_id)
        if doc:
            doc.status = DocumentStatus.failed
            doc.error_message = str(exc)
            db.commit()


def confirm_document(db: Session, document: Document) -> Document:
    """Mark extracted items verified and publish timeline events."""
    for med in document.medications:
        med.verified = True
    for obs in document.observations:
        obs.verified = True
    for cond in document.conditions:
        cond.verified = True
    for enc in document.encounters:
        enc.verified = True

    # Remove prior timeline rows for this document
    existing = (
        db.query(TimelineEvent)
        .filter(TimelineEvent.document_id == document.id)
        .all()
    )
    for row in existing:
        db.delete(row)

    event_date = document.record_date or date.today()
    kind_map = {
        "prescription": TimelineKind.prescription,
        "lab_report": TimelineKind.lab,
        "discharge_summary": TimelineKind.discharge,
        "diagnostic_report": TimelineKind.diagnosis,
    }
    db.add(
        TimelineEvent(
            patient_id=document.patient_id,
            event_date=event_date,
            kind=kind_map.get(document.doc_type.value, TimelineKind.document),
            title=f"{document.doc_type.value.replace('_', ' ').title()}: {document.original_filename}",
            description=document.source_facility,
            ref_type="document",
            ref_id=document.id,
            document_id=document.id,
        )
    )

    for cond in document.conditions:
        db.add(
            TimelineEvent(
                patient_id=document.patient_id,
                event_date=cond.onset_date or event_date,
                kind=TimelineKind.diagnosis,
                title=cond.name,
                description=cond.icd10_code,
                ref_type="condition",
                ref_id=cond.id,
                document_id=document.id,
            )
        )

    document.status = DocumentStatus.confirmed
    db.commit()
    db.refresh(document)
    return document
