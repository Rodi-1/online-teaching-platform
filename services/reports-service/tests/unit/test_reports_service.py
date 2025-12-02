"""
Unit tests for reports service - testing pure business logic
"""
import pytest
import os
from unittest.mock import Mock, patch
from uuid import uuid4

from app.services.reports_service import ReportsService


class TestCheckTeacherOrAdmin:
    """Tests for _check_teacher_or_admin method - role validation"""
    
    def test_teacher_allowed(self):
        """Test that teacher role is allowed"""
        mock_repo = Mock()
        service = ReportsService(mock_repo)
        
        # Should not raise
        service._check_teacher_or_admin("teacher")
    
    def test_admin_allowed(self):
        """Test that admin role is allowed"""
        mock_repo = Mock()
        service = ReportsService(mock_repo)
        
        # Should not raise
        service._check_teacher_or_admin("admin")
    
    def test_manager_allowed(self):
        """Test that manager role is allowed"""
        mock_repo = Mock()
        service = ReportsService(mock_repo)
        
        # Should not raise
        service._check_teacher_or_admin("manager")
    
    def test_student_forbidden(self):
        """Test that student role is forbidden"""
        from fastapi import HTTPException
        
        mock_repo = Mock()
        service = ReportsService(mock_repo)
        
        with pytest.raises(HTTPException) as exc_info:
            service._check_teacher_or_admin("student")
        
        assert exc_info.value.status_code == 403


class TestGenerateFilePath:
    """Tests for _generate_file_path method - file path generation"""
    
    @patch('app.services.reports_service.settings')
    def test_generate_file_path_pdf(self, mock_settings):
        """Test PDF file path generation"""
        mock_settings.REPORT_STORAGE_PATH = "/data/reports"
        
        mock_repo = Mock()
        service = ReportsService(mock_repo)
        
        report_id = uuid4()
        file_path = service._generate_file_path(report_id, "pdf")
        
        # Check path contains expected parts (platform-independent)
        assert "rep-" in file_path
        assert file_path.endswith(".pdf")
        # Normalize path for comparison
        assert "reports" in file_path.replace("\\", "/")
    
    @patch('app.services.reports_service.settings')
    def test_generate_file_path_xlsx(self, mock_settings):
        """Test XLSX file path generation"""
        mock_settings.REPORT_STORAGE_PATH = "/data/reports"
        
        mock_repo = Mock()
        service = ReportsService(mock_repo)
        
        report_id = uuid4()
        file_path = service._generate_file_path(report_id, "xlsx")
        
        assert file_path.endswith(".xlsx")
        assert "rep-" in file_path


class TestBuildDownloadUrl:
    """Tests for _build_download_url method - URL building"""
    
    @patch('app.services.reports_service.settings')
    def test_build_download_url(self, mock_settings):
        """Test download URL building"""
        mock_settings.REPORT_STORAGE_BASE_URL = "https://files.example.com/reports/"
        
        mock_repo = Mock()
        service = ReportsService(mock_repo)
        
        file_path = "/data/reports/rep-12345678.pdf"
        url = service._build_download_url(file_path)
        
        assert url == "https://files.example.com/reports/rep-12345678.pdf"
    
    @patch('app.services.reports_service.settings')
    def test_build_download_url_no_trailing_slash(self, mock_settings):
        """Test URL building when base URL has no trailing slash"""
        mock_settings.REPORT_STORAGE_BASE_URL = "https://files.example.com/reports"
        
        mock_repo = Mock()
        service = ReportsService(mock_repo)
        
        file_path = "/data/reports/rep-12345678.xlsx"
        url = service._build_download_url(file_path)
        
        assert url == "https://files.example.com/reports/rep-12345678.xlsx"
