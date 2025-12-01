"""
Repository for notification data access
"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, update
from sqlalchemy.orm import Session

from app.models.db_models import Notification
from app.models.schemas import NotificationCreateInternal


class NotificationsRepository:
    """Repository for notifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        data: NotificationCreateInternal
    ) -> Notification:
        """
        Create a new notification
        
        Args:
            data: Notification creation data
            
        Returns:
            Created Notification
        """
        notification = Notification(
            user_id=data.user_id,
            type=data.type,
            title=data.title,
            body=data.body,
            data=data.data,
            send_email=data.send_email,
            send_push=data.send_push,
            is_read=False
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def list_notifications_for_user(
        self,
        user_id: UUID,
        status: Optional[str] = "all",
        notification_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        offset: int = 0,
        count: int = 20
    ) -> Tuple[List[Notification], int]:
        """
        List notifications for a user with filters and pagination
        
        Args:
            user_id: User UUID
            status: Filter by status ("unread", "read", "all")
            notification_type: Filter by notification type (optional)
            date_from: Filter by created_at >= date_from (optional)
            date_to: Filter by created_at <= date_to (optional)
            offset: Number of records to skip
            count: Maximum number of records to return
            
        Returns:
            Tuple of (notifications list, total count)
        """
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id
        )
        
        # Apply status filter
        if status == "unread":
            query = query.filter(Notification.is_read == False)
        elif status == "read":
            query = query.filter(Notification.is_read == True)
        # "all" - no filter
        
        # Apply type filter
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        
        # Apply date filters
        if date_from:
            query = query.filter(Notification.created_at >= date_from)
        
        if date_to:
            query = query.filter(Notification.created_at <= date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and order
        notifications = query.order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(count).all()
        
        return notifications, total
    
    def get_notification(
        self,
        notification_id: UUID
    ) -> Optional[Notification]:
        """
        Get notification by ID
        
        Args:
            notification_id: Notification UUID
            
        Returns:
            Notification or None if not found
        """
        return self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
    
    def mark_read(
        self,
        notification_id: UUID
    ) -> Optional[Notification]:
        """
        Mark notification as read
        
        Args:
            notification_id: Notification UUID
            
        Returns:
            Updated Notification or None if not found
        """
        notification = self.get_notification(notification_id)
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(notification)
        return notification
    
    def mark_all_read(
        self,
        user_id: UUID,
        notification_type: Optional[str] = None
    ) -> int:
        """
        Mark all notifications as read for a user
        
        Args:
            user_id: User UUID
            notification_type: Filter by notification type (optional)
            
        Returns:
            Number of updated records
        """
        query = update(Notification).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        
        # Apply type filter if specified
        if notification_type:
            query = query.where(Notification.type == notification_type)
        
        # Set is_read and read_at
        query = query.values(
            is_read=True,
            read_at=datetime.utcnow()
        )
        
        result = self.db.execute(query)
        self.db.commit()
        
        return result.rowcount
    
    def count_unread(
        self,
        user_id: UUID,
        notification_type: Optional[str] = None
    ) -> int:
        """
        Count unread notifications for a user
        
        Args:
            user_id: User UUID
            notification_type: Filter by notification type (optional)
            
        Returns:
            Number of unread notifications
        """
        query = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )
        
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        
        return query.count()

