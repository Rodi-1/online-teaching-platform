"""Gradebook repository"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.db_models import GradeEntry, EntryType
from app.models.schemas import HomeworkGradeCreate, TestGradeCreate


class GradebookRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_homework_grade(self, data: HomeworkGradeCreate, percent: float, grade: int) -> GradeEntry:
        entry = GradeEntry(
            type=EntryType.HOMEWORK,
            student_id=data.student_id,
            course_id=data.course_id,
            lesson_id=data.lesson_id,
            homework_id=data.homework_id,
            title=data.title,
            score=data.score,
            max_score=data.max_score,
            percent=percent,
            grade=grade,
            graded_at=data.graded_at,
            comment=data.comment
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
    
    def create_test_grade(self, data: TestGradeCreate, percent: float, grade: int) -> GradeEntry:
        entry = GradeEntry(
            type=EntryType.TEST,
            student_id=data.student_id,
            course_id=data.course_id,
            test_id=data.test_id,
            attempt_id=data.attempt_id,
            title=data.title,
            score=data.score,
            max_score=data.max_score,
            percent=percent,
            grade=grade,
            graded_at=data.graded_at,
            comment=data.comment
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
    
    def list_student_grades(
        self, student_id: UUID, course_id: Optional[UUID] = None,
        entry_type: Optional[EntryType] = None, from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None, offset: int = 0, count: int = 50
    ) -> Tuple[List[GradeEntry], int]:
        query = self.db.query(GradeEntry).filter(GradeEntry.student_id == student_id)
        if course_id:
            query = query.filter(GradeEntry.course_id == course_id)
        if entry_type:
            query = query.filter(GradeEntry.type == entry_type)
        if from_date:
            query = query.filter(GradeEntry.graded_at >= from_date)
        if to_date:
            query = query.filter(GradeEntry.graded_at <= to_date)
        total = query.count()
        entries = query.order_by(GradeEntry.graded_at.desc()).offset(offset).limit(count).all()
        return entries, total
    
    def list_course_gradebook(
        self, course_id: UUID, student_id: Optional[UUID] = None,
        entry_type: Optional[EntryType] = None, from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[GradeEntry]:
        query = self.db.query(GradeEntry).filter(GradeEntry.course_id == course_id)
        if student_id:
            query = query.filter(GradeEntry.student_id == student_id)
        if entry_type:
            query = query.filter(GradeEntry.type == entry_type)
        if from_date:
            query = query.filter(GradeEntry.graded_at >= from_date)
        if to_date:
            query = query.filter(GradeEntry.graded_at <= to_date)
        return query.order_by(GradeEntry.graded_at.desc()).all()

