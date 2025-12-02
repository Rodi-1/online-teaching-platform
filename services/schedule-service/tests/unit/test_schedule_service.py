"""
Unit tests for schedule service - testing pure business logic
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.schedule_service import ScheduleService


class TestCheckTeacherOrAdmin:
    """Tests for _check_teacher_or_admin method - role validation"""
    
    def test_teacher_allowed(self):
        """Test that teacher role is allowed"""
        mock_repo = Mock()
        service = ScheduleService(mock_repo)
        
        # Should not raise
        service._check_teacher_or_admin("teacher")
    
    def test_admin_allowed(self):
        """Test that admin role is allowed"""
        mock_repo = Mock()
        service = ScheduleService(mock_repo)
        
        # Should not raise
        service._check_teacher_or_admin("admin")
    
    def test_student_forbidden(self):
        """Test that student role is forbidden"""
        from fastapi import HTTPException
        
        mock_repo = Mock()
        service = ScheduleService(mock_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            service._check_teacher_or_admin("student")
        
        assert exc_info.value.status_code == 403
        assert "teacher" in exc_info.value.detail.lower() or "admin" in exc_info.value.detail.lower()
    
    def test_unknown_role_forbidden(self):
        """Test that unknown role is forbidden"""
        from fastapi import HTTPException
        
        mock_repo = Mock()
        service = ScheduleService(mock_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            service._check_teacher_or_admin("guest")
        
        assert exc_info.value.status_code == 403


class TestValidateDates:
    """Tests for _validate_dates method - date validation"""
    
    def test_valid_dates(self):
        """Test that valid date range passes"""
        mock_repo = Mock()
        service = ScheduleService(mock_repo)
        
        start_at = datetime.utcnow()
        end_at = start_at + timedelta(hours=2)
        
        # Should not raise
        service._validate_dates(start_at, end_at)
    
    def test_end_before_start_raises_error(self):
        """Test that end_at before start_at raises error"""
        from fastapi import HTTPException
        
        mock_repo = Mock()
        service = ScheduleService(mock_repo)
        
        start_at = datetime.utcnow()
        end_at = start_at - timedelta(hours=1)
        
        with pytest.raises(HTTPException) as exc_info:
            service._validate_dates(start_at, end_at)
        
        assert exc_info.value.status_code == 400
        assert "end_at" in exc_info.value.detail.lower()
    
    def test_same_start_end_raises_error(self):
        """Test that start_at == end_at raises error"""
        from fastapi import HTTPException
        
        mock_repo = Mock()
        service = ScheduleService(mock_repo)
        
        same_time = datetime.utcnow()
        
        with pytest.raises(HTTPException) as exc_info:
            service._validate_dates(same_time, same_time)
        
        assert exc_info.value.status_code == 400
