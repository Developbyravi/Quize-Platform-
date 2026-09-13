from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ParticipantRegister(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    mobile_number: str = Field(..., min_length=10, max_length=15)
    college_name: str = Field(..., min_length=2)
    department: str = Field(..., min_length=2)
    year: str = Field(...)
    prn_student_id: str = Field(..., min_length=2)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    user_id: int

class ParticipantOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    mobile_number: str
    college_name: str
    department: str
    year: str
    prn_student_id: str
    is_disqualified: bool
    disqualification_reason: Optional[str] = None
    violations_count: int

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    participant: Optional[ParticipantOut] = None

    class Config:
        from_attributes = True
