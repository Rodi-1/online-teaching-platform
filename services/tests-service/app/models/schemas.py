"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ============= Question Schemas =============

class TestQuestionCreate(BaseModel):
    """Schema for creating a test question"""
    id: str = Field(..., max_length=50, description="Local question ID (e.g., 'q1')")
    type: str = Field(..., description="Question type: single_choice, multiple_choice, text, number")
    text: str = Field(..., description="Question text")
    options: Optional[List[str]] = Field(default=None, description="Answer options for choice questions")
    correct_answers: Optional[List[Union[str, int, float]]] = Field(default=None, description="Correct answers")
    max_score: float = Field(default=1.0, ge=0, description="Maximum score for this question")
    
    model_config = ConfigDict(from_attributes=True)


class TestQuestionOut(BaseModel):
    """Schema for question output (without correct answers)"""
    id: str
    type: str
    text: str
    options: Optional[List[str]] = None
    max_score: float
    
    model_config = ConfigDict(from_attributes=True)


class TestQuestionDetail(BaseModel):
    """Schema for question with correct answers (for teachers)"""
    id: UUID
    test_id: UUID
    local_id: str
    type: str
    text: str
    options: Optional[List[str]] = None
    correct_answers: Optional[List[Union[str, int, float]]] = None
    max_score: float
    order_index: int
    
    model_config = ConfigDict(from_attributes=True)


# ============= Test Schemas =============

class TestCreate(BaseModel):
    """Schema for creating a test"""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    lesson_id: Optional[UUID] = None
    time_limit_minutes: Optional[int] = Field(default=None, ge=1)
    questions: List[TestQuestionCreate]
    
    model_config = ConfigDict(from_attributes=True)


class TestOut(BaseModel):
    """Schema for test output"""
    id: UUID
    course_id: UUID
    lesson_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    max_score: float
    status: str
    available_from: Optional[datetime] = None
    available_to: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TestPublishRequest(BaseModel):
    """Schema for publishing a test"""
    available_from: Optional[datetime] = None
    available_to: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TestForStudentOut(BaseModel):
    """Schema for test info for students"""
    test_id: UUID
    course_id: UUID
    title: str
    status: str
    available_from: Optional[datetime] = None
    available_to: Optional[datetime] = None
    time_limit_minutes: Optional[int] = None
    max_score: float
    attempts_used: int = 0
    last_result: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class TestsListResponse(BaseModel):
    """Schema for tests list response"""
    items: List[TestForStudentOut]
    total: int
    offset: int = 0
    count: int = 20
    
    model_config = ConfigDict(from_attributes=True)


# ============= Attempt Schemas =============

class TestAttemptStartResponse(BaseModel):
    """Schema for starting a test attempt"""
    attempt_id: UUID
    test_id: UUID
    student_id: UUID
    started_at: datetime
    expires_at: Optional[datetime] = None
    status: str
    questions: List[TestQuestionOut]
    
    model_config = ConfigDict(from_attributes=True)


class AnswerSubmit(BaseModel):
    """Schema for submitting an answer"""
    question_id: str = Field(..., description="Local question ID")
    value: Union[str, int, float, List[str]] = Field(..., description="Answer value")
    
    model_config = ConfigDict(from_attributes=True)


class AttemptSubmitRequest(BaseModel):
    """Schema for submitting attempt answers"""
    answers: List[AnswerSubmit]
    
    model_config = ConfigDict(from_attributes=True)


class AnswerDetail(BaseModel):
    """Schema for answer detail in result"""
    question_id: str
    question_text: str
    your_answer: Union[str, int, float, List[str], None]
    correct_answers: Optional[List[Union[str, int, float]]] = None
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    max_score: float
    
    model_config = ConfigDict(from_attributes=True)


class AttemptResult(BaseModel):
    """Schema for attempt result"""
    attempt_id: UUID
    test_id: UUID
    student_id: UUID
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    score: Optional[float] = None
    max_score: Optional[float] = None
    percent: Optional[float] = None
    grade: Optional[int] = None
    details: Optional[List[AnswerDetail]] = None
    
    model_config = ConfigDict(from_attributes=True)


class AttemptBriefOut(BaseModel):
    """Schema for brief attempt info"""
    id: UUID
    test_id: UUID
    student_id: UUID
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    score: Optional[float] = None
    max_score: Optional[float] = None
    percent: Optional[float] = None
    grade: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class AttemptsListResponse(BaseModel):
    """Schema for attempts list response"""
    items: List[AttemptBriefOut]
    total: int
    offset: int = 0
    count: int = 20
    
    model_config = ConfigDict(from_attributes=True)

