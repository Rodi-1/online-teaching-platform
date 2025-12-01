"""
Repository for reports and operations data access
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.db_models import ReportOperation, Report


class ReportsRepository:
    """Repository for managing reports and operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # Operation methods
    # ========================================================================
    
    def create_operation(
        self,
        type: str,
        format: str,
        filters_json: Optional[dict],
        requested_by: str
    ) -> ReportOperation:
        """
        Create a new report operation
        
        Args:
            type: Report type
            format: Report format
            filters_json: Filters as JSON
            requested_by: User ID who requested
            
        Returns:
            Created operation
        """
        operation = ReportOperation(
            type=type,
            format=format,
            filters_json=filters_json,
            requested_by=requested_by,
            status="pending",
            requested_at=datetime.utcnow()
        )
        self.db.add(operation)
        self.db.commit()
        self.db.refresh(operation)
        return operation
    
    def set_operation_started(self, operation_id: UUID) -> Optional[ReportOperation]:
        """
        Mark operation as started
        
        Args:
            operation_id: Operation UUID
            
        Returns:
            Updated operation or None
        """
        operation = self.get_operation(operation_id)
        if not operation:
            return None
        
        operation.status = "in_progress"
        operation.started_at = datetime.utcnow()
        operation.progress_percent = 0
        
        self.db.commit()
        self.db.refresh(operation)
        return operation
    
    def set_operation_progress(
        self,
        operation_id: UUID,
        progress_percent: int
    ) -> Optional[ReportOperation]:
        """
        Update operation progress
        
        Args:
            operation_id: Operation UUID
            progress_percent: Progress percentage (0-100)
            
        Returns:
            Updated operation or None
        """
        operation = self.get_operation(operation_id)
        if not operation:
            return None
        
        operation.progress_percent = max(0, min(100, progress_percent))
        
        self.db.commit()
        self.db.refresh(operation)
        return operation
    
    def set_operation_completed(
        self,
        operation_id: UUID,
        report_id: UUID
    ) -> Optional[ReportOperation]:
        """
        Mark operation as completed
        
        Args:
            operation_id: Operation UUID
            report_id: Generated report UUID
            
        Returns:
            Updated operation or None
        """
        operation = self.get_operation(operation_id)
        if not operation:
            return None
        
        operation.status = "completed"
        operation.finished_at = datetime.utcnow()
        operation.progress_percent = 100
        operation.report_id = report_id
        
        self.db.commit()
        self.db.refresh(operation)
        return operation
    
    def set_operation_failed(
        self,
        operation_id: UUID,
        error_message: str
    ) -> Optional[ReportOperation]:
        """
        Mark operation as failed
        
        Args:
            operation_id: Operation UUID
            error_message: Error description
            
        Returns:
            Updated operation or None
        """
        operation = self.get_operation(operation_id)
        if not operation:
            return None
        
        operation.status = "failed"
        operation.finished_at = datetime.utcnow()
        operation.error_message = error_message
        
        self.db.commit()
        self.db.refresh(operation)
        return operation
    
    def get_operation(self, operation_id: UUID) -> Optional[ReportOperation]:
        """
        Get operation by ID
        
        Args:
            operation_id: Operation UUID
            
        Returns:
            Operation or None
        """
        return self.db.query(ReportOperation).filter(
            ReportOperation.id == operation_id
        ).first()
    
    # ========================================================================
    # Report methods
    # ========================================================================
    
    def create_report(
        self,
        type: str,
        format: str,
        filters_json: Optional[dict],
        created_by: str,
        file_path: str,
        download_url: str,
        size_bytes: Optional[int] = None
    ) -> Report:
        """
        Create a new report
        
        Args:
            type: Report type
            format: Report format
            filters_json: Filters as JSON
            created_by: User ID who created
            file_path: Path to file
            download_url: Download URL
            size_bytes: File size
            
        Returns:
            Created report
        """
        report = Report(
            type=type,
            format=format,
            filters_json=filters_json,
            created_by=created_by,
            file_path=file_path,
            download_url=download_url,
            size_bytes=size_bytes,
            status="completed",
            created_at=datetime.utcnow(),
            ready_at=datetime.utcnow()
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def get_report(self, report_id: UUID) -> Optional[Report]:
        """
        Get report by ID
        
        Args:
            report_id: Report UUID
            
        Returns:
            Report or None
        """
        return self.db.query(Report).filter(Report.id == report_id).first()
    
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
    ) -> tuple[list[Report], int]:
        """
        List reports with filters
        
        Args:
            type: Filter by type
            format: Filter by format
            status: Filter by status (None means 'completed')
            created_by: Filter by creator
            from_date: Filter by created_at >= from_date
            to_date: Filter by created_at <= to_date
            offset: Pagination offset
            count: Number of items
            
        Returns:
            Tuple of (reports list, total count)
        """
        query = self.db.query(Report)
        
        # Apply filters
        if type:
            query = query.filter(Report.type == type)
        if format:
            query = query.filter(Report.format == format)
        if status:
            if status == "all":
                pass  # No filter
            else:
                query = query.filter(Report.status == status)
        else:
            # Default: only completed
            query = query.filter(Report.status == "completed")
        
        if created_by:
            query = query.filter(Report.created_by == created_by)
        if from_date:
            query = query.filter(Report.created_at >= from_date)
        if to_date:
            query = query.filter(Report.created_at <= to_date)
        
        # Get total
        total = query.count()
        
        # Get paginated results
        reports = query.order_by(Report.created_at.desc()).offset(offset).limit(count).all()
        
        return reports, total

