from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_patient
from app.core.database import get_db
from app.models.entities import Patient
from app.services.fhir_mapper import build_everything_bundle, patient_to_fhir

router = APIRouter(prefix="/fhir", tags=["fhir"])


@router.get("/Patient/{patient_id}")
def get_patient_resource(
    patient_id: int,
    current: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> dict:
    if current.id != patient_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_to_fhir(patient)


@router.get("/Patient/{patient_id}/$everything")
def everything(
    patient_id: int,
    current: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> dict:
    if current.id != patient_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    patient = (
        db.query(Patient)
        .options(
            joinedload(Patient.documents),
            joinedload(Patient.medications),
            joinedload(Patient.observations),
            joinedload(Patient.conditions),
            joinedload(Patient.encounters),
        )
        .filter(Patient.id == patient_id)
        .first()
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return build_everything_bundle(patient)


@router.get("/me/$everything")
def my_everything(
    patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)
) -> dict:
    loaded = (
        db.query(Patient)
        .options(
            joinedload(Patient.documents),
            joinedload(Patient.medications),
            joinedload(Patient.observations),
            joinedload(Patient.conditions),
            joinedload(Patient.encounters),
        )
        .filter(Patient.id == patient.id)
        .first()
    )
    return build_everything_bundle(loaded)
