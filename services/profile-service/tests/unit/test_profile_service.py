"""
Unit tests for profile service - testing business logic
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4
from datetime import datetime

from app.services.profile_service import ProfileService


class TestCreateAchievement:
    """Tests for create_achievement duplicate checking"""
    
    def test_create_achievement_success(self):
        """Test successful achievement creation"""
        mock_repo = Mock()
        service = ProfileService(mock_repo)
        
        user_id = uuid4()
        
        # Mock - no duplicate exists
        mock_repo.achievement_exists.return_value = False
        
        mock_achievement = MagicMock()
        mock_achievement.id = uuid4()
        mock_achievement.user_id = user_id
        mock_achievement.code = "first_homework"
        mock_achievement.title = "First Homework"
        mock_achievement.description = "Completed first homework"
        mock_achievement.icon_url = None
        mock_achievement.received_at = datetime.utcnow()
        mock_repo.create_achievement.return_value = mock_achievement
        
        from app.models.schemas import AchievementCreateRequest
        data = AchievementCreateRequest(
            code="first_homework",
            title="First Homework",
            description="Completed first homework",
            received_at=datetime.utcnow()
        )
        
        result = service.create_achievement(user_id, data, check_duplicate=True)
        
        mock_repo.create_achievement.assert_called_once()
    
    def test_create_achievement_duplicate_raises_error(self):
        """Test that duplicate achievement raises ValueError"""
        mock_repo = Mock()
        service = ProfileService(mock_repo)
        
        user_id = uuid4()
        
        # Mock - duplicate exists
        mock_repo.achievement_exists.return_value = True
        
        from app.models.schemas import AchievementCreateRequest
        data = AchievementCreateRequest(
            code="first_homework",
            title="First Homework",
            description="Completed first homework",
            received_at=datetime.utcnow()
        )
        
        with pytest.raises(ValueError) as exc_info:
            service.create_achievement(user_id, data, check_duplicate=True)
        
        assert "already exists" in str(exc_info.value)
    
    def test_create_achievement_skip_duplicate_check(self):
        """Test that duplicate check can be skipped"""
        mock_repo = Mock()
        service = ProfileService(mock_repo)
        
        user_id = uuid4()
        
        mock_achievement = MagicMock()
        mock_achievement.id = uuid4()
        mock_achievement.user_id = user_id
        mock_achievement.code = "first_homework"
        mock_achievement.title = "First Homework"
        mock_achievement.description = "Completed first homework"
        mock_achievement.icon_url = None
        mock_achievement.received_at = datetime.utcnow()
        mock_repo.create_achievement.return_value = mock_achievement
        
        from app.models.schemas import AchievementCreateRequest
        data = AchievementCreateRequest(
            code="first_homework",
            title="First Homework",
            description="Completed first homework",
            received_at=datetime.utcnow()
        )
        
        # Should not check for duplicate
        result = service.create_achievement(user_id, data, check_duplicate=False)
        
        mock_repo.achievement_exists.assert_not_called()
        mock_repo.create_achievement.assert_called_once()
