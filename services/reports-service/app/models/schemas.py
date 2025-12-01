"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Report Generation Schemas
# ============================================================================

class ReportGenerateFilters(BaseModel):
    """Filters for report generation"""
    course_id: Optional[UUID] = Field(None, description="Course ID filter")
    student_id: Optional[UUID] = Field(None, description="Student ID filter")
    from_date: Optional[datetime] = Field(None, alias="from", description="Start date filter")
    to_date: Optional[datetime] = Field(None, alias="to", description="End date filter")
    
    class Config:
        populate_by_name = True


class ReportGenerateRequest(BaseModel):
    """Request schema for report generation"""
    type: str = Field(..., pattern="^(course_performance|student_progress|attendance)$", description="Report type")
    format: str = Field(..., pattern="^(pdf|xlsx)$", description="Report format")
    filters: Optional[ReportGenerateFilters] = Field(None, description="Report filters")


class ReportOperationOut(BaseModel):
    """Response schema for report operation status"""
    operation_id: UUID
    status: str
    type: str
    format: str
    requested_by: str
    requested_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    progress_percent: Optional[int] = None
    report_id: Optional[UUID] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Report Schemas
# ============================================================================

class ReportOut(BaseModel):
    """Response schema for report details"""
    id: UUID
    type: str
    format: str
    status: str
    created_by: str
    created_at: datetime
    ready_at: Optional[datetime] = None
    filters: Optional[dict] = None
    download_url: Optional[str] = None
    size_bytes: Optional[int] = None
    
    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    """Simplified report item for list view"""
    id: UUID
    type: str
    format: str
    status: str
    created_at: datetime
    ready_at: Optional[datetime] = None
    size_bytes: Optional[int] = None
    
    class Config:
        from_attributes = True


class ReportsListResponse(BaseModel):
    """Response schema for reports list"""
    items: list[ReportListItem]
    total: int
    offset: int
    count: int


class ReportDownloadLink(BaseModel):
    """Response schema for report download link"""
    report_id: UUID
    download_url: str
    expires_at: Optional[datetime] = None


# ============================================================================
# Common Schemas
# ============================================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str

