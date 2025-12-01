"""
Tests for user endpoints
"""
import pytest
from fastapi import status


def test_get_current_user(client, test_user_data):
    """Test getting current user profile"""
    # Register and login
    client.post("/api/users", json=test_user_data)
    login_response = client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["first_name"] == test_user_data["first_name"]


def test_get_current_user_unauthorized(client):
    """Test getting current user without token fails"""
    response = client.get("/api/users/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_profile(client, test_user_data):
    """Test updating user profile"""
    # Register and login
    client.post("/api/users", json=test_user_data)
    login_response = client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]
    
    # Update profile
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }
    response = client.patch(
        "/api/users/me",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"


def test_list_users_admin(client, test_user_data, admin_user_data):
    """Test listing users as admin"""
    # Register regular user
    client.post("/api/users", json=test_user_data)
    
    # Register admin user
    client.post("/api/users", json=admin_user_data)
    admin_login_response = client.post("/api/auth/login", json={
        "email": admin_user_data["email"],
        "password": admin_user_data["password"]
    })
    admin_token = admin_login_response.json()["access_token"]
    
    # List users as admin
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 2  # At least test user and admin


def test_list_users_forbidden_for_non_admin(client, test_user_data):
    """Test listing users as non-admin user fails"""
    # Register and login as student
    client.post("/api/users", json=test_user_data)
    login_response = client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]
    
    # Try to list users
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_password_validation(client, test_user_data):
    """Test password validation (minimum length)"""
    invalid_data = test_user_data.copy()
    invalid_data["password"] = "short"
    
    response = client.post("/api/users", json=invalid_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_email_validation(client, test_user_data):
    """Test email validation"""
    invalid_data = test_user_data.copy()
    invalid_data["email"] = "invalid-email"
    
    response = client.post("/api/users", json=invalid_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

