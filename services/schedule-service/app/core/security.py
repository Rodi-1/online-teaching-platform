"""
Security utilities for token verification and user authentication
"""
from typing import Optional
from fastapi import Header, HTTPException, status


def get_current_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """
    Extract user_id from request headers (set by API Gateway/Auth middleware)
    
    Args:
        x_user_id: User ID from header
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If user_id header is missing
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials"
        )
    return x_user_id


def get_current_user_role(x_user_role: Optional[str] = Header(None)) -> str:
    """
    Extract user role from request headers (set by API Gateway/Auth middleware)
    
    Args:
        x_user_role: User role from header
        
    Returns:
        User role string
        
    Raises:
        HTTPException: If user_role header is missing
    """
    if not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing role information"
        )
    return x_user_role


def require_role(allowed_roles: list[str], user_role: str) -> None:
    """
    Check if user has one of the allowed roles
    
    Args:
        allowed_roles: List of allowed role names
        user_role: Current user's role
        
    Raises:
        HTTPException: If user doesn't have required role
    """
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
        )

