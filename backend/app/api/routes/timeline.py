from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_patient
from app.core.database import get_db
from app.models.entities import Patient, TimelineEvent, TimelineKind
from app.schemas.clinical import TimelineEventOut

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.get("", response_model=list[TimelineEventOut])
def get_timeline(
    kind: TimelineKind | None = None,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
) -> list[TimelineEvent]:
    q = db.query(TimelineEvent).filter(TimelineEvent.patient_id == patient.id)
    if kind:
        q = q.filter(TimelineEvent.kind == kind)
    return q.order_by(TimelineEvent.event_date.desc(), TimelineEvent.id.desc()).all()
