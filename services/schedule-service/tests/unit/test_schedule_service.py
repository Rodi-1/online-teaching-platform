"""
Unit tests for schedule service
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta

from app.services.schedule_service import ScheduleService
from app.models.schemas import LessonCreate


def test_create_lesson_validates_dates():
    """Test that create_lesson validates end_at > start_at"""
    # Arrange
    mock_repo = Mock()
    service = ScheduleService(mock_repo)
    
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time - timedelta(hours=1)  # End before start
    
    lesson_data = LessonCreate(
        title="Test Lesson",
        description="Test",
        start_at=start_time,
        end_at=end_time,
        location_type="online",
        online_link="https://meet.example.com"
    )
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.create_lesson(
            course_id=uuid4(),
            data=lesson_data,
            user_role="teacher"
        )
    
    assert exc_info.value.status_code == 400
    assert "after" in exc_info.value.detail.lower()


def test_update_finished_lesson_raises_error():
    """Test that updating finished lesson raises error"""
    # Arrange
    mock_repo = Mock()
    
    lesson = MagicMock(
        id=uuid4(),
        status="finished",
        title="Old Title"
    )
    mock_repo.get_lesson.return_value = lesson
    
    service = ScheduleService(mock_repo)
    
    from app.models.schemas import LessonUpdate
    update_data = LessonUpdate(title="New Title")
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.update_lesson(
            lesson_id=lesson.id,
            data=update_data,
            user_role="teacher"
        )
    
    assert exc_info.value.status_code == 400
    assert "finished" in exc_info.value.detail.lower()

