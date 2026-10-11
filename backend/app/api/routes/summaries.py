from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_patient
from app.core.database import get_db
from app.models.entities import Patient, Summary
from app.schemas.clinical import SummaryOut

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.get("", response_model=list[SummaryOut])
def list_summaries(
    language: str | None = None,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> list[Summary]:
    q = db.query(Summary).filter(Summary.patient_id == patient.id)
    if language:
        q = q.filter(Summary.language == language)
    return q.order_by(Summary.created_at.desc()).all()


@router.get("/document/{document_id}", response_model=SummaryOut)
def get_document_summary(
    document_id: int,
    language: str = "en",
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Summary:
    summary = (
        db.query(Summary)
        .filter(
            Summary.patient_id == patient.id,
            Summary.document_id == document_id,
            Summary.language == language,
        )
        .first()
    )
    if not summary:
        summary = (
            db.query(Summary)
            .filter(Summary.patient_id == patient.id, Summary.document_id == document_id)
            .first()
        )
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary
