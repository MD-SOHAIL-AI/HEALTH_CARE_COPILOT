import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_patient
from app.core.config import get_settings
from app.core.database import SessionLocal, get_db
from app.models.entities import (
    Condition,
    Document,
    DocumentStatus,
    DocumentType,
    Medication,
    Observation,
    Patient,
)
from app.schemas.clinical import (
    ConditionUpdate,
    DocumentConfirmRequest,
    DocumentOut,
    DocumentUpdate,
    MedicationUpdate,
    ObservationUpdate,
)
from app.services.pipeline import confirm_document, process_document
from app.services.reference_ranges import interpret_value

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


def _run_pipeline(document_id: int) -> None:
    db = SessionLocal()
    try:
        process_document(db, document_id)
    finally:
        db.close()


def _load_document(db: Session, document_id: int, patient_id: int) -> Document:
    doc = (
        db.query(Document)
        .options(
            joinedload(Document.medications),
            joinedload(Document.observations),
            joinedload(Document.conditions),
            joinedload(Document.encounters),
            joinedload(Document.summaries),
        )
        .filter(Document.id == document_id, Document.patient_id == patient_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("", response_model=list[DocumentOut])
def list_documents(
    patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)
) -> list[Document]:
    return (
        db.query(Document)
        .options(
            joinedload(Document.medications),
            joinedload(Document.observations),
            joinedload(Document.conditions),
            joinedload(Document.encounters),
            joinedload(Document.summaries),
        )
        .filter(Document.patient_id == patient.id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.post("", response_model=DocumentOut)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: DocumentType = Form(...),
    record_date: str | None = Form(None),
    source_facility: str | None = Form(None),
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Document:
    suffix = Path(file.filename or "upload.bin").suffix
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    dest = settings.upload_path / stored_name
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    from datetime import date as date_cls

    parsed_date = None
    if record_date:
        try:
            parsed_date = date_cls.fromisoformat(record_date)
        except ValueError:
            parsed_date = None

    doc = Document(
        patient_id=patient.id,
        doc_type=doc_type,
        original_filename=file.filename or stored_name,
        file_path=str(dest),
        mime_type=file.content_type or "application/octet-stream",
        status=DocumentStatus.uploaded,
        record_date=parsed_date,
        source_facility=source_facility,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(_run_pipeline, doc.id)
    return _load_document(db, doc.id, patient.id)


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Document:
    return _load_document(db, document_id, patient.id)


@router.patch("/{document_id}", response_model=DocumentOut)
def update_document(
    document_id: int,
    payload: DocumentUpdate,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Document:
    doc = _load_document(db, document_id, patient.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(doc, key, value)
    db.commit()
    return _load_document(db, document_id, patient.id)


@router.get("/{document_id}/file")
def download_file(
    document_id: int,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> FileResponse:
    doc = _load_document(db, document_id, patient.id)
    path = Path(doc.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing on server")
    return FileResponse(path, media_type=doc.mime_type, filename=doc.original_filename)


@router.post("/{document_id}/reprocess", response_model=DocumentOut)
def reprocess(
    document_id: int,
    background_tasks: BackgroundTasks,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Document:
    doc = _load_document(db, document_id, patient.id)
    doc.status = DocumentStatus.uploaded
    doc.error_message = None
    db.commit()
    background_tasks.add_task(_run_pipeline, doc.id)
    return _load_document(db, document_id, patient.id)


@router.post("/{document_id}/confirm", response_model=DocumentOut)
def confirm(
    document_id: int,
    payload: DocumentConfirmRequest,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Document:
    doc = _load_document(db, document_id, patient.id)
    if doc.status not in (DocumentStatus.needs_review, DocumentStatus.confirmed):
        raise HTTPException(status_code=400, detail="Document is not ready for confirmation")

    # Apply optional edits by index order
    for i, patch in enumerate(payload.medications):
        if i < len(doc.medications):
            _apply_update(doc.medications[i], patch)
    for i, patch in enumerate(payload.observations):
        if i < len(doc.observations):
            _apply_update(doc.observations[i], patch)
            obs = doc.observations[i]
            if obs.value is not None:
                obs.interpretation = interpret_value(obs.value, obs.ref_low, obs.ref_high)
    for i, patch in enumerate(payload.conditions):
        if i < len(doc.conditions):
            _apply_update(doc.conditions[i], patch)

    confirm_document(db, doc)
    return _load_document(db, document_id, patient.id)


def _apply_update(
    entity: Medication | Observation | Condition,
    patch: MedicationUpdate | ObservationUpdate | ConditionUpdate,
) -> None:
    for key, value in patch.model_dump(exclude_unset=True).items():
        setattr(entity, key, value)
