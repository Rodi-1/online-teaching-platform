"""Pydantic schemas for Gradebook Service"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .db_models import EntryType


# Input schemas
class HomeworkGradeCreate(BaseModel):
    """Schema for creating a homework grade entry"""
    student_id: UUID
    course_id: UUID
    lesson_id: Optional[UUID] = None
    homework_id: UUID
    score: float = Field(..., ge=0)
    max_score: float = Field(..., gt=0)
    graded_at: datetime
    comment: Optional[str] = None
    title: Optional[str] = "Домашнее задание"


class TestGradeCreate(BaseModel):
    """Schema for creating a test grade entry"""
    student_id: UUID
    course_id: UUID
    test_id: UUID
    attempt_id: Optional[UUID] = None
    score: float = Field(..., ge=0)
    max_score: float = Field(..., gt=0)
    graded_at: datetime
    comment: Optional[str] = None
    title: Optional[str] = "Тест"


# Output schemas
class GradeEntryOut(BaseModel):
    """Schema for grade entry output"""
    id: UUID
    type: EntryType
    student_id: UUID
    course_id: UUID
    lesson_id: Optional[UUID]
    homework_id: Optional[UUID]
    test_id: Optional[UUID]
    attempt_id: Optional[UUID]
    title: str
    score: float
    max_score: float
    percent: float
    grade: int
    graded_at: datetime
    comment: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class StudentGradesResponse(BaseModel):
    """Schema for student grades list response"""
    items: List[GradeEntryOut]
    total: int
    offset: int
    count: int


class CourseGradebookItem(BaseModel):
    """Schema for course gradebook item"""
    student_id: UUID
    student_name: Optional[str] = None
    entry_id: UUID
    type: EntryType
    work_title: str
    work_id: UUID
    score: float
    max_score: float
    grade: int
    graded_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CourseGradebookResponse(BaseModel):
    """Schema for course gradebook response"""
    course_id: UUID
    course_title: Optional[str] = None
    items: List[CourseGradebookItem]
    total: int


class MessageResponse(BaseModel):
    """Generic message response"""
    result: str = "ok"
    message: str

