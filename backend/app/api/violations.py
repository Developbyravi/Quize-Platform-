from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.violation import Violation
from app.models.user import User, Participant
from app.api.auth import get_current_user
from app.core.logging import log_event

router = APIRouter(prefix="/violations", tags=["Anti-Cheating"])

class ViolationReport(BaseModel):
    violation_type: str # TAB_SWITCH, WINDOW_BLUR, MULTIPLE_SESSIONS
    details: Optional[str] = None

@router.post("")
def report_violation(data: ViolationReport, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    participant = current_user.participant_profile
    if not participant:
        raise HTTPException(status_code=403, detail="Participant profile missing.")

    v = Violation(
        participant_id=participant.id,
        violation_type=data.violation_type,
        details=data.details or "Tab switch / window blur detected"
    )
    db.add(v)
    participant.violations_count += 1
    db.commit()

    log_event("ANTI_CHEAT_VIOLATION", f"Type: {data.violation_type}, Count: {participant.violations_count}", participant.id)

    return {
        "message": "Violation logged.",
        "total_violations": participant.violations_count
    }
