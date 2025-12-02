"""
Unit tests for homeworks service
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta

from app.services.homeworks_service import HomeworksService
from app.models.schemas import HomeworkCreate


def test_create_homework_validates_due_date():
    """Test that create_homework validates due date is in future"""
    # Arrange
    mock_repo = Mock()
    service = HomeworksService(mock_repo)
    
    past_date = datetime.utcnow() - timedelta(days=1)
    homework_data = HomeworkCreate(
        title="Test Homework",
        description="Test description",
        due_at=past_date,
        max_score=100
    )
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.create_homework(
            course_id=uuid4(),
            data=homework_data,
            created_by=str(uuid4()),
            user_role="teacher"
        )
    
    assert exc_info.value.status_code == 400
    assert "future" in exc_info.value.detail.lower()


def test_grade_submission_validates_score():
    """Test that grade_submission validates score against max_score"""
    # Arrange
    mock_repo = Mock()
    
    homework = MagicMock(
        id=uuid4(),
        max_score=100,
        status="assigned"
    )
    submission = MagicMock(
        id=uuid4(),
        homework_id=homework.id,
        student_id=uuid4()
    )
    
    mock_repo.get_homework.return_value = homework
    mock_repo.get_submission.return_value = submission
    
    service = HomeworksService(mock_repo)
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.grade_submission(
            homework_id=homework.id,
            submission_id=submission.id,
            score=150,  # More than max_score
            teacher_comment="Good work",
            status="checked",
            teacher_id=str(uuid4())
        )
    
    assert exc_info.value.status_code == 400
    assert "max_score" in exc_info.value.detail.lower()

