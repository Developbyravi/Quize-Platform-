from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User, Participant
from app.models.round import Round, RoundAttempt
from app.models.question import Question, QuestionOption, TestCase
from app.models.submission import Submission
from app.models.leaderboard import Score
from app.models.violation import Violation
from app.models.setting import ContestSettings
from app.schemas.round import RoundStatusUpdate
from app.schemas.setting import ContestSettingsOut, ContestSettingsUpdate
from app.schemas.question import QuestionCreateUpdate, QuestionOutAdmin
from pydantic import BaseModel
from app.models.activity import ActivityLog
from app.api.auth import get_current_admin
from app.core.security import get_password_hash
from app.utils.backup import export_database_snapshot
from app.core.logging import log_event
from app.services.scoring import update_participant_score

class ForceSubmitRequest(BaseModel):
    round_id: int
    reason: str

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    total_participants = db.query(Participant).count()
    active_participants = db.query(Participant).filter(Participant.is_disqualified == False).count()
    
    r1_completed = db.query(RoundAttempt).filter(RoundAttempt.round_id == 1, RoundAttempt.is_submitted == True).count()
    r2_completed = db.query(RoundAttempt).filter(RoundAttempt.round_id == 2, RoundAttempt.is_submitted == True).count()
    r3_completed = db.query(RoundAttempt).filter(RoundAttempt.round_id == 3, RoundAttempt.is_submitted == True).count()
    
    total_submissions = db.query(Submission).count()
    avg_score = db.query(func.avg(Score.total_score)).scalar() or 0.0
    highest_score = db.query(func.max(Score.total_score)).scalar() or 0.0

    return {
        "total_participants": total_participants,
        "active_participants": active_participants,
        "r1_completed": r1_completed,
        "r2_completed": r2_completed,
        "r3_completed": r3_completed,
        "total_submissions": total_submissions,
        "average_score": round(float(avg_score), 2),
        "highest_score": round(float(highest_score), 2)
    }

@router.get("/participants")
def get_participants(
    search: Optional[str] = None,
    disqualified_only: bool = False,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    query = db.query(Participant).join(User)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Participant.full_name.ilike(s)) |
            (User.email.ilike(s)) |
            (Participant.prn_student_id.ilike(s)) |
            (Participant.college_name.ilike(s))
        )
    if disqualified_only:
        query = query.filter(Participant.is_disqualified == True)

    parts = query.all()
    res = []
    for p in parts:
        res.append({
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
    return res

@router.post("/participants/{id}/disqualify")
def toggle_disqualification(id: int, reason: Optional[str] = "Admin Disqualification", db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    p = db.query(Participant).filter(Participant.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found.")
    
    p.is_disqualified = not p.is_disqualified
    p.disqualification_reason = reason if p.is_disqualified else None
    db.commit()

    log_event("PARTICIPANT_DISQUALIFY_TOGGLE", f"Participant {p.id} Disqualified: {p.is_disqualified}", current_admin.id)
    return {"message": f"Participant status updated. Disqualified: {p.is_disqualified}"}

@router.post("/participants/{id}/reset-password")
def reset_participant_password(id: int, new_password: str = "reset123", db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    p = db.query(Participant).filter(Participant.id == id).first()
    if not p or not p.user:
        raise HTTPException(status_code=404, detail="Participant user not found.")
    
    p.user.hashed_password = get_password_hash(new_password)
    db.commit()

    log_event("PASSWORD_RESET_ADMIN", f"Password reset for participant {p.id}", current_admin.id)
    return {"message": f"Password reset successfully for {p.full_name} to '{new_password}'."}

@router.get("/submissions")
def get_submissions(
    status_filter: Optional[str] = None,
    round_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    query = db.query(Submission).order_by(desc(Submission.submitted_at))
    if status_filter:
        query = query.filter(Submission.status == status_filter)
    if round_id:
        query = query.filter(Submission.round_id == round_id)

    subs = query.limit(100).all()
    res = []
    for s in subs:
        res.append({
            "id": s.id,
            "participant_name": s.participant.full_name if s.participant else "Unknown",
            "question_id": s.question_id,
            "round_id": s.round_id,
            "language": s.language,
            "status": s.status,
            "score": s.score,
            "passed_test_cases": s.passed_test_cases,
            "total_test_cases": s.total_test_cases,
            "execution_time_ms": s.execution_time_ms,
            "memory_kb": s.memory_kb,
            "source_code": s.source_code,
            "stdout": s.stdout,
            "stderr": s.stderr,
            "compile_output": s.compile_output,
            "submitted_at": s.submitted_at
        })
    return res

@router.put("/rounds/{id}/status")
def update_round_status(id: int, data: RoundStatusUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    rnd = db.query(Round).filter(Round.id == id).first()
    if not rnd:
        raise HTTPException(status_code=404, detail="Round not found.")
    
    rnd.status = data.status
    db.commit()

    log_event("ROUND_STATUS_CHANGED", f"Round {rnd.round_number} set to {data.status}", current_admin.id)
    return {"message": f"Round {rnd.round_number} status updated to {data.status}."}

@router.get("/settings", response_model=ContestSettingsOut)
def get_contest_settings(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    st = db.query(ContestSettings).first()
    if not st:
        st = ContestSettings()
        db.add(st)
        db.commit()
        db.refresh(st)
    return st

@router.put("/settings", response_model=ContestSettingsOut)
def update_contest_settings(data: ContestSettingsUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    st = db.query(ContestSettings).first()
    if not st:
        st = ContestSettings()
        db.add(st)

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(st, field, val)

    db.commit()
    db.refresh(st)
    log_event("SETTINGS_UPDATED", "Contest settings updated by admin.", current_admin.id)
    return st

@router.post("/emergency-lock")
def emergency_lock_participants(lock: bool = True, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    st = db.query(ContestSettings).first()
    if not st:
        st = ContestSettings()
        db.add(st)

    st.lock_all_participants = lock
    db.commit()
    log_event("EMERGENCY_LOCK", f"Lock All Participants: {lock}", current_admin.id)
    return {"message": f"Emergency Lock status set to: {lock}"}

@router.post("/maintenance-mode")
def toggle_maintenance_mode(enable: bool = True, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    st = db.query(ContestSettings).first()
    if not st:
        st = ContestSettings()
        db.add(st)

    st.maintenance_mode = enable
    db.commit()
    log_event("MAINTENANCE_MODE", f"Maintenance Mode set to: {enable}", current_admin.id)
    return {"message": f"Maintenance Mode set to: {enable}"}

@router.get("/export")
def export_contest_data(format: str = "json", db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    snapshot = export_database_snapshot(db)
    if format == "csv":
        # Return simple CSV of leaderboard results
        scores = db.query(Score).all()
        csv_lines = ["Rank,Participant Name,College,Department,Round 1,Round 2,Round 3,Total Score,Total Time (s)"]
        for sc in scores:
            p = sc.participant
            if p:
                csv_lines.append(f'"{p.full_name}","{p.college_name}","{p.department}",{sc.round1_score},{sc.round2_score},{sc.round3_score},{sc.total_score},{sc.total_time_sec}')
        csv_content = "\n".join(csv_lines)
        return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="contest_results.csv"'})
    return snapshot


# --- Question Management Endpoints ---

@router.get("/questions", response_model=List[QuestionOutAdmin])
def get_admin_questions(
    round_id: Optional[int] = None,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    query = db.query(Question)
    if round_id:
        query = query.filter(Question.round_id == round_id)
    if category:
        query = query.filter(Question.category == category)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (Question.title.ilike(s)) |
            (Question.description.ilike(s))
        )
    return query.order_by(Question.round_id, Question.order_index, Question.id).all()


@router.get("/questions/{id}", response_model=QuestionOutAdmin)
def get_admin_question_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")
    return q


@router.post("/questions", response_model=QuestionOutAdmin, status_code=status.HTTP_201_CREATED)
def create_question(
    data: QuestionCreateUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    # Validation logic per round
    if data.round_id == 1:
        if not data.options or len(data.options) < 2:
            raise HTTPException(status_code=400, detail="Round 1 MCQ questions require at least 2 options.")
        correct_count = sum(1 for opt in data.options if opt.is_correct)
        if correct_count != 1:
            raise HTTPException(status_code=400, detail="Round 1 MCQ questions must have exactly 1 correct option.")
    elif data.round_id in (2, 3):
        if not data.test_cases:
            raise HTTPException(status_code=400, detail="Round 2 & 3 coding questions must have at least 1 test case.")

    try:
        q = Question(
            round_id=data.round_id,
            title=data.title,
            description=data.description,
            code_snippet=data.code_snippet,
            category=data.category,
            marks=data.marks,
            negative_marks=data.negative_marks,
            difficulty=data.difficulty,
            language=data.language,
            order_index=data.order_index,
            input_format=data.input_format,
            output_format=data.output_format,
            constraints=data.constraints,
            sample_input=data.sample_input,
            sample_output=data.sample_output,
        )
        db.add(q)
        db.flush()

        if data.round_id == 1 and data.options:
            for opt in data.options:
                option_obj = QuestionOption(
                    question_id=q.id,
                    option_key=opt.option_key,
                    option_text=opt.option_text,
                    is_correct=opt.is_correct
                )
                db.add(option_obj)

        if data.round_id in (2, 3) and data.test_cases:
            for tc in data.test_cases:
                tc_obj = TestCase(
                    question_id=q.id,
                    input_data=tc.input_data,
                    expected_output=tc.expected_output,
                    is_hidden=tc.is_hidden,
                    weight=tc.weight
                )
                db.add(tc_obj)

        db.commit()
        db.refresh(q)
        log_event("QUESTION_CREATED", f"Admin created question {q.id} in Round {q.round_id}", current_admin.id)
        return q
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create question: {str(e)}")


@router.put("/questions/{id}", response_model=QuestionOutAdmin)
def update_question(
    id: int,
    data: QuestionCreateUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")

    if data.round_id == 1:
        if not data.options or len(data.options) < 2:
            raise HTTPException(status_code=400, detail="Round 1 MCQ questions require at least 2 options.")
        correct_count = sum(1 for opt in data.options if opt.is_correct)
        if correct_count != 1:
            raise HTTPException(status_code=400, detail="Round 1 MCQ questions must have exactly 1 correct option.")
    elif data.round_id in (2, 3):
        if not data.test_cases:
            raise HTTPException(status_code=400, detail="Round 2 & 3 coding questions must have at least 1 test case.")

    try:
        q.round_id = data.round_id
        q.title = data.title
        q.description = data.description
        q.code_snippet = data.code_snippet
        q.category = data.category
        q.marks = data.marks
        q.negative_marks = data.negative_marks
        q.difficulty = data.difficulty
        q.language = data.language
        q.order_index = data.order_index
        q.input_format = data.input_format
        q.output_format = data.output_format
        q.constraints = data.constraints
        q.sample_input = data.sample_input
        q.sample_output = data.sample_output

        # Clear existing options & test cases
        db.query(QuestionOption).filter(QuestionOption.question_id == q.id).delete()
        db.query(TestCase).filter(TestCase.question_id == q.id).delete()

        if data.round_id == 1 and data.options:
            for opt in data.options:
                option_obj = QuestionOption(
                    question_id=q.id,
                    option_key=opt.option_key,
                    option_text=opt.option_text,
                    is_correct=opt.is_correct
                )
                db.add(option_obj)

        if data.round_id in (2, 3) and data.test_cases:
            for tc in data.test_cases:
                tc_obj = TestCase(
                    question_id=q.id,
                    input_data=tc.input_data,
                    expected_output=tc.expected_output,
                    is_hidden=tc.is_hidden,
                    weight=tc.weight
                )
                db.add(tc_obj)

        db.commit()
        db.refresh(q)
        log_event("QUESTION_UPDATED", f"Admin updated question {q.id}", current_admin.id)
        return q
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update question: {str(e)}")


@router.delete("/questions/{id}")
def delete_question(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    q = db.query(Question).filter(Question.id == id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found.")

    try:
        db.delete(q)
        db.commit()
        log_event("QUESTION_DELETED", f"Admin deleted question {id}", current_admin.id)
        return {"message": "Question deleted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete question: {str(e)}")


@router.post("/questions/{id}/duplicate", response_model=QuestionOutAdmin)
def duplicate_question(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    orig = db.query(Question).filter(Question.id == id).first()
    if not orig:
        raise HTTPException(status_code=404, detail="Question not found.")

    try:
        new_q = Question(
            round_id=orig.round_id,
            title=f"{orig.title} (Copy)",
            description=orig.description,
            code_snippet=orig.code_snippet,
            category=orig.category,
            marks=orig.marks,
            negative_marks=orig.negative_marks,
            difficulty=orig.difficulty,
            language=orig.language,
            order_index=orig.order_index + 1,
            input_format=orig.input_format,
            output_format=orig.output_format,
            constraints=orig.constraints,
            sample_input=orig.sample_input,
            sample_output=orig.sample_output
        )
        db.add(new_q)
        db.flush()

        for opt in orig.options:
            db.add(QuestionOption(
                question_id=new_q.id,
                option_key=opt.option_key,
                option_text=opt.option_text,
                is_correct=opt.is_correct
            ))

        for tc in orig.test_cases:
            db.add(TestCase(
                question_id=new_q.id,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
                is_hidden=tc.is_hidden,
                weight=tc.weight
            ))

        db.commit()
        db.refresh(new_q)
        log_event("QUESTION_DUPLICATED", f"Admin duplicated question {orig.id} to new ID {new_q.id}", current_admin.id)
        return new_q
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to duplicate question: {str(e)}")


# --- Live Activity & Force Submit Endpoints ---

@router.get("/activity")
def get_admin_activity_feed(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    logs = db.query(ActivityLog).order_by(desc(ActivityLog.timestamp)).limit(limit).all()
    res = []
    for l in logs:
        res.append({
            "id": l.id,
            "user_id": l.user_id,
            "user_email": l.user.email if l.user else None,
            "event_type": l.event_type,
            "round_id": l.round_id,
            "question_id": l.question_id,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            "metadata_json": l.metadata_json,
            "ip_address": l.ip_address
        })
    return res


@router.get("/activity/{user_id}")
def get_user_activity_timeline(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    logs = db.query(ActivityLog).filter(ActivityLog.user_id == user_id).order_by(desc(ActivityLog.timestamp)).all()
    res = []
    for l in logs:
        res.append({
            "id": l.id,
            "user_id": l.user_id,
            "event_type": l.event_type,
            "round_id": l.round_id,
            "question_id": l.question_id,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            "metadata_json": l.metadata_json,
            "ip_address": l.ip_address
        })
    return res


@router.post("/participants/{id}/force-submit")
def force_submit_participant_round(
    id: int,
    data: ForceSubmitRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    p = db.query(Participant).filter(Participant.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found.")

    attempt = db.query(RoundAttempt).filter(
        RoundAttempt.participant_id == p.id,
        RoundAttempt.round_id == data.round_id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Round attempt not found for this participant.")

    attempt.is_submitted = True
    attempt.submitted_at = datetime.now(timezone.utc)
    attempt.submission_type = "ADMIN_FORCED"
    db.commit()

    update_participant_score(db, p.id)

    log = ActivityLog(
        user_id=p.user_id,
        event_type="ADMIN_FORCED_SUBMISSION",
        round_id=data.round_id,
        metadata_json=f'{{"admin_id": {current_admin.id}, "reason": "{data.reason}"}}'
    )
    db.add(log)
    db.commit()

    log_event("ADMIN_FORCED_SUBMISSION", f"Admin {current_admin.id} force submitted participant {p.id} Round {data.round_id}. Reason: {data.reason}", current_admin.id)

    return {
        "message": f"Participant's Round {data.round_id} has been force-submitted.",
        "status": "submitted",
        "submission_type": "ADMIN_FORCED",
        "reason": data.reason
    }


@router.get("/statistics")
def get_contest_statistics(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    # Round 1 stats
    r1_questions = db.query(Question).filter(Question.round_id == 1).all()
    r1_stats = []
    for q in r1_questions:
        ans_list = db.query(QuizAnswer).filter(QuizAnswer.question_id == q.id).all()
        total_ans = len(ans_list)
        correct_ans = sum(1 for a in ans_list if a.is_correct)
        incorrect_ans = total_ans - correct_ans
        r1_stats.append({
            "question_id": q.id,
            "title": q.title,
            "order_index": q.order_index,
            "total_answers": total_ans,
            "correct": correct_ans,
            "incorrect": incorrect_ans,
            "accuracy": round((correct_ans / total_ans * 100), 1) if total_ans > 0 else 0.0
        })

    # Round 2 & 3 stats
    def coding_stats(round_id: int):
        q_list = db.query(Question).filter(Question.round_id == round_id).all()
        res = []
        for q in q_list:
            subs = db.query(Submission).filter(Submission.question_id == q.id).all()
            total_subs = len(subs)
            accepted_subs = sum(1 for s in subs if s.status == "ACCEPTED")
            comp_errs = sum(1 for s in subs if s.status == "COMPILATION_ERROR")
            runtime_errs = sum(1 for s in subs if s.status == "RUNTIME_ERROR")
            avg_score = (sum(s.score for s in subs) / total_subs) if total_subs > 0 else 0.0
            res.append({
                "question_id": q.id,
                "title": q.title,
                "order_index": q.order_index,
                "total_submissions": total_subs,
                "accepted": accepted_subs,
                "compilation_errors": comp_errs,
                "runtime_errors": runtime_errs,
                "average_score": round(avg_score, 2),
                "max_marks": q.marks
            })
        return res

    return {
        "round1_mcq_stats": r1_stats,
        "round2_debug_stats": coding_stats(2),
        "round3_coding_stats": coding_stats(3)
    }


