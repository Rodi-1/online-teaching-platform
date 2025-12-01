"""
Tests for schedule endpoints
"""
import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


def test_create_lesson_success(client, teacher_headers, sample_lesson_data):
    """Test successful lesson creation"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == sample_lesson_data["title"]
    assert data["description"] == sample_lesson_data["description"]
    assert data["location_type"] == sample_lesson_data["location_type"]
    assert "id" in data
    assert data["status"] == "scheduled"


def test_create_lesson_forbidden_for_student(client, student_headers, sample_lesson_data):
    """Test that students cannot create lessons"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=student_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_lesson_invalid_dates(client, teacher_headers, sample_lesson_data):
    """Test lesson creation with invalid dates (end_at before start_at)"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Swap start and end dates
    invalid_data = sample_lesson_data.copy()
    invalid_data["start_at"], invalid_data["end_at"] = invalid_data["end_at"], invalid_data["start_at"]
    
    response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=invalid_data,
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_lesson_success(client, teacher_headers, sample_lesson_data):
    """Test successful lesson update"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create lesson first
    create_response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=teacher_headers
    )
    lesson_id = create_response.json()["id"]
    
    # Update lesson
    update_data = {
        "title": "Updated Lesson Title",
        "location_type": "offline",
        "room": "Room 302"
    }
    
    response = client.patch(
        f"/api/lessons/{lesson_id}",
        json=update_data,
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["location_type"] == update_data["location_type"]
    assert data["room"] == update_data["room"]


def test_update_lesson_forbidden_for_student(client, teacher_headers, student_headers, sample_lesson_data):
    """Test that students cannot update lessons"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create lesson as teacher
    create_response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=teacher_headers
    )
    lesson_id = create_response.json()["id"]
    
    # Try to update as student
    response = client.patch(
        f"/api/lessons/{lesson_id}",
        json={"title": "Hacked"},
        headers=student_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_lesson(client, teacher_headers, sample_lesson_data):
    """Test getting a lesson by ID"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create lesson
    create_response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=teacher_headers
    )
    lesson_id = create_response.json()["id"]
    
    # Get lesson
    response = client.get(f"/api/lessons/{lesson_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == lesson_id
    assert data["title"] == sample_lesson_data["title"]


def test_get_lesson_not_found(client):
    """Test getting a non-existent lesson"""
    lesson_id = "99999999-9999-9999-9999-999999999999"
    
    response = client.get(f"/api/lessons/{lesson_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_course_schedule(client, teacher_headers, sample_lesson_data):
    """Test getting schedule for a course"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create a lesson
    client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=teacher_headers
    )
    
    # Get course schedule
    response = client.get(f"/api/courses/{course_id}/schedule")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "course_id" in data
    assert "items" in data
    assert len(data["items"]) >= 1


def test_get_my_schedule(client, student_headers):
    """Test getting current user's schedule"""
    response = client.get(
        "/api/schedule/me",
        headers=student_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "offset" in data
    assert "count" in data


def test_set_attendance_success(client, teacher_headers, sample_lesson_data, sample_attendance_data):
    """Test successful attendance marking"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create lesson
    create_response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=teacher_headers
    )
    lesson_id = create_response.json()["id"]
    
    # Set attendance
    response = client.post(
        f"/api/lessons/{lesson_id}/attendance",
        json=sample_attendance_data,
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["lesson_id"] == lesson_id
    assert len(data["items"]) == len(sample_attendance_data["items"])
    assert "updated_at" in data


def test_set_attendance_forbidden_for_student(client, teacher_headers, student_headers, sample_lesson_data, sample_attendance_data):
    """Test that students cannot set attendance"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create lesson as teacher
    create_response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=teacher_headers
    )
    lesson_id = create_response.json()["id"]
    
    # Try to set attendance as student
    response = client.post(
        f"/api/lessons/{lesson_id}/attendance",
        json=sample_attendance_data,
        headers=student_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_attendance(client, teacher_headers, sample_lesson_data, sample_attendance_data):
    """Test getting attendance for a lesson"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create lesson
    create_response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=teacher_headers
    )
    lesson_id = create_response.json()["id"]
    
    # Set attendance
    client.post(
        f"/api/lessons/{lesson_id}/attendance",
        json=sample_attendance_data,
        headers=teacher_headers
    )
    
    # Get attendance
    response = client.get(
        f"/api/lessons/{lesson_id}/attendance",
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["lesson_id"] == lesson_id
    assert "items" in data
    assert len(data["items"]) >= 1


def test_admin_can_create_lesson(client, admin_headers, sample_lesson_data):
    """Test that admins can create lessons"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED


def test_update_finished_lesson_fails(client, teacher_headers, sample_lesson_data):
    """Test that finished lessons cannot be updated"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create lesson
    create_response = client.post(
        f"/api/courses/{course_id}/lessons",
        json=sample_lesson_data,
        headers=teacher_headers
    )
    lesson_id = create_response.json()["id"]
    
    # Mark as finished
    client.patch(
        f"/api/lessons/{lesson_id}",
        json={"status": "finished"},
        headers=teacher_headers
    )
    
    # Try to update
    response = client.patch(
        f"/api/lessons/{lesson_id}",
        json={"title": "Should fail"},
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

