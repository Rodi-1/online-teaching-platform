"""
Schedule API endpoints
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.dependencies import ScheduleServiceDep, CurrentUserId, CurrentUserRole
from app.models.schemas import (
    LessonCreate, LessonUpdate, LessonOut,
    ScheduleResponse, CourseScheduleResponse,
    AttendanceSetRequest, AttendanceResponse, AttendanceSetResponse
)


router = APIRouter()


# ============================================================================
# Lesson Management Endpoints
# ============================================================================

@router.post(
    "/courses/{course_id}/lessons",
    response_model=LessonOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lesson",
    description="Create a new lesson for a course. Requires teacher or admin role."
)
async def create_lesson(
    course_id: UUID,
    data: LessonCreate,
    service: ScheduleServiceDep,
    user_role: CurrentUserRole
) -> LessonOut:
    """
    Create a new lesson for a course
    
    - **course_id**: UUID of the course
    - **data**: Lesson creation data
    """
    return service.create_lesson(course_id, data, user_role)


@router.patch(
    "/lessons/{lesson_id}",
    response_model=LessonOut,
    summary="Update a lesson",
    description="Update an existing lesson. Requires teacher or admin role."
)
async def update_lesson(
    lesson_id: UUID,
    data: LessonUpdate,
    service: ScheduleServiceDep,
    user_role: CurrentUserRole
) -> LessonOut:
    """
    Update an existing lesson
    
    - **lesson_id**: UUID of the lesson
    - **data**: Lesson update data (all fields optional)
    """
    return service.update_lesson(lesson_id, data, user_role)


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonOut,
    summary="Get a lesson",
    description="Get details of a specific lesson"
)
async def get_lesson(
    lesson_id: UUID,
    service: ScheduleServiceDep
) -> LessonOut:
    """
    Get lesson details
    
    - **lesson_id**: UUID of the lesson
    """
    return service.get_lesson(lesson_id)


# ============================================================================
# Schedule Endpoints
# ============================================================================

@router.get(
    "/schedule/me",
    response_model=ScheduleResponse,
    summary="Get current user's schedule",
    description="Get schedule for the currently authenticated user"
)
async def get_my_schedule(
    service: ScheduleServiceDep,
    user_id: CurrentUserId,
    user_role: CurrentUserRole,
    date_from: Optional[datetime] = Query(None, description="Start date filter (UTC)"),
    date_to: Optional[datetime] = Query(None, description="End date filter (UTC)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    count: int = Query(50, ge=1, le=100, description="Number of items to return")
) -> ScheduleResponse:
    """
    Get current user's schedule
    
    Returns lessons from all courses the user is enrolled in or teaching.
    
    - **date_from**: Optional start date filter
    - **date_to**: Optional end date filter
    - **offset**: Pagination offset (default: 0)
    - **count**: Number of items (default: 50, max: 100)
    """
    # TODO: Fetch course_ids from course service or enrollment service
    # For now, using empty list - would need to be integrated with other services
    course_ids = []  # Would call enrollment/course service here
    
    items, total = service.get_user_schedule(
        UUID(user_id),
        user_role,
        course_ids,
        date_from,
        date_to,
        offset,
        count
    )
    
    return ScheduleResponse(
        items=items,
        total=total,
        offset=offset,
        count=len(items)
    )


@router.get(
    "/courses/{course_id}/schedule",
    response_model=CourseScheduleResponse,
    summary="Get course schedule",
    description="Get all lessons for a specific course"
)
async def get_course_schedule(
    course_id: UUID,
    service: ScheduleServiceDep,
    date_from: Optional[datetime] = Query(None, description="Start date filter (UTC)"),
    date_to: Optional[datetime] = Query(None, description="End date filter (UTC)")
) -> CourseScheduleResponse:
    """
    Get schedule for a specific course
    
    - **course_id**: UUID of the course
    - **date_from**: Optional start date filter
    - **date_to**: Optional end date filter
    """
    lessons = service.get_course_schedule(course_id, date_from, date_to)
    
    return CourseScheduleResponse(
        course_id=course_id,
        course_title="Unknown Course",  # Would fetch from course service
        items=lessons
    )


# ============================================================================
# Attendance Endpoints
# ============================================================================

@router.post(
    "/lessons/{lesson_id}/attendance",
    response_model=AttendanceSetResponse,
    summary="Set attendance for a lesson",
    description="Mark attendance for students. Requires teacher or admin role."
)
async def set_attendance(
    lesson_id: UUID,
    data: AttendanceSetRequest,
    service: ScheduleServiceDep,
    user_role: CurrentUserRole
) -> AttendanceSetResponse:
    """
    Set attendance for a lesson
    
    Creates or updates attendance records for multiple students.
    
    - **lesson_id**: UUID of the lesson
    - **data**: Attendance data for students
    """
    items, updated_at = service.set_attendance(lesson_id, data.items, user_role)
    
    return AttendanceSetResponse(
        lesson_id=lesson_id,
        items=items,
        updated_at=updated_at
    )


@router.get(
    "/lessons/{lesson_id}/attendance",
    response_model=AttendanceResponse,
    summary="Get attendance for a lesson",
    description="Get attendance records for a lesson. Teachers see all, students see only their own."
)
async def get_attendance(
    lesson_id: UUID,
    service: ScheduleServiceDep,
    user_id: CurrentUserId,
    user_role: CurrentUserRole
) -> AttendanceResponse:
    """
    Get attendance for a lesson
    
    - Teachers and admins can see all attendance records
    - Students can only see their own attendance
    
    - **lesson_id**: UUID of the lesson
    """
    # Get lesson to include in response
    lesson = service.get_lesson(lesson_id)
    
    # Get attendance items
    items = service.get_attendance(lesson_id, UUID(user_id), user_role)
    
    return AttendanceResponse(
        lesson_id=lesson_id,
        course_id=lesson.course_id,
        lesson_title=lesson.title,
        items=items
    )

