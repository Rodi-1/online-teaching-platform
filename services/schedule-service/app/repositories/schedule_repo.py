"""
Repository for schedule and attendance data access
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.db_models import Lesson, LessonAttendance
from app.models.schemas import LessonCreate, LessonUpdate, AttendanceItemUpdate


class ScheduleRepository:
    """Repository for managing lessons and attendance"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # Lesson methods
    # ========================================================================
    
    def create_lesson(self, course_id: UUID, data: LessonCreate) -> Lesson:
        """
        Create a new lesson
        
        Args:
            course_id: Course UUID
            data: Lesson creation data
            
        Returns:
            Created lesson
        """
        lesson = Lesson(
            course_id=course_id,
            title=data.title,
            description=data.description,
            start_at=data.start_at,
            end_at=data.end_at,
            location_type=data.location_type,
            room=data.room,
            online_link=data.online_link,
            status="scheduled"
        )
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson
    
    def get_lesson(self, lesson_id: UUID) -> Optional[Lesson]:
        """
        Get lesson by ID
        
        Args:
            lesson_id: Lesson UUID
            
        Returns:
            Lesson or None if not found
        """
        return self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    def update_lesson(self, lesson_id: UUID, data: LessonUpdate) -> Optional[Lesson]:
        """
        Update lesson
        
        Args:
            lesson_id: Lesson UUID
            data: Lesson update data
            
        Returns:
            Updated lesson or None if not found
        """
        lesson = self.get_lesson(lesson_id)
        if not lesson:
            return None
        
        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lesson, field, value)
        
        self.db.commit()
        self.db.refresh(lesson)
        return lesson
    
    def list_lessons_for_course(
        self,
        course_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> list[Lesson]:
        """
        List all lessons for a course
        
        Args:
            course_id: Course UUID
            date_from: Start date filter (optional)
            date_to: End date filter (optional)
            
        Returns:
            List of lessons
        """
        query = self.db.query(Lesson).filter(Lesson.course_id == course_id)
        
        if date_from:
            query = query.filter(Lesson.start_at >= date_from)
        if date_to:
            query = query.filter(Lesson.start_at <= date_to)
        
        return query.order_by(Lesson.start_at).all()
    
    def list_lessons_for_user(
        self,
        course_ids: list[UUID],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        offset: int = 0,
        count: int = 50
    ) -> tuple[list[Lesson], int]:
        """
        List lessons for user's courses
        
        Args:
            course_ids: List of course UUIDs user is enrolled in
            date_from: Start date filter (optional)
            date_to: End date filter (optional)
            offset: Pagination offset
            count: Number of items to return
            
        Returns:
            Tuple of (lessons list, total count)
        """
        query = self.db.query(Lesson).filter(Lesson.course_id.in_(course_ids))
        
        if date_from:
            query = query.filter(Lesson.start_at >= date_from)
        if date_to:
            query = query.filter(Lesson.start_at <= date_to)
        
        total = query.count()
        lessons = query.order_by(Lesson.start_at).offset(offset).limit(count).all()
        
        return lessons, total
    
    # ========================================================================
    # Attendance methods
    # ========================================================================
    
    def set_attendance(
        self,
        lesson_id: UUID,
        items: list[AttendanceItemUpdate]
    ) -> list[LessonAttendance]:
        """
        Set attendance for multiple students
        Creates or updates attendance records
        
        Args:
            lesson_id: Lesson UUID
            items: List of attendance items
            
        Returns:
            List of created/updated attendance records
        """
        result = []
        now = datetime.utcnow()
        
        for item in items:
            # Try to find existing attendance record
            attendance = self.db.query(LessonAttendance).filter(
                and_(
                    LessonAttendance.lesson_id == lesson_id,
                    LessonAttendance.student_id == item.student_id
                )
            ).first()
            
            if attendance:
                # Update existing record
                attendance.status = item.status
                attendance.comment = item.comment
                attendance.marked_at = now
            else:
                # Create new record
                attendance = LessonAttendance(
                    lesson_id=lesson_id,
                    student_id=item.student_id,
                    status=item.status,
                    comment=item.comment,
                    marked_at=now
                )
                self.db.add(attendance)
            
            result.append(attendance)
        
        self.db.commit()
        
        # Refresh all records
        for attendance in result:
            self.db.refresh(attendance)
        
        return result
    
    def get_attendance(self, lesson_id: UUID) -> list[LessonAttendance]:
        """
        Get all attendance records for a lesson
        
        Args:
            lesson_id: Lesson UUID
            
        Returns:
            List of attendance records
        """
        return self.db.query(LessonAttendance).filter(
            LessonAttendance.lesson_id == lesson_id
        ).all()
    
    def get_student_attendance(
        self,
        lesson_id: UUID,
        student_id: UUID
    ) -> Optional[LessonAttendance]:
        """
        Get attendance record for a specific student and lesson
        
        Args:
            lesson_id: Lesson UUID
            student_id: Student UUID
            
        Returns:
            Attendance record or None
        """
        return self.db.query(LessonAttendance).filter(
            and_(
                LessonAttendance.lesson_id == lesson_id,
                LessonAttendance.student_id == student_id
            )
        ).first()

