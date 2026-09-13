from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List
from app.core.database import get_db
from app.models.leaderboard import Score
from app.models.user import User, Participant
from app.models.setting import ContestSettings
from app.schemas.leaderboard import LeaderboardOut, LeaderboardEntry
from app.api.auth import get_current_user

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("", response_model=LeaderboardOut)
def get_leaderboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    settings = db.query(ContestSettings).first()
    is_vis = settings.leaderboard_visible if settings else True
    is_froz = settings.leaderboard_frozen if settings else False

    if current_user.role != "admin" and not is_vis:
        return {
            "is_visible": False,
            "is_frozen": is_froz,
            "entries": []
        }

    # 3-tier tie-breaking algorithm query:
    # 1. total_score DESC
    # 2. total_time_sec ASC
    # 3. last_submission_timestamp ASC
    scores = db.query(Score).join(Participant, Score.participant_id == Participant.id).order_by(
        desc(Score.total_score),
        asc(Score.total_time_sec),
        asc(Score.last_submission_timestamp)
    ).all()

    entries = []
    for rank, sc in enumerate(scores, 1):
        part = sc.participant
        if not part:
            continue
        entries.append({
            "rank": rank,
            "participant_id": part.id,
            "full_name": part.full_name,
            "college_name": part.college_name,
            "department": part.department,
            "round1_score": sc.round1_score,
            "round2_score": sc.round2_score,
            "round3_score": sc.round3_score,
            "total_score": sc.total_score,
            "total_time_sec": sc.total_time_sec,
            "last_submission_timestamp": sc.last_submission_timestamp,
            "is_disqualified": part.is_disqualified
        })

    return {
        "is_visible": is_vis,
        "is_frozen": is_froz,
        "entries": entries
    }
