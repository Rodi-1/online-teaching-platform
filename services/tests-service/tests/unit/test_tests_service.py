"""
Unit tests for tests service - testing pure business logic
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from app.services.tests_service import TestsService


class TestCalculateGrade:
    """Tests for _calculate_grade method - pure logic"""
    
    def test_calculate_grade_excellent(self):
        """Test that 90%+ returns grade 5"""
        mock_repo = Mock()
        service = TestsService(mock_repo)
        
        assert service._calculate_grade(95.0) == 5
        assert service._calculate_grade(90.0) == 5
        assert service._calculate_grade(100.0) == 5
    
    def test_calculate_grade_good(self):
        """Test that 75-89% returns grade 4"""
        mock_repo = Mock()
        service = TestsService(mock_repo)
        
        assert service._calculate_grade(85.0) == 4
        assert service._calculate_grade(75.0) == 4
        assert service._calculate_grade(89.9) == 4
    
    def test_calculate_grade_satisfactory(self):
        """Test that 60-74% returns grade 3"""
        mock_repo = Mock()
        service = TestsService(mock_repo)
        
        assert service._calculate_grade(70.0) == 3
        assert service._calculate_grade(60.0) == 3
    
    def test_calculate_grade_unsatisfactory(self):
        """Test that <60% returns grade 2"""
        mock_repo = Mock()
        service = TestsService(mock_repo)
        
        assert service._calculate_grade(50.0) == 2
        assert service._calculate_grade(30.0) == 2
        assert service._calculate_grade(0.0) == 2


class TestCheckAnswer:
    """Tests for _check_answer method - answer checking logic"""
    
    def test_check_single_choice_correct(self):
        """Test single choice correct answer"""
        mock_repo = Mock()
        service = TestsService(mock_repo)
        
        question = MagicMock()
        question.type = "single_choice"
        question.correct_answers = ["B"]
        question.max_score = 10.0
        
        is_correct, score = service._check_answer(question, "B")
        
        assert is_correct is True
        assert score == 10.0
    
    def test_check_single_choice_incorrect(self):
        """Test single choice incorrect answer"""
        mock_repo = Mock()
        service = TestsService(mock_repo)
        
        question = MagicMock()
        question.type = "single_choice"
        question.correct_answers = ["B"]
        question.max_score = 10.0
        
        is_correct, score = service._check_answer(question, "A")
        
        assert is_correct is False
        assert score == 0.0
    
    def test_check_multiple_choice_correct(self):
        """Test multiple choice correct answer (all correct options selected)"""
        mock_repo = Mock()
        service = TestsService(mock_repo)
        
        question = MagicMock()
        question.type = "multiple_choice"
        question.correct_answers = ["A", "C"]
        question.max_score = 10.0
        
        is_correct, score = service._check_answer(question, ["A", "C"])
        
        assert is_correct is True
        assert score == 10.0
    
    def test_check_multiple_choice_incorrect(self):
        """Test multiple choice incorrect answer (missing option)"""
        mock_repo = Mock()
        service = TestsService(mock_repo)
        
        question = MagicMock()
        question.type = "multiple_choice"
        question.correct_answers = ["A", "C"]
        question.max_score = 10.0
        
        is_correct, score = service._check_answer(question, ["A"])
        
        assert is_correct is False
        assert score == 0.0
    
    def test_check_text_answer_correct(self):
        """Test text answer - case insensitive comparison"""
        mock_repo = Mock()
        service = TestsService(mock_repo)
        
        question = MagicMock()
        question.type = "text"
        question.correct_answers = ["Python"]
        question.max_score = 5.0
        
        is_correct, score = service._check_answer(question, "python")
        
        assert is_correct is True
        assert score == 5.0
    
    def test_check_answer_no_correct_answers(self):
        """Test answer when no correct answers defined (manual grading)"""
        mock_repo = Mock()
        service = TestsService(mock_repo)
        
        question = MagicMock()
        question.type = "text"
        question.correct_answers = None
        question.max_score = 10.0
        
        is_correct, score = service._check_answer(question, "any answer")
        
        assert is_correct is None
        assert score == 10.0
