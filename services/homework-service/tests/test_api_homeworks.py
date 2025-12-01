"""
Tests for homework endpoints
"""
import pytest
from fastapi import status


def test_create_homework_success(client, teacher_token, sample_homework_data):
    """Test successful homework creation"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    response = client.post(
        f"/api/courses/{course_id}/homeworks",
        json=sample_homework_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == sample_homework_data["title"]
    assert data["description"] == sample_homework_data["description"]
    assert data["max_score"] == sample_homework_data["max_score"]
    assert "id" in data
    assert data["status"] == "assigned"


def test_create_homework_forbidden_for_student(client, student_token, sample_homework_data):
    """Test that students cannot create homeworks"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    response = client.post(
        f"/api/courses/{course_id}/homeworks",
        json=sample_homework_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_homework_unauthorized(client, sample_homework_data):
    """Test that unauthorized users cannot create homeworks"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    response = client.post(
        f"/api/courses/{course_id}/homeworks",
        json=sample_homework_data
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Missing auth header


def test_list_course_homeworks(client, teacher_token, sample_homework_data):
    """Test listing homeworks for a course"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create a homework first
    client.post(
        f"/api/courses/{course_id}/homeworks",
        json=sample_homework_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    
    # List homeworks
    response = client.get(
        f"/api/courses/{course_id}/homeworks",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


def test_submit_homework_success(client, teacher_token, student_token, sample_homework_data, sample_submission_data):
    """Test successful homework submission"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create homework as teacher
    homework_response = client.post(
        f"/api/courses/{course_id}/homeworks",
        json=sample_homework_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    homework_id = homework_response.json()["id"]
    
    # Submit as student
    response = client.post(
        f"/api/homeworks/{homework_id}/submissions",
        json=sample_submission_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["answer_text"] == sample_submission_data["answer_text"]
    assert data["status"] == "submitted"
    assert "id" in data


def test_submit_homework_forbidden_for_teacher(client, teacher_token, sample_homework_data, sample_submission_data):
    """Test that teachers cannot submit homeworks"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create homework
    homework_response = client.post(
        f"/api/courses/{course_id}/homeworks",
        json=sample_homework_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    homework_id = homework_response.json()["id"]
    
    # Try to submit as teacher
    response = client.post(
        f"/api/homeworks/{homework_id}/submissions",
        json=sample_submission_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_grade_submission_success(client, teacher_token, student_token, sample_homework_data, sample_submission_data):
    """Test successful submission grading"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create homework
    homework_response = client.post(
        f"/api/courses/{course_id}/homeworks",
        json=sample_homework_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    homework_id = homework_response.json()["id"]
    
    # Submit as student
    submission_response = client.post(
        f"/api/homeworks/{homework_id}/submissions",
        json=sample_submission_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    submission_id = submission_response.json()["id"]
    
    # Grade as teacher
    grade_data = {
        "score": 9,
        "teacher_comment": "Good work!",
        "status": "checked"
    }
    
    response = client.post(
        f"/api/homeworks/{homework_id}/submissions/{submission_id}:grade",
        json=grade_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["score"] == 9
    assert data["teacher_comment"] == "Good work!"
    assert data["status"] == "checked"
    assert data["checked_at"] is not None


def test_grade_submission_forbidden_for_student(client, teacher_token, student_token, sample_homework_data, sample_submission_data):
    """Test that students cannot grade submissions"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create and submit homework
    homework_response = client.post(
        f"/api/courses/{course_id}/homeworks",
        json=sample_homework_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    homework_id = homework_response.json()["id"]
    
    submission_response = client.post(
        f"/api/homeworks/{homework_id}/submissions",
        json=sample_submission_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    submission_id = submission_response.json()["id"]
    
    # Try to grade as student
    grade_data = {
        "score": 10,
        "status": "checked"
    }
    
    response = client.post(
        f"/api/homeworks/{homework_id}/submissions/{submission_id}:grade",
        json=grade_data,
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_student_homeworks(client, teacher_token, student_token, sample_homework_data):
    """Test listing homeworks for a student"""
    course_id = "12345678-1234-5678-1234-567812345678"
    
    # Create homework as teacher
    client.post(
        f"/api/courses/{course_id}/homeworks",
        json=sample_homework_data,
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    
    # List student's homeworks
    response = client.get(
        "/api/students/me/homeworks",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data

