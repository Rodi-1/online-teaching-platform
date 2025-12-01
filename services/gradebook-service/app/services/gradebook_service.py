"""Gradebook service - business logic"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.db_models import GradeEntry, EntryType
from app.models.schemas import HomeworkGradeCreate, TestGradeCreate
from app.repositories.gradebook_repo import GradebookRepository


class GradebookService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = GradebookRepository(db)
    
    def calculate_grade(self, score: float, max_score: float) -> Tuple[float, int]:
        """Calculate percent and grade (5-point scale)"""
        if max_score <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="max_score must be positive")
        if score < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="score cannot be negative")
        if score > max_score:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="score cannot exceed max_score")
        
        percent = (score / max_score) * 100
        if percent >= 90:
            grade = 5
        elif percent >= 75:
            grade = 4
        elif percent >= 60:
            grade = 3
        else:
            grade = 2
        return percent, grade
    
    def create_homework_grade(self, data: HomeworkGradeCreate) -> GradeEntry:
        percent, grade = self.calculate_grade(data.score, data.max_score)
        return self.repo.create_homework_grade(data, percent, grade)
    
    def create_test_grade(self, data: TestGradeCreate) -> GradeEntry:
        percent, grade = self.calculate_grade(data.score, data.max_score)
        return self.repo.create_test_grade(data, percent, grade)
    
    def list_student_grades(
        self, student_id: UUID, course_id: Optional[UUID] = None,
        entry_type: Optional[EntryType] = None, from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None, offset: int = 0, count: int = 50
    ) -> Tuple[List[GradeEntry], int]:
        return self.repo.list_student_grades(student_id, course_id, entry_type, from_date, to_date, offset, count)
    
    def list_course_gradebook(
        self, course_id: UUID, student_id: Optional[UUID] = None,
        entry_type: Optional[EntryType] = None, from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[GradeEntry]:
        return self.repo.list_course_gradebook(course_id, student_id, entry_type, from_date, to_date)

