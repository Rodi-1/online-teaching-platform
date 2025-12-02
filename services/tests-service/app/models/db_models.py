"""
Database ORM models for Tests Service
"""
from datetime import datetime
from typing import Optional
import uuid
import enum

from sqlalchemy import DateTime, String, Integer, Float, Text, Boolean, JSON, Enum as SQLEnum, Index, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.guid import GUID


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class TestStatus(str, enum.Enum):
    """Test status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class QuestionType(str, enum.Enum):
    """Question type enumeration"""
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    NUMBER = "number"


class AttemptStatus(str, enum.Enum):
    """Attempt status enumeration"""
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    EXPIRED = "expired"


class Test(Base):
    """Test model representing the tests table"""
    __tablename__ = "tests"
    
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
    lesson_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        SQLEnum(TestStatus, name="test_status"),
        nullable=False,
        default=TestStatus.DRAFT
    )
    available_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    available_to: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
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
        return f"<Test(id={self.id}, title={self.title}, status={self.status})>"


class TestQuestion(Base):
    """Test question model representing the test_questions table"""
    __tablename__ = "test_questions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    test_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    local_id: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(
        SQLEnum(QuestionType, name="question_type"),
        nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    correct_answers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    max_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    def __repr__(self) -> str:
        return f"<TestQuestion(id={self.id}, test_id={self.test_id}, local_id={self.local_id})>"


class TestAttempt(Base):
    """Test attempt model representing the test_attempts table"""
    __tablename__ = "test_attempts"
    
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    test_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        nullable=False,
        index=True
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(AttemptStatus, name="attempt_status"),
        nullable=False,
        default=AttemptStatus.IN_PROGRESS
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    grade: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Composite index for test_id and student_id
    __table_args__ = (
        Index('ix_test_attempts_test_id_student_id', 'test_id', 'student_id'),
    )
    
    def __repr__(self) -> str:
        return f"<TestAttempt(id={self.id}, test_id={self.test_id}, student_id={self.student_id}, status={self.status})>"


class TestAnswer(Base):
    """Test answer model representing the test_answers table"""
    __tablename__ = "test_answers"
    
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("test_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("test_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    def __repr__(self) -> str:
        return f"<TestAnswer(id={self.id}, attempt_id={self.attempt_id}, question_id={self.question_id})>"

