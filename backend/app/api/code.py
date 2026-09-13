from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from app.core.database import get_db
from app.models.round import Round, RoundAttempt, CodeDraft
from app.models.user import User, Participant
from app.models.question import Question, TestCase
from app.models.submission import Submission
from app.models.setting import ContestSettings
from app.schemas.submission import CodeRunRequest, CodeSubmitRequest, CodeExecutionResult, SubmissionOut
from app.schemas.round import DraftSaveRequest
from app.api.auth import get_current_user
from app.api.rounds import check_contest_accessible
from app.services.timer import validate_attempt_active
from app.services.judge0 import judge0_service
from app.services.scoring import update_participant_score
from app.core.ratelimit import rate_limiter
from app.core.logging import log_event

router = APIRouter(prefix="/code", tags=["Code Execution"])

@router.post("/autosave")
def save_code_draft(data: DraftSaveRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    participant = current_user.participant_profile
    if not participant:
        raise HTTPException(status_code=403, detail="Participant profile missing.")

    draft = db.query(CodeDraft).filter(
        CodeDraft.participant_id == participant.id,
        CodeDraft.question_id == data.question_id
    ).first()

    if not draft:
        draft = CodeDraft(
            participant_id=participant.id,
            question_id=data.question_id,
            round_id=data.round_id,
            code=data.code,
            language=data.language
        )
        db.add(draft)
    else:
        draft.code = data.code
        draft.language = data.language
        draft.updated_at = datetime.now(timezone.utc)

    db.commit()
    return {"message": "Draft autosaved successfully."}

@router.get("/draft/{question_id}")
def get_code_draft(question_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    participant = current_user.participant_profile
    if not participant:
        raise HTTPException(status_code=403, detail="Participant profile missing.")

    draft = db.query(CodeDraft).filter(
        CodeDraft.participant_id == participant.id,
        CodeDraft.question_id == question_id
    ).first()

    if not draft:
        return {"code": None, "language": None}
    return {"code": draft.code, "language": draft.language, "updated_at": draft.updated_at}

@router.post("/run", response_model=CodeExecutionResult)
async def run_code(data: CodeRunRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    participant = current_user.participant_profile
    if not participant:
        raise HTTPException(status_code=403, detail="Participant profile missing.")

    # 1. Rate limit check
    settings = db.query(ContestSettings).first()
    limit_sec = settings.run_code_rate_limit_sec if settings else 3
    rate_limiter.check_rate_limit(user_id=participant.id, action="run_code", min_interval_sec=limit_sec)

    # 2. Question & attempt validation
    question = db.query(Question).filter(Question.id == data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    rnd = db.query(Round).filter(Round.id == data.round_id).first()
    attempt = db.query(RoundAttempt).filter(
        RoundAttempt.participant_id == participant.id,
        RoundAttempt.round_id == data.round_id
    ).first()

    if attempt:
        validate_attempt_active(db, attempt, rnd)

    # Use custom input or sample input
    stdin_input = data.custom_input if data.custom_input is not None else (question.sample_input or "")

    # Execute via Judge0
    result = await judge0_service.execute_code(
        source_code=data.source_code,
        language=data.language,
        stdin_data=stdin_input,
        expected_output=None
    )

    log_event("CODE_RUN", f"Q: {question.id}, Status: {result['status']}", participant.id)
    return result

@router.post("/submit", response_model=CodeExecutionResult)
async def submit_code(data: CodeSubmitRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    participant = current_user.participant_profile
    if not participant:
        raise HTTPException(status_code=403, detail="Participant profile missing.")

    # 1. Rate limit check
    settings = db.query(ContestSettings).first()
    limit_sec = settings.submit_code_rate_limit_sec if settings else 5
    rate_limiter.check_rate_limit(user_id=participant.id, action="submit_code", min_interval_sec=limit_sec)

    # 2. Question & round attempt validation
    question = db.query(Question).filter(Question.id == data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    rnd = db.query(Round).filter(Round.id == data.round_id).first()
    attempt = db.query(RoundAttempt).filter(
        RoundAttempt.participant_id == participant.id,
        RoundAttempt.round_id == data.round_id
    ).first()

    if not attempt:
        raise HTTPException(status_code=400, detail="Must start round attempt before submitting code.")

    validate_attempt_active(db, attempt, rnd)

    # 3. Fetch test cases (including hidden test cases)
    test_cases = db.query(TestCase).filter(TestCase.question_id == question.id).all()
    if not test_cases:
        # Fallback to sample input/output if no test cases defined
        test_cases = [TestCase(input_data=question.sample_input or "", expected_output=question.sample_output or "", is_hidden=False)]

    total_cases = len(test_cases)
    passed_cases = 0
    total_exec_time = 0.0
    max_memory = 0.0

    last_status = "ACCEPTED"
    last_stdout = ""
    last_stderr = ""
    last_compile = ""

    for tc in test_cases:
        res = await judge0_service.execute_code(
            source_code=data.source_code,
            language=data.language,
            stdin_data=tc.input_data,
            expected_output=None
        )

        if res["status"] == "SERVICE_UNAVAILABLE":
            return res

        if res.get("time"):
            total_exec_time += res["time"]
        if res.get("memory"):
            max_memory = max(max_memory, res["memory"])

        last_stdout = res.get("stdout") or ""
        last_stderr = res.get("stderr") or ""
        last_compile = res.get("compile_output") or ""

        # Compare actual output against expected output
        actual_out = (res.get("stdout") or "").strip()
        exp_out = (tc.expected_output or "").strip()

        if res["status"] == "ACCEPTED" and actual_out == exp_out:
            passed_cases += 1
        else:
            if res["status"] != "ACCEPTED":
                last_status = res["status"]
            else:
                last_status = "WRONG_ANSWER"

    # Calculate partial score
    pass_ratio = passed_cases / total_cases if total_cases > 0 else 0.0
    final_status = "ACCEPTED" if passed_cases == total_cases else last_status
    awarded_score = round(pass_ratio * question.marks, 2)

    # Create submission record
    sub = Submission(
        participant_id=participant.id,
        question_id=question.id,
        round_id=data.round_id,
        source_code=data.source_code,
        language=data.language,
        status=final_status,
        score=awarded_score,
        passed_test_cases=passed_cases,
        total_test_cases=total_cases,
        execution_time_ms=round(total_exec_time, 2),
        memory_kb=round(max_memory, 2),
        stdout=last_stdout if passed_cases > 0 else None,
        stderr=last_stderr if last_stderr else None,
        compile_output=last_compile if last_compile else None
    )
    db.add(sub)
    db.commit()

    # Recalculate global scores & update leaderboard
    update_participant_score(db, participant.id)

    log_event("CODE_SUBMITTED", f"Q: {question.id}, Score: {awarded_score} ({passed_cases}/{total_cases} passed)", participant.id)

    return {
        "status": final_status,
        "score": awarded_score,
        "passed_test_cases": passed_cases,
        "total_test_cases": total_cases,
        "execution_time_ms": round(total_exec_time, 2),
        "memory_kb": round(max_memory, 2),
        "stdout": last_stdout if final_status == "ACCEPTED" else "Test case output hidden for security.",
        "stderr": last_stderr if last_stderr else None,
        "compile_output": last_compile if last_compile else None,
        "error_message": None
    }
