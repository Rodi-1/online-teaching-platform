"""
Tests for authentication endpoints
"""
import pytest
from fastapi import status


def test_register_user_success(client, test_user_data):
    """Test successful user registration"""
    response = client.post("/api/users", json=test_user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["first_name"] == test_user_data["first_name"]
    assert data["last_name"] == test_user_data["last_name"]
    assert data["role"] == test_user_data["role"]
    assert "password" not in data
    assert "password_hash" not in data
    assert data["is_email_confirmed"] is False
    assert data["is_phone_confirmed"] is False


def test_register_user_duplicate_email(client, test_user_data):
    """Test registration with duplicate email fails"""
    # Register first user
    client.post("/api/users", json=test_user_data)
    
    # Try to register with same email
    response = client.post("/api/users", json=test_user_data)
    
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "email" in response.json()["detail"].lower()


def test_login_success(client, test_user_data):
    """Test successful login"""
    # Register user
    client.post("/api/users", json=test_user_data)
    
    # Login
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert "expires_in" in data
    assert "user" in data
    assert data["user"]["email"] == test_user_data["email"]


def test_login_wrong_password(client, test_user_data):
    """Test login with wrong password fails"""
    # Register user
    client.post("/api/users", json=test_user_data)
    
    # Try to login with wrong password
    login_data = {
        "email": test_user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with nonexistent user fails"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "password123"
    }
    response = client.post("/api/auth/login", json=login_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout(client, test_user_data):
    """Test logout endpoint"""
    # Register and login
    client.post("/api/users", json=test_user_data)
    login_response = client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = login_response.json()["access_token"]
    
    # Logout
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["result"] == "ok"

