from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    round_id = Column(Integer, ForeignKey("rounds.id"), nullable=False, index=True)
    source_code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False) # c, cpp, java, python
    
    status = Column(String(50), nullable=False) # ACCEPTED, WRONG_ANSWER, COMPILATION_ERROR, RUNTIME_ERROR, TIME_LIMIT_EXCEEDED, SERVICE_UNAVAILABLE
    score = Column(Float, default=0.0)
    passed_test_cases = Column(Integer, default=0)
    total_test_cases = Column(Integer, default=0)
    execution_time_ms = Column(Float, nullable=True)
    memory_kb = Column(Float, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    compile_output = Column(Text, nullable=True)
    
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    participant = relationship("Participant", back_populates="submissions")

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("round_attempts.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    selected_option = Column(String(10), nullable=True) # A, B, C, D
    is_marked_for_review = Column(Boolean, default=False)
    is_correct = Column(Boolean, default=False)
    score_awarded = Column(Float, default=0.0)

    attempt = relationship("RoundAttempt", back_populates="quiz_answers")
