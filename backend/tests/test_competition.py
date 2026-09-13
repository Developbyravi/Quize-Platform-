import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User, Participant
from app.models.round import Round, RoundAttempt
from app.models.question import Question, QuestionOption, TestCase
from app.models.setting import ContestSettings
from app.models.leaderboard import Score
from app.core.ratelimit import rate_limiter

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_competition.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    rate_limiter._last_call.clear()
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    st = ContestSettings(maintenance_mode=False, lock_all_participants=False)
    db.add(st)
    r1 = Round(round_number=1, title="R1", duration_minutes=20, status="ACTIVE")
    r2 = Round(round_number=2, title="R2", duration_minutes=35, status="ACTIVE")
    r3 = Round(round_number=3, title="R3", duration_minutes=60, status="ACTIVE")
    db.add_all([r1, r2, r3])
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def get_auth_headers(email="student@engday.edu", prn="PRN001", mobile="9999999999"):
    res = client.post("/api/auth/register", json={
        "full_name": "Test Student",
        "email": email,
        "mobile_number": mobile,
        "college_name": "COEP Tech",
        "department": "CSE",
        "year": "TE",
        "prn_student_id": prn,
        "password": "password123"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_participant_registration_and_login():
    res = client.post("/api/auth/register", json={
        "full_name": "John Doe",
        "email": "john@engday.edu",
        "mobile_number": "9876543210",
        "college_name": "COEP",
        "department": "CSE",
        "year": "BE",
        "prn_student_id": "PRN100",
        "password": "password123"
    })
    assert res.status_code == 201
    assert "access_token" in res.json()

    login_res = client.post("/api/auth/login", json={
        "email": "john@engday.edu",
        "password": "password123"
    })
    assert login_res.status_code == 200
    assert login_res.json()["role"] == "participant"

def test_maintenance_mode_enforcement():
    headers = get_auth_headers("maint@engday.edu", "PRN_MAINT", "9000000001")
    db = TestingSessionLocal()
    st = db.query(ContestSettings).first()
    st.maintenance_mode = True
    db.commit()
    db.close()

    res = client.get("/api/rounds", headers=headers)
    assert res.status_code == 503
    assert "Maintenance Mode" in res.json()["detail"]

def test_emergency_participant_lock():
    headers = get_auth_headers("lock@engday.edu", "PRN_LOCK", "9000000002")
    db = TestingSessionLocal()
    st = db.query(ContestSettings).first()
    st.lock_all_participants = True
    db.commit()
    db.close()

    res = client.get("/api/rounds", headers=headers)
    assert res.status_code == 403
    assert "locked by competition administrators" in res.json()["detail"]

def test_autosave_and_draft_recovery():
    headers = get_auth_headers("draft@engday.edu", "PRN_DRAFT", "9000000003")
    
    res = client.post("/api/code/autosave", headers=headers, json={
        "question_id": 1,
        "round_id": 2,
        "code": "def solve(): return 42",
        "language": "python"
    })
    assert res.status_code == 200

    get_res = client.get("/api/code/draft/1", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["code"] == "def solve(): return 42"

def test_rate_limiting_on_run_code():
    headers = get_auth_headers("rate@engday.edu", "PRN_RATE", "9000000004")
    db = TestingSessionLocal()
    q = Question(id=1, round_id=2, title="Q1", description="desc", language="python")
    db.add(q)
    db.commit()
    db.close()

    client.post("/api/rounds/2/start", headers=headers)

    client.post("/api/code/run", headers=headers, json={
        "question_id": 1,
        "round_id": 2,
        "source_code": "print('hello')",
        "language": "python"
    })

    res = client.post("/api/code/run", headers=headers, json={
        "question_id": 1,
        "round_id": 2,
        "source_code": "print('hello')",
        "language": "python"
    })
    assert res.status_code == 429
    assert "Rate limit exceeded" in res.json()["detail"]

def test_judge0_fail_safe_messaging():
    headers = get_auth_headers("j0fail@engday.edu", "PRN_J0FAIL", "9000000005")
    db = TestingSessionLocal()
    q = Question(id=1, round_id=2, title="Q1", description="desc", language="python")
    db.add(q)
    db.commit()
    db.close()

    client.post("/api/rounds/2/start", headers=headers)

    res = client.post("/api/code/run", headers=headers, json={
        "question_id": 1,
        "round_id": 2,
        "source_code": "print('test')",
        "language": "python"
    })
    assert res.status_code == 200
    assert res.json()["status"] == "SERVICE_UNAVAILABLE"
    assert "Code execution service unavailable" in res.json()["error_message"]

def test_leaderboard_tie_breaking():
    db = TestingSessionLocal()
    
    u1 = User(email="u1@engday.edu", hashed_password="pw", role="participant")
    u2 = User(email="u2@engday.edu", hashed_password="pw", role="participant")
    db.add_all([u1, u2])
    db.commit()

    p1 = Participant(user_id=u1.id, full_name="Alice", mobile_number="1111111111", college_name="C1", department="D1", year="1", prn_student_id="PRN_A")
    p2 = Participant(user_id=u2.id, full_name="Bob", mobile_number="2222222222", college_name="C2", department="D2", year="2", prn_student_id="PRN_B")
    db.add_all([p1, p2])
    db.commit()

    s1 = Score(participant_id=p1.id, total_score=100.0, total_time_sec=120.0)
    s2 = Score(participant_id=p2.id, total_score=100.0, total_time_sec=200.0)
    db.add_all([s1, s2])
    db.commit()
    db.close()

    headers = get_auth_headers("lb_viewer@engday.edu", "PRN_LB_VIEW", "9000000006")
    res = client.get("/api/leaderboard", headers=headers)
    assert res.status_code == 200
    entries = res.json()["entries"]
    
    alice_entry = [e for e in entries if e["full_name"] == "Alice"][0]
    bob_entry = [e for e in entries if e["full_name"] == "Bob"][0]
    assert alice_entry["rank"] < bob_entry["rank"]

from app.core.security import create_access_token

def get_admin_headers():
    db = TestingSessionLocal()
    admin_user = User(email="admin_test@engday.edu", hashed_password="adminpassword", role="admin")
    db.add(admin_user)
    db.commit()
    token = create_access_token(admin_user.id, "admin")
    db.close()
    return {"Authorization": f"Bearer {token}"}

def test_admin_question_crud_round1_mcq():
    headers = get_admin_headers()
    
    # 1. Create MCQ Question
    payload = {
        "round_id": 1,
        "title": "What is Python?",
        "description": "Select correct statement about Python programming.",
        "category": "Python",
        "marks": 5.0,
        "negative_marks": 1.0,
        "difficulty": "Easy",
        "language": "python",
        "order_index": 1,
        "options": [
            {"option_key": "A", "option_text": "Interpreted language", "is_correct": True},
            {"option_key": "B", "option_text": "Compiled only language", "is_correct": False},
            {"option_key": "C", "option_text": "Hardware language", "is_correct": False},
            {"option_key": "D", "option_text": "None of the above", "is_correct": False}
        ]
    }
    create_res = client.post("/api/admin/questions", headers=headers, json=payload)
    assert create_res.status_code == 201
    q_data = create_res.json()
    assert q_data["title"] == "What is Python?"
    assert len(q_data["options"]) == 4
    q_id = q_data["id"]

    # 2. Get Question
    get_res = client.get(f"/api/admin/questions/{q_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["category"] == "Python"

    # 3. Duplicate Question
    dup_res = client.post(f"/api/admin/questions/{q_id}/duplicate", headers=headers)
    assert dup_res.status_code == 200
    assert dup_res.json()["title"] == "What is Python? (Copy)"
    dup_id = dup_res.json()["id"]

    # 4. Delete Duplicated Question
    del_res = client.delete(f"/api/admin/questions/{dup_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["message"] == "Question deleted successfully."

def test_admin_question_crud_round3_coding_and_schema_security():
    headers = get_admin_headers()
    
    payload = {
        "round_id": 3,
        "title": "Two Sum Problem",
        "description": "Find indices of two numbers that add up to target.",
        "category": "DSA",
        "marks": 20.0,
        "negative_marks": 0.0,
        "difficulty": "Medium",
        "language": "python",
        "order_index": 1,
        "input_format": "N\nArray elements\nTarget",
        "output_format": "Space separated indices",
        "test_cases": [
            {"input_data": "4\n2 7 11 15\n9", "expected_output": "0 1", "is_hidden": False, "weight": 1.0},
            {"input_data": "3\n3 2 4\n6", "expected_output": "1 2", "is_hidden": True, "weight": 1.0}
        ]
    }
    create_res = client.post("/api/admin/questions", headers=headers, json=payload)
    assert create_res.status_code == 201
    q_id = create_res.json()["id"]

    # Admin GET sees hidden test cases
    admin_get = client.get(f"/api/admin/questions/{q_id}", headers=headers)
    assert admin_get.status_code == 200
    assert len(admin_get.json()["test_cases"]) == 2

    # Participant GET quiz questions filters hidden test cases
    participant_headers = get_auth_headers("part_sec@engday.edu", "PRN_SEC", "9000000099")
    part_get = client.get("/api/quiz/3/questions", headers=participant_headers)
    assert part_get.status_code == 200
    p_questions = part_get.json()
    p_q = [q for q in p_questions if q["id"] == q_id][0]
    # Verify participant only sees sample_test_cases where is_hidden == False
    assert "test_cases" not in p_q or p_q.get("test_cases") is None
    assert len(p_q.get("sample_test_cases", [])) == 1
    assert p_q["sample_test_cases"][0]["is_hidden"] is False

def test_admin_question_validation_errors():
    headers = get_admin_headers()

    # R1 without options
    res1 = client.post("/api/admin/questions", headers=headers, json={
        "round_id": 1,
        "title": "Invalid MCQ",
        "description": "No options provided",
        "options": []
    })
    assert res1.status_code == 400

    # R3 without test cases
    res2 = client.post("/api/admin/questions", headers=headers, json={
        "round_id": 3,
        "title": "Invalid Coding",
        "description": "No test cases provided",
        "test_cases": []
    })
    assert res2.status_code == 400

