"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Lesson Schemas
# ============================================================================

class LessonCreate(BaseModel):
    """Schema for creating a new lesson"""
    title: str = Field(..., min_length=1, max_length=255, description="Lesson title")
    description: Optional[str] = Field(None, description="Lesson description")
    start_at: datetime = Field(..., description="Lesson start datetime (UTC)")
    end_at: datetime = Field(..., description="Lesson end datetime (UTC)")
    location_type: str = Field(..., pattern="^(online|offline)$", description="Location type: online or offline")
    room: Optional[str] = Field(None, max_length=255, description="Room number for offline lessons")
    online_link: Optional[str] = Field(None, description="Online meeting link")
    
    @field_validator('end_at')
    @classmethod
    def validate_end_after_start(cls, v, info):
        """Validate that end_at is after start_at"""
        if 'start_at' in info.data and v <= info.data['start_at']:
            raise ValueError('end_at must be after start_at')
        return v


class LessonUpdate(BaseModel):
    """Schema for updating a lesson (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    location_type: Optional[str] = Field(None, pattern="^(online|offline)$")
    room: Optional[str] = Field(None, max_length=255)
    online_link: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|cancelled|finished)$")


class LessonOut(BaseModel):
    """Schema for lesson response"""
    id: UUID
    course_id: UUID
    title: str
    description: Optional[str]
    start_at: datetime
    end_at: datetime
    location_type: str
    room: Optional[str]
    online_link: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Schedule Schemas
# ============================================================================

class ScheduleItemMe(BaseModel):
    """Schema for a schedule item in user's personal schedule"""
    lesson_id: UUID
    course_id: UUID
    course_title: str = Field(default="Unknown Course", description="Course title")
    title: str
    start_at: datetime
    end_at: datetime
    location_type: str
    room: Optional[str]
    online_link: Optional[str]
    role: str = Field(..., description="User's role in this course (student/teacher)")
    status: str


class ScheduleResponse(BaseModel):
    """Schema for schedule list response"""
    items: list[ScheduleItemMe]
    total: int
    offset: int
    count: int


class CourseScheduleResponse(BaseModel):
    """Schema for course schedule response"""
    course_id: UUID
    course_title: str = Field(default="Unknown Course")
    items: list[LessonOut]


# ============================================================================
# Attendance Schemas
# ============================================================================

class AttendanceItemUpdate(BaseModel):
    """Schema for updating attendance for a single student"""
    student_id: UUID
    status: str = Field(..., pattern="^(present|absent|late)$", description="Attendance status")
    comment: Optional[str] = None


class AttendanceSetRequest(BaseModel):
    """Schema for batch attendance update request"""
    items: list[AttendanceItemUpdate]


class AttendanceItemOut(BaseModel):
    """Schema for attendance item response"""
    student_id: UUID
    student_name: str = Field(default="Unknown Student")
    status: str
    comment: Optional[str]
    marked_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceResponse(BaseModel):
    """Schema for attendance response"""
    lesson_id: UUID
    course_id: UUID
    lesson_title: str
    items: list[AttendanceItemOut]


class AttendanceSetResponse(BaseModel):
    """Schema for attendance set response"""
    lesson_id: UUID
    items: list[AttendanceItemOut]
    updated_at: datetime

