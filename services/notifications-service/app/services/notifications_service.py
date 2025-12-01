"""
Business logic for notifications
"""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.models.schemas import (
    NotificationOut,
    NotificationsListResponse,
    NotificationCreateInternal,
    UnreadCountResponse,
    MarkAllReadResponse
)
from app.repositories.notifications_repo import NotificationsRepository


logger = logging.getLogger(__name__)


class NotificationsService:
    """Service for notifications business logic"""
    
    def __init__(self, repo: NotificationsRepository):
        self.repo = repo
    
    def create_notification(
        self,
        data: NotificationCreateInternal
    ) -> NotificationOut:
        """
        Create a new notification
        
        Args:
            data: Notification creation data
            
        Returns:
            Created NotificationOut
        """
        # Log email/push flags for future implementation
        if data.send_email:
            logger.info(f"Email notification requested for user {data.user_id}")
        
        if data.send_push:
            logger.info(f"Push notification requested for user {data.user_id}")
        
        # Create notification in database
        notification = self.repo.create_notification(data)
        
        return NotificationOut.model_validate(notification)
    
    def list_notifications(
        self,
        user_id: UUID,
        status: str = "all",
        notification_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        offset: int = 0,
        count: int = 20
    ) -> NotificationsListResponse:
        """
        List notifications for a user with filters
        
        Args:
            user_id: User UUID
            status: Filter by status ("unread", "read", "all")
            notification_type: Filter by notification type (optional)
            date_from: Filter by created_at >= date_from (optional)
            date_to: Filter by created_at <= date_to (optional)
            offset: Number of records to skip
            count: Maximum number of records to return
            
        Returns:
            NotificationsListResponse with notifications and metadata
        """
        notifications, total = self.repo.list_notifications_for_user(
            user_id=user_id,
            status=status,
            notification_type=notification_type,
            date_from=date_from,
            date_to=date_to,
            offset=offset,
            count=count
        )
        
        items = [
            NotificationOut.model_validate(notification)
            for notification in notifications
        ]
        
        return NotificationsListResponse(
            items=items,
            total=total,
            offset=offset,
            count=count
        )
    
    def mark_notification_read(
        self,
        notification_id: UUID,
        current_user_id: UUID
    ) -> NotificationOut:
        """
        Mark notification as read
        
        Args:
            notification_id: Notification UUID
            current_user_id: Current user UUID (for authorization)
            
        Returns:
            Updated NotificationOut
            
        Raises:
            HTTPException: If notification not found or unauthorized
        """
        # Get notification
        notification = self.repo.get_notification(notification_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Check authorization - only owner can mark as read
        if notification.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this notification"
            )
        
        # Mark as read
        updated_notification = self.repo.mark_read(notification_id)
        
        return NotificationOut.model_validate(updated_notification)
    
    def mark_all_read(
        self,
        user_id: UUID,
        notification_type: Optional[str] = None
    ) -> MarkAllReadResponse:
        """
        Mark all notifications as read for a user
        
        Args:
            user_id: User UUID
            notification_type: Filter by notification type (optional)
            
        Returns:
            MarkAllReadResponse with count of updated notifications
        """
        updated_count = self.repo.mark_all_read(
            user_id=user_id,
            notification_type=notification_type
        )
        
        return MarkAllReadResponse(
            user_id=user_id,
            updated_count=updated_count,
            type_filter=notification_type
        )
    
    def count_unread(
        self,
        user_id: UUID,
        notification_type: Optional[str] = None
    ) -> UnreadCountResponse:
        """
        Count unread notifications for a user
        
        Args:
            user_id: User UUID
            notification_type: Filter by notification type (optional)
            
        Returns:
            UnreadCountResponse with unread count
        """
        unread_count = self.repo.count_unread(
            user_id=user_id,
            notification_type=notification_type
        )
        
        return UnreadCountResponse(
            user_id=user_id,
            type_filter=notification_type,
            unread_count=unread_count
        )

