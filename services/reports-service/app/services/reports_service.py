"""
Business logic for reports service
"""
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.models.schemas import (
    ReportGenerateRequest, ReportOperationOut, ReportOut,
    ReportDownloadLink, ReportListItem
)
from app.repositories.reports_repo import ReportsRepository


settings = get_settings()


class ReportsService:
    """Service for reports business logic"""
    
    def __init__(self, repo: ReportsRepository):
        self.repo = repo
    
    # ========================================================================
    # Helper methods
    # ========================================================================
    
    def _check_teacher_or_admin(self, user_role: str) -> None:
        """
        Check if user is teacher, admin, or manager
        
        Args:
            user_role: User's role
            
        Raises:
            HTTPException: If user is not authorized
        """
        if user_role not in ["teacher", "admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers, admins and managers can perform this action"
            )
    
    def _generate_file_path(self, report_id: UUID, format: str) -> str:
        """
        Generate file path for report
        
        Args:
            report_id: Report UUID
            format: Report format
            
        Returns:
            File path
        """
        filename = f"rep-{str(report_id)[:8]}.{format}"
        return os.path.join(settings.REPORT_STORAGE_PATH, filename)
    
    def _build_download_url(self, file_path: str) -> str:
        """
        Build download URL from file path
        
        Args:
            file_path: File path
            
        Returns:
            Download URL
        """
        filename = os.path.basename(file_path)
        return settings.REPORT_STORAGE_BASE_URL.rstrip('/') + '/' + filename
    
    def _generate_report_file(
        self,
        type: str,
        format: str,
        filters: Optional[dict],
        file_path: str
    ) -> int:
        """
        Generate actual report file (stub implementation)
        
        In production, this would:
        1. Fetch data from other services (gradebook, schedule, etc.)
        2. Generate PDF/XLSX with library (reportlab, openpyxl, etc.)
        3. Save to file_path
        
        Args:
            type: Report type
            format: Report format
            filters: Report filters
            file_path: Path where to save file
            
        Returns:
            File size in bytes
        """
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Stub: create simple text file
        content = f"""Report Generated
Type: {type}
Format: {format}
Filters: {filters}
Generated at: {datetime.utcnow().isoformat()}

This is a stub implementation.
In production, this would contain actual report data.
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Return file size
        return os.path.getsize(file_path)
    
    # ========================================================================
    # Main service methods
    # ========================================================================
    
    def start_generation(
        self,
        request: ReportGenerateRequest,
        requested_by: str
    ) -> ReportOperationOut:
        """
        Start report generation operation
        
        Args:
            request: Generation request
            requested_by: User ID who requested
            
        Returns:
            Operation status
        """
        # Extract filters - use mode="json" to convert UUID to strings
        filters_dict = None
        if request.filters:
            filters_dict = request.filters.model_dump(
                mode="json",
                by_alias=True,
                exclude_none=True
            )
        
        # Create operation
        operation = self.repo.create_operation(
            type=request.type,
            format=request.format,
            filters_json=filters_dict,
            requested_by=requested_by
        )
        
        # Start generation (synchronous for simplicity)
        try:
            # Mark as started
            self.repo.set_operation_started(operation.id)
            
            # Generate file
            file_path = self._generate_file_path(uuid.uuid4(), request.format)
            size_bytes = self._generate_report_file(
                request.type,
                request.format,
                filters_dict,
                file_path
            )
            
            # Build download URL
            download_url = self._build_download_url(file_path)
            
            # Create report record
            report = self.repo.create_report(
                type=request.type,
                format=request.format,
                filters_json=filters_dict,
                created_by=requested_by,
                file_path=file_path,
                download_url=download_url,
                size_bytes=size_bytes
            )
            
            # Mark operation as completed
            self.repo.set_operation_completed(operation.id, report.id)
            
            # Get updated operation
            operation = self.repo.get_operation(operation.id)
            
        except Exception as e:
            # Mark as failed
            self.repo.set_operation_failed(operation.id, str(e))
            operation = self.repo.get_operation(operation.id)
        
        return ReportOperationOut.model_validate(operation)
    
    def get_operation_status(
        self,
        operation_id: UUID,
        user_id: str,
        user_role: str
    ) -> ReportOperationOut:
        """
        Get operation status
        
        Args:
            operation_id: Operation UUID
            user_id: Current user ID
            user_role: Current user role
            
        Returns:
            Operation status
            
        Raises:
            HTTPException: If operation not found or access denied
        """
        operation = self.repo.get_operation(operation_id)
        if not operation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operation not found"
            )
        
        # Check access (owner or admin)
        if operation.requested_by != user_id and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this operation"
            )
        
        return ReportOperationOut.model_validate(operation)
    
    def list_reports(
        self,
        type: Optional[str] = None,
        format: Optional[str] = None,
        status: Optional[str] = None,
        created_by: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        offset: int = 0,
        count: int = 20
    ) -> tuple[list[ReportListItem], int]:
        """
        List reports with filters
        
        Args:
            type: Filter by type
            format: Filter by format
            status: Filter by status
            created_by: Filter by creator
            from_date: Filter by date from
            to_date: Filter by date to
            offset: Pagination offset
            count: Number of items
            
        Returns:
            Tuple of (report items, total count)
        """
        reports, total = self.repo.list_reports(
            type=type,
            format=format,
            status=status,
            created_by=created_by,
            from_date=from_date,
            to_date=to_date,
            offset=offset,
            count=count
        )
        
        items = [ReportListItem.model_validate(r) for r in reports]
        return items, total
    
    def get_report(
        self,
        report_id: UUID,
        user_id: str,
        user_role: str
    ) -> ReportOut:
        """
        Get report details
        
        Args:
            report_id: Report UUID
            user_id: Current user ID
            user_role: Current user role
            
        Returns:
            Report details
            
        Raises:
            HTTPException: If report not found or access denied
        """
        report = self.repo.get_report(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Check access (creator or admin)
        if report.created_by != user_id and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this report"
            )
        
        return ReportOut.model_validate(report)
    
    def get_download_link(
        self,
        report_id: UUID,
        user_id: str,
        user_role: str
    ) -> ReportDownloadLink:
        """
        Get download link for report
        
        Args:
            report_id: Report UUID
            user_id: Current user ID
            user_role: Current user role
            
        Returns:
            Download link
            
        Raises:
            HTTPException: If report not found or access denied
        """
        report = self.repo.get_report(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Check access
        if report.created_by != user_id and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this report"
            )
        
        if not report.download_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report file not available"
            )
        
        # Create download link with expiration
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        return ReportDownloadLink(
            report_id=report_id,
            download_url=report.download_url,
            expires_at=expires_at
        )
    
    def regenerate_report(
        self,
        report_id: UUID,
        requested_by: str,
        user_role: str
    ) -> ReportOperationOut:
        """
        Regenerate an existing report
        
        Args:
            report_id: Report UUID to regenerate
            requested_by: User ID who requested
            user_role: User role
            
        Returns:
            New operation status
            
        Raises:
            HTTPException: If report not found or access denied
        """
        # Get original report
        report = self.repo.get_report(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Check access (creator or admin)
        if report.created_by != requested_by and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to regenerate this report"
            )
        
        # Create new generation request with same parameters
        request = ReportGenerateRequest(
            type=report.type,
            format=report.format,
            filters=report.filters_json
        )
        
        # Start new generation
        return self.start_generation(request, requested_by)

