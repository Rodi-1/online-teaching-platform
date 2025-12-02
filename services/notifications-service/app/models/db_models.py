"""
Database ORM models for Notifications Service
"""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import DateTime, String, Boolean, Text, JSON, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.guid import GUID


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class Notification(Base):
    """Notification model representing the notifications table"""
    __tablename__ = "notifications"
    
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
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict
    )
    
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Optional fields for external notifications
    send_email: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    send_push: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Create compound index for user_id and is_read
    __table_args__ = (
        Index('ix_notifications_user_id_is_read', 'user_id', 'is_read'),
    )
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user_id={self.user_id}, type={self.type}, is_read={self.is_read})>"

