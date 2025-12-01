"""Database ORM models for Gradebook Service"""
from datetime import datetime
from typing import Optional
import uuid
import enum

from sqlalchemy import DateTime, String, Float, Integer, Text, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class EntryType(str, enum.Enum):
    """Grade entry type enumeration"""
    HOMEWORK = "homework"
    TEST = "test"


class GradeEntry(Base):
    """Grade entry model representing the gradebook_entries table"""
    __tablename__ = "gradebook_entries"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(SQLEnum(EntryType, name="entry_type"), nullable=False, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    lesson_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    homework_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    test_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    attempt_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    percent: Mapped[float] = mapped_column(Float, nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    graded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    __table_args__ = (
        Index('idx_course_student', 'course_id', 'student_id'),
    )
    
    def __repr__(self) -> str:
        return f"<GradeEntry(id={self.id}, type={self.type}, student_id={self.student_id}, score={self.score}/{self.max_score})>"

