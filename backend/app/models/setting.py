from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime, timezone
from app.core.database import Base

class ContestSettings(Base):
    __tablename__ = "contest_settings"

    id = Column(Integer, primary_key=True, index=True)
    contest_title = Column(String(255), default="Engineering Day Coding Challenge")
    subtitle = Column(String(255), default="Engineering Day 2026 — Coding Competition")
    
    maintenance_mode = Column(Boolean, default=False)
    lock_all_participants = Column(Boolean, default=False)
    
    leaderboard_visible = Column(Boolean, default=True)
    leaderboard_frozen = Column(Boolean, default=False)
    
    max_cheating_warnings = Column(Integer, default=3)
    max_participants = Column(Integer, default=100)
    
    run_code_rate_limit_sec = Column(Integer, default=3)
    submit_code_rate_limit_sec = Column(Integer, default=5)
    
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
