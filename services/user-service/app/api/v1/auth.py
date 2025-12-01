"""
Authentication API endpoints
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.schemas import LoginRequest, Token, MessageResponse, UserOut
from app.models.db_models import User
from app.services.users_service import UserService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user with email and password, returns access token"
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login endpoint
    
    Authenticates user and returns access token with user information
    """
    service = UserService(db)
    
    # Authenticate user
    user = service.authenticate(request.email, request.password)
    
    # Issue tokens
    tokens = service.issue_tokens(user)
    
    # Return response
    return Token(
        access_token=tokens["access_token"],
        expires_in=tokens["expires_in"],
        user=UserOut.model_validate(user)
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logout user and revoke refresh tokens"
)
def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    Logout endpoint
    
    Revokes all refresh tokens for the current user
    """
    service = UserService(db)
    service.logout(current_user)
    
    return MessageResponse(
        result="ok",
        message="Сессия завершена"
    )

