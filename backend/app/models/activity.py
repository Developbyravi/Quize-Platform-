from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True) # REGISTER, LOGIN, ROUND_STARTED, QUESTION_VIEWED, ANSWER_SELECTED, CODE_RUN, CODE_SUBMITTED, ROUND_SUBMITTED, AUTO_SUBMITTED, TAB_SWITCH, PAGE_HIDDEN, ADMIN_FORCED_SUBMISSION, etc.
    round_id = Column(Integer, ForeignKey("rounds.id"), nullable=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    metadata_json = Column(Text, nullable=True)
    ip_address = Column(String(100), nullable=True)
    user_agent = Column(String(255), nullable=True)

    user = relationship("User")
    round = relationship("Round")
    question = relationship("Question")
