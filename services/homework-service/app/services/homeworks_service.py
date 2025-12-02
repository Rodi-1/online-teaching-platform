"""
Homework service - business logic layer
"""
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from uuid import UUID
import httpx

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.db_models import Homework, HomeworkSubmission, HomeworkStatus, SubmissionStatus
from app.models.schemas import HomeworkCreate, SubmissionCreate, GradeSubmissionRequest
from app.repositories.homeworks_repo import HomeworkRepository


class HomeworkService:
    """Service for homework-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = HomeworkRepository(db)
        self.settings = get_settings()
    
    def create_homework(
        self,
        course_id: UUID,
        data: HomeworkCreate
    ) -> Homework:
        """
        Create a new homework
        
        Args:
            course_id: Course ID
            data: Homework creation data
            
        Returns:
            Created homework
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate due_at is in the future
        # Make due_at timezone-aware if it isn't
        due_at = data.due_at
        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=timezone.utc)
        if due_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date must be in the future"
            )
        
        # Validate max_score
        if data.max_score <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Max score must be positive"
            )
        
        # Create homework
        homework = self.repo.create_homework(course_id, data)
        
        return homework
    
    def get_homework(self, homework_id: UUID) -> Homework:
        """
        Get homework by ID
        
        Args:
            homework_id: Homework ID
            
        Returns:
            Homework object
            
        Raises:
            HTTPException: If homework not found
        """
        homework = self.repo.get_homework(homework_id)
        if not homework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Homework not found"
            )
        return homework
    
    def list_homeworks_for_course(
        self,
        course_id: UUID,
        lesson_id: Optional[UUID] = None,
        status: Optional[HomeworkStatus] = None,
        offset: int = 0,
        count: int = 20
    ) -> Tuple[List[Homework], int]:
        """
        List homeworks for a course
        
        Args:
            course_id: Course ID
            lesson_id: Optional lesson filter
            status: Optional status filter
            offset: Pagination offset
            count: Number of items to return
            
        Returns:
            Tuple of (homeworks_list, total_count)
        """
        return self.repo.list_homeworks_for_course(
            course_id, lesson_id, status, offset, count
        )
    
    def create_submission(
        self,
        homework_id: UUID,
        student_id: UUID,
        data: SubmissionCreate
    ) -> HomeworkSubmission:
        """
        Create a submission for a homework
        
        Args:
            homework_id: Homework ID
            student_id: Student ID
            data: Submission data
            
        Returns:
            Created submission
            
        Raises:
            HTTPException: If validation fails
        """
        # Get homework
        homework = self.get_homework(homework_id)
        
        # Check if homework is closed
        if homework.status == HomeworkStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot submit to a closed homework"
            )
        
        # Check if submission already exists
        existing_submission = self.repo.get_submission_by_homework_and_student(
            homework_id, student_id
        )
        
        if existing_submission:
            # Update existing submission instead of creating new one
            existing_submission.answer_text = data.answer_text
            existing_submission.attachments = data.attachments or []
            existing_submission.status = SubmissionStatus.SUBMITTED
            existing_submission.score = None
            existing_submission.teacher_comment = None
            existing_submission.checked_at = None
            
            self.db.add(existing_submission)
            self.db.commit()
            self.db.refresh(existing_submission)
            
            return existing_submission
        
        # Create new submission
        submission = self.repo.create_submission(homework_id, student_id, data)
        
        return submission
    
    def get_submission(
        self,
        submission_id: UUID,
        user_id: UUID,
        user_role: str
    ) -> HomeworkSubmission:
        """
        Get submission by ID with access control
        
        Args:
            submission_id: Submission ID
            user_id: Current user ID
            user_role: Current user role
            
        Returns:
            Submission object
            
        Raises:
            HTTPException: If submission not found or access denied
        """
        submission = self.repo.get_submission(submission_id)
        
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Check access rights
        if user_role == "student" and submission.student_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own submissions"
            )
        
        return submission
    
    def list_student_homeworks(
        self,
        student_id: UUID,
        status: Optional[str] = None,
        offset: int = 0,
        count: int = 20
    ) -> Tuple[List[dict], int]:
        """
        List homeworks for a student
        
        Args:
            student_id: Student ID
            status: Optional status filter (active/submitted/checked)
            offset: Pagination offset
            count: Number of items to return
            
        Returns:
            Tuple of (homeworks_list, total_count)
        """
        return self.repo.list_student_homeworks(
            student_id, status, offset, count
        )
    
    def grade_submission(
        self,
        submission_id: UUID,
        data: GradeSubmissionRequest
    ) -> HomeworkSubmission:
        """
        Grade a submission
        
        Args:
            submission_id: Submission ID
            data: Grading data
            
        Returns:
            Updated submission
            
        Raises:
            HTTPException: If validation fails
        """
        # Get submission
        submission = self.repo.get_submission(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )
        
        # Get homework
        homework = self.repo.get_homework(submission.homework_id)
        if not homework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Homework not found"
            )
        
        # Validate score
        if data.score > homework.max_score:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Score cannot exceed max score ({homework.max_score})"
            )
        
        if data.score < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Score cannot be negative"
            )
        
        # Update submission
        updated_submission = self.repo.grade_submission(
            submission_id,
            data.score,
            data.status,
            data.teacher_comment
        )
        
        # Optionally: Call gradebook service to record the grade
        try:
            self._notify_gradebook(
                student_id=submission.student_id,
                course_id=homework.course_id,
                homework_id=homework.id,
                score=data.score,
                max_score=homework.max_score,
                graded_at=datetime.now(timezone.utc)
            )
        except Exception as e:
            # Log error but don't fail the grading
            print(f"Failed to notify gradebook service: {e}")
        
        return updated_submission
    
    def _notify_gradebook(
        self,
        student_id: UUID,
        course_id: UUID,
        homework_id: UUID,
        score: float,
        max_score: float,
        graded_at: datetime
    ):
        """
        Notify gradebook service about a new grade
        
        This is an optional integration - if gradebook service is not available,
        the grading still succeeds
        """
        gradebook_url = f"{self.settings.GRADEBOOK_SERVICE_URL}/api/gradebook/homework"
        
        payload = {
            "student_id": str(student_id),
            "course_id": str(course_id),
            "homework_id": str(homework_id),
            "score": score,
            "max_score": max_score,
            "graded_at": graded_at.isoformat()
        }
        
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(gradebook_url, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as e:
            print(f"HTTP error when notifying gradebook: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error when notifying gradebook: {e}")
            raise

