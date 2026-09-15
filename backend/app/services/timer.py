from datetime import datetime, timezone, timedelta
from typing import Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.round import Round, RoundAttempt
from app.core.logging import log_event

def get_remaining_seconds(attempt: RoundAttempt, round_obj: Round) -> int:
    """
    Calculates remaining time in seconds based strictly on server timestamps.
    """
    if attempt.is_submitted:
        return 0
    
    start = attempt.start_time
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    duration_sec = round_obj.duration_minutes * 60
    elapsed_sec = (now - start).total_seconds()
    
    remaining = duration_sec - elapsed_sec
    return max(0, int(remaining))

def validate_attempt_active(db: Session, attempt: RoundAttempt, round_obj: Round, grace_seconds: int = 10) -> bool:
    """
    Checks whether an attempt is still within duration + grace period.
    Auto-submits if time has expired.
    """
    if attempt.is_submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This round attempt has already been submitted and locked."
        )
        
    remaining = get_remaining_seconds(attempt, round_obj)
    if remaining <= -grace_seconds:
        # Time expired beyond grace period -> Auto-submit as TIME_EXPIRED
        attempt.is_submitted = True
        attempt.submission_type = "TIME_EXPIRED"
        attempt.submitted_at = datetime.now(timezone.utc)
        db.commit()

        # Update scores and activity log
        try:
            from app.services.scoring import update_participant_score
            from app.models.activity import ActivityLog
            update_participant_score(db, attempt.participant_id)
            log = ActivityLog(
                user_id=attempt.participant.user_id if attempt.participant else None,
                event_type="TIME_EXPIRED",
                round_id=attempt.round_id,
                metadata_json='{"reason": "Timer expired"}'
            )
            db.add(log)
            db.commit()
        except Exception:
            pass

        log_event("AUTO_SUBMIT_EXPIRED", f"Attempt {attempt.id} auto-submitted due to timer expiration.", attempt.participant_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Time limit for this round has expired. Your submission has been automatically locked."
        )
    return True
