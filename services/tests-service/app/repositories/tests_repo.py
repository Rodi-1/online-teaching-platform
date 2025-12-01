"""
Repository for tests data access
"""
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.db_models import Test, TestQuestion, TestAttempt, TestAnswer, TestStatus, AttemptStatus
from app.models.schemas import TestCreate, TestQuestionCreate, AnswerSubmit


class TestsRepository:
    """Repository for tests, questions, attempts, and answers"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============= Test Methods =============
    
    def create_test(self, course_id: UUID, data: TestCreate) -> Test:
        """Create a new test with questions"""
        # Calculate max_score from questions
        max_score = sum(q.max_score for q in data.questions)
        
        test = Test(
            course_id=course_id,
            lesson_id=data.lesson_id,
            title=data.title,
            description=data.description,
            time_limit_minutes=data.time_limit_minutes,
            max_score=max_score,
            status=TestStatus.DRAFT
        )
        self.db.add(test)
        self.db.flush()
        
        # Create questions
        for index, question_data in enumerate(data.questions):
            question = TestQuestion(
                test_id=test.id,
                local_id=question_data.id,
                type=question_data.type,
                text=question_data.text,
                options=question_data.options,
                correct_answers=question_data.correct_answers,
                max_score=question_data.max_score,
                order_index=index
            )
            self.db.add(question)
        
        self.db.commit()
        self.db.refresh(test)
        return test
    
    def get_test(self, test_id: UUID) -> Optional[Test]:
        """Get test by ID"""
        return self.db.query(Test).filter(Test.id == test_id).first()
    
    def publish_test(
        self,
        test_id: UUID,
        available_from: Optional[datetime] = None,
        available_to: Optional[datetime] = None
    ) -> Optional[Test]:
        """Publish a test"""
        test = self.get_test(test_id)
        if test:
            test.status = TestStatus.PUBLISHED
            test.available_from = available_from
            test.available_to = available_to
            self.db.commit()
            self.db.refresh(test)
        return test
    
    def get_questions(self, test_id: UUID) -> List[TestQuestion]:
        """Get all questions for a test"""
        return self.db.query(TestQuestion).filter(
            TestQuestion.test_id == test_id
        ).order_by(TestQuestion.order_index).all()
    
    def get_question_by_local_id(self, test_id: UUID, local_id: str) -> Optional[TestQuestion]:
        """Get question by test_id and local_id"""
        return self.db.query(TestQuestion).filter(
            and_(
                TestQuestion.test_id == test_id,
                TestQuestion.local_id == local_id
            )
        ).first()
    
    # ============= Attempt Methods =============
    
    def create_attempt(self, test_id: UUID, student_id: UUID) -> TestAttempt:
        """Create a new test attempt"""
        attempt = TestAttempt(
            test_id=test_id,
            student_id=student_id,
            status=AttemptStatus.IN_PROGRESS
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt
    
    def get_attempt(self, attempt_id: UUID) -> Optional[TestAttempt]:
        """Get attempt by ID"""
        return self.db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()
    
    def count_attempts(self, test_id: UUID, student_id: UUID) -> int:
        """Count attempts for a test by a student"""
        return self.db.query(TestAttempt).filter(
            and_(
                TestAttempt.test_id == test_id,
                TestAttempt.student_id == student_id
            )
        ).count()
    
    def get_last_attempt(self, test_id: UUID, student_id: UUID) -> Optional[TestAttempt]:
        """Get last attempt for a test by a student"""
        return self.db.query(TestAttempt).filter(
            and_(
                TestAttempt.test_id == test_id,
                TestAttempt.student_id == student_id
            )
        ).order_by(TestAttempt.started_at.desc()).first()
    
    def finish_attempt(
        self,
        attempt_id: UUID,
        score: float,
        max_score: float,
        percent: float,
        grade: Optional[int] = None
    ) -> Optional[TestAttempt]:
        """Finish an attempt with results"""
        attempt = self.get_attempt(attempt_id)
        if attempt:
            attempt.status = AttemptStatus.FINISHED
            attempt.finished_at = datetime.utcnow()
            attempt.score = score
            attempt.max_score = max_score
            attempt.percent = percent
            attempt.grade = grade
            self.db.commit()
            self.db.refresh(attempt)
        return attempt
    
    def list_attempts(
        self,
        test_id: Optional[UUID] = None,
        student_id: Optional[UUID] = None,
        status: Optional[str] = None,
        offset: int = 0,
        count: int = 20
    ) -> Tuple[List[TestAttempt], int]:
        """List attempts with filters"""
        query = self.db.query(TestAttempt)
        
        if test_id:
            query = query.filter(TestAttempt.test_id == test_id)
        
        if student_id:
            query = query.filter(TestAttempt.student_id == student_id)
        
        if status:
            query = query.filter(TestAttempt.status == status)
        
        total = query.count()
        attempts = query.order_by(
            TestAttempt.started_at.desc()
        ).offset(offset).limit(count).all()
        
        return attempts, total
    
    # ============= Answer Methods =============
    
    def save_answer(
        self,
        attempt_id: UUID,
        question_id: UUID,
        value: Any,
        is_correct: Optional[bool] = None,
        score: Optional[float] = None
    ) -> TestAnswer:
        """Save or update an answer"""
        # Check if answer already exists
        answer = self.db.query(TestAnswer).filter(
            and_(
                TestAnswer.attempt_id == attempt_id,
                TestAnswer.question_id == question_id
            )
        ).first()
        
        if answer:
            answer.value = value
            answer.is_correct = is_correct
            answer.score = score
        else:
            answer = TestAnswer(
                attempt_id=attempt_id,
                question_id=question_id,
                value=value,
                is_correct=is_correct,
                score=score
            )
            self.db.add(answer)
        
        self.db.commit()
        self.db.refresh(answer)
        return answer
    
    def get_answers(self, attempt_id: UUID) -> List[TestAnswer]:
        """Get all answers for an attempt"""
        return self.db.query(TestAnswer).filter(
            TestAnswer.attempt_id == attempt_id
        ).all()

