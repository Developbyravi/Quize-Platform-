from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("rounds.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    code_snippet = Column(Text, nullable=True) # Buggy code or initial boilerplate
    category = Column(String(100), nullable=True) # DSA, OOP, C++, Python, Debugging, Output
    marks = Column(Float, default=5.0)
    negative_marks = Column(Float, default=0.0)
    difficulty = Column(String(50), default="Medium") # Easy, Medium, Hard
    language = Column(String(50), default="python") # c, cpp, java, python
    order_index = Column(Integer, default=1)
    
    # Input/Output specifications for Round 2 & 3
    input_format = Column(Text, nullable=True)
    output_format = Column(Text, nullable=True)
    constraints = Column(Text, nullable=True)
    sample_input = Column(Text, nullable=True)
    sample_output = Column(Text, nullable=True)
    
    round = relationship("Round", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="question", cascade="all, delete-orphan")

class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    option_key = Column(String(10), nullable=False) # A, B, C, D
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)

    question = relationship("Question", back_populates="options")

class TestCase(Base):
    __test__ = False
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=True) # NEVER expose hidden test cases to participant
    weight = Column(Float, default=1.0)

    question = relationship("Question", back_populates="test_cases")
