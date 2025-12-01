"""
Pydantic schemas for Homework Service request/response validation
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from .db_models import HomeworkStatus, SubmissionStatus


# Homework schemas
class HomeworkCreate(BaseModel):
    """Schema for creating a homework"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    lesson_id: Optional[UUID] = None
    due_at: datetime
    max_score: float = Field(..., gt=0)
    attachments: Optional[List[str]] = Field(default_factory=list)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Домашнее задание по теме \"Функции\"",
                "description": "Решить задачи 1–10 из файла и загрузить ответы в формате PDF.",
                "lesson_id": None,
                "due_at": "2025-03-01T18:00:00Z",
                "max_score": 10,
                "attachments": [
                    "https://files.example.com/homeworks/hw1_tasks.pdf"
                ]
            }
        }
    )


class HomeworkOut(BaseModel):
    """Schema for homework output"""
    id: UUID
    course_id: UUID
    lesson_id: Optional[UUID]
    title: str
    description: str
    due_at: datetime
    max_score: float
    status: HomeworkStatus
    attachments: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class HomeworkListItem(BaseModel):
    """Schema for homework in list (simplified)"""
    id: UUID
    course_id: UUID
    lesson_id: Optional[UUID]
    title: str
    due_at: datetime
    max_score: float
    status: HomeworkStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class HomeworkListResponse(BaseModel):
    """Schema for homeworks list response with pagination"""
    items: List[HomeworkListItem]
    total: int
    offset: int
    count: int


# Submission schemas
class SubmissionCreate(BaseModel):
    """Schema for creating a submission"""
    answer_text: Optional[str] = None
    attachments: Optional[List[str]] = Field(default_factory=list)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "answer_text": "Решения задач приведены в приложенном файле.",
                "attachments": [
                    "https://files.example.com/submissions/hw1_ivanov.pdf"
                ]
            }
        }
    )


class SubmissionOut(BaseModel):
    """Schema for submission output"""
    id: UUID
    homework_id: UUID
    student_id: UUID
    answer_text: Optional[str]
    attachments: Optional[List[str]]
    status: SubmissionStatus
    score: Optional[float]
    teacher_comment: Optional[str]
    created_at: datetime
    checked_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class GradeSubmissionRequest(BaseModel):
    """Schema for grading a submission"""
    score: float = Field(..., ge=0)
    teacher_comment: Optional[str] = None
    status: SubmissionStatus = SubmissionStatus.CHECKED
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "score": 9,
                "teacher_comment": "Хорошая работа, одна ошибка в задаче 7.",
                "status": "checked"
            }
        }
    )


class GradeSubmissionResponse(SubmissionOut):
    """Schema for grading response (same as SubmissionOut)"""
    pass


# Student homework list schemas
class StudentHomeworkItem(BaseModel):
    """Schema for student's homework item"""
    homework_id: UUID
    course_id: UUID
    title: str
    due_at: datetime
    max_score: float
    status: HomeworkStatus
    submission_id: Optional[UUID] = None
    submission_status: Optional[SubmissionStatus] = None
    score: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class StudentHomeworkListResponse(BaseModel):
    """Schema for student's homework list response"""
    items: List[StudentHomeworkItem]
    total: int
    offset: int
    count: int


# Generic response schemas
class MessageResponse(BaseModel):
    """Generic message response schema"""
    result: str = "ok"
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "result": "ok",
                "message": "Operation completed successfully"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Error message"
            }
        }
    )

