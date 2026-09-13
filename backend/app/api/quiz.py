from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.round import Round, RoundAttempt
from app.models.question import Question, QuestionOption
from app.models.user import User, Participant
from app.models.submission import QuizAnswer
from app.schemas.question import QuestionOutParticipant
from app.schemas.quiz import QuizAnswerSave, QuizStateOut
from app.api.auth import get_current_user
from app.api.rounds import check_contest_accessible
from app.services.timer import get_remaining_seconds, validate_attempt_active
from app.services.scoring import update_participant_score
from app.core.logging import log_event

router = APIRouter(prefix="/quiz", tags=["Quiz (Round 1)"])

@router.get("/{round_id}/questions", response_model=List[QuestionOutParticipant])
def get_quiz_questions(round_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    rnd = db.query(Round).filter(Round.id == round_id).first()
    if not rnd:
        rnd = db.query(Round).filter(Round.round_number == round_id).first()
    if not rnd or rnd.status != "ACTIVE":
        raise HTTPException(status_code=403, detail=f"Round {round_id} is not currently active.")

    questions = db.query(Question).filter(Question.round_id == rnd.id).order_by(Question.order_index).all()
    res = []
    for q in questions:
        q_out = QuestionOutParticipant.model_validate(q)
        q_out.sample_test_cases = [tc for tc in q.test_cases if not tc.is_hidden]
        res.append(q_out)
    return res

@router.get("/1/state", response_model=QuizStateOut)
def get_quiz_state(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    participant = current_user.participant_profile
    if not participant:
        raise HTTPException(status_code=403, detail="Participant profile missing.")

    rnd = db.query(Round).filter(Round.round_number == 1).first()
    attempt = db.query(RoundAttempt).filter(
        RoundAttempt.participant_id == participant.id,
        RoundAttempt.round_id == rnd.id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Round 1 has not been started yet.")

    remaining = get_remaining_seconds(attempt, rnd)

    # Fetch all saved answers for state restoration
    saved_answers = db.query(QuizAnswer).filter(QuizAnswer.attempt_id == attempt.id).all()
    answers_list = [
        {
            "question_id": ans.question_id,
            "selected_option": ans.selected_option,
            "is_marked_for_review": ans.is_marked_for_review
        }
        for ans in saved_answers
    ]

    return {
        "round_id": rnd.id,
        "attempt_id": attempt.id,
        "remaining_seconds": remaining,
        "is_submitted": attempt.is_submitted,
        "answers": answers_list
    }

@router.post("/1/answer")
def save_quiz_answer(data: QuizAnswerSave, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    participant = current_user.participant_profile
    if not participant:
        raise HTTPException(status_code=403, detail="Participant profile required.")

    rnd = db.query(Round).filter(Round.round_number == 1).first()
    attempt = db.query(RoundAttempt).filter(
        RoundAttempt.participant_id == participant.id,
        RoundAttempt.round_id == rnd.id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="No active attempt found.")

    validate_attempt_active(db, attempt, rnd)

    # Upsert quiz answer
    answer = db.query(QuizAnswer).filter(
        QuizAnswer.attempt_id == attempt.id,
        QuizAnswer.question_id == data.question_id
    ).first()

    if not answer:
        answer = QuizAnswer(
            attempt_id=attempt.id,
            question_id=data.question_id,
            selected_option=data.selected_option,
            is_marked_for_review=data.is_marked_for_review
        )
        db.add(answer)
    else:
        answer.selected_option = data.selected_option
        answer.is_marked_for_review = data.is_marked_for_review

    db.commit()
    return {"message": "Answer saved incrementally."}

@router.post("/1/submit")
def submit_quiz_round(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    check_contest_accessible(db, current_user)
    participant = current_user.participant_profile
    if not participant:
        raise HTTPException(status_code=403, detail="Participant profile required.")

    rnd = db.query(Round).filter(Round.round_number == 1).first()
    attempt = db.query(RoundAttempt).filter(
        RoundAttempt.participant_id == participant.id,
        RoundAttempt.round_id == rnd.id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="No active attempt found.")

    if attempt.is_submitted:
        raise HTTPException(status_code=400, detail="Round 1 has already been submitted.")

    # Calculate final score for Round 1
    questions = db.query(Question).filter(Question.round_id == rnd.id).all()
    saved_answers = {
        ans.question_id: ans for ans in db.query(QuizAnswer).filter(QuizAnswer.attempt_id == attempt.id).all()
    }

    total_score = 0.0
    correct_count = 0
    wrong_count = 0

    for q in questions:
        correct_opt = db.query(QuestionOption).filter(
            QuestionOption.question_id == q.id,
            QuestionOption.is_correct == True
        ).first()

        ans = saved_answers.get(q.id)
        if ans and ans.selected_option:
            if correct_opt and ans.selected_option == correct_opt.option_key:
                ans.is_correct = True
                ans.score_awarded = q.marks
                total_score += q.marks
                correct_count += 1
            else:
                ans.is_correct = False
                penalty = q.negative_marks if rnd.allow_negative_marking else 0.0
                ans.score_awarded = -penalty
                total_score -= penalty
                wrong_count += 1

    attempt.score = max(0.0, round(total_score, 2))
    attempt.is_submitted = True
    attempt.submitted_at = datetime.now(timezone.utc)
    db.commit()

    update_participant_score(db, participant.id)
    log_event("ROUND1_SUBMITTED", f"Score: {attempt.score} (Correct: {correct_count}, Wrong: {wrong_count})", participant.id)

    return {
        "message": "Round 1 submitted successfully.",
        "score": attempt.score,
        "correct_answers": correct_count,
        "wrong_answers": wrong_count,
        "total_questions": len(questions)
    }
