"""
Homework repository for database operations
"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from app.models.db_models import (
    Homework,
    HomeworkSubmission,
    HomeworkStatus,
    SubmissionStatus
)
from app.models.schemas import HomeworkCreate, SubmissionCreate


class HomeworkRepository:
    """Repository for homework-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Homework CRUD operations
    
    def create_homework(
        self,
        course_id: UUID,
        data: HomeworkCreate
    ) -> Homework:
        """Create a new homework"""
        homework = Homework(
            course_id=course_id,
            title=data.title,
            description=data.description,
            lesson_id=data.lesson_id,
            due_at=data.due_at,
            max_score=data.max_score,
            attachments=data.attachments or [],
            status=HomeworkStatus.ASSIGNED  # По умолчанию сразу assigned
        )
        self.db.add(homework)
        self.db.commit()
        self.db.refresh(homework)
        return homework
    
    def get_homework(self, homework_id: UUID) -> Optional[Homework]:
        """Get homework by ID"""
        return self.db.query(Homework).filter(Homework.id == homework_id).first()
    
    def list_homeworks_for_course(
        self,
        course_id: UUID,
        lesson_id: Optional[UUID] = None,
        status: Optional[HomeworkStatus] = None,
        offset: int = 0,
        count: int = 20
    ) -> Tuple[List[Homework], int]:
        """
        List homeworks for a course with filters
        
        Returns:
            Tuple of (homeworks_list, total_count)
        """
        query = self.db.query(Homework).filter(Homework.course_id == course_id)
        
        # Apply filters
        if lesson_id:
            query = query.filter(Homework.lesson_id == lesson_id)
        if status:
            query = query.filter(Homework.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        homeworks = query.order_by(Homework.due_at.desc()).offset(offset).limit(count).all()
        
        return homeworks, total
    
    def update_homework(self, homework: Homework) -> Homework:
        """Update homework in database"""
        homework.updated_at = datetime.utcnow()
        self.db.add(homework)
        self.db.commit()
        self.db.refresh(homework)
        return homework
    
    # Submission CRUD operations
    
    def create_submission(
        self,
        homework_id: UUID,
        student_id: UUID,
        data: SubmissionCreate
    ) -> HomeworkSubmission:
        """Create a new submission"""
        submission = HomeworkSubmission(
            homework_id=homework_id,
            student_id=student_id,
            answer_text=data.answer_text,
            attachments=data.attachments or [],
            status=SubmissionStatus.SUBMITTED
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission
    
    def get_submission(self, submission_id: UUID) -> Optional[HomeworkSubmission]:
        """Get submission by ID"""
        return self.db.query(HomeworkSubmission).filter(
            HomeworkSubmission.id == submission_id
        ).first()
    
    def get_submission_by_homework_and_student(
        self,
        homework_id: UUID,
        student_id: UUID
    ) -> Optional[HomeworkSubmission]:
        """Get submission by homework and student"""
        return self.db.query(HomeworkSubmission).filter(
            and_(
                HomeworkSubmission.homework_id == homework_id,
                HomeworkSubmission.student_id == student_id
            )
        ).first()
    
    def list_student_homeworks(
        self,
        student_id: UUID,
        status: Optional[str] = None,
        offset: int = 0,
        count: int = 20
    ) -> Tuple[List[dict], int]:
        """
        List homeworks for a student with submission info
        
        Returns combined data from homeworks and submissions
        """
        # Build query joining homeworks with submissions
        query = self.db.query(
            Homework,
            HomeworkSubmission
        ).outerjoin(
            HomeworkSubmission,
            and_(
                HomeworkSubmission.homework_id == Homework.id,
                HomeworkSubmission.student_id == student_id
            )
        )
        
        # Apply status filter
        if status:
            if status == "active":
                # Active means no submission yet or needs_fix
                query = query.filter(
                    or_(
                        HomeworkSubmission.id == None,
                        HomeworkSubmission.status == SubmissionStatus.NEEDS_FIX
                    )
                )
            elif status == "submitted":
                query = query.filter(HomeworkSubmission.status == SubmissionStatus.SUBMITTED)
            elif status == "checked":
                query = query.filter(HomeworkSubmission.status == SubmissionStatus.CHECKED)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        results = query.order_by(Homework.due_at.desc()).offset(offset).limit(count).all()
        
        # Format results
        items = []
        for homework, submission in results:
            item = {
                "homework_id": homework.id,
                "course_id": homework.course_id,
                "title": homework.title,
                "due_at": homework.due_at,
                "max_score": homework.max_score,
                "status": homework.status,
                "submission_id": submission.id if submission else None,
                "submission_status": submission.status if submission else None,
                "score": submission.score if submission else None
            }
            items.append(item)
        
        return items, total
    
    def grade_submission(
        self,
        submission_id: UUID,
        score: float,
        status: SubmissionStatus,
        comment: Optional[str] = None
    ) -> HomeworkSubmission:
        """Grade a submission"""
        submission = self.get_submission(submission_id)
        if not submission:
            raise ValueError("Submission not found")
        
        submission.score = score
        submission.status = status
        submission.teacher_comment = comment
        submission.checked_at = datetime.utcnow()
        
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        
        return submission
    
    def list_submissions_for_homework(
        self,
        homework_id: UUID,
        offset: int = 0,
        count: int = 20
    ) -> Tuple[List[HomeworkSubmission], int]:
        """
        List all submissions for a homework
        """
        query = self.db.query(HomeworkSubmission).filter(
            HomeworkSubmission.homework_id == homework_id
        )
        
        total = query.count()
        submissions = query.order_by(HomeworkSubmission.created_at.desc()).offset(offset).limit(count).all()
        
        return submissions, total

