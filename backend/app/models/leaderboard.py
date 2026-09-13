from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"), unique=True, nullable=False, index=True)
    round1_score = Column(Float, default=0.0)
    round2_score = Column(Float, default=0.0)
    round3_score = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0, index=True)
    
    round1_time_sec = Column(Float, default=0.0)
    round2_time_sec = Column(Float, default=0.0)
    round3_time_sec = Column(Float, default=0.0)
    total_time_sec = Column(Float, default=0.0, index=True)
    
    last_submission_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    participant = relationship("Participant")
