"""
API dependencies for authentication and authorization
"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status, Header
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import get_settings


settings = get_settings()


class CurrentUser:
    """Current user information extracted from JWT token"""
    def __init__(self, user_id: UUID, role: str, email: str):
        self.id = user_id
        self.role = role
        self.email = email


def get_current_user(authorization: str = Header(...)) -> CurrentUser:
    """
    Get current user from JWT token
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    # Extract token from header
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Decode JWT token
        # Note: In real scenario, use same JWT_SECRET as user-service
        # For simplicity, we assume user-service and homework-service share secret
        payload = jwt.decode(
            token,
            settings.JWT_SECRET if hasattr(settings, 'JWT_SECRET') else "secret",
            algorithms=["HS256"]
        )
        
        user_id_str: str = payload.get("sub")
        role: str = payload.get("role")
        email: str = payload.get("email")
        
        if not user_id_str or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = UUID(user_id_str)
        
        return CurrentUser(user_id=user_id, role=role, email=email)
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_teacher(
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> CurrentUser:
    """
    Require user to be a teacher
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if teacher
        
    Raises:
        HTTPException: If user is not a teacher
    """
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can perform this action"
        )
    
    return current_user


def require_student(
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> CurrentUser:
    """
    Require user to be a student
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if student
        
    Raises:
        HTTPException: If user is not a student
    """
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can perform this action"
        )
    
    return current_user

