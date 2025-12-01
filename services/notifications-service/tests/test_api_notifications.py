"""
Test cases for notifications API endpoints
"""
from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastapi import status


class TestNotificationsEndpoints:
    """Test cases for notifications endpoints"""
    
    def test_get_my_notifications_empty(self, client, mock_jwt_token):
        """Test GET /api/notifications/me returns empty list initially"""
        response = client.get(
            "/api/notifications/me",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["items"]) == 0
    
    def test_create_notification(self, client, mock_jwt_token, sample_user_id):
        """Test POST /api/notifications creates notification"""
        notification_data = {
            "user_id": str(sample_user_id),
            "type": "homework",
            "title": "Новое домашнее задание",
            "body": "По курсу \"Алгебра\" выдано новое ДЗ.",
            "data": {
                "course_id": str(uuid4()),
                "homework_id": str(uuid4()),
                "due_at": "2025-03-01T18:00:00Z"
            },
            "send_email": True,
            "send_push": False
        }
        
        response = client.post(
            "/api/notifications",
            json=notification_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user_id"] == str(sample_user_id)
        assert data["type"] == "homework"
        assert data["title"] == notification_data["title"]
        assert data["is_read"] == False
        assert "id" in data
    
    def test_get_notifications_after_creation(self, client, mock_jwt_token, sample_user_id):
        """Test getting notifications after creation"""
        # Create notification
        notification_data = {
            "user_id": str(sample_user_id),
            "type": "test",
            "title": "Test Notification",
            "body": "Test body",
            "send_email": False,
            "send_push": False
        }
        
        client.post(
            "/api/notifications",
            json=notification_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Get notifications
        response = client.get(
            "/api/notifications/me",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["type"] == "test"
    
    def test_mark_notification_read(self, client, mock_jwt_token, sample_user_id):
        """Test POST /api/notifications/{id}/read marks notification as read"""
        # Create notification
        notification_data = {
            "user_id": str(sample_user_id),
            "type": "achievement",
            "title": "New Achievement",
            "body": "You earned an achievement!",
            "send_email": False,
            "send_push": False
        }
        
        create_response = client.post(
            "/api/notifications",
            json=notification_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        notification_id = create_response.json()["id"]
        
        # Mark as read
        response = client.post(
            f"/api/notifications/{notification_id}/read",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_read"] == True
        assert data["read_at"] is not None
    
    def test_mark_notification_read_not_found(self, client, mock_jwt_token):
        """Test marking non-existent notification returns 404"""
        fake_id = str(uuid4())
        
        response = client.post(
            f"/api/notifications/{fake_id}/read",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_unread_count(self, client, mock_jwt_token, sample_user_id):
        """Test GET /api/notifications/me/unread-count returns correct count"""
        # Create multiple notifications
        for i in range(3):
            notification_data = {
                "user_id": str(sample_user_id),
                "type": "system",
                "title": f"Notification {i}",
                "body": f"Body {i}",
                "send_email": False,
                "send_push": False
            }
            
            client.post(
                "/api/notifications",
                json=notification_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )
        
        # Get unread count
        response = client.get(
            "/api/notifications/me/unread-count",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["unread_count"] == 3
        assert data["user_id"] == str(sample_user_id)
    
    def test_filter_by_status_unread(self, client, mock_jwt_token, sample_user_id):
        """Test filtering notifications by unread status"""
        # Create notifications
        for i in range(2):
            notification_data = {
                "user_id": str(sample_user_id),
                "type": "homework",
                "title": f"Homework {i}",
                "body": f"Body {i}",
                "send_email": False,
                "send_push": False
            }
            
            response = client.post(
                "/api/notifications",
                json=notification_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )
            
            # Mark first one as read
            if i == 0:
                notification_id = response.json()["id"]
                client.post(
                    f"/api/notifications/{notification_id}/read",
                    headers={"Authorization": f"Bearer {mock_jwt_token}"}
                )
        
        # Get only unread
        response = client.get(
            "/api/notifications/me?status=unread",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert all(not item["is_read"] for item in data["items"])
    
    def test_mark_all_read(self, client, mock_jwt_token, sample_user_id):
        """Test POST /api/notifications:mark-all-read marks all as read"""
        # Create multiple notifications
        for i in range(3):
            notification_data = {
                "user_id": str(sample_user_id),
                "type": "schedule",
                "title": f"Schedule {i}",
                "body": f"Body {i}",
                "send_email": False,
                "send_push": False
            }
            
            client.post(
                "/api/notifications",
                json=notification_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )
        
        # Mark all as read
        response = client.post(
            "/api/notifications:mark-all-read",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["updated_count"] == 3
        assert data["user_id"] == str(sample_user_id)
        
        # Verify all are read
        get_response = client.get(
            "/api/notifications/me/unread-count",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        assert get_response.json()["unread_count"] == 0
    
    def test_filter_by_type(self, client, mock_jwt_token, sample_user_id):
        """Test filtering notifications by type"""
        # Create notifications of different types
        types = ["homework", "test", "homework"]
        for notification_type in types:
            notification_data = {
                "user_id": str(sample_user_id),
                "type": notification_type,
                "title": f"{notification_type} notification",
                "body": "Body",
                "send_email": False,
                "send_push": False
            }
            
            client.post(
                "/api/notifications",
                json=notification_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )
        
        # Filter by homework type
        response = client.get(
            "/api/notifications/me?type=homework",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert all(item["type"] == "homework" for item in data["items"])
    
    def test_pagination(self, client, mock_jwt_token, sample_user_id):
        """Test pagination of notifications"""
        # Create multiple notifications
        for i in range(5):
            notification_data = {
                "user_id": str(sample_user_id),
                "type": "system",
                "title": f"Notification {i}",
                "body": f"Body {i}",
                "send_email": False,
                "send_push": False
            }
            
            client.post(
                "/api/notifications",
                json=notification_data,
                headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )
        
        # Get with pagination
        response = client.get(
            "/api/notifications/me?offset=0&count=3",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3
        assert data["offset"] == 0
        assert data["count"] == 3
    
    def test_unauthorized_access(self, client):
        """Test access without token returns 401"""
        response = client.get("/api/notifications/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

