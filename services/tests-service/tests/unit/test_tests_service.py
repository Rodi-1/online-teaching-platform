"""
Unit tests for tests service
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta

from app.services.tests_service import TestsService


def test_create_test_validates_time_limit():
    """Test that create_test validates time_limit is positive"""
    # Arrange
    mock_repo = Mock()
    service = TestsService(mock_repo)
    
    from app.models.schemas import TestCreate
    invalid_data = TestCreate(
        title="Test",
        description="Test",
        time_limit=-10,  # Invalid negative time
        max_score=100,
        passing_score=60
    )
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.create_test(
            course_id=uuid4(),
            data=invalid_data,
            user_role="teacher"
        )
    
    assert exc_info.value.status_code == 400


def test_submit_test_validates_deadline():
    """Test that submit_test checks if test is not past deadline"""
    # Arrange
    mock_repo = Mock()
    
    # Test with past deadline
    test = MagicMock(
        id=uuid4(),
        available_until=datetime.utcnow() - timedelta(days=1),
        status="published"
    )
    mock_repo.get_test.return_value = test
    
    service = TestsService(mock_repo)
    
    from app.models.schemas import TestSubmissionCreate
    submission_data = TestSubmissionCreate(answers={})
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.submit_test(
            test_id=test.id,
            student_id=uuid4(),
            data=submission_data
        )
    
    assert exc_info.value.status_code == 400

