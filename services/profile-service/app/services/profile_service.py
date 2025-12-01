"""
Business logic for profile and achievements
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.models.schemas import (
    ProfileOut,
    ProfileUpdateRequest,
    AchievementOut,
    AchievementsListResponse,
    AchievementCreateRequest,
    UpdateStatsRequest,
    UpdateStatsResponse,
    ProgressStats
)
from app.repositories.profile_repo import ProfileRepository


class ProfileService:
    """Service for profile and achievements business logic"""
    
    def __init__(self, repo: ProfileRepository):
        self.repo = repo
    
    def get_profile(
        self,
        user_id: UUID,
        include_achievements: bool = True,
        achievements_limit: int = 10
    ) -> ProfileOut:
        """
        Get user profile with optional achievements
        
        Args:
            user_id: User UUID
            include_achievements: Whether to include achievements
            achievements_limit: Maximum number of achievements to include
            
        Returns:
            ProfileOut with profile data and achievements
        """
        # Get or create profile
        profile = self.repo.get_or_create_profile(user_id)
        
        # Prepare progress stats
        progress = ProgressStats(
            total_courses=profile.total_courses,
            completed_courses=profile.completed_courses,
            active_courses=profile.active_courses,
            average_grade=profile.average_grade,
            homeworks_completed=profile.homeworks_completed,
            tests_passed=profile.tests_passed
        )
        
        # Get achievements if requested
        achievements = None
        if include_achievements:
            achievements_list, _ = self.repo.list_achievements(
                user_id=user_id,
                offset=0,
                count=achievements_limit
            )
            achievements = [
                AchievementOut.model_validate(achievement)
                for achievement in achievements_list
            ]
        
        # Build response
        return ProfileOut(
            user_id=profile.user_id,
            avatar_url=profile.avatar_url,
            about=profile.about,
            social_links=profile.social_links or [],
            progress=progress,
            achievements=achievements
        )
    
    def update_profile(
        self,
        user_id: UUID,
        update_data: ProfileUpdateRequest
    ) -> ProfileOut:
        """
        Update user profile
        
        Args:
            user_id: User UUID
            update_data: Profile update data
            
        Returns:
            Updated ProfileOut
        """
        # Update profile
        profile = self.repo.update_profile(
            user_id=user_id,
            avatar_url=update_data.avatar_url,
            about=update_data.about,
            social_links=update_data.social_links
        )
        
        # Return updated profile (without achievements to save performance)
        return self.get_profile(user_id, include_achievements=False)
    
    def get_achievements(
        self,
        user_id: UUID,
        code: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        offset: int = 0,
        count: int = 50
    ) -> AchievementsListResponse:
        """
        Get user achievements with filters and pagination
        
        Args:
            user_id: User UUID
            code: Filter by achievement code (optional)
            date_from: Filter by received_at >= date_from (optional)
            date_to: Filter by received_at <= date_to (optional)
            offset: Number of records to skip
            count: Maximum number of records to return
            
        Returns:
            AchievementsListResponse with achievements and metadata
        """
        achievements, total = self.repo.list_achievements(
            user_id=user_id,
            code=code,
            date_from=date_from,
            date_to=date_to,
            offset=offset,
            count=count
        )
        
        items = [
            AchievementOut.model_validate(achievement)
            for achievement in achievements
        ]
        
        return AchievementsListResponse(
            user_id=user_id,
            items=items,
            total=total,
            offset=offset,
            count=count
        )
    
    def create_achievement(
        self,
        user_id: UUID,
        data: AchievementCreateRequest,
        check_duplicate: bool = True
    ) -> AchievementOut:
        """
        Create new achievement for user
        
        Args:
            user_id: User UUID
            data: Achievement creation data
            check_duplicate: Whether to check for duplicates (optional)
            
        Returns:
            Created AchievementOut
            
        Raises:
            ValueError: If duplicate achievement exists and check_duplicate is True
        """
        # Check for duplicate if requested
        if check_duplicate and self.repo.achievement_exists(user_id, data.code):
            raise ValueError(
                f"Achievement with code '{data.code}' already exists for user {user_id}"
            )
        
        # Create achievement
        achievement = self.repo.create_achievement(user_id, data)
        
        return AchievementOut.model_validate(achievement)
    
    def update_stats(
        self,
        user_id: UUID,
        stats: UpdateStatsRequest
    ) -> UpdateStatsResponse:
        """
        Update user statistics
        
        Args:
            user_id: User UUID
            stats: Statistics update request
            
        Returns:
            UpdateStatsResponse with updated stats
        """
        # Update statistics
        profile = self.repo.update_stats(user_id, stats)
        
        # Prepare progress stats
        progress = ProgressStats(
            total_courses=profile.total_courses,
            completed_courses=profile.completed_courses,
            active_courses=profile.active_courses,
            average_grade=profile.average_grade,
            homeworks_completed=profile.homeworks_completed,
            tests_passed=profile.tests_passed
        )
        
        return UpdateStatsResponse(
            user_id=profile.user_id,
            progress=progress,
            updated_at=profile.updated_at
        )

