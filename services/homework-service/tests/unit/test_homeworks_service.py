"""
Unit tests for homeworks service - testing business logic
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from app.services.homeworks_service import HomeworkService
from app.models.schemas import GradeSubmissionRequest
from app.models.db_models import SubmissionStatus


class TestGradeSubmission:
    """Tests for grade_submission validation"""
    
    def test_grade_exceeds_max_score_raises_error(self):
        """Test that score > max_score raises HTTPException"""
        from fastapi import HTTPException
        
        mock_db = Mock()
        service = HomeworkService(mock_db)
        
        # Mock homework with max_score=100
        homework = MagicMock()
        homework.id = uuid4()
        homework.max_score = 100
        homework.status = "assigned"
        
        # Mock submission
        submission = MagicMock()
        submission.id = uuid4()
        submission.homework_id = homework.id
        submission.student_id = uuid4()
        
        service.repo = Mock()
        service.repo.get_submission.return_value = submission
        service.repo.get_homework.return_value = homework
        
        grade_data = GradeSubmissionRequest(
            score=150,  # Exceeds max_score
            teacher_comment="Good work",
            status=SubmissionStatus.CHECKED
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.grade_submission(
                submission_id=submission.id,
                data=grade_data
            )
        
        assert exc_info.value.status_code == 400
    
    def test_negative_score_raises_error(self):
        """Test that negative score raises HTTPException"""
        from fastapi import HTTPException
        
        mock_db = Mock()
        service = HomeworkService(mock_db)
        
        homework = MagicMock()
        homework.id = uuid4()
        homework.max_score = 100
        
        submission = MagicMock()
        submission.id = uuid4()
        submission.homework_id = homework.id
        
        service.repo = Mock()
        service.repo.get_submission.return_value = submission
        service.repo.get_homework.return_value = homework
        
        # GradeSubmissionRequest has ge=0 validation, but let's test service logic
        # We need to bypass pydantic validation for this test
        grade_data = Mock()
        grade_data.score = -10
        grade_data.teacher_comment = "Test"
        grade_data.status = SubmissionStatus.CHECKED
        
        with pytest.raises(HTTPException) as exc_info:
            service.grade_submission(
                submission_id=submission.id,
                data=grade_data
            )
        
        assert exc_info.value.status_code == 400
        assert "negative" in exc_info.value.detail.lower()
    
    def test_submission_not_found_raises_error(self):
        """Test that missing submission raises HTTPException"""
        from fastapi import HTTPException
        
        mock_db = Mock()
        service = HomeworkService(mock_db)
        
        service.repo = Mock()
        service.repo.get_submission.return_value = None
        
        grade_data = GradeSubmissionRequest(
            score=80,
            teacher_comment="Good work",
            status=SubmissionStatus.CHECKED
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.grade_submission(
                submission_id=uuid4(),
                data=grade_data
            )
        
        assert exc_info.value.status_code == 404
        assert "submission" in exc_info.value.detail.lower()


class TestCreateHomework:
    """Tests for create_homework validation"""
    
    def test_past_due_date_raises_error(self):
        """Test that past due date raises HTTPException"""
        from fastapi import HTTPException
        from app.models.schemas import HomeworkCreate
        
        mock_db = Mock()
        service = HomeworkService(mock_db)
        
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        
        homework_data = HomeworkCreate(
            title="Test Homework",
            description="Test description",
            due_at=past_date,
            max_score=100
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_homework(
                course_id=uuid4(),
                data=homework_data
            )
        
        assert exc_info.value.status_code == 400
        assert "future" in exc_info.value.detail.lower()
