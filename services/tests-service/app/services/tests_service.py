"""
Business logic for tests
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Union
from uuid import UUID

from fastapi import HTTPException, status

from app.models.schemas import (
    TestCreate, TestOut, TestPublishRequest, TestAttemptStartResponse,
    AttemptSubmitRequest, AttemptResult, TestQuestionOut, AnswerDetail,
    TestForStudentOut, TestsListResponse, AttemptsListResponse, AttemptBriefOut
)
from app.repositories.tests_repo import TestsRepository
from app.models.db_models import TestStatus, AttemptStatus


logger = logging.getLogger(__name__)


class TestsService:
    """Service for tests business logic"""
    
    def __init__(self, repo: TestsRepository):
        self.repo = repo
    
    def create_test(self, course_id: UUID, data: TestCreate) -> TestOut:
        """Create a new test"""
        test = self.repo.create_test(course_id, data)
        return TestOut.model_validate(test)
    
    def publish_test(self, test_id: UUID, data: TestPublishRequest) -> TestOut:
        """Publish a test"""
        test = self.repo.get_test(test_id)
        if not test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
        
        test = self.repo.publish_test(test_id, data.available_from, data.available_to)
        return TestOut.model_validate(test)
    
    def start_attempt(self, test_id: UUID, student_id: UUID) -> TestAttemptStartResponse:
        """Start a new attempt"""
        test = self.repo.get_test(test_id)
        if not test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
        
        # Check if test is published
        if test.status != TestStatus.PUBLISHED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Test is not published")
        
        # Check availability
        now = datetime.utcnow()
        if test.available_from and now < test.available_from:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Test is not yet available")
        
        if test.available_to and now > test.available_to:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Test is no longer available")
        
        # Create attempt
        attempt = self.repo.create_attempt(test_id, student_id)
        
        # Get questions without correct answers
        questions = self.repo.get_questions(test_id)
        questions_out = [
            TestQuestionOut(
                id=q.local_id,
                type=q.type,
                text=q.text,
                options=q.options,
                max_score=q.max_score
            )
            for q in questions
        ]
        
        expires_at = None
        if test.time_limit_minutes:
            expires_at = attempt.started_at + timedelta(minutes=test.time_limit_minutes)
        
        return TestAttemptStartResponse(
            attempt_id=attempt.id,
            test_id=test.id,
            student_id=student_id,
            started_at=attempt.started_at,
            expires_at=expires_at,
            status=attempt.status,
            questions=questions_out
        )
    
    def submit_attempt(
        self,
        test_id: UUID,
        attempt_id: UUID,
        data: AttemptSubmitRequest,
        current_user_id: UUID
    ) -> AttemptResult:
        """Submit and check answers"""
        attempt = self.repo.get_attempt(attempt_id)
        if not attempt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
        
        # Check ownership
        if attempt.student_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your attempt")
        
        # Check status
        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Attempt already finished")
        
        test = self.repo.get_test(test_id)
        questions = self.repo.get_questions(test_id)
        
        # Check answers and calculate score
        total_score = 0.0
        max_total_score = test.max_score
        details = []
        
        for answer_data in data.answers:
            question = self.repo.get_question_by_local_id(test_id, answer_data.question_id)
            if not question:
                continue
            
            is_correct, score = self._check_answer(question, answer_data.value)
            
            # Save answer
            self.repo.save_answer(
                attempt_id=attempt.id,
                question_id=question.id,
                value=answer_data.value,
                is_correct=is_correct,
                score=score
            )
            
            total_score += score if score else 0
            
            details.append(AnswerDetail(
                question_id=question.local_id,
                question_text=question.text,
                your_answer=answer_data.value,
                correct_answers=question.correct_answers,
                is_correct=is_correct,
                score=score,
                max_score=question.max_score
            ))
        
        # Calculate percent and grade
        percent = (total_score / max_total_score * 100) if max_total_score > 0 else 0
        grade = self._calculate_grade(percent)
        
        # Finish attempt
        self.repo.finish_attempt(attempt_id, total_score, max_total_score, percent, grade)
        
        return AttemptResult(
            attempt_id=attempt.id,
            test_id=test.id,
            student_id=attempt.student_id,
            status=AttemptStatus.FINISHED,
            started_at=attempt.started_at,
            finished_at=datetime.utcnow(),
            score=total_score,
            max_score=max_total_score,
            percent=percent,
            grade=grade,
            details=details
        )
    
    def _check_answer(self, question, value) -> tuple[Optional[bool], Optional[float]]:
        """Check if answer is correct"""
        if not question.correct_answers:
            return None, question.max_score
        
        is_correct = False
        
        if question.type == "single_choice":
            is_correct = str(value) in [str(ans) for ans in question.correct_answers]
        elif question.type == "multiple_choice":
            if isinstance(value, list):
                is_correct = set(str(v) for v in value) == set(str(ans) for ans in question.correct_answers)
        elif question.type in ["text", "number"]:
            is_correct = str(value).strip().lower() in [str(ans).strip().lower() for ans in question.correct_answers]
        
        score = question.max_score if is_correct else 0.0
        return is_correct, score
    
    def _calculate_grade(self, percent: float) -> int:
        """Calculate grade from percent"""
        if percent >= 90:
            return 5
        elif percent >= 75:
            return 4
        elif percent >= 60:
            return 3
        elif percent >= 50:
            return 2
        else:
            return 2
    
    def get_attempt_result(
        self,
        test_id: UUID,
        attempt_id: UUID,
        current_user_id: UUID
    ) -> AttemptResult:
        """Get attempt result"""
        attempt = self.repo.get_attempt(attempt_id)
        if not attempt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
        
        # Check ownership
        if attempt.student_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your attempt")
        
        # Get answers and questions
        answers = self.repo.get_answers(attempt.id)
        questions = {q.id: q for q in self.repo.get_questions(test_id)}
        
        details = []
        for answer in answers:
            question = questions.get(answer.question_id)
            if question:
                details.append(AnswerDetail(
                    question_id=question.local_id,
                    question_text=question.text,
                    your_answer=answer.value,
                    correct_answers=question.correct_answers,
                    is_correct=answer.is_correct,
                    score=answer.score,
                    max_score=question.max_score
                ))
        
        return AttemptResult(
            attempt_id=attempt.id,
            test_id=test_id,
            student_id=attempt.student_id,
            status=attempt.status,
            started_at=attempt.started_at,
            finished_at=attempt.finished_at,
            score=attempt.score,
            max_score=attempt.max_score,
            percent=attempt.percent,
            grade=attempt.grade,
            details=details
        )
    
    def list_attempts(
        self,
        test_id: UUID,
        student_id: Optional[UUID] = None,
        status: Optional[str] = None,
        offset: int = 0,
        count: int = 20
    ) -> AttemptsListResponse:
        """List attempts"""
        attempts, total = self.repo.list_attempts(test_id, student_id, status, offset, count)
        
        items = [AttemptBriefOut.model_validate(attempt) for attempt in attempts]
        
        return AttemptsListResponse(
            items=items,
            total=total,
            offset=offset,
            count=count
        )

