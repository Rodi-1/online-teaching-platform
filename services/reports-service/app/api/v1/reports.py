"""
Reports API endpoints
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.dependencies import ReportsServiceDep, CurrentUserId, CurrentUserRole
from app.models.schemas import (
    ReportGenerateRequest, ReportOperationOut,
    ReportOut, ReportsListResponse, ReportListItem,
    ReportDownloadLink
)
from app.core.security import require_role


router = APIRouter()


# ============================================================================
# Report Generation Endpoints
# ============================================================================

@router.post(
    "/reports:generate",
    response_model=ReportOperationOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start report generation",
    description="Start a long-running report generation operation. Requires teacher, admin or manager role."
)
async def generate_report(
    request: ReportGenerateRequest,
    service: ReportsServiceDep,
    user_id: CurrentUserId,
    user_role: CurrentUserRole
) -> ReportOperationOut:
    """
    Start report generation operation
    
    Returns operation_id to track status.
    
    - **type**: Report type (course_performance, student_progress, attendance)
    - **format**: Report format (pdf, xlsx)
    - **filters**: Optional filters (course_id, student_id, from, to)
    """
    # Check permissions
    require_role(["teacher", "admin", "manager"], user_role)
    
    return service.start_generation(request, user_id)


@router.get(
    "/reports/operations/{operation_id}",
    response_model=ReportOperationOut,
    summary="Get operation status",
    description="Get status of report generation operation"
)
async def get_operation_status(
    operation_id: UUID,
    service: ReportsServiceDep,
    user_id: CurrentUserId,
    user_role: CurrentUserRole
) -> ReportOperationOut:
    """
    Get operation status
    
    Track the progress and status of report generation.
    
    - **operation_id**: UUID of the operation
    """
    return service.get_operation_status(operation_id, user_id, user_role)


# ============================================================================
# Reports Management Endpoints
# ============================================================================

@router.get(
    "/reports",
    response_model=ReportsListResponse,
    summary="List generated reports",
    description="Get list of generated reports with filters"
)
async def list_reports(
    service: ReportsServiceDep,
    user_role: CurrentUserRole,
    type: Optional[str] = Query(None, description="Filter by report type"),
    format: Optional[str] = Query(None, description="Filter by format"),
    status: Optional[str] = Query("completed", description="Filter by status (completed/failed/all)"),
    from_date: Optional[datetime] = Query(None, alias="from", description="Filter by created_at >= from"),
    to_date: Optional[datetime] = Query(None, alias="to", description="Filter by created_at <= to"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    count: int = Query(20, ge=1, le=100, description="Number of items to return")
) -> ReportsListResponse:
    """
    List generated reports
    
    Filter and paginate through available reports.
    
    - **type**: Optional filter by report type
    - **format**: Optional filter by format
    - **status**: Filter by status (default: completed)
    - **from**: Optional date filter (created_at >=)
    - **to**: Optional date filter (created_at <=)
    - **offset**: Pagination offset (default: 0)
    - **count**: Number of items (default: 20, max: 100)
    """
    # Check permissions
    require_role(["teacher", "admin", "manager"], user_role)
    
    items, total = service.list_reports(
        type=type,
        format=format,
        status=status,
        from_date=from_date,
        to_date=to_date,
        offset=offset,
        count=count
    )
    
    return ReportsListResponse(
        items=items,
        total=total,
        offset=offset,
        count=len(items)
    )


@router.get(
    "/reports/{report_id}",
    response_model=ReportOut,
    summary="Get report details",
    description="Get detailed information about a specific report"
)
async def get_report(
    report_id: UUID,
    service: ReportsServiceDep,
    user_id: CurrentUserId,
    user_role: CurrentUserRole
) -> ReportOut:
    """
    Get report details
    
    Retrieve full metadata for a specific report.
    
    - **report_id**: UUID of the report
    """
    return service.get_report(report_id, user_id, user_role)


@router.get(
    "/reports/{report_id}/download",
    response_model=ReportDownloadLink,
    summary="Get download link",
    description="Get download link for report file"
)
async def get_download_link(
    report_id: UUID,
    service: ReportsServiceDep,
    user_id: CurrentUserId,
    user_role: CurrentUserRole
) -> ReportDownloadLink:
    """
    Get download link for report
    
    Returns a URL to download the report file.
    
    - **report_id**: UUID of the report
    """
    return service.get_download_link(report_id, user_id, user_role)


@router.post(
    "/reports/{report_id}:regenerate",
    response_model=ReportOperationOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Regenerate report",
    description="Start regeneration of an existing report with same parameters"
)
async def regenerate_report(
    report_id: UUID,
    service: ReportsServiceDep,
    user_id: CurrentUserId,
    user_role: CurrentUserRole
) -> ReportOperationOut:
    """
    Regenerate an existing report
    
    Creates a new operation with the same parameters as the original report.
    
    - **report_id**: UUID of the report to regenerate
    """
    return service.regenerate_report(report_id, user_id, user_role)

