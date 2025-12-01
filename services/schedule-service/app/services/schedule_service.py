"""
Business logic for schedule service
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.models.schemas import (
    LessonCreate, LessonUpdate, LessonOut,
    ScheduleItemMe, AttendanceItemUpdate, AttendanceItemOut
)
from app.repositories.schedule_repo import ScheduleRepository


class ScheduleService:
    """Service for schedule business logic"""
    
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo
    
    # ========================================================================
    # Helper methods
    # ========================================================================
    
    def _check_teacher_or_admin(self, user_role: str) -> None:
        """
        Check if user is teacher or admin
        
        Args:
            user_role: User's role
            
        Raises:
            HTTPException: If user is not teacher or admin
        """
        if user_role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers and admins can perform this action"
            )
    
    def _validate_dates(self, start_at: datetime, end_at: datetime) -> None:
        """
        Validate that end_at is after start_at
        
        Args:
            start_at: Start datetime
            end_at: End datetime
            
        Raises:
            HTTPException: If dates are invalid
        """
        if end_at <= start_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_at must be after start_at"
            )
    
    # ========================================================================
    # Lesson methods
    # ========================================================================
    
    def create_lesson(
        self,
        course_id: UUID,
        data: LessonCreate,
        user_role: str
    ) -> LessonOut:
        """
        Create a new lesson
        
        Args:
            course_id: Course UUID
            data: Lesson creation data
            user_role: User's role
            
        Returns:
            Created lesson
            
        Raises:
            HTTPException: If user is not authorized or data is invalid
        """
        # Check permissions
        self._check_teacher_or_admin(user_role)
        
        # Validate dates
        self._validate_dates(data.start_at, data.end_at)
        
        # Create lesson
        lesson = self.repo.create_lesson(course_id, data)
        return LessonOut.model_validate(lesson)
    
    def update_lesson(
        self,
        lesson_id: UUID,
        data: LessonUpdate,
        user_role: str
    ) -> LessonOut:
        """
        Update a lesson
        
        Args:
            lesson_id: Lesson UUID
            data: Lesson update data
            user_role: User's role
            
        Returns:
            Updated lesson
            
        Raises:
            HTTPException: If lesson not found or user is not authorized
        """
        # Check permissions
        self._check_teacher_or_admin(user_role)
        
        # Get existing lesson
        lesson = self.repo.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Validate dates if both are being updated
        if data.start_at and data.end_at:
            self._validate_dates(data.start_at, data.end_at)
        elif data.start_at:
            self._validate_dates(data.start_at, lesson.end_at)
        elif data.end_at:
            self._validate_dates(lesson.start_at, data.end_at)
        
        # Don't allow updating finished lessons (optional business rule)
        if lesson.status == "finished":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update finished lesson"
            )
        
        # Update lesson
        updated_lesson = self.repo.update_lesson(lesson_id, data)
        return LessonOut.model_validate(updated_lesson)
    
    def get_lesson(self, lesson_id: UUID) -> LessonOut:
        """
        Get lesson by ID
        
        Args:
            lesson_id: Lesson UUID
            
        Returns:
            Lesson
            
        Raises:
            HTTPException: If lesson not found
        """
        lesson = self.repo.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        return LessonOut.model_validate(lesson)
    
    # ========================================================================
    # Schedule methods
    # ========================================================================
    
    def get_user_schedule(
        self,
        user_id: UUID,
        user_role: str,
        course_ids: list[UUID],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        offset: int = 0,
        count: int = 50
    ) -> tuple[list[ScheduleItemMe], int]:
        """
        Get schedule for user
        
        Args:
            user_id: User UUID
            user_role: User's role
            course_ids: List of course IDs user is enrolled in
            date_from: Start date filter
            date_to: End date filter
            offset: Pagination offset
            count: Number of items to return
            
        Returns:
            Tuple of (schedule items, total count)
        """
        if not course_ids:
            return [], 0
        
        lessons, total = self.repo.list_lessons_for_user(
            course_ids, date_from, date_to, offset, count
        )
        
        # Convert to ScheduleItemMe
        items = [
            ScheduleItemMe(
                lesson_id=lesson.id,
                course_id=lesson.course_id,
                course_title="Unknown Course",  # Would need to fetch from course service
                title=lesson.title,
                start_at=lesson.start_at,
                end_at=lesson.end_at,
                location_type=lesson.location_type,
                room=lesson.room,
                online_link=lesson.online_link,
                role=user_role,
                status=lesson.status
            )
            for lesson in lessons
        ]
        
        return items, total
    
    def get_course_schedule(
        self,
        course_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> list[LessonOut]:
        """
        Get schedule for a course
        
        Args:
            course_id: Course UUID
            date_from: Start date filter
            date_to: End date filter
            
        Returns:
            List of lessons
        """
        lessons = self.repo.list_lessons_for_course(course_id, date_from, date_to)
        return [LessonOut.model_validate(lesson) for lesson in lessons]
    
    # ========================================================================
    # Attendance methods
    # ========================================================================
    
    def set_attendance(
        self,
        lesson_id: UUID,
        items: list[AttendanceItemUpdate],
        user_role: str
    ) -> tuple[list[AttendanceItemOut], datetime]:
        """
        Set attendance for a lesson
        
        Args:
            lesson_id: Lesson UUID
            items: List of attendance items
            user_role: User's role
            
        Returns:
            Tuple of (attendance items, update timestamp)
            
        Raises:
            HTTPException: If lesson not found or user is not authorized
        """
        # Check permissions
        self._check_teacher_or_admin(user_role)
        
        # Verify lesson exists
        lesson = self.repo.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Set attendance
        now = datetime.utcnow()
        attendance_records = self.repo.set_attendance(lesson_id, items)
        
        # Convert to response schema
        result = [
            AttendanceItemOut(
                student_id=record.student_id,
                student_name="Unknown Student",  # Would need to fetch from user service
                status=record.status,
                comment=record.comment,
                marked_at=record.marked_at
            )
            for record in attendance_records
        ]
        
        return result, now
    
    def get_attendance(
        self,
        lesson_id: UUID,
        user_id: UUID,
        user_role: str
    ) -> list[AttendanceItemOut]:
        """
        Get attendance for a lesson
        
        Args:
            lesson_id: Lesson UUID
            user_id: Current user's UUID
            user_role: User's role
            
        Returns:
            List of attendance items
            
        Raises:
            HTTPException: If lesson not found
        """
        # Verify lesson exists
        lesson = self.repo.get_lesson(lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found"
            )
        
        # Get attendance
        if user_role in ["teacher", "admin"]:
            # Teachers and admins can see all attendance
            attendance_records = self.repo.get_attendance(lesson_id)
        else:
            # Students can only see their own attendance
            attendance_record = self.repo.get_student_attendance(lesson_id, user_id)
            attendance_records = [attendance_record] if attendance_record else []
        
        # Convert to response schema
        return [
            AttendanceItemOut(
                student_id=record.student_id,
                student_name="Unknown Student",  # Would need to fetch from user service
                status=record.status,
                comment=record.comment,
                marked_at=record.marked_at
            )
            for record in attendance_records
        ]

