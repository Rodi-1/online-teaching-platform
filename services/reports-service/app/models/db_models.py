"""
Database ORM models for Reports Service
"""
from datetime import datetime
from typing import Optional
import uuid
import enum

from sqlalchemy import DateTime, String, Text, Integer, Enum as SQLEnum, Index, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class OperationStatus(str, enum.Enum):
    """Operation status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportStatus(str, enum.Enum):
    """Report status enumeration"""
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class ReportType(str, enum.Enum):
    """Report type enumeration"""
    COURSE_PERFORMANCE = "course_performance"
    STUDENT_PROGRESS = "student_progress"
    ATTENDANCE = "attendance"


class ReportFormat(str, enum.Enum):
    """Report format enumeration"""
    PDF = "pdf"
    XLSX = "xlsx"


class ReportOperation(Base):
    """ReportOperation model representing the report_operations table"""
    __tablename__ = "report_operations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(OperationStatus, name="operation_status"),
        nullable=False,
        default=OperationStatus.PENDING,
        index=True
    )
    type: Mapped[str] = mapped_column(
        SQLEnum(ReportType, name="report_type"),
        nullable=False
    )
    format: Mapped[str] = mapped_column(
        SQLEnum(ReportFormat, name="report_format"),
        nullable=False
    )
    requested_by: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    progress_percent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    report_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="SET NULL"),
        nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    filters_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        return f"<ReportOperation(id={self.id}, status={self.status}, type={self.type})>"


class Report(Base):
    """Report model representing the reports table"""
    __tablename__ = "reports"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    type: Mapped[str] = mapped_column(
        SQLEnum(ReportType, name="report_type"),
        nullable=False,
        index=True
    )
    format: Mapped[str] = mapped_column(
        SQLEnum(ReportFormat, name="report_format"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(ReportStatus, name="report_status"),
        nullable=False,
        default=ReportStatus.COMPLETED
    )
    created_by: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )
    ready_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    filters_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    download_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Report(id={self.id}, type={self.type}, status={self.status})>"

