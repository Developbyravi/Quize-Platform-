from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="participant", nullable=False) # participant / admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    participant_profile = relationship("Participant", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    mobile_number = Column(String(50), unique=True, index=True, nullable=False)
    college_name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    year = Column(String(50), nullable=False)
    prn_student_id = Column(String(100), unique=True, index=True, nullable=False)
    
    is_disqualified = Column(Boolean, default=False)
    disqualification_reason = Column(Text, nullable=True)
    violations_count = Column(Integer, default=0)

    user = relationship("User", back_populates="participant_profile")
    attempts = relationship("RoundAttempt", back_populates="participant", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="participant", cascade="all, delete-orphan")
    code_drafts = relationship("CodeDraft", back_populates="participant", cascade="all, delete-orphan")
    violations = relationship("Violation", back_populates="participant", cascade="all, delete-orphan")
