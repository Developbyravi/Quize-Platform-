from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CodeRunRequest(BaseModel):
    question_id: int
    round_id: int
    source_code: str
    language: str # c, cpp, java, python
    custom_input: Optional[str] = None

class CodeSubmitRequest(BaseModel):
    question_id: int
    round_id: int
    source_code: str
    language: str # c, cpp, java, python

class CodeExecutionResult(BaseModel):
    status: str # ACCEPTED, WRONG_ANSWER, COMPILATION_ERROR, RUNTIME_ERROR, TIME_LIMIT_EXCEEDED, SERVICE_UNAVAILABLE
    score: float = 0.0
    passed_test_cases: int = 0
    total_test_cases: int = 0
    execution_time_ms: Optional[float] = None
    memory_kb: Optional[float] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None
    error_message: Optional[str] = None

class SubmissionOut(BaseModel):
    id: int
    participant_id: int
    question_id: int
    round_id: int
    language: str
    status: str
    score: float
    passed_test_cases: int
    total_test_cases: int
    execution_time_ms: Optional[float] = None
    memory_kb: Optional[float] = None
    submitted_at: datetime

    class Config:
        from_attributes = True
