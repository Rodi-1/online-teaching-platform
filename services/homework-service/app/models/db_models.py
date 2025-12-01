"""
Database ORM models for Homework Service
"""
from datetime import datetime
from typing import Optional
import uuid
import enum

from sqlalchemy import Boolean, DateTime, String, Float, Integer, Text, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class HomeworkStatus(str, enum.Enum):
    """Homework status enumeration"""
    DRAFT = "draft"
    ASSIGNED = "assigned"
    CLOSED = "closed"


class SubmissionStatus(str, enum.Enum):
    """Submission status enumeration"""
    SUBMITTED = "submitted"
    CHECKED = "checked"
    NEEDS_FIX = "needs_fix"


class Homework(Base):
    """Homework model representing the homeworks table"""
    __tablename__ = "homeworks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    lesson_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    due_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(HomeworkStatus, name="homework_status"),
        nullable=False,
        default=HomeworkStatus.DRAFT
    )
    attachments: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<Homework(id={self.id}, title={self.title}, status={self.status})>"


class HomeworkSubmission(Base):
    """Homework submission model representing the homework_submissions table"""
    __tablename__ = "homework_submissions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    homework_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attachments: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=list
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(SubmissionStatus, name="submission_status"),
        nullable=False,
        default=SubmissionStatus.SUBMITTED
    )
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    teacher_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    checked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    def __repr__(self) -> str:
        return f"<HomeworkSubmission(id={self.id}, homework_id={self.homework_id}, status={self.status})>"

