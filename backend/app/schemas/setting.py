from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ContestSettingsOut(BaseModel):
    id: int
    contest_title: str
    subtitle: str
    maintenance_mode: bool
    lock_all_participants: bool
    leaderboard_visible: bool
    leaderboard_frozen: bool
    max_cheating_warnings: int
    max_participants: int
    run_code_rate_limit_sec: int
    submit_code_rate_limit_sec: int
    updated_at: datetime

    class Config:
        from_attributes = True

class ContestSettingsUpdate(BaseModel):
    contest_title: Optional[str] = None
    subtitle: Optional[str] = None
    maintenance_mode: Optional[bool] = None
    lock_all_participants: Optional[bool] = None
    leaderboard_visible: Optional[bool] = None
    leaderboard_frozen: Optional[bool] = None
    max_cheating_warnings: Optional[int] = None
    max_participants: Optional[int] = None
    run_code_rate_limit_sec: Optional[int] = None
    submit_code_rate_limit_sec: Optional[int] = None
