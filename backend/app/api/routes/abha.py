from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_patient
from app.core.database import get_db
from app.models.entities import Condition, Medication, Observation, Patient
from app.schemas.patient import AbhaImportRequest, AbhaLinkRequest, AbhaLinkResponse, PatientOut
from app.services.fhir_mapper import SAMPLE_ABHA_BUNDLE

router = APIRouter(prefix="/abha", tags=["abha"])

# Demo OTP accepted for mock ABHA linking
MOCK_OTP = "123456"


@router.post("/link", response_model=AbhaLinkResponse)
def link_abha(
    payload: AbhaLinkRequest,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> AbhaLinkResponse:
    if payload.otp != MOCK_OTP:
        raise HTTPException(status_code=400, detail="Invalid OTP. Use 123456 for the demo.")

    digits = "".join(ch for ch in payload.abha_number if ch.isdigit())
    if len(digits) < 10:
        raise HTTPException(status_code=400, detail="ABHA number looks invalid")

    formatted = "-".join([digits[i : i + 4] for i in range(0, min(len(digits), 14), 4)])
    address = f"{patient.name.split()[0].lower()}.{digits[-4:]}@abdm"

    patient.abha_number = formatted
    patient.abha_address = address
    db.commit()

    return AbhaLinkResponse(
        abha_number=formatted,
        abha_address=address,
        message="ABHA linked successfully (mock). This is a demo flow, not a real ABDM connection.",
    )


@router.post("/import", response_model=PatientOut)
def import_abha_bundle(
    payload: AbhaImportRequest,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> Patient:
    bundle = payload.bundle if payload.bundle and not payload.use_sample else SAMPLE_ABHA_BUNDLE
    entries = bundle.get("entry") or []

    for entry in entries:
        resource = entry.get("resource") or {}
        rtype = resource.get("resourceType")
        if rtype == "Condition":
            code = resource.get("code") or {}
            coding = (code.get("coding") or [{}])[0]
            onset = resource.get("onsetDateTime")
            db.add(
                Condition(
                    patient_id=patient.id,
                    name=code.get("text") or coding.get("display") or "Imported condition",
                    icd10_code=coding.get("code"),
                    clinical_status=(
                        ((resource.get("clinicalStatus") or {}).get("coding") or [{}])[0].get(
                            "code", "active"
                        )
                    ),
                    onset_date=date.fromisoformat(onset[:10]) if onset else None,
                    confidence=1.0,
                    verified=True,
                )
            )
        elif rtype == "MedicationRequest":
            med = resource.get("medicationCodeableConcept") or {}
            dosage = ((resource.get("dosageInstruction") or [{}])[0]).get("text")
            authored = resource.get("authoredOn")
            db.add(
                Medication(
                    patient_id=patient.id,
                    name=med.get("text") or "Imported medicine",
                    dosage=dosage,
                    frequency=dosage,
                    start_date=date.fromisoformat(authored[:10]) if authored else None,
                    is_active=resource.get("status", "active") == "active",
                    confidence=1.0,
                    verified=True,
                )
            )
        elif rtype == "Observation":
            code = resource.get("code") or {}
            qty = resource.get("valueQuantity") or {}
            effective = resource.get("effectiveDateTime")
            db.add(
                Observation(
                    patient_id=patient.id,
                    test_name=code.get("text") or "Imported observation",
                    value=qty.get("value"),
                    unit=qty.get("unit"),
                    effective_date=date.fromisoformat(effective[:10]) if effective else None,
                    confidence=1.0,
                    verified=True,
                )
            )

    if not patient.abha_number:
        patient.abha_number = "12-3456-7890-1234"
        patient.abha_address = f"{patient.name.split()[0].lower()}.demo@abdm"

    db.commit()
    db.refresh(patient)
    return patient


@router.get("/status", response_model=PatientOut)
def abha_status(patient: Patient = Depends(get_current_patient)) -> Patient:
    return patient
