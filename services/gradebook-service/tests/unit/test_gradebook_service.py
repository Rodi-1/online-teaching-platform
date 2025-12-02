"""
Unit tests for gradebook service
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from app.services.gradebook_service import GradebookService


def test_record_grade_validates_score_range():
    """Test that record_grade validates score is within valid range"""
    # Arrange
    mock_repo = Mock()
    service = GradebookService(mock_repo)
    
    # Act & Assert - negative score
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.record_grade(
            student_id=uuid4(),
            course_id=uuid4(),
            assignment_type="homework",
            assignment_id=uuid4(),
            score=-10,  # Invalid negative score
            max_score=100,
            recorded_by=str(uuid4())
        )
    
    assert exc_info.value.status_code == 400


def test_record_grade_validates_score_not_exceeds_max():
    """Test that score cannot exceed max_score"""
    # Arrange
    mock_repo = Mock()
    service = GradebookService(mock_repo)
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.record_grade(
            student_id=uuid4(),
            course_id=uuid4(),
            assignment_type="test",
            assignment_id=uuid4(),
            score=150,  # Exceeds max_score
            max_score=100,
            recorded_by=str(uuid4())
        )
    
    assert exc_info.value.status_code == 400

