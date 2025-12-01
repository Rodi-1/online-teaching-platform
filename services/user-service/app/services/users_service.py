"""
User service - business logic layer
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_confirmation_code,
    create_refresh_token as generate_refresh_token
)
from app.core.config import get_settings
from app.models.db_models import User, UserRole, UserStatus
from app.models.schemas import UserCreate, UpdateProfileRequest
from app.repositories.users_repo import UserRepository


class UserService:
    """Service for user-related business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)
        self.settings = get_settings()
    
    def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        existing_user = self.repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        # Check if phone already exists (if provided)
        if user_data.phone:
            existing_phone = self.repo.get_by_phone(user_data.phone)
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this phone already exists"
                )
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user
        user = self.repo.create_user(
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            phone=user_data.phone
        )
        
        # Generate email confirmation code
        code = generate_confirmation_code()
        self.repo.create_email_confirmation(user.id, code)
        
        # TODO: Send email confirmation code via notifications service
        # For now, just log it
        print(f"Email confirmation code for {user.email}: {code}")
        
        return user
    
    def authenticate(self, email: str, password: str) -> User:
        """
        Authenticate user by email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Authenticated user
            
        Raises:
            HTTPException: If authentication fails
        """
        # Get user by email
        user = self.repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check user status
        if user.status == UserStatus.BLOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is blocked"
            )
        
        if user.status == UserStatus.DELETED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deleted"
            )
        
        return user
    
    def issue_tokens(self, user: User) -> dict:
        """
        Issue access and refresh tokens for user
        
        Args:
            user: User object
            
        Returns:
            Dictionary with access_token and expires_in
        """
        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "role": user.role,
                "email": user.email
            }
        )
        
        # Create refresh token (optional)
        refresh_token = generate_refresh_token()
        self.repo.create_refresh_token(user.id, refresh_token)
        
        return {
            "access_token": access_token,
            "expires_in": self.settings.ACCESS_TOKEN_EXPIRES_MIN * 60  # in seconds
        }
    
    def logout(self, user: User) -> None:
        """
        Logout user (revoke all refresh tokens)
        
        Args:
            user: User object
        """
        self.repo.revoke_all_user_refresh_tokens(user.id)
    
    def confirm_email(self, email: str, code: str) -> User:
        """
        Confirm user email with code
        
        Args:
            email: User email
            code: Confirmation code
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found or code is invalid
        """
        # Get user
        user = self.repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already confirmed
        if user.is_email_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already confirmed"
            )
        
        # Get confirmation
        confirmation = self.repo.get_email_confirmation(user.id, code)
        if not confirmation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired confirmation code"
            )
        
        # Mark as confirmed
        user.is_email_confirmed = True
        self.repo.update_user(user)
        self.repo.mark_email_confirmation_used(confirmation)
        
        return user
    
    def confirm_phone(self, phone: str, code: str) -> User:
        """
        Confirm user phone with code
        
        Args:
            phone: User phone
            code: Confirmation code
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found or code is invalid
        """
        # Get user
        user = self.repo.get_by_phone(phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already confirmed
        if user.is_phone_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already confirmed"
            )
        
        # Get confirmation
        confirmation = self.repo.get_phone_confirmation(user.id, code)
        if not confirmation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired confirmation code"
            )
        
        # Mark as confirmed
        user.is_phone_confirmed = True
        self.repo.update_user(user)
        self.repo.mark_phone_confirmation_used(confirmation)
        
        return user
    
    def request_password_reset(self, email: str) -> None:
        """
        Request password reset (generate code)
        
        Args:
            email: User email
        """
        # Get user (but don't reveal if they exist or not)
        user = self.repo.get_by_email(email)
        
        if user:
            # Generate reset code
            code = generate_confirmation_code()
            self.repo.create_password_reset_token(user.id, code)
            
            # TODO: Send reset code via notifications service
            # For now, just log it
            print(f"Password reset code for {user.email}: {code}")
    
    def reset_password(self, email: str, code: str, new_password: str) -> User:
        """
        Reset password with code
        
        Args:
            email: User email
            code: Reset code
            new_password: New password
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found or code is invalid
        """
        # Get user
        user = self.repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get reset token
        reset_token = self.repo.get_password_reset_token(user.id, code)
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset code"
            )
        
        # Update password
        user.password_hash = hash_password(new_password)
        self.repo.update_user(user)
        self.repo.mark_password_reset_token_used(reset_token)
        
        # Revoke all refresh tokens for security
        self.repo.revoke_all_user_refresh_tokens(user.id)
        
        return user
    
    def update_profile(self, user_id: UUID, changes: UpdateProfileRequest) -> User:
        """
        Update user profile
        
        Args:
            user_id: User ID
            changes: Profile changes
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found
        """
        # Get user
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Apply changes
        if changes.first_name is not None:
            user.first_name = changes.first_name
        
        if changes.last_name is not None:
            user.last_name = changes.last_name
        
        if changes.phone is not None:
            # Check if phone is already taken
            if changes.phone != user.phone:
                existing_phone = self.repo.get_by_phone(changes.phone)
                if existing_phone and existing_phone.id != user.id:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Phone number already in use"
                    )
                user.phone = changes.phone
                user.is_phone_confirmed = False  # Reset confirmation
        
        # Update user
        return self.repo.update_user(user)
    
    def get_user_by_id(self, user_id: UUID) -> User:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object
            
        Raises:
            HTTPException: If user not found
        """
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    def list_users(
        self,
        offset: int = 0,
        count: int = 20,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None
    ) -> Tuple[List[User], int]:
        """
        List users with pagination and filters
        
        Args:
            offset: Offset for pagination
            count: Number of items to return
            role: Filter by role
            status: Filter by status
            
        Returns:
            Tuple of (users_list, total_count)
        """
        return self.repo.list_users(offset, count, role, status)

