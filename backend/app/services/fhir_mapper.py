"""Map MedCare entities to FHIR R4-style JSON resources (ABDM-ready)."""

from datetime import date, datetime
from typing import Any

from app.models.entities import (
    Condition,
    Document,
    Encounter,
    Medication,
    Observation,
    Patient,
)


def _date(d: date | datetime | None) -> str | None:
    if d is None:
        return None
    if isinstance(d, datetime):
        return d.date().isoformat()
    return d.isoformat()


def patient_to_fhir(patient: Patient) -> dict[str, Any]:
    resource: dict[str, Any] = {
        "resourceType": "Patient",
        "id": patient.fhir_id,
        "name": [{"text": patient.name}],
        "gender": patient.gender.value if patient.gender else "unknown",
        "telecom": [],
        "identifier": [],
    }
    if patient.date_of_birth:
        resource["birthDate"] = _date(patient.date_of_birth)
    if patient.phone:
        resource["telecom"].append({"system": "phone", "value": patient.phone})
    if patient.abha_number:
        resource["identifier"].append(
            {
                "system": "https://healthid.ndhm.gov.in",
                "value": patient.abha_number,
                "type": {"text": "ABHA Number"},
            }
        )
    if patient.abha_address:
        resource["identifier"].append(
            {
                "system": "https://abdm.gov.in/abha-address",
                "value": patient.abha_address,
                "type": {"text": "ABHA Address"},
            }
        )
    return resource


def document_to_fhir(doc: Document) -> dict[str, Any]:
    return {
        "resourceType": "DocumentReference",
        "id": doc.fhir_id,
        "status": "current" if doc.status.value == "confirmed" else "preliminary",
        "type": {"text": doc.doc_type.value},
        "date": _date(doc.record_date or doc.created_at),
        "content": [
            {
                "attachment": {
                    "contentType": doc.mime_type,
                    "title": doc.original_filename,
                    "url": f"/api/documents/{doc.id}/file",
                }
            }
        ],
        "custodian": {"display": doc.source_facility} if doc.source_facility else None,
    }


def medication_to_fhir(med: Medication, patient: Patient) -> dict[str, Any]:
    return {
        "resourceType": "MedicationRequest",
        "id": med.fhir_id,
        "status": "active" if med.is_active else "completed",
        "intent": "order",
        "medicationCodeableConcept": {
            "text": f"{med.name} {med.strength or ''}".strip()
        },
        "subject": {"reference": f"Patient/{patient.fhir_id}"},
        "authoredOn": _date(med.start_date),
        "dosageInstruction": [
            {
                "text": " ".join(
                    filter(None, [med.dosage, med.frequency, med.route, med.instructions])
                ),
                "route": {"text": med.route} if med.route else None,
            }
        ],
    }


def observation_to_fhir(obs: Observation, patient: Patient) -> dict[str, Any]:
    coding = []
    if obs.loinc_code:
        coding.append(
            {"system": "http://loinc.org", "code": obs.loinc_code, "display": obs.test_name}
        )
    resource: dict[str, Any] = {
        "resourceType": "Observation",
        "id": obs.fhir_id,
        "status": "final" if obs.verified else "preliminary",
        "code": {"coding": coding, "text": obs.test_name},
        "subject": {"reference": f"Patient/{patient.fhir_id}"},
        "effectiveDateTime": _date(obs.effective_date),
    }
    if obs.value is not None:
        resource["valueQuantity"] = {
            "value": obs.value,
            "unit": obs.unit,
            "system": "http://unitsofmeasure.org",
        }
    elif obs.value_text:
        resource["valueString"] = obs.value_text
    if obs.ref_low is not None or obs.ref_high is not None:
        resource["referenceRange"] = [
            {"low": {"value": obs.ref_low}, "high": {"value": obs.ref_high}}
        ]
    if obs.interpretation and obs.interpretation.value != "unknown":
        resource["interpretation"] = [{"coding": [{"code": obs.interpretation.value}]}]
    return resource


def condition_to_fhir(cond: Condition, patient: Patient) -> dict[str, Any]:
    coding = []
    if cond.icd10_code:
        coding.append(
            {
                "system": "http://hl7.org/fhir/sid/icd-10",
                "code": cond.icd10_code,
                "display": cond.name,
            }
        )
    return {
        "resourceType": "Condition",
        "id": cond.fhir_id,
        "clinicalStatus": {"coding": [{"code": cond.clinical_status}]},
        "code": {"coding": coding, "text": cond.name},
        "subject": {"reference": f"Patient/{patient.fhir_id}"},
        "onsetDateTime": _date(cond.onset_date),
    }


def encounter_to_fhir(enc: Encounter, patient: Patient) -> dict[str, Any]:
    return {
        "resourceType": "Encounter",
        "id": enc.fhir_id,
        "status": "finished",
        "class": {"code": "IMP", "display": "inpatient encounter"},
        "subject": {"reference": f"Patient/{patient.fhir_id}"},
        "period": {"start": _date(enc.admit_date), "end": _date(enc.discharge_date)},
        "serviceProvider": {"display": enc.facility} if enc.facility else None,
        "reasonCode": [{"text": enc.reason}] if enc.reason else [],
    }


def build_everything_bundle(patient: Patient) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []

    def add(resource: dict[str, Any]) -> None:
        cleaned = {k: v for k, v in resource.items() if v is not None}
        entries.append(
            {
                "fullUrl": f"urn:uuid:{cleaned['id']}",
                "resource": cleaned,
            }
        )

    add(patient_to_fhir(patient))
    for doc in patient.documents:
        add(document_to_fhir(doc))
    for med in patient.medications:
        if med.verified:
            add(medication_to_fhir(med, patient))
    for obs in patient.observations:
        if obs.verified:
            add(observation_to_fhir(obs, patient))
    for cond in patient.conditions:
        if cond.verified:
            add(condition_to_fhir(cond, patient))
    for enc in patient.encounters:
        if enc.verified:
            add(encounter_to_fhir(enc, patient))

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total": len(entries),
        "entry": entries,
    }


SAMPLE_ABHA_BUNDLE: dict[str, Any] = {
    "resourceType": "Bundle",
    "type": "collection",
    "entry": [
        {
            "resource": {
                "resourceType": "Condition",
                "id": "sample-cond-htn",
                "code": {"text": "Essential Hypertension", "coding": [{"code": "I10"}]},
                "clinicalStatus": {"coding": [{"code": "active"}]},
                "onsetDateTime": "2023-01-15",
            }
        },
        {
            "resource": {
                "resourceType": "MedicationRequest",
                "id": "sample-med-amlo",
                "status": "active",
                "medicationCodeableConcept": {"text": "Amlodipine 5 mg"},
                "dosageInstruction": [{"text": "1 tablet once daily"}],
                "authoredOn": "2025-06-01",
            }
        },
        {
            "resource": {
                "resourceType": "Observation",
                "id": "sample-obs-bp",
                "status": "final",
                "code": {"text": "Blood Pressure Systolic"},
                "valueQuantity": {"value": 138, "unit": "mmHg"},
                "effectiveDateTime": "2025-06-01",
            }
        },
    ],
}
