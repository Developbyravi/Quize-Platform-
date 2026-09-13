from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LeaderboardEntry(BaseModel):
    rank: int
    participant_id: int
    full_name: str
    college_name: str
    department: str
    round1_score: float
    round2_score: float
    round3_score: float
    total_score: float
    total_time_sec: float
    last_submission_timestamp: datetime
    is_disqualified: bool = False

    class Config:
        from_attributes = True

class LeaderboardOut(BaseModel):
    is_visible: bool
    is_frozen: bool
    entries: List[LeaderboardEntry]
