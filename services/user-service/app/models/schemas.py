"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .db_models import UserRole, UserStatus


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    """Schema for user registration"""
    phone: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student@example.com",
                "phone": "+79990001122",
                "password": "password123",
                "first_name": "Иван",
                "last_name": "Иванов",
                "role": "student"
            }
        }
    )


class UserOut(UserBase):
    """Schema for user output (without sensitive data)"""
    id: UUID
    phone: Optional[str] = None
    is_email_confirmed: bool
    is_phone_confirmed: bool
    status: UserStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserOut):
    """Schema for user as stored in database (includes password_hash)"""
    password_hash: str
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Authentication schemas
class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str = Field(..., min_length=1)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student@example.com",
                "password": "password123"
            }
        }
    )


class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserOut


# Profile update schemas
class UpdateProfileRequest(BaseModel):
    """Schema for partial profile update"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "Иван-Антон",
                "last_name": "Иванов",
                "phone": "+79995556677"
            }
        }
    )


# Email confirmation schemas
class ConfirmEmailRequest(BaseModel):
    """Schema for email confirmation request"""
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=10)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student@example.com",
                "code": "483921"
            }
        }
    )


class ConfirmPhoneRequest(BaseModel):
    """Schema for phone confirmation request"""
    phone: str = Field(..., min_length=1, max_length=20)
    code: str = Field(..., min_length=4, max_length=10)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phone": "+79990001122",
                "code": "902134"
            }
        }
    )


# Password reset schemas
class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student@example.com"
            }
        }
    )


class PasswordResetConfirmRequest(BaseModel):
    """Schema for password reset confirmation"""
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=10)
    new_password: str = Field(..., min_length=8, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "student@example.com",
                "code": "583920",
                "new_password": "NewPassword123"
            }
        }
    )


# Admin schemas
class UserListItem(BaseModel):
    """Schema for user in list (simplified)"""
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UsersListResponse(BaseModel):
    """Schema for users list response with pagination"""
    items: List[UserListItem]
    total: int
    offset: int
    count: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "student1@example.com",
                        "first_name": "Иван",
                        "last_name": "Иванов",
                        "role": "student",
                        "status": "active",
                        "created_at": "2025-02-10T12:30:00Z"
                    }
                ],
                "total": 1,
                "offset": 0,
                "count": 20
            }
        }
    )


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

