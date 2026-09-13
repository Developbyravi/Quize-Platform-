from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from app.models.leaderboard import Score
from app.models.round import RoundAttempt
from app.models.submission import Submission, QuizAnswer
from app.models.question import Question
from app.models.user import Participant
from app.core.logging import log_event

def update_participant_score(db: Session, participant_id: int):
    """
    Recalculates scores and total contest duration for a participant.
    Updates or inserts the 'scores' table entry.
    """
    score_entry = db.query(Score).filter(Score.participant_id == participant_id).first()
    if not score_entry:
        score_entry = Score(participant_id=participant_id)
        db.add(score_entry)

    # 1. Round 1 Score (MCQs)
    r1_attempt = db.query(RoundAttempt).filter(
        RoundAttempt.participant_id == participant_id,
        RoundAttempt.round_id == 1
    ).first()
    
    r1_score = 0.0
    r1_time = 0.0
    if r1_attempt:
        r1_score = r1_attempt.score
        if r1_attempt.submitted_at and r1_attempt.start_time:
            s_time = r1_attempt.start_time.replace(tzinfo=timezone.utc) if r1_attempt.start_time.tzinfo is None else r1_attempt.start_time
            sub_time = r1_attempt.submitted_at.replace(tzinfo=timezone.utc) if r1_attempt.submitted_at.tzinfo is None else r1_attempt.submitted_at
            r1_time = max(0.0, (sub_time - s_time).total_seconds())

    # 2. Round 2 & 3 Scores (Best score per question)
    def calc_round_coding_score(round_num: int):
        q_ids = [q.id for q in db.query(Question.id).filter(Question.round_id == round_num).all()]
        total_rnd_score = 0.0
        for q_id in q_ids:
            best_sub = db.query(func.max(Submission.score)).filter(
                Submission.participant_id == participant_id,
                Submission.question_id == q_id
            ).scalar()
            if best_sub:
                total_rnd_score += float(best_sub)
        
        rnd_attempt = db.query(RoundAttempt).filter(
            RoundAttempt.participant_id == participant_id,
            RoundAttempt.round_id == round_num
        ).first()
        rnd_time = 0.0
        if rnd_attempt and rnd_attempt.start_time:
            s_time = rnd_attempt.start_time.replace(tzinfo=timezone.utc) if rnd_attempt.start_time.tzinfo is None else rnd_attempt.start_time
            end_t = rnd_attempt.submitted_at or datetime.now(timezone.utc)
            if end_t.tzinfo is None:
                end_t = end_t.replace(tzinfo=timezone.utc)
            rnd_time = max(0.0, (end_t - s_time).total_seconds())
            
        return total_rnd_score, rnd_time

    r2_score, r2_time = calc_round_coding_score(2)
    r3_score, r3_time = calc_round_coding_score(3)

    score_entry.round1_score = round(r1_score, 2)
    score_entry.round2_score = round(r2_score, 2)
    score_entry.round3_score = round(r3_score, 2)
    score_entry.total_score = round(r1_score + r2_score + r3_score, 2)
    
    score_entry.round1_time_sec = round(r1_time, 2)
    score_entry.round2_time_sec = round(r2_time, 2)
    score_entry.round3_time_sec = round(r3_time, 2)
    score_entry.total_time_sec = round(r1_time + r2_time + r3_time, 2)

    # Last accepted or submitted timestamp for tie-breaking
    latest_sub = db.query(func.max(Submission.submitted_at)).filter(
        Submission.participant_id == participant_id
    ).scalar()
    
    if latest_sub:
        score_entry.last_submission_timestamp = latest_sub
    else:
        score_entry.last_submission_timestamp = datetime.now(timezone.utc)

    db.commit()
    log_event("SCORE_UPDATED", f"Participant {participant_id} Total Score: {score_entry.total_score}", participant_id)
