"""
Unit tests for reports service
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4

from app.services.reports_service import ReportsService
from app.models.schemas import ReportGenerateRequest


def test_start_generation_creates_operation():
    """Test that start_generation creates operation with pending status"""
    # Arrange
    mock_repo = Mock()
    operation = MagicMock(
        id=uuid4(),
        status="pending",
        type="course_performance",
        format="xlsx"
    )
    mock_repo.create_operation.return_value = operation
    mock_repo.set_operation_started.return_value = operation
    mock_repo.set_operation_completed.return_value = operation
    mock_repo.get_operation.return_value = operation
    
    report = MagicMock(id=uuid4())
    mock_repo.create_report.return_value = report
    
    service = ReportsService(mock_repo)
    
    request = ReportGenerateRequest(
        type="course_performance",
        format="xlsx"
    )
    
    # Act
    with patch.object(service, '_generate_report_file', return_value=1024):
        result = service.start_generation(request, "user-123")
    
    # Assert
    mock_repo.create_operation.assert_called_once()
    assert result.type == "course_performance"
    assert result.format == "xlsx"


def test_regenerate_report_reuses_parameters():
    """Test that regenerate_report uses same parameters as original"""
    # Arrange
    mock_repo = Mock()
    
    original_report = MagicMock(
        id=uuid4(),
        type="student_progress",
        format="pdf",
        filters_json={"student_id": "student-123"},
        created_by="user-123"
    )
    mock_repo.get_report.return_value = original_report
    
    operation = MagicMock(id=uuid4(), status="pending")
    mock_repo.create_operation.return_value = operation
    mock_repo.set_operation_started.return_value = operation
    mock_repo.set_operation_completed.return_value = operation
    mock_repo.get_operation.return_value = operation
    
    new_report = MagicMock(id=uuid4())
    mock_repo.create_report.return_value = new_report
    
    service = ReportsService(mock_repo)
    
    # Act
    with patch.object(service, '_generate_report_file', return_value=1024):
        result = service.regenerate_report(
            report_id=original_report.id,
            requested_by="user-123",
            user_role="teacher"
        )
    
    # Assert
    create_call = mock_repo.create_operation.call_args
    assert create_call[1]['type'] == "student_progress"
    assert create_call[1]['format'] == "pdf"
    assert create_call[1]['filters_json'] == {"student_id": "student-123"}

