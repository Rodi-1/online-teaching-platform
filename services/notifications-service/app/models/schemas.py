"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ============= Output Schemas =============

class NotificationOut(BaseModel):
    """Notification output schema"""
    id: UUID
    user_id: UUID
    type: str
    title: str
    body: str
    data: Optional[Dict[str, Any]] = Field(default=None)
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class NotificationsListResponse(BaseModel):
    """Response schema for notifications list"""
    items: List[NotificationOut]
    total: int
    offset: int = 0
    count: int = 20
    
    model_config = ConfigDict(from_attributes=True)


class UnreadCountResponse(BaseModel):
    """Response schema for unread count"""
    user_id: UUID
    type_filter: Optional[str] = None
    unread_count: int
    
    model_config = ConfigDict(from_attributes=True)


class MarkAllReadResponse(BaseModel):
    """Response schema for mark all read operation"""
    user_id: UUID
    updated_count: int
    type_filter: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============= Input Schemas =============

class NotificationCreateInternal(BaseModel):
    """Schema for creating notification from internal services"""
    user_id: UUID
    type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=255)
    body: str = Field(..., max_length=10000)
    data: Optional[Dict[str, Any]] = Field(default=None)
    send_email: bool = Field(default=False)
    send_push: bool = Field(default=False)
    
    model_config = ConfigDict(from_attributes=True)


# ============= Filter Enums =============

class NotificationStatusFilter(str):
    """Notification status filter enum"""
    UNREAD = "unread"
    READ = "read"
    ALL = "all"

