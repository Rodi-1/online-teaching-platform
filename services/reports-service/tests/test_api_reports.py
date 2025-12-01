"""
Tests for reports endpoints
"""
import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


def test_generate_report_success(client, teacher_headers, sample_report_request):
    """Test successful report generation"""
    response = client.post(
        "/api/reports:generate",
        json=sample_report_request,
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert "operation_id" in data
    assert data["status"] in ["pending", "completed"]
    assert data["type"] == sample_report_request["type"]
    assert data["format"] == sample_report_request["format"]


def test_generate_report_forbidden_for_student(client, student_headers, sample_report_request):
    """Test that students cannot generate reports"""
    response = client.post(
        "/api/reports:generate",
        json=sample_report_request,
        headers=student_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_generate_report_manager_allowed(client, manager_headers, sample_report_request):
    """Test that managers can generate reports"""
    response = client.post(
        "/api/reports:generate",
        json=sample_report_request,
        headers=manager_headers
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED


def test_get_operation_status(client, teacher_headers, sample_report_request):
    """Test getting operation status"""
    # Generate report
    gen_response = client.post(
        "/api/reports:generate",
        json=sample_report_request,
        headers=teacher_headers
    )
    operation_id = gen_response.json()["operation_id"]
    
    # Get operation status
    response = client.get(
        f"/api/reports/operations/{operation_id}",
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["operation_id"] == operation_id
    assert "status" in data


def test_get_operation_not_found(client, teacher_headers):
    """Test getting non-existent operation"""
    operation_id = "99999999-9999-9999-9999-999999999999"
    
    response = client.get(
        f"/api/reports/operations/{operation_id}",
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_reports(client, teacher_headers, sample_report_request):
    """Test listing reports"""
    # Generate a report
    client.post(
        "/api/reports:generate",
        json=sample_report_request,
        headers=teacher_headers
    )
    
    # List reports
    response = client.get(
        "/api/reports",
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "offset" in data
    assert "count" in data


def test_list_reports_with_filters(client, teacher_headers, sample_report_request):
    """Test listing reports with filters"""
    # Generate a report
    client.post(
        "/api/reports:generate",
        json=sample_report_request,
        headers=teacher_headers
    )
    
    # List with filters
    response = client.get(
        "/api/reports?type=course_performance&format=xlsx",
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data["items"], list)


def test_list_reports_forbidden_for_student(client, student_headers):
    """Test that students cannot list reports"""
    response = client.get(
        "/api/reports",
        headers=student_headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_report_details(client, teacher_headers, sample_report_request):
    """Test getting report details"""
    # Generate report
    gen_response = client.post(
        "/api/reports:generate",
        json=sample_report_request,
        headers=teacher_headers
    )
    
    # Get operation to find report_id
    operation_id = gen_response.json()["operation_id"]
    op_response = client.get(
        f"/api/reports/operations/{operation_id}",
        headers=teacher_headers
    )
    
    data = op_response.json()
    if data["status"] == "completed" and data["report_id"]:
        report_id = data["report_id"]
        
        # Get report details
        response = client.get(
            f"/api/reports/{report_id}",
            headers=teacher_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        report_data = response.json()
        assert report_data["id"] == report_id
        assert "type" in report_data
        assert "format" in report_data


def test_get_download_link(client, teacher_headers, sample_report_request):
    """Test getting download link"""
    # Generate report
    gen_response = client.post(
        "/api/reports:generate",
        json=sample_report_request,
        headers=teacher_headers
    )
    
    # Get operation to find report_id
    operation_id = gen_response.json()["operation_id"]
    op_response = client.get(
        f"/api/reports/operations/{operation_id}",
        headers=teacher_headers
    )
    
    data = op_response.json()
    if data["status"] == "completed" and data["report_id"]:
        report_id = data["report_id"]
        
        # Get download link
        response = client.get(
            f"/api/reports/{report_id}/download",
            headers=teacher_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        link_data = response.json()
        assert link_data["report_id"] == report_id
        assert "download_url" in link_data


def test_regenerate_report(client, teacher_headers, sample_report_request):
    """Test report regeneration"""
    # Generate report
    gen_response = client.post(
        "/api/reports:generate",
        json=sample_report_request,
        headers=teacher_headers
    )
    
    # Get operation to find report_id
    operation_id = gen_response.json()["operation_id"]
    op_response = client.get(
        f"/api/reports/operations/{operation_id}",
        headers=teacher_headers
    )
    
    data = op_response.json()
    if data["status"] == "completed" and data["report_id"]:
        report_id = data["report_id"]
        
        # Regenerate report
        response = client.post(
            f"/api/reports/{report_id}:regenerate",
            headers=teacher_headers
        )
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        regen_data = response.json()
        assert "operation_id" in regen_data
        assert regen_data["type"] == sample_report_request["type"]
        assert regen_data["format"] == sample_report_request["format"]


def test_regenerate_not_found(client, teacher_headers):
    """Test regenerating non-existent report"""
    report_id = "99999999-9999-9999-9999-999999999999"
    
    response = client.post(
        f"/api/reports/{report_id}:regenerate",
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_admin_can_generate_report(client, admin_headers, sample_report_request):
    """Test that admins can generate reports"""
    response = client.post(
        "/api/reports:generate",
        json=sample_report_request,
        headers=admin_headers
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED


def test_invalid_report_type(client, teacher_headers):
    """Test generation with invalid report type"""
    invalid_request = {
        "type": "invalid_type",
        "format": "xlsx"
    }
    
    response = client.post(
        "/api/reports:generate",
        json=invalid_request,
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_invalid_format(client, teacher_headers):
    """Test generation with invalid format"""
    invalid_request = {
        "type": "course_performance",
        "format": "invalid_format"
    }
    
    response = client.post(
        "/api/reports:generate",
        json=invalid_request,
        headers=teacher_headers
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

