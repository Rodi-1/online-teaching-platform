"""
Test cases for profile API endpoints
"""
from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastapi import status


class TestProfileEndpoints:
    """Test cases for profile endpoints"""
    
    def test_get_my_profile_creates_if_not_exists(self, client, mock_jwt_token):
        """Test GET /api/profile/me creates profile if it doesn't exist"""
        response = client.get(
            "/api/profile/me",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "user_id" in data
        assert "progress" in data
        assert data["progress"]["total_courses"] == 0
        assert data["progress"]["homeworks_completed"] == 0
    
    def test_update_my_profile(self, client, mock_jwt_token):
        """Test PATCH /api/profile/me updates profile"""
        # First create profile
        client.get(
            "/api/profile/me",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Update profile
        update_data = {
            "avatar_url": "https://example.com/avatar.png",
            "about": "Test user profile",
            "social_links": ["https://github.com/testuser"]
        }
        
        response = client.patch(
            "/api/profile/me",
            json=update_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["avatar_url"] == update_data["avatar_url"]
        assert data["about"] == update_data["about"]
        assert data["social_links"] == update_data["social_links"]
    
    def test_get_my_profile_without_auth(self, client):
        """Test GET /api/profile/me without authentication returns 401"""
        response = client.get("/api/profile/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAchievementEndpoints:
    """Test cases for achievement endpoints"""
    
    def test_create_achievement(self, client, mock_jwt_token, sample_user_id):
        """Test POST /api/profile/users/{user_id}/achievements creates achievement"""
        achievement_data = {
            "code": "first_homework",
            "title": "First Homework",
            "description": "Completed first homework assignment",
            "icon_url": "https://example.com/icon.png",
            "received_at": datetime.utcnow().isoformat()
        }
        
        response = client.post(
            f"/api/profile/users/{sample_user_id}/achievements",
            json=achievement_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == achievement_data["code"]
        assert data["title"] == achievement_data["title"]
        assert "id" in data
    
    def test_create_duplicate_achievement_fails(self, client, mock_jwt_token, sample_user_id):
        """Test creating duplicate achievement returns 400"""
        achievement_data = {
            "code": "test_achievement",
            "title": "Test Achievement",
            "description": "Test description",
            "received_at": datetime.utcnow().isoformat()
        }
        
        # Create first achievement
        response1 = client.post(
            f"/api/profile/users/{sample_user_id}/achievements",
            json=achievement_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to create duplicate
        response2 = client.post(
            f"/api/profile/users/{sample_user_id}/achievements",
            json=achievement_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_user_achievements(self, client, mock_jwt_token, sample_user_id):
        """Test GET /api/profile/users/{user_id}/achievements returns achievements"""
        # Create an achievement first
        achievement_data = {
            "code": "test_ach",
            "title": "Test",
            "description": "Test description",
            "received_at": datetime.utcnow().isoformat()
        }
        
        client.post(
            f"/api/profile/users/{sample_user_id}/achievements",
            json=achievement_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Get achievements
        response = client.get(
            f"/api/profile/users/{sample_user_id}/achievements",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
    
    def test_get_achievements_with_pagination(self, client, mock_jwt_token, sample_user_id):
        """Test achievement pagination"""
        # Create multiple achievements
        for i in range(5):
            achievement_data = {
                "code": f"achievement_{i}",
                "title": f"Achievement {i}",
                "description": f"Description {i}",
                "received_at": datetime.utcnow().isoformat()
            }
            client.post(
                f"/api/profile/users/{sample_user_id}/achievements",
                json=achievement_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )
        
        # Get with pagination
        response = client.get(
            f"/api/profile/users/{sample_user_id}/achievements?offset=0&count=3",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3


class TestStatsEndpoints:
    """Test cases for statistics endpoints"""
    
    def test_update_stats(self, client, mock_jwt_token, sample_user_id):
        """Test POST /api/profile/users/{user_id}/stats:update updates statistics"""
        # First create profile
        client.get(
            "/api/profile/me",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Update stats
        stats_data = {
            "homeworks_completed_delta": 1,
            "tests_passed_delta": 1,
            "average_grade": 4.5
        }
        
        response = client.post(
            f"/api/profile/users/{sample_user_id}/stats:update",
            json=stats_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "progress" in data
        assert data["progress"]["homeworks_completed"] == 1
        assert data["progress"]["tests_passed"] == 1
        assert data["progress"]["average_grade"] == 4.5
    
    def test_update_stats_multiple_times(self, client, mock_jwt_token, sample_user_id):
        """Test updating stats multiple times accumulates deltas"""
        # Create profile
        client.get(
            "/api/profile/me",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # First update
        client.post(
            f"/api/profile/users/{sample_user_id}/stats:update",
            json={"homeworks_completed_delta": 2},
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Second update
        response = client.post(
            f"/api/profile/users/{sample_user_id}/stats:update",
            json={"homeworks_completed_delta": 3},
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["progress"]["homeworks_completed"] == 5

