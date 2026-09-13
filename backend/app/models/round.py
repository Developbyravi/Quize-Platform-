from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Round(Base):
    __tablename__ = "rounds"

    id = Column(Integer, primary_key=True, index=True)
    round_number = Column(Integer, unique=True, index=True, nullable=False) # 1, 2, 3
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=30)
    max_marks = Column(Float, default=100.0)
    status = Column(String(50), default="LOCKED", nullable=False) # LOCKED, UPCOMING, ACTIVE, COMPLETED
    allow_negative_marking = Column(Boolean, default=False)
    negative_mark_value = Column(Float, default=0.25)
    max_attempts = Column(Integer, default=1)
    
    questions = relationship("Question", back_populates="round", cascade="all, delete-orphan")
    attempts = relationship("RoundAttempt", back_populates="round", cascade="all, delete-orphan")

class RoundAttempt(Base):
    __tablename__ = "round_attempts"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False, index=True)
    round_id = Column(Integer, ForeignKey("rounds.id"), nullable=False, index=True)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_time = Column(DateTime, nullable=True) # Expected max end time
    submitted_at = Column(DateTime, nullable=True)
    is_submitted = Column(Boolean, default=False, index=True)
    score = Column(Float, default=0.0)
    
    participant = relationship("Participant", back_populates="attempts")
    round = relationship("Round", back_populates="attempts")
    quiz_answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete-orphan")

class CodeDraft(Base):
    __tablename__ = "code_drafts"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    round_id = Column(Integer, ForeignKey("rounds.id"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    participant = relationship("Participant", back_populates="code_drafts")
