"""
API dependencies
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.schedule_repo import ScheduleRepository
from app.services.schedule_service import ScheduleService
from app.core.security import get_current_user_id, get_current_user_role


# Database dependency
DbSession = Annotated[Session, Depends(get_db)]

# User authentication dependencies
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentUserRole = Annotated[str, Depends(get_current_user_role)]


def get_schedule_repository(db: DbSession) -> ScheduleRepository:
    """Get schedule repository instance"""
    return ScheduleRepository(db)


def get_schedule_service(
    repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)]
) -> ScheduleService:
    """Get schedule service instance"""
    return ScheduleService(repo)


# Service dependency
ScheduleServiceDep = Annotated[ScheduleService, Depends(get_schedule_service)]

