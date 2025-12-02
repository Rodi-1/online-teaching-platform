"""
Database ORM models for Schedule Service
"""
from datetime import datetime
from typing import Optional
import uuid
import enum

from sqlalchemy import DateTime, String, Text, Enum as SQLEnum, Index, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.guid import GUID


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class LocationType(str, enum.Enum):
    """Location type enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"


class LessonStatus(str, enum.Enum):
    """Lesson status enumeration"""
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    FINISHED = "finished"


class AttendanceStatus(str, enum.Enum):
    """Attendance status enumeration"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"


class Lesson(Base):
    """Lesson model representing the lessons table"""
    __tablename__ = "lessons"
    
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    location_type: Mapped[str] = mapped_column(
        SQLEnum(LocationType, name="location_type"),
        nullable=False,
        default=LocationType.ONLINE
    )
    room: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    online_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        SQLEnum(LessonStatus, name="lesson_status"),
        nullable=False,
        default=LessonStatus.SCHEDULED
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
    
    __table_args__ = (
        Index('idx_course_start', 'course_id', 'start_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Lesson(id={self.id}, title={self.title}, status={self.status})>"


class LessonAttendance(Base):
    """Lesson attendance model representing the lesson_attendance table"""
    __tablename__ = "lesson_attendance"
    
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(AttendanceStatus, name="attendance_status"),
        nullable=False,
        default=AttendanceStatus.PRESENT
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    marked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    __table_args__ = (
        Index('idx_lesson_student', 'lesson_id', 'student_id', unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<LessonAttendance(id={self.id}, lesson_id={self.lesson_id}, status={self.status})>"

