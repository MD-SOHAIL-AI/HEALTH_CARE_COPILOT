from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_patient
from app.core.database import get_db
from app.models.entities import Condition, Patient
from app.schemas.clinical import ConditionOut

router = APIRouter(prefix="/conditions", tags=["conditions"])


@router.get("", response_model=list[ConditionOut])
def list_conditions(
    patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)
) -> list[Condition]:
    return (
        db.query(Condition)
        .filter(Condition.patient_id == patient.id, Condition.verified.is_(True))
        .order_by(Condition.created_at.desc())
        .all()
    )
