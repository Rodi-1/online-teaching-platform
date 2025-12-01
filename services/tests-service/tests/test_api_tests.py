"""
Test cases for tests API endpoints
"""
from uuid import UUID
import pytest
from fastapi import status


class TestTestsEndpoints:
    """Test cases for tests endpoints"""
    
    def test_create_test(self, client, mock_jwt_token, sample_course_id):
        """Test POST /api/courses/{course_id}/tests creates a test"""
        test_data = {
            "title": "Test по математике",
            "description": "Тест по основам алгебры",
            "time_limit_minutes": 30,
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "text": "Сколько будет 2+2?",
                    "options": ["3", "4", "5"],
                    "correct_answers": ["4"],
                    "max_score": 10
                },
                {
                    "id": "q2",
                    "type": "multiple_choice",
                    "text": "Выберите чётные числа",
                    "options": ["1", "2", "3", "4"],
                    "correct_answers": ["2", "4"],
                    "max_score": 10
                }
            ]
        }
        
        response = client.post(
            f"/api/courses/{sample_course_id}/tests",
            json=test_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == test_data["title"]
        assert data["max_score"] == 20  # Sum of question scores
        assert data["status"] == "draft"
    
    def test_publish_test(self, client, mock_jwt_token, sample_course_id):
        """Test POST /api/tests/{test_id}:publish publishes a test"""
        # First create a test
        test_data = {
            "title": "Test",
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "text": "Question 1",
                    "options": ["A", "B"],
                    "correct_answers": ["A"],
                    "max_score": 10
                }
            ]
        }
        
        create_response = client.post(
            f"/api/courses/{sample_course_id}/tests",
            json=test_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        test_id = create_response.json()["id"]
        
        # Publish the test
        publish_data = {
            "available_from": "2025-01-01T00:00:00Z",
            "available_to": "2025-12-31T23:59:59Z"
        }
        
        response = client.post(
            f"/api/tests/{test_id}:publish",
            json=publish_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "published"
        assert data["available_from"] is not None
    
    def test_start_attempt(self, client, mock_jwt_token, sample_course_id):
        """Test POST /api/tests/{test_id}/attempts:start starts an attempt"""
        # Create and publish a test
        test_data = {
            "title": "Test",
            "time_limit_minutes": 30,
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "text": "Question?",
                    "options": ["A", "B"],
                    "correct_answers": ["A"],
                    "max_score": 10
                }
            ]
        }
        
        create_response = client.post(
            f"/api/courses/{sample_course_id}/tests",
            json=test_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        test_id = create_response.json()["id"]
        
        client.post(
            f"/api/tests/{test_id}:publish",
            json={},
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Start attempt
        response = client.post(
            f"/api/tests/{test_id}/attempts:start",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["test_id"] == test_id
        assert data["status"] == "in_progress"
        assert len(data["questions"]) == 1
        # Correct answers should not be visible
        assert "correct_answers" not in str(data["questions"])
    
    def test_submit_attempt(self, client, mock_jwt_token, sample_course_id):
        """Test POST /api/tests/{test_id}/attempts/{attempt_id}/submit submits answers"""
        # Create and publish test
        test_data = {
            "title": "Test",
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "text": "2+2=?",
                    "options": ["3", "4", "5"],
                    "correct_answers": ["4"],
                    "max_score": 10
                }
            ]
        }
        
        create_response = client.post(
            f"/api/courses/{sample_course_id}/tests",
            json=test_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        test_id = create_response.json()["id"]
        
        client.post(
            f"/api/tests/{test_id}:publish",
            json={},
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Start attempt
        start_response = client.post(
            f"/api/tests/{test_id}/attempts:start",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        attempt_id = start_response.json()["attempt_id"]
        
        # Submit answers
        submit_data = {
            "answers": [
                {
                    "question_id": "q1",
                    "value": "4"
                }
            ]
        }
        
        response = client.post(
            f"/api/tests/{test_id}/attempts/{attempt_id}/submit",
            json=submit_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "finished"
        assert data["score"] == 10
        assert data["max_score"] == 10
        assert data["percent"] == 100
        assert data["grade"] == 5
        assert len(data["details"]) == 1
        assert data["details"][0]["is_correct"] == True
    
    def test_submit_attempt_wrong_answer(self, client, mock_jwt_token, sample_course_id):
        """Test submitting wrong answer returns 0 score"""
        # Create and publish test
        test_data = {
            "title": "Test",
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "text": "2+2=?",
                    "options": ["3", "4", "5"],
                    "correct_answers": ["4"],
                    "max_score": 10
                }
            ]
        }
        
        create_response = client.post(
            f"/api/courses/{sample_course_id}/tests",
            json=test_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        test_id = create_response.json()["id"]
        
        client.post(
            f"/api/tests/{test_id}:publish",
            json={},
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        start_response = client.post(
            f"/api/tests/{test_id}/attempts:start",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        attempt_id = start_response.json()["attempt_id"]
        
        # Submit wrong answer
        submit_data = {
            "answers": [
                {
                    "question_id": "q1",
                    "value": "3"  # Wrong answer
                }
            ]
        }
        
        response = client.post(
            f"/api/tests/{test_id}/attempts/{attempt_id}/submit",
            json=submit_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["score"] == 0
        assert data["percent"] == 0
        assert data["grade"] == 2
        assert data["details"][0]["is_correct"] == False
    
    def test_get_attempt_result(self, client, mock_jwt_token, sample_course_id):
        """Test GET /api/tests/{test_id}/attempts/{attempt_id} returns results"""
        # Create, publish, start, and complete test
        test_data = {
            "title": "Test",
            "questions": [
                {"id": "q1", "type": "single_choice", "text": "Q1", "options": ["A", "B"], "correct_answers": ["A"], "max_score": 10}
            ]
        }
        
        create_response = client.post(
            f"/api/courses/{sample_course_id}/tests",
            json=test_data,
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        test_id = create_response.json()["id"]
        
        client.post(f"/api/tests/{test_id}:publish", json={}, headers={"Authorization": f"Bearer {mock_jwt_token}"})
        start_response = client.post(f"/api/tests/{test_id}/attempts:start", headers={"Authorization": f"Bearer {mock_jwt_token}"})
        attempt_id = start_response.json()["attempt_id"]
        
        client.post(
            f"/api/tests/{test_id}/attempts/{attempt_id}/submit",
            json={"answers": [{"question_id": "q1", "value": "A"}]},
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        # Get result
        response = client.get(
            f"/api/tests/{test_id}/attempts/{attempt_id}",
            headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "finished"
        assert "details" in data


    def test_unauthorized_access(self, client):
        """Test access without token returns 401"""
        response = client.post("/api/courses/00000000-0000-0000-0000-000000000000/tests", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

