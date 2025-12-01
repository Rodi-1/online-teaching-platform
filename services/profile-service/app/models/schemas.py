"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ============= Profile Schemas =============

class ProgressStats(BaseModel):
    """Progress statistics for user profile"""
    total_courses: int = Field(default=0, ge=0)
    completed_courses: int = Field(default=0, ge=0)
    active_courses: int = Field(default=0, ge=0)
    average_grade: Optional[float] = Field(default=None, ge=0, le=5)
    homeworks_completed: int = Field(default=0, ge=0)
    tests_passed: int = Field(default=0, ge=0)
    
    model_config = ConfigDict(from_attributes=True)


class ProfileBase(BaseModel):
    """Base profile schema with common fields"""
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    about: Optional[str] = Field(default=None, max_length=5000)
    social_links: Optional[List[str]] = Field(default=None)


class ProfileUpdateRequest(BaseModel):
    """Request schema for updating user profile"""
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    about: Optional[str] = Field(default=None, max_length=5000)
    social_links: Optional[List[str]] = Field(default=None)
    
    model_config = ConfigDict(from_attributes=True)


class AchievementOut(BaseModel):
    """Achievement output schema"""
    id: UUID
    code: str
    title: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    received_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProfileOut(ProfileBase):
    """Profile output schema with all data"""
    user_id: UUID
    progress: ProgressStats
    achievements: Optional[List[AchievementOut]] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============= Achievement Schemas =============

class AchievementCreateRequest(BaseModel):
    """Request schema for creating achievement"""
    code: str = Field(..., max_length=100)
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    icon_url: Optional[str] = Field(default=None, max_length=500)
    received_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AchievementsListResponse(BaseModel):
    """Response schema for achievements list"""
    user_id: UUID
    items: List[AchievementOut]
    total: int
    offset: int = 0
    count: int = 50
    
    model_config = ConfigDict(from_attributes=True)


# ============= Statistics Update Schemas =============

class UpdateStatsRequest(BaseModel):
    """Request schema for updating user statistics"""
    homeworks_completed_delta: Optional[int] = Field(default=None)
    tests_passed_delta: Optional[int] = Field(default=None)
    total_courses_delta: Optional[int] = Field(default=None)
    completed_courses_delta: Optional[int] = Field(default=None)
    active_courses_delta: Optional[int] = Field(default=None)
    average_grade: Optional[float] = Field(default=None, ge=0, le=5)
    
    model_config = ConfigDict(from_attributes=True)


class UpdateStatsResponse(BaseModel):
    """Response schema for statistics update"""
    user_id: UUID
    progress: ProgressStats
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

