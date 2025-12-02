"""
Unit tests for notifications service - testing authorization logic
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime

from app.services.notifications_service import NotificationsService


class TestMarkNotificationRead:
    """Tests for mark_notification_read authorization"""
    
    def test_owner_can_mark_read(self):
        """Test that notification owner can mark it as read"""
        mock_repo = Mock()
        service = NotificationsService(mock_repo)
        
        user_id = uuid4()
        notification_id = uuid4()
        
        # Mock notification owned by user with all required fields
        mock_notification = MagicMock()
        mock_notification.id = notification_id
        mock_notification.user_id = user_id
        mock_notification.type = "system"
        mock_notification.title = "Test notification"
        mock_notification.body = "Test body"
        mock_notification.data = {}
        mock_notification.is_read = False
        mock_notification.created_at = datetime.utcnow()
        mock_notification.read_at = None
        
        mock_repo.get_notification.return_value = mock_notification
        mock_repo.mark_read.return_value = mock_notification
        
        # Should not raise
        result = service.mark_notification_read(notification_id, user_id)
        
        mock_repo.mark_read.assert_called_once_with(notification_id)
    
    def test_non_owner_cannot_mark_read(self):
        """Test that non-owner cannot mark notification as read"""
        from fastapi import HTTPException
        
        mock_repo = Mock()
        service = NotificationsService(mock_repo)
        
        owner_id = uuid4()
        other_user_id = uuid4()
        notification_id = uuid4()
        
        # Mock notification owned by different user
        mock_notification = MagicMock()
        mock_notification.user_id = owner_id
        mock_repo.get_notification.return_value = mock_notification
        
        with pytest.raises(HTTPException) as exc_info:
            service.mark_notification_read(notification_id, other_user_id)
        
        assert exc_info.value.status_code == 403
        assert "authorized" in exc_info.value.detail.lower()
    
    def test_notification_not_found(self):
        """Test that 404 is raised when notification not found"""
        from fastapi import HTTPException
        
        mock_repo = Mock()
        service = NotificationsService(mock_repo)
        
        mock_repo.get_notification.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            service.mark_notification_read(uuid4(), uuid4())
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
