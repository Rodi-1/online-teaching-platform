"""
API dependencies for authentication and service injection
"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, oauth2_scheme
from app.db.session import get_db
from app.repositories.profile_repo import ProfileRepository
from app.services.profile_service import ProfileService


def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UUID:
    """
    Get current authenticated user ID from JWT token
    
    Args:
        token: JWT access token
        
    Returns:
        Current user ID
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Decode token
    payload = decode_access_token(token)
    
    # Get user_id from token
    user_id_str: str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def get_profile_service(
    db: Session = Depends(get_db)
) -> ProfileService:
    """
    Get profile service instance with injected dependencies
    
    Args:
        db: Database session
        
    Returns:
        ProfileService instance
    """
    repo = ProfileRepository(db)
    return ProfileService(repo)

