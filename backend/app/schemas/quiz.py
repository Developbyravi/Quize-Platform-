from pydantic import BaseModel
from typing import Optional, List

class QuizAnswerSave(BaseModel):
    question_id: int
    selected_option: Optional[str] = None
    is_marked_for_review: bool = False

class QuizStateOut(BaseModel):
    round_id: int
    attempt_id: int
    remaining_seconds: int
    is_submitted: bool
    answers: List[dict] # question_id -> {selected_option, is_marked_for_review}
