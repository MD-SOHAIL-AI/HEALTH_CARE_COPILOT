from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_patient
from app.core.database import get_db
from app.models.entities import Medication, Patient
from app.schemas.clinical import MedicationOut, MedicationUpdate

router = APIRouter(prefix="/medications", tags=["medications"])


@router.get("", response_model=list[MedicationOut])
def list_medications(
    active_only: bool = False,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> list[Medication]:
    q = db.query(Medication).filter(
        Medication.patient_id == patient.id, Medication.verified.is_(True)
    )
    if active_only:
        q = q.filter(Medication.is_active.is_(True))
    return q.order_by(Medication.created_at.desc()).all()


@router.patch("/{medication_id}", response_model=MedicationOut)
def update_medication(
    medication_id: int,
    payload: MedicationUpdate,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Medication:
    med = (
        db.query(Medication)
        .filter(Medication.id == medication_id, Medication.patient_id == patient.id)
        .first()
    )
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(med, key, value)
    db.commit()
    db.refresh(med)
    return med
