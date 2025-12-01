"""Tests for gradebook endpoints"""
from datetime import datetime, timedelta

def test_create_homework_grade(client, teacher_token):
    data = {
        "student_id": "87654321-4321-8765-4321-876543218765",
        "course_id": "11111111-1111-1111-1111-111111111111",
        "homework_id": "22222222-2222-2222-2222-222222222222",
        "score": 9, "max_score": 10,
        "graded_at": datetime.utcnow().isoformat() + "Z",
        "title": "ДЗ по теме Функции"
    }
    response = client.post("/api/gradebook/homework", json=data, headers={"Authorization": f"Bearer {teacher_token}"})
    assert response.status_code == 201
    result = response.json()
    assert result["score"] == 9
    assert result["percent"] == 90.0
    assert result["grade"] == 5

def test_create_test_grade(client, teacher_token):
    data = {
        "student_id": "87654321-4321-8765-4321-876543218765",
        "course_id": "11111111-1111-1111-1111-111111111111",
        "test_id": "33333333-3333-3333-3333-333333333333",
        "score": 18, "max_score": 20,
        "graded_at": datetime.utcnow().isoformat() + "Z",
        "title": "Тест по теме Функции"
    }
    response = client.post("/api/gradebook/tests", json=data, headers={"Authorization": f"Bearer {teacher_token}"})
    assert response.status_code == 201
    result = response.json()
    assert result["grade"] == 5

def test_get_student_grades(client, teacher_token):
    # Create grade first
    data = {
        "student_id": "87654321-4321-8765-4321-876543218765",
        "course_id": "11111111-1111-1111-1111-111111111111",
        "homework_id": "22222222-2222-2222-2222-222222222222",
        "score": 9, "max_score": 10,
        "graded_at": datetime.utcnow().isoformat() + "Z",
        "title": "ДЗ"
    }
    client.post("/api/gradebook/homework", json=data, headers={"Authorization": f"Bearer {teacher_token}"})
    
    response = client.get("/api/students/87654321-4321-8765-4321-876543218765/grades",
                         headers={"Authorization": f"Bearer {teacher_token}"})
    assert response.status_code == 200
    result = response.json()
    assert result["total"] >= 1
    assert len(result["items"]) >= 1

