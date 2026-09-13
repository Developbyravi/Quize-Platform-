from pydantic import BaseModel, Field
from typing import Optional, List

# --- Option Schemas ---
class OptionCreate(BaseModel):
    option_key: str = Field(..., description="Option key (e.g., A, B, C, D)")
    option_text: str = Field(..., min_length=1)
    is_correct: bool = False

class OptionOutParticipant(BaseModel):
    id: int
    option_key: str
    option_text: str

    class Config:
        from_attributes = True

class OptionOutAdmin(BaseModel):
    id: int
    option_key: str
    option_text: str
    is_correct: bool

    class Config:
        from_attributes = True


# --- Test Case Schemas ---
class TestCaseCreate(BaseModel):
    input_data: str = ""
    expected_output: str = Field(..., min_length=1)
    is_hidden: bool = True
    weight: float = 1.0

class TestCaseOutPublic(BaseModel):
    id: int
    input_data: str
    expected_output: str
    is_hidden: bool = False

    class Config:
        from_attributes = True

class TestCaseOutAdmin(BaseModel):
    id: int
    input_data: str
    expected_output: str
    is_hidden: bool
    weight: float

    class Config:
        from_attributes = True


# --- Question Output Schemas ---
class QuestionOutParticipant(BaseModel):
    id: int
    round_id: int
    title: str
    description: str
    code_snippet: Optional[str] = None
    category: Optional[str] = None
    marks: float
    negative_marks: float
    difficulty: str
    language: str
    order_index: int
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    options: List[OptionOutParticipant] = []
    sample_test_cases: List[TestCaseOutPublic] = []

    class Config:
        from_attributes = True

class QuestionOutAdmin(BaseModel):
    id: int
    round_id: int
    title: str
    description: str
    code_snippet: Optional[str] = None
    category: Optional[str] = None
    marks: float
    negative_marks: float
    difficulty: str
    language: str
    order_index: int
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    options: List[OptionOutAdmin] = []
    test_cases: List[TestCaseOutAdmin] = []

    class Config:
        from_attributes = True


# --- Question Create/Update Payload ---
class QuestionCreateUpdate(BaseModel):
    round_id: int
    title: str = Field(..., min_length=2)
    description: str = Field(..., min_length=2)
    code_snippet: Optional[str] = None
    category: Optional[str] = "DSA"
    marks: float = 5.0
    negative_marks: float = 0.0
    difficulty: str = "Medium"
    language: str = "python"
    order_index: int = 1
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    sample_input: Optional[str] = None
    sample_output: Optional[str] = None
    options: List[OptionCreate] = []
    test_cases: List[TestCaseCreate] = []
