"""Gradebook API endpoints"""
from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, require_teacher, CurrentUser
from app.db.session import get_db
from app.models.schemas import *
from app.models.db_models import EntryType
from app.services.gradebook_service import GradebookService

router = APIRouter(tags=["Gradebook"])

@router.post("/gradebook/homework", response_model=GradeEntryOut, status_code=status.HTTP_201_CREATED)
def create_homework_grade(
    data: HomeworkGradeCreate,
    current_user: Annotated[CurrentUser, Depends(require_teacher)],
    db: Session = Depends(get_db)
):
    """Record homework grade"""
    service = GradebookService(db)
    entry = service.create_homework_grade(data)
    return GradeEntryOut.model_validate(entry)

@router.post("/gradebook/tests", response_model=GradeEntryOut, status_code=status.HTTP_201_CREATED)
def create_test_grade(
    data: TestGradeCreate,
    current_user: Annotated[CurrentUser, Depends(require_teacher)],
    db: Session = Depends(get_db)
):
    """Record test grade"""
    service = GradebookService(db)
    entry = service.create_test_grade(data)
    return GradeEntryOut.model_validate(entry)

@router.get("/students/{student_id}/grades", response_model=StudentGradesResponse)
def get_student_grades(
    student_id: Annotated[UUID, Path()],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    course_id: Optional[UUID] = Query(None),
    entry_type: Optional[EntryType] = Query(None, alias="type"),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    offset: int = Query(0, ge=0),
    count: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get student grades with filters"""
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only view own grades")
    service = GradebookService(db)
    entries, total = service.list_student_grades(student_id, course_id, entry_type, from_date, to_date, offset, count)
    return StudentGradesResponse(items=[GradeEntryOut.model_validate(e) for e in entries], total=total, offset=offset, count=count)

@router.get("/courses/{course_id}/gradebook", response_model=CourseGradebookResponse)
def get_course_gradebook(
    course_id: Annotated[UUID, Path()],
    current_user: Annotated[CurrentUser, Depends(require_teacher)],
    student_id: Optional[UUID] = Query(None),
    entry_type: Optional[EntryType] = Query(None, alias="type"),
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db)
):
    """Get course gradebook (teacher only)"""
    service = GradebookService(db)
    entries = service.list_course_gradebook(course_id, student_id, entry_type, from_date, to_date)
    items = [CourseGradebookItem(
        student_id=e.student_id, entry_id=e.id, type=e.type, work_title=e.title,
        work_id=e.homework_id or e.test_id, score=e.score, max_score=e.max_score,
        grade=e.grade, graded_at=e.graded_at
    ) for e in entries]
    return CourseGradebookResponse(course_id=course_id, items=items, total=len(items))

