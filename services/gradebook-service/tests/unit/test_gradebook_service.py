"""
Unit tests for gradebook service - testing pure business logic
"""
import pytest
from unittest.mock import Mock
from uuid import uuid4

from app.services.gradebook_service import GradebookService


class TestCalculateGrade:
    """Tests for calculate_grade method - pure logic without DB"""
    
    def test_calculate_grade_excellent(self):
        """Test that 90%+ returns grade 5"""
        # Arrange
        mock_db = Mock()
        service = GradebookService(mock_db)
        
        # Act
        percent, grade = service.calculate_grade(score=95, max_score=100)
        
        # Assert
        assert percent == 95.0
        assert grade == 5
    
    def test_calculate_grade_good(self):
        """Test that 75-89% returns grade 4"""
        mock_db = Mock()
        service = GradebookService(mock_db)
        
        percent, grade = service.calculate_grade(score=80, max_score=100)
        
        assert percent == 80.0
        assert grade == 4
    
    def test_calculate_grade_satisfactory(self):
        """Test that 60-74% returns grade 3"""
        mock_db = Mock()
        service = GradebookService(mock_db)
        
        percent, grade = service.calculate_grade(score=65, max_score=100)
        
        assert percent == 65.0
        assert grade == 3
    
    def test_calculate_grade_unsatisfactory(self):
        """Test that <60% returns grade 2"""
        mock_db = Mock()
        service = GradebookService(mock_db)
        
        percent, grade = service.calculate_grade(score=45, max_score=100)
        
        assert percent == 45.0
        assert grade == 2
    
    def test_calculate_grade_negative_score_raises_error(self):
        """Test that negative score raises HTTPException"""
        from fastapi import HTTPException
        
        mock_db = Mock()
        service = GradebookService(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            service.calculate_grade(score=-10, max_score=100)
        
        assert exc_info.value.status_code == 400
        assert "negative" in exc_info.value.detail.lower()
    
    def test_calculate_grade_score_exceeds_max_raises_error(self):
        """Test that score > max_score raises HTTPException"""
        from fastapi import HTTPException
        
        mock_db = Mock()
        service = GradebookService(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            service.calculate_grade(score=150, max_score=100)
        
        assert exc_info.value.status_code == 400
        assert "exceed" in exc_info.value.detail.lower()
    
    def test_calculate_grade_zero_max_score_raises_error(self):
        """Test that max_score <= 0 raises HTTPException"""
        from fastapi import HTTPException
        
        mock_db = Mock()
        service = GradebookService(mock_db)
        
        with pytest.raises(HTTPException) as exc_info:
            service.calculate_grade(score=50, max_score=0)
        
        assert exc_info.value.status_code == 400
        assert "positive" in exc_info.value.detail.lower()
