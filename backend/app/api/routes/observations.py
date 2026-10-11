from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_patient
from app.core.database import get_db
from app.models.entities import Observation, Patient
from app.schemas.clinical import LabTrendOut, LabTrendPoint, ObservationOut

router = APIRouter(prefix="/observations", tags=["observations"])


@router.get("", response_model=list[ObservationOut])
def list_observations(
    patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)
) -> list[Observation]:
    return (
        db.query(Observation)
        .filter(Observation.patient_id == patient.id, Observation.verified.is_(True))
        .order_by(Observation.effective_date.desc())
        .all()
    )


@router.get("/trends", response_model=list[LabTrendOut])
def lab_trends(
    patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)
) -> list[LabTrendOut]:
    rows = (
        db.query(Observation)
        .filter(
            Observation.patient_id == patient.id,
            Observation.verified.is_(True),
            Observation.value.is_not(None),
        )
        .order_by(Observation.effective_date.asc())
        .all()
    )
    grouped: dict[str, list[Observation]] = defaultdict(list)
    for row in rows:
        grouped[row.test_name].append(row)

    trends: list[LabTrendOut] = []
    for test_name, points in grouped.items():
        first = points[0]
        trends.append(
            LabTrendOut(
                test_name=test_name,
                unit=first.unit,
                ref_low=first.ref_low,
                ref_high=first.ref_high,
                points=[
                    LabTrendPoint(
                        effective_date=p.effective_date,
                        value=p.value,
                        unit=p.unit,
                        interpretation=p.interpretation,
                        document_id=p.document_id,
                    )
                    for p in points
                ],
            )
        )
    return trends
