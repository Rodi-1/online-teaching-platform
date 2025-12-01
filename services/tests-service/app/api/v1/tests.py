"""
Tests API endpoints
"""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import get_current_user_id, get_tests_service
from app.models.schemas import (
    TestCreate, TestOut, TestPublishRequest, TestAttemptStartResponse,
    AttemptSubmitRequest, AttemptResult, AttemptsListResponse
)
from app.services.tests_service import TestsService


router = APIRouter()


@router.post(
    "/courses/{course_id}/tests",
    response_model=TestOut,
    status_code=status.HTTP_201_CREATED,
    tags=["tests"]
)
async def create_test(
    course_id: UUID,
    data: TestCreate,
    service: Annotated[TestsService, Depends(get_tests_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
) -> TestOut:
    """Create a new test (teachers only)"""
    # In production: check if user is a teacher for this course
    return service.create_test(course_id, data)


@router.post(
    "/tests/{test_id}:publish",
    response_model=TestOut,
    tags=["tests"]
)
async def publish_test(
    test_id: UUID,
    data: TestPublishRequest,
    service: Annotated[TestsService, Depends(get_tests_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
) -> TestOut:
    """Publish a test (teachers only)"""
    return service.publish_test(test_id, data)


@router.post(
    "/tests/{test_id}/attempts:start",
    response_model=TestAttemptStartResponse,
    tags=["attempts"]
)
async def start_attempt(
    test_id: UUID,
    service: Annotated[TestsService, Depends(get_tests_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
) -> TestAttemptStartResponse:
    """Start a new test attempt (students)"""
    return service.start_attempt(test_id, current_user_id)


@router.post(
    "/tests/{test_id}/attempts/{attempt_id}/submit",
    response_model=AttemptResult,
    tags=["attempts"]
)
async def submit_attempt(
    test_id: UUID,
    attempt_id: UUID,
    data: AttemptSubmitRequest,
    service: Annotated[TestsService, Depends(get_tests_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
) -> AttemptResult:
    """Submit attempt answers and get results"""
    return service.submit_attempt(test_id, attempt_id, data, current_user_id)


@router.get(
    "/tests/{test_id}/attempts/{attempt_id}",
    response_model=AttemptResult,
    tags=["attempts"]
)
async def get_attempt_result(
    test_id: UUID,
    attempt_id: UUID,
    service: Annotated[TestsService, Depends(get_tests_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)]
) -> AttemptResult:
    """Get attempt result"""
    return service.get_attempt_result(test_id, attempt_id, current_user_id)


@router.get(
    "/tests/{test_id}/attempts",
    response_model=AttemptsListResponse,
    tags=["attempts"]
)
async def list_attempts(
    test_id: UUID,
    service: Annotated[TestsService, Depends(get_tests_service)],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
    student_id: Optional[UUID] = Query(default=None, description="Filter by student"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    offset: int = Query(default=0, ge=0),
    count: int = Query(default=20, ge=1, le=100)
) -> AttemptsListResponse:
    """List attempts for a test"""
    # In production: if not teacher, filter to current user only
    filter_student_id = student_id if student_id else current_user_id
    return service.list_attempts(test_id, filter_student_id, status, offset, count)

