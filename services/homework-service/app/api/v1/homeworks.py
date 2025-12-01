"""
Homeworks API endpoints
"""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    require_teacher,
    require_student,
    CurrentUser
)
from app.db.session import get_db
from app.models.schemas import (
    HomeworkCreate,
    HomeworkOut,
    HomeworkListResponse,
    HomeworkListItem,
    SubmissionCreate,
    SubmissionOut,
    GradeSubmissionRequest,
    GradeSubmissionResponse,
    StudentHomeworkItem,
    StudentHomeworkListResponse,
    MessageResponse
)
from app.models.db_models import HomeworkStatus, SubmissionStatus
from app.services.homeworks_service import HomeworkService


router = APIRouter(tags=["Homeworks"])


@router.post(
    "/courses/{course_id}/homeworks",
    response_model=HomeworkOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create homework",
    description="Create a new homework for a course (teacher only)"
)
def create_homework(
    course_id: Annotated[UUID, Path(description="Course ID")],
    homework_data: HomeworkCreate,
    current_user: Annotated[CurrentUser, Depends(require_teacher)],
    db: Session = Depends(get_db)
):
    """
    Create a new homework assignment
    
    Only teachers can create homeworks
    """
    service = HomeworkService(db)
    homework = service.create_homework(course_id, homework_data)
    return HomeworkOut.model_validate(homework)


@router.get(
    "/courses/{course_id}/homeworks",
    response_model=HomeworkListResponse,
    status_code=status.HTTP_200_OK,
    summary="List homeworks for course",
    description="Get list of homeworks for a course (teacher only)"
)
def list_course_homeworks(
    course_id: Annotated[UUID, Path(description="Course ID")],
    current_user: Annotated[CurrentUser, Depends(require_teacher)],
    lesson_id: Optional[UUID] = Query(None, description="Filter by lesson ID"),
    hw_status: Optional[HomeworkStatus] = Query(None, alias="status", description="Filter by homework status"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    count: int = Query(20, ge=1, le=100, description="Number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List homeworks for a course with optional filters
    
    Only teachers can view course homeworks
    """
    service = HomeworkService(db)
    homeworks, total = service.list_homeworks_for_course(
        course_id, lesson_id, hw_status, offset, count
    )
    
    return HomeworkListResponse(
        items=[HomeworkListItem.model_validate(hw) for hw in homeworks],
        total=total,
        offset=offset,
        count=count
    )


@router.get(
    "/students/me/homeworks",
    response_model=StudentHomeworkListResponse,
    status_code=status.HTTP_200_OK,
    summary="List student's homeworks",
    description="Get list of homeworks for current student"
)
def list_student_homeworks(
    current_user: Annotated[CurrentUser, Depends(require_student)],
    hw_status: Optional[str] = Query(None, alias="status", description="Filter by status (active/submitted/checked)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    count: int = Query(20, ge=1, le=100, description="Number of items to return"),
    db: Session = Depends(get_db)
):
    """
    List homeworks for the current student with submission info
    
    Only students can view their own homeworks
    """
    service = HomeworkService(db)
    items, total = service.list_student_homeworks(
        current_user.id, hw_status, offset, count
    )
    
    # Convert dict items to Pydantic models
    homework_items = [StudentHomeworkItem(**item) for item in items]
    
    return StudentHomeworkListResponse(
        items=homework_items,
        total=total,
        offset=offset,
        count=count
    )


@router.post(
    "/homeworks/{homework_id}/submissions",
    response_model=SubmissionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Submit homework solution",
    description="Submit a solution for a homework (student only)"
)
def create_submission(
    homework_id: Annotated[UUID, Path(description="Homework ID")],
    submission_data: SubmissionCreate,
    current_user: Annotated[CurrentUser, Depends(require_student)],
    db: Session = Depends(get_db)
):
    """
    Submit a solution for a homework
    
    Only students can submit solutions
    If submission already exists, it will be updated
    """
    service = HomeworkService(db)
    submission = service.create_submission(
        homework_id, current_user.id, submission_data
    )
    return SubmissionOut.model_validate(submission)


@router.get(
    "/homeworks/{homework_id}/submissions/{submission_id}",
    response_model=SubmissionOut,
    status_code=status.HTTP_200_OK,
    summary="Get submission details",
    description="Get details of a homework submission"
)
def get_submission(
    homework_id: Annotated[UUID, Path(description="Homework ID")],
    submission_id: Annotated[UUID, Path(description="Submission ID")],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Get submission details
    
    Students can only view their own submissions
    Teachers can view all submissions
    """
    service = HomeworkService(db)
    submission = service.get_submission(
        submission_id, current_user.id, current_user.role
    )
    
    # Verify submission belongs to the homework
    if submission.homework_id != homework_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found for this homework"
        )
    
    return SubmissionOut.model_validate(submission)


@router.post(
    "/homeworks/{homework_id}/submissions/{submission_id}:grade",
    response_model=GradeSubmissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Grade submission",
    description="Grade a homework submission (teacher only)"
)
def grade_submission(
    homework_id: Annotated[UUID, Path(description="Homework ID")],
    submission_id: Annotated[UUID, Path(description="Submission ID")],
    grade_data: GradeSubmissionRequest,
    current_user: Annotated[CurrentUser, Depends(require_teacher)],
    db: Session = Depends(get_db)
):
    """
    Grade a homework submission
    
    Only teachers can grade submissions
    This will also notify the gradebook service (if available)
    """
    service = HomeworkService(db)
    
    # Verify submission belongs to the homework
    submission = service.repo.get_submission(submission_id)
    if not submission or submission.homework_id != homework_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found for this homework"
        )
    
    graded_submission = service.grade_submission(submission_id, grade_data)
    return GradeSubmissionResponse.model_validate(graded_submission)

