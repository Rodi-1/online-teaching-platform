"""
Unit tests for profile service
"""
import pytest
from unittest.mock import Mock, MagicMock
from uuid import uuid4

from app.services.profile_service import ProfileService


def test_update_profile_validates_phone():
    """Test that update_profile validates phone format"""
    # Arrange
    mock_repo = Mock()
    
    profile = MagicMock(
        user_id=uuid4(),
        phone=None
    )
    mock_repo.get_profile.return_value = profile
    
    service = ProfileService(mock_repo)
    
    from app.models.schemas import ProfileUpdate
    invalid_data = ProfileUpdate(phone="invalid-phone")
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.update_profile(
            user_id=profile.user_id,
            data=invalid_data,
            current_user_id=str(profile.user_id)
        )
    
    assert exc_info.value.status_code == 400


def test_update_profile_checks_ownership():
    """Test that user can only update their own profile"""
    # Arrange
    mock_repo = Mock()
    
    profile = MagicMock(user_id=uuid4())
    mock_repo.get_profile.return_value = profile
    
    service = ProfileService(mock_repo)
    
    from app.models.schemas import ProfileUpdate
    data = ProfileUpdate(bio="New bio")
    
    # Act & Assert
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        service.update_profile(
            user_id=profile.user_id,
            data=data,
            current_user_id=str(uuid4())  # Different user
        )
    
    assert exc_info.value.status_code == 403

