"""
Notifications API endpoints
"""
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import get_current_user_id, get_notifications_service
from app.models.schemas import (
    NotificationOut,
    NotificationsListResponse,
    NotificationCreateInternal,
    UnreadCountResponse,
    MarkAllReadResponse
)
from app.services.notifications_service import NotificationsService


router = APIRouter()


@router.get("/me", response_model=NotificationsListResponse, tags=["notifications"])
async def get_my_notifications(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
    status: str = Query(default="all", description="Filter by status: unread, read, all"),
    type: Optional[str] = Query(default=None, description="Filter by notification type"),
    date_from: Optional[datetime] = Query(default=None, alias="from", description="Filter by created_at >= date_from"),
    date_to: Optional[datetime] = Query(default=None, alias="to", description="Filter by created_at <= date_to"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    count: int = Query(default=20, ge=1, le=100, description="Maximum number of records to return")
) -> NotificationsListResponse:
    """
    Get list of notifications for current user
    
    Args:
        current_user_id: Current authenticated user ID
        service: Notifications service instance
        status: Filter by status ("unread", "read", "all")
        type: Filter by notification type (optional)
        date_from: Filter by created_at >= date_from (optional)
        date_to: Filter by created_at <= date_to (optional)
        offset: Number of records to skip
        count: Maximum number of records to return
        
    Returns:
        List of notifications with pagination metadata
    """
    # Validate status parameter
    if status not in ["unread", "read", "all"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be one of: unread, read, all"
        )
    
    return service.list_notifications(
        user_id=current_user_id,
        status=status,
        notification_type=type,
        date_from=date_from,
        date_to=date_to,
        offset=offset,
        count=count
    )


@router.post(
    "/{notification_id}/read",
    response_model=NotificationOut,
    tags=["notifications"]
)
async def mark_notification_read(
    notification_id: UUID,
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)]
) -> NotificationOut:
    """
    Mark notification as read
    
    Args:
        notification_id: Notification UUID
        current_user_id: Current authenticated user ID
        service: Notifications service instance
        
    Returns:
        Updated notification
        
    Raises:
        HTTPException: 404 if notification not found, 403 if unauthorized
    """
    return service.mark_notification_read(
        notification_id=notification_id,
        current_user_id=current_user_id
    )


@router.post(
    ":mark-all-read",
    response_model=MarkAllReadResponse,
    tags=["notifications"]
)
async def mark_all_notifications_read(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
    type: Optional[str] = Query(default=None, description="Filter by notification type")
) -> MarkAllReadResponse:
    """
    Mark all notifications as read for current user
    
    Args:
        current_user_id: Current authenticated user ID
        service: Notifications service instance
        type: Filter by notification type (optional)
        
    Returns:
        Response with count of updated notifications
    """
    return service.mark_all_read(
        user_id=current_user_id,
        notification_type=type
    )


@router.get(
    "/me/unread-count",
    response_model=UnreadCountResponse,
    tags=["notifications"]
)
async def get_unread_count(
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
    type: Optional[str] = Query(default=None, description="Filter by notification type")
) -> UnreadCountResponse:
    """
    Get count of unread notifications for current user
    
    Args:
        current_user_id: Current authenticated user ID
        service: Notifications service instance
        type: Filter by notification type (optional)
        
    Returns:
        Unread count response
    """
    return service.count_unread(
        user_id=current_user_id,
        notification_type=type
    )


@router.post(
    "",
    response_model=NotificationOut,
    status_code=status.HTTP_201_CREATED,
    tags=["notifications"]
)
async def create_notification(
    data: NotificationCreateInternal,
    service: Annotated[NotificationsService, Depends(get_notifications_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
) -> NotificationOut:
    """
    Create a new notification (internal services only)
    
    This endpoint is designed for machine-to-machine communication from other services:
    - homework-service: notify about new homework assignments
    - gradebook-service: notify about grades
    - achievement-service: notify about new achievements
    
    Args:
        data: Notification creation data
        service: Notifications service instance
        current_user_id: Current authenticated user ID
        
    Returns:
        Created notification
        
    Note:
        In production, restrict this endpoint to internal services only
        using service-to-service authentication (e.g., API keys, mutual TLS)
    """
    # In production, add authorization check:
    # if not is_internal_service(current_user_id):
    #     raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return service.create_notification(data)

