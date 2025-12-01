"""
API dependencies for authentication and service injection
"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, oauth2_scheme
from app.db.session import get_db
from app.repositories.tests_repo import TestsRepository
from app.services.tests_service import TestsService


def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UUID:
    """Get current authenticated user ID from JWT token"""
    payload = decode_access_token(token)
    
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


def get_tests_service(
    db: Session = Depends(get_db)
) -> TestsService:
    """Get tests service instance with injected dependencies"""
    repo = TestsRepository(db)
    return TestsService(repo)

