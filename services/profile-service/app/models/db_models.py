"""
Database ORM models for Profile Service
"""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import DateTime, String, Float, Integer, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.guid import GUID


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class UserProfile(Base):
    """User profile model representing the user_profiles table"""
    __tablename__ = "user_profiles"
    
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Profile information
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    about: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    social_links: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=list
    )
    
    # Aggregated statistics
    total_courses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_courses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active_courses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_grade: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    homeworks_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tests_passed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Service fields
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
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"


class Achievement(Base):
    """Achievement model representing the achievements table"""
    __tablename__ = "achievements"
    
    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        nullable=False,
        index=True
    )
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    def __repr__(self) -> str:
        return f"<Achievement(id={self.id}, user_id={self.user_id}, code={self.code})>"

