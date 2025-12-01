"""
Repository for profile and achievement data access
"""
from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.db_models import UserProfile, Achievement
from app.models.schemas import AchievementCreateRequest, UpdateStatsRequest


class ProfileRepository:
    """Repository for user profiles and achievements"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============= Profile Methods =============
    
    def get_profile_by_user_id(self, user_id: UUID) -> Optional[UserProfile]:
        """
        Get user profile by user_id
        
        Args:
            user_id: User UUID
            
        Returns:
            UserProfile or None if not found
        """
        return self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
    
    def create_profile(self, user_id: UUID) -> UserProfile:
        """
        Create a new user profile
        
        Args:
            user_id: User UUID
            
        Returns:
            Created UserProfile
        """
        profile = UserProfile(
            user_id=user_id,
            total_courses=0,
            completed_courses=0,
            active_courses=0,
            homeworks_completed=0,
            tests_passed=0
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def get_or_create_profile(self, user_id: UUID) -> UserProfile:
        """
        Get existing profile or create new one
        
        Args:
            user_id: User UUID
            
        Returns:
            UserProfile
        """
        profile = self.get_profile_by_user_id(user_id)
        if not profile:
            profile = self.create_profile(user_id)
        return profile
    
    def update_profile(
        self,
        user_id: UUID,
        avatar_url: Optional[str] = None,
        about: Optional[str] = None,
        social_links: Optional[List[str]] = None
    ) -> Optional[UserProfile]:
        """
        Update user profile fields
        
        Args:
            user_id: User UUID
            avatar_url: New avatar URL (optional)
            about: New about text (optional)
            social_links: New social links list (optional)
            
        Returns:
            Updated UserProfile or None if not found
        """
        profile = self.get_or_create_profile(user_id)
        
        if avatar_url is not None:
            profile.avatar_url = avatar_url
        if about is not None:
            profile.about = about
        if social_links is not None:
            profile.social_links = social_links
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def update_stats(
        self,
        user_id: UUID,
        stats: UpdateStatsRequest
    ) -> UserProfile:
        """
        Update user statistics
        
        Args:
            user_id: User UUID
            stats: Statistics update request
            
        Returns:
            Updated UserProfile
        """
        profile = self.get_or_create_profile(user_id)
        
        # Apply deltas
        if stats.homeworks_completed_delta is not None:
            profile.homeworks_completed += stats.homeworks_completed_delta
        
        if stats.tests_passed_delta is not None:
            profile.tests_passed += stats.tests_passed_delta
        
        if stats.total_courses_delta is not None:
            profile.total_courses += stats.total_courses_delta
        
        if stats.completed_courses_delta is not None:
            profile.completed_courses += stats.completed_courses_delta
        
        if stats.active_courses_delta is not None:
            profile.active_courses += stats.active_courses_delta
        
        # Replace average_grade if provided
        if stats.average_grade is not None:
            profile.average_grade = stats.average_grade
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    # ============= Achievement Methods =============
    
    def list_achievements(
        self,
        user_id: UUID,
        code: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        offset: int = 0,
        count: int = 50
    ) -> Tuple[List[Achievement], int]:
        """
        List user achievements with filters and pagination
        
        Args:
            user_id: User UUID
            code: Filter by achievement code (optional)
            date_from: Filter by received_at >= date_from (optional)
            date_to: Filter by received_at <= date_to (optional)
            offset: Number of records to skip
            count: Maximum number of records to return
            
        Returns:
            Tuple of (achievements list, total count)
        """
        query = self.db.query(Achievement).filter(Achievement.user_id == user_id)
        
        # Apply filters
        if code:
            query = query.filter(Achievement.code == code)
        
        if date_from:
            query = query.filter(Achievement.received_at >= date_from)
        
        if date_to:
            query = query.filter(Achievement.received_at <= date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and order
        achievements = query.order_by(
            Achievement.received_at.desc()
        ).offset(offset).limit(count).all()
        
        return achievements, total
    
    def create_achievement(
        self,
        user_id: UUID,
        data: AchievementCreateRequest
    ) -> Achievement:
        """
        Create a new achievement for user
        
        Args:
            user_id: User UUID
            data: Achievement creation data
            
        Returns:
            Created Achievement
        """
        achievement = Achievement(
            user_id=user_id,
            code=data.code,
            title=data.title,
            description=data.description,
            icon_url=data.icon_url,
            received_at=data.received_at
        )
        self.db.add(achievement)
        self.db.commit()
        self.db.refresh(achievement)
        return achievement
    
    def achievement_exists(
        self,
        user_id: UUID,
        code: str
    ) -> bool:
        """
        Check if achievement with given code already exists for user
        
        Args:
            user_id: User UUID
            code: Achievement code
            
        Returns:
            True if exists, False otherwise
        """
        return self.db.query(Achievement).filter(
            and_(
                Achievement.user_id == user_id,
                Achievement.code == code
            )
        ).first() is not None

