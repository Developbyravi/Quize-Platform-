from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.models.activity import ActivityLog
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/activity", tags=["Activity Logging"])

class ActivityReport(BaseModel):
    event_type: str
    round_id: Optional[int] = None
    question_id: Optional[int] = None
    metadata_json: Optional[str] = None

@router.post("")
def record_activity(
    data: ActivityReport,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    log = ActivityLog(
        user_id=current_user.id,
        event_type=data.event_type,
        round_id=data.round_id,
        question_id=data.question_id,
        metadata_json=data.metadata_json,
        ip_address=ip_addr,
        user_agent=user_agent
    )
    db.add(log)
    db.commit()
    return {"message": "Activity recorded successfully."}
