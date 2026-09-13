from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User, Participant
from app.models.round import Round, RoundAttempt, CodeDraft
from app.models.question import Question, QuestionOption, TestCase
from app.models.submission import Submission, QuizAnswer
from app.models.leaderboard import Score
from app.models.violation import Violation
from app.models.setting import ContestSettings

def export_database_snapshot(db: Session) -> dict:
    """
    Safely exports complete competition state as a JSON-serializable dictionary.
    Excludes hashed passwords from public export.
    """
    participants = []
    for p in db.query(Participant).all():
        participants.append({
            "id": p.id,
            "user_id": p.user_id,
            "full_name": p.full_name,
            "email": p.user.email if p.user else "",
            "mobile_number": p.mobile_number,
            "college_name": p.college_name,
            "department": p.department,
            "year": p.year,
            "prn_student_id": p.prn_student_id,
            "is_disqualified": p.is_disqualified,
            "disqualification_reason": p.disqualification_reason,
            "violations_count": p.violations_count
        })

    rounds = []
    for r in db.query(Round).all():
        rounds.append({
            "id": r.id,
            "round_number": r.round_number,
            "title": r.title,
            "duration_minutes": r.duration_minutes,
            "max_marks": r.max_marks,
            "status": r.status
        })

    questions = []
    for q in db.query(Question).all():
        questions.append({
            "id": q.id,
            "round_id": q.round_id,
            "title": q.title,
            "description": q.description,
            "category": q.category,
            "marks": q.marks,
            "difficulty": q.difficulty,
            "language": q.language
        })

    submissions = []
    for s in db.query(Submission).all():
        submissions.append({
            "id": s.id,
            "participant_id": s.participant_id,
            "question_id": s.question_id,
            "round_id": s.round_id,
            "language": s.language,
            "status": s.status,
            "score": s.score,
            "passed_test_cases": s.passed_test_cases,
            "total_test_cases": s.total_test_cases,
            "execution_time_ms": s.execution_time_ms,
            "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None
        })

    scores = []
    for sc in db.query(Score).all():
        scores.append({
            "participant_id": sc.participant_id,
            "round1_score": sc.round1_score,
            "round2_score": sc.round2_score,
            "round3_score": sc.round3_score,
            "total_score": sc.total_score,
            "total_time_sec": sc.total_time_sec,
            "last_submission_timestamp": sc.last_submission_timestamp.isoformat() if sc.last_submission_timestamp else None
        })

    return {
        "exported_at": datetime.utcnow().isoformat(),
        "participants_count": len(participants),
        "submissions_count": len(submissions),
        "participants": participants,
        "rounds": rounds,
        "questions": questions,
        "submissions": submissions,
        "scores": scores
    }
