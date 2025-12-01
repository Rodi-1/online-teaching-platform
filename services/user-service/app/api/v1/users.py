"""
Users API endpoints
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, require_admin
from app.db.session import get_db
from app.models.schemas import (
    UserCreate,
    UserOut,
    UpdateProfileRequest,
    ConfirmEmailRequest,
    ConfirmPhoneRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    UsersListResponse,
    UserListItem,
    MessageResponse
)
from app.models.db_models import User, UserRole, UserStatus
from app.services.users_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email, password and personal information"
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Creates a new user account and sends email confirmation code
    """
    service = UserService(db)
    user = service.register_user(user_data)
    return UserOut.model_validate(user)


@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get profile information for the currently authenticated user"
)
def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get current user profile
    
    Returns profile information for the authenticated user
    """
    return UserOut.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Partially update profile information for the current user"
)
def update_current_user_profile(
    updates: UpdateProfileRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    
    Allows partial updates of first_name, last_name, and phone
    """
    service = UserService(db)
    updated_user = service.update_profile(current_user.id, updates)
    return UserOut.model_validate(updated_user)


@router.post(
    "/confirm-email",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm email",
    description="Confirm user email address with verification code"
)
def confirm_email(
    request: ConfirmEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm email address
    
    Validates confirmation code and marks email as confirmed
    """
    service = UserService(db)
    service.confirm_email(request.email, request.code)
    
    return MessageResponse(
        result="ok",
        message="Email успешно подтверждён"
    )


@router.post(
    "/confirm-phone",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm phone",
    description="Confirm user phone number with verification code"
)
def confirm_phone(
    request: ConfirmPhoneRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm phone number
    
    Validates confirmation code and marks phone as confirmed
    """
    service = UserService(db)
    service.confirm_phone(request.phone, request.code)
    
    return MessageResponse(
        result="ok",
        message="Телефон успешно подтверждён"
    )


@router.post(
    ":request-password-reset",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Request password reset code to be sent to user email"
)
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset
    
    Generates and sends password reset code (if user exists)
    """
    service = UserService(db)
    service.request_password_reset(request.email)
    
    return MessageResponse(
        result="ok",
        message="Если пользователь существует, инструкции по восстановлению пароля отправлены"
    )


@router.post(
    ":reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset user password using verification code"
)
def reset_password(
    request: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password with code
    
    Validates reset code and updates user password
    """
    service = UserService(db)
    service.reset_password(request.email, request.code, request.new_password)
    
    return MessageResponse(
        result="ok",
        message="Пароль успешно изменён"
    )


@router.get(
    "",
    response_model=UsersListResponse,
    status_code=status.HTTP_200_OK,
    summary="List users (admin)",
    description="Get paginated list of users with optional filters (admin only)"
)
def list_users(
    current_user: Annotated[User, Depends(require_admin)],
    offset: int = Query(0, ge=0, description="Pagination offset"),
    count: int = Query(20, ge=1, le=100, description="Number of items to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    status: Optional[UserStatus] = Query(None, description="Filter by user status"),
    db: Session = Depends(get_db)
):
    """
    List users (admin only)
    
    Returns paginated list of users with optional filters
    """
    service = UserService(db)
    users, total = service.list_users(offset, count, role, status)
    
    return UsersListResponse(
        items=[UserListItem.model_validate(user) for user in users],
        total=total,
        offset=offset,
        count=count
    )

