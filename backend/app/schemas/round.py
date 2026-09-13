from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoundOut(BaseModel):
    id: int
    round_number: int
    title: str
    description: Optional[str] = None
    duration_minutes: int
    max_marks: float
    status: str
    allow_negative_marking: bool
    negative_mark_value: float
    max_attempts: int

    class Config:
        from_attributes = True

class RoundStatusUpdate(BaseModel):
    status: str # LOCKED, UPCOMING, ACTIVE, COMPLETED

class RoundAttemptOut(BaseModel):
    id: int
    round_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    remaining_seconds: int
    is_submitted: bool
    score: float

    class Config:
        from_attributes = True

class DraftSaveRequest(BaseModel):
    question_id: int
    round_id: int
    code: str
    language: str
