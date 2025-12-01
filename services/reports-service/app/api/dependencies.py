"""
API dependencies
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.reports_repo import ReportsRepository
from app.services.reports_service import ReportsService
from app.core.security import get_current_user_id, get_current_user_role


# Database dependency
DbSession = Annotated[Session, Depends(get_db)]

# User authentication dependencies
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentUserRole = Annotated[str, Depends(get_current_user_role)]


def get_reports_repository(db: DbSession) -> ReportsRepository:
    """Get reports repository instance"""
    return ReportsRepository(db)


def get_reports_service(
    repo: Annotated[ReportsRepository, Depends(get_reports_repository)]
) -> ReportsService:
    """Get reports service instance"""
    return ReportsService(repo)


# Service dependency
ReportsServiceDep = Annotated[ReportsService, Depends(get_reports_service)]

