"""
Unit tests for notifications service
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from app.services.notifications_service import NotificationsService


def test_create_notification_validates_type():
    """Test that create_notification validates notification type"""
    # Arrange
    mock_repo = Mock()
    service = NotificationsService(mock_repo)
    
    from app.models.schemas import NotificationCreate
    invalid_data = NotificationCreate(
        user_id=uuid4(),
        type="invalid_type",  # Invalid type
        title="Test",
        message="Test message"
    )
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.create_notification(invalid_data)
    
    assert exc_info.value.status_code == 400


def test_mark_as_read_checks_ownership():
    """Test that user can only mark their own notifications as read"""
    # Arrange
    mock_repo = Mock()
    
    notification = MagicMock(
        id=uuid4(),
        user_id=uuid4(),
        is_read=False
    )
    mock_repo.get_notification.return_value = notification
    
    service = NotificationsService(mock_repo)
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.mark_as_read(
            notification_id=notification.id,
            user_id=uuid4()  # Different user
        )
    
    assert exc_info.value.status_code == 403

