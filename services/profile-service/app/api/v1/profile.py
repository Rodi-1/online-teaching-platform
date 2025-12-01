"""
Profile and achievements API endpoints
"""
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import get_current_user_id, get_profile_service
from app.models.schemas import (
    ProfileOut,
    ProfileUpdateRequest,
    AchievementCreateRequest,
    AchievementOut,
    AchievementsListResponse,
    UpdateStatsRequest,
    UpdateStatsResponse
)
from app.services.profile_service import ProfileService


router = APIRouter()


@router.get("/me", response_model=ProfileOut, tags=["profile"])
async def get_my_profile(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
    include_achievements: bool = Query(default=True, description="Include achievements in response")
) -> ProfileOut:
    """
    Get current user's profile with optional achievements
    
    Args:
        current_user_id: Current authenticated user ID
        service: Profile service instance
        include_achievements: Whether to include achievements
        
    Returns:
        User profile with progress statistics and achievements
    """
    return service.get_profile(
        user_id=current_user_id,
        include_achievements=include_achievements
    )


@router.patch("/me", response_model=ProfileOut, tags=["profile"])
async def update_my_profile(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    service: Annotated[ProfileService, Depends(get_profile_service)],
    update_data: ProfileUpdateRequest
) -> ProfileOut:
    """
    Update current user's profile
    
    Args:
        current_user_id: Current authenticated user ID
        service: Profile service instance
        update_data: Profile update data
        
    Returns:
        Updated user profile
    """
    return service.update_profile(
        user_id=current_user_id,
        update_data=update_data
    )


@router.get(
    "/users/{user_id}/achievements",
    response_model=AchievementsListResponse,
    tags=["achievements"]
)
async def get_user_achievements(
    user_id: UUID,
    service: Annotated[ProfileService, Depends(get_profile_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    code: Optional[str] = Query(default=None, description="Filter by achievement code"),
    date_from: Optional[datetime] = Query(default=None, description="Filter by received_at >= date_from"),
    date_to: Optional[datetime] = Query(default=None, description="Filter by received_at <= date_to"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    count: int = Query(default=50, ge=1, le=100, description="Maximum number of records to return")
) -> AchievementsListResponse:
    """
    Get user achievements with filters and pagination
    
    Args:
        user_id: Target user ID
        service: Profile service instance
        current_user_id: Current authenticated user ID
        code: Filter by achievement code (optional)
        date_from: Filter by received_at >= date_from (optional)
        date_to: Filter by received_at <= date_to (optional)
        offset: Number of records to skip
        count: Maximum number of records to return
        
    Returns:
        List of user achievements with pagination metadata
        
    Note:
        In production, add role-based access control here
        (e.g., only allow users to see their own achievements unless they're teachers/admins)
    """
    # In production, add authorization check:
    # if current_user_id != user_id and not has_teacher_or_admin_role(current_user_id):
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return service.get_achievements(
        user_id=user_id,
        code=code,
        date_from=date_from,
        date_to=date_to,
        offset=offset,
        count=count
    )


@router.post(
    "/users/{user_id}/achievements",
    response_model=AchievementOut,
    status_code=status.HTTP_201_CREATED,
    tags=["achievements"]
)
async def create_user_achievement(
    user_id: UUID,
    service: Annotated[ProfileService, Depends(get_profile_service)],
    data: AchievementCreateRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
) -> AchievementOut:
    """
    Create a new achievement for user
    
    Args:
        user_id: Target user ID
        service: Profile service instance
        data: Achievement creation data
        current_user_id: Current authenticated user ID
        
    Returns:
        Created achievement
        
    Raises:
        HTTPException: If duplicate achievement exists or validation fails
        
    Note:
        In production, restrict this endpoint to internal services, teachers, or admins only
    """
    # In production, add authorization check:
    # if not has_teacher_admin_or_service_role(current_user_id):
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        return service.create_achievement(
            user_id=user_id,
            data=data,
            check_duplicate=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/users/{user_id}/stats:update",
    response_model=UpdateStatsResponse,
    tags=["statistics"]
)
async def update_user_stats(
    user_id: UUID,
    service: Annotated[ProfileService, Depends(get_profile_service)],
    stats: UpdateStatsRequest,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
) -> UpdateStatsResponse:
    """
    Update user statistics (custom operation)
    
    This endpoint is designed for machine-to-machine communication from other services:
    - homework-service: updates homeworks_completed
    - tests-service: updates tests_passed
    - gradebook-service: updates average_grade and course counters
    
    Args:
        user_id: Target user ID
        service: Profile service instance
        stats: Statistics update data
        current_user_id: Current authenticated user ID
        
    Returns:
        Updated statistics
        
    Note:
        In production, restrict this endpoint to internal services only
        using service-to-service authentication (e.g., API keys, mutual TLS)
    """
    # In production, add authorization check:
    # if not is_internal_service(current_user_id):
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return service.update_stats(user_id=user_id, stats=stats)

