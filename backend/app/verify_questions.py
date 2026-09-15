import sys
from app.core.database import SessionLocal
import app.models.user
import app.models.round
import app.models.question
import app.models.submission
import app.models.activity
import app.models.violation
import app.models.leaderboard
import app.models.setting
from app.models.round import Round
from app.models.question import Question, QuestionOption, TestCase

def verify_competition_questions():
    db = SessionLocal()
    errors = []
    warnings = []

    print("=== ENGINEERING DAY 2026 QUESTION VERIFICATION ===")

    try:
        # 1. Verify Round 1 (20 MCQs, 20 Marks Total)
        r1_q = db.query(Question).filter(Question.round_id == 1).order_by(Question.order_index).all()
        print(f"Round 1 Questions Count: {len(r1_q)} (Expected: 20)")
        if len(r1_q) != 20:
            errors.append(f"Round 1 has {len(r1_q)} questions instead of 20.")
        
        r1_marks = sum(q.marks for q in r1_q)
        print(f"Round 1 Total Marks: {r1_marks} (Expected: 20.0)")
        if r1_marks != 20.0:
            errors.append(f"Round 1 total marks is {r1_marks} instead of 20.0.")

        for q in r1_q:
            if q.marks != 1.0:
                errors.append(f"Round 1 Question {q.order_index} marks = {q.marks} (Expected 1.0).")
            if q.negative_marks != 0.0:
                errors.append(f"Round 1 Question {q.order_index} negative marks = {q.negative_marks} (Expected 0.0).")
            opts = db.query(QuestionOption).filter(QuestionOption.question_id == q.id).all()
            if len(opts) != 4:
                errors.append(f"Round 1 Question {q.order_index} has {len(opts)} options (Expected 4).")
            correct_opts = [opt for opt in opts if opt.is_correct]
            if len(correct_opts) != 1:
                errors.append(f"Round 1 Question {q.order_index} has {len(correct_opts)} correct options (Expected 1).")

        # 2. Verify Round 2 (3 Debugging Problems, 30 Marks Total)
        r2_q = db.query(Question).filter(Question.round_id == 2).order_by(Question.order_index).all()
        print(f"Round 2 Problems Count: {len(r2_q)} (Expected: 3)")
        if len(r2_q) != 3:
            errors.append(f"Round 2 has {len(r2_q)} problems instead of 3.")

        r2_marks = sum(q.marks for q in r2_q)
        print(f"Round 2 Total Marks: {r2_marks} (Expected: 30.0)")
        if r2_marks != 30.0:
            errors.append(f"Round 2 total marks is {r2_marks} instead of 30.0.")

        for q in r2_q:
            if q.marks != 10.0:
                errors.append(f"Round 2 Problem {q.order_index} marks = {q.marks} (Expected 10.0).")
            if not q.code_snippet:
                errors.append(f"Round 2 Problem {q.order_index} missing starter code.")
            tcs = db.query(TestCase).filter(TestCase.question_id == q.id).all()
            if len(tcs) == 0:
                errors.append(f"Round 2 Problem {q.order_index} has 0 test cases.")

        # 3. Verify Round 3 (2 Coding Problems, 50 Marks Total)
        r3_q = db.query(Question).filter(Question.round_id == 3).order_by(Question.order_index).all()
        print(f"Round 3 Problems Count: {len(r3_q)} (Expected: 2)")
        if len(r3_q) != 2:
            errors.append(f"Round 3 has {len(r3_q)} problems instead of 2.")

        r3_marks = sum(q.marks for q in r3_q)
        print(f"Round 3 Total Marks: {r3_marks} (Expected: 50.0)")
        if r3_marks != 50.0:
            errors.append(f"Round 3 total marks is {r3_marks} instead of 50.0.")

        if len(r3_q) >= 2:
            if r3_q[0].marks != 20.0:
                errors.append(f"Round 3 Problem 1 marks = {r3_q[0].marks} (Expected 20.0).")
            if r3_q[1].marks != 30.0:
                errors.append(f"Round 3 Problem 2 marks = {r3_q[1].marks} (Expected 30.0).")

        for q in r3_q:
            tcs = db.query(TestCase).filter(TestCase.question_id == q.id).all()
            if len(tcs) == 0:
                errors.append(f"Round 3 Problem {q.order_index} has 0 test cases.")

        print("--------------------------------------------------")
        if errors:
            print("VERIFICATION FAILED WITH ERRORS:")
            for err in errors:
                print(f"  [ERROR] {err}")
            sys.exit(1)
        else:
            print("[SUCCESS] VERIFICATION PASSED! All question counts, marks, options, and test cases match authoritative rules.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_competition_questions()
