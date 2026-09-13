from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import List
from app.core.database import get_db
from app.models.round import Round, RoundAttempt
from app.models.user import User, Participant
from app.models.setting import ContestSettings
from app.schemas.round import RoundOut, RoundAttemptOut
from app.api.auth import get_current_user
from app.services.timer import get_remaining_seconds
from app.core.logging import log_event

router = APIRouter(prefix="/rounds", tags=["Rounds"])

def check_contest_accessible(db: Session, user: User):
    settings = db.query(ContestSettings).first()
    if not settings:
        return
    if user.role != "admin":
        if settings.maintenance_mode:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Competition is currently in Maintenance Mode. Please wait for an administrator to re-open the portal."
            )
        if settings.lock_all_participants:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="All participants have been locked by competition administrators."
            )
        if user.participant_profile and user.participant_profile.is_disqualified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You have been disqualified: {user.participant_profile.disqualification_reason or 'Cheating violation'}"
            )

@router.get("", response_model=List[RoundOut])
def get_rounds(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    rounds = db.query(Round).order_by(Round.round_number).all()
    return rounds

@router.get("/{id}", response_model=RoundOut)
def get_round_detail(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    rnd = db.query(Round).filter(Round.id == id).first()
    if not rnd:
        raise HTTPException(status_code=404, detail="Round not found.")
    return rnd

@router.post("/{id}/start", response_model=RoundAttemptOut)
def start_round(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    if current_user.role != "participant" or not current_user.participant_profile:
        raise HTTPException(status_code=403, detail="Only registered participants can attempt competition rounds.")

    participant = current_user.participant_profile
    rnd = db.query(Round).filter(Round.id == id).first()
    if not rnd:
        raise HTTPException(status_code=404, detail="Round not found.")

    if rnd.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Round {rnd.round_number} is currently {rnd.status}. You cannot enter this round now."
        )

    # Check for existing attempt
    attempt = db.query(RoundAttempt).filter(
        RoundAttempt.participant_id == participant.id,
        RoundAttempt.round_id == id
    ).first()

    now = datetime.now(timezone.utc)

    if not attempt:
        # Create new attempt with authoritative start timestamp
        attempt = RoundAttempt(
            participant_id=participant.id,
            round_id=id,
            start_time=now,
            end_time=now + timedelta(minutes=rnd.duration_minutes),
            is_submitted=False,
            score=0.0
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        log_event("ROUND_STARTED", f"Round {rnd.round_number} started.", participant.id)
    
    remaining = get_remaining_seconds(attempt, rnd)

    return {
        "id": attempt.id,
        "round_id": attempt.round_id,
        "start_time": attempt.start_time,
        "end_time": attempt.end_time,
        "remaining_seconds": remaining,
        "is_submitted": attempt.is_submitted,
        "score": attempt.score
    }

@router.get("/{id}/attempt", response_model=RoundAttemptOut)
def get_current_attempt(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    participant = current_user.participant_profile
    if not participant:
        raise HTTPException(status_code=403, detail="Participant profile missing.")

    rnd = db.query(Round).filter(Round.id == id).first()
    if not rnd:
        raise HTTPException(status_code=404, detail="Round not found.")

    attempt = db.query(RoundAttempt).filter(
        RoundAttempt.participant_id == participant.id,
        RoundAttempt.round_id == id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="No active attempt found for this round.")

    remaining = get_remaining_seconds(attempt, rnd)

    return {
        "id": attempt.id,
        "round_id": attempt.round_id,
        "start_time": attempt.start_time,
        "end_time": attempt.end_time,
        "remaining_seconds": remaining,
        "is_submitted": attempt.is_submitted,
        "score": attempt.score
    }
