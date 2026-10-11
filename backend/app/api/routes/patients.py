from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_patient, get_current_user
from app.core.database import get_db
from app.models.entities import (
    Document,
    DocumentStatus,
    Interpretation,
    Medication,
    Observation,
    Patient,
    Summary,
    User,
)
from app.schemas.clinical import DashboardOut, DocumentOut, MedicationOut, ObservationOut, SummaryOut
from app.schemas.patient import PatientOut, PatientUpdate

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/me", response_model=PatientOut)
def get_my_patient(patient: Patient = Depends(get_current_patient)) -> Patient:
    return patient


@router.patch("/me", response_model=PatientOut)
def update_my_patient(
    payload: PatientUpdate,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Patient:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(patient, key, value)
    if "name" in data:
        user.full_name = data["name"]
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/me/dashboard", response_model=DashboardOut)
def dashboard(patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)) -> DashboardOut:
    active_meds = (
        db.query(Medication)
        .filter(
            Medication.patient_id == patient.id,
            Medication.is_active.is_(True),
            Medication.verified.is_(True),
        )
        .order_by(Medication.created_at.desc())
        .limit(10)
        .all()
    )
    abnormal = (
        db.query(Observation)
        .filter(
            Observation.patient_id == patient.id,
            Observation.verified.is_(True),
            Observation.interpretation.in_([Interpretation.H, Interpretation.L]),
        )
        .order_by(Observation.effective_date.desc())
        .limit(8)
        .all()
    )
    latest_summary = (
        db.query(Summary)
        .filter(Summary.patient_id == patient.id, Summary.language == patient.preferred_language)
        .order_by(Summary.created_at.desc())
        .first()
    )
    if not latest_summary:
        latest_summary = (
            db.query(Summary)
            .filter(Summary.patient_id == patient.id)
            .order_by(Summary.created_at.desc())
            .first()
        )
    recent_docs = (
        db.query(Document)
        .filter(Document.patient_id == patient.id)
        .order_by(Document.created_at.desc())
        .limit(5)
        .all()
    )
    counts = {s.value: 0 for s in DocumentStatus}
    for doc in db.query(Document).filter(Document.patient_id == patient.id).all():
        counts[doc.status.value] = counts.get(doc.status.value, 0) + 1

    return DashboardOut(
        patient=PatientOut.model_validate(patient).model_dump(),
        active_medications=[MedicationOut.model_validate(m) for m in active_meds],
        recent_abnormal=[ObservationOut.model_validate(o) for o in abnormal],
        latest_summary=SummaryOut.model_validate(latest_summary) if latest_summary else None,
        recent_documents=[DocumentOut.model_validate(d) for d in recent_docs],
        document_counts=counts,
    )
