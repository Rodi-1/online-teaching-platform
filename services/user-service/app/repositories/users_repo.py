"""
User repository for database operations
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.models.db_models import (
    User,
    RefreshToken,
    PasswordResetToken,
    EmailConfirmation,
    PhoneConfirmation,
    UserRole,
    UserStatus
)


class UserRepository:
    """Repository for user-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # User CRUD operations
    
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number"""
        return self.db.query(User).filter(User.phone == phone).first()
    
    def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        role: UserRole,
        phone: Optional[str] = None
    ) -> User:
        """Create a new user"""
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=phone,
            is_email_confirmed=False,
            is_phone_confirmed=False,
            status=UserStatus.ACTIVE
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_user(self, user: User) -> User:
        """Update user in database"""
        user.updated_at = datetime.utcnow()
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def list_users(
        self,
        offset: int = 0,
        count: int = 20,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None
    ) -> tuple[List[User], int]:
        """
        List users with pagination and filters
        
        Returns:
            Tuple of (users_list, total_count)
        """
        query = self.db.query(User)
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        if status:
            query = query.filter(User.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset(offset).limit(count).all()
        
        return users, total
    
    # Email confirmation operations
    
    def create_email_confirmation(
        self,
        user_id: UUID,
        code: str,
        expires_minutes: int = 30
    ) -> EmailConfirmation:
        """Create email confirmation code"""
        confirmation = EmailConfirmation(
            user_id=user_id,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes),
            used=False
        )
        self.db.add(confirmation)
        self.db.commit()
        self.db.refresh(confirmation)
        return confirmation
    
    def get_email_confirmation(
        self,
        user_id: UUID,
        code: str
    ) -> Optional[EmailConfirmation]:
        """Get valid email confirmation by user_id and code"""
        return self.db.query(EmailConfirmation).filter(
            EmailConfirmation.user_id == user_id,
            EmailConfirmation.code == code,
            EmailConfirmation.used == False,
            EmailConfirmation.expires_at > datetime.utcnow()
        ).first()
    
    def mark_email_confirmation_used(self, confirmation: EmailConfirmation) -> None:
        """Mark email confirmation as used"""
        confirmation.used = True
        self.db.add(confirmation)
        self.db.commit()
    
    # Phone confirmation operations
    
    def create_phone_confirmation(
        self,
        user_id: UUID,
        code: str,
        expires_minutes: int = 30
    ) -> PhoneConfirmation:
        """Create phone confirmation code"""
        confirmation = PhoneConfirmation(
            user_id=user_id,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes),
            used=False
        )
        self.db.add(confirmation)
        self.db.commit()
        self.db.refresh(confirmation)
        return confirmation
    
    def get_phone_confirmation(
        self,
        user_id: UUID,
        code: str
    ) -> Optional[PhoneConfirmation]:
        """Get valid phone confirmation by user_id and code"""
        return self.db.query(PhoneConfirmation).filter(
            PhoneConfirmation.user_id == user_id,
            PhoneConfirmation.code == code,
            PhoneConfirmation.used == False,
            PhoneConfirmation.expires_at > datetime.utcnow()
        ).first()
    
    def mark_phone_confirmation_used(self, confirmation: PhoneConfirmation) -> None:
        """Mark phone confirmation as used"""
        confirmation.used = True
        self.db.add(confirmation)
        self.db.commit()
    
    # Password reset operations
    
    def create_password_reset_token(
        self,
        user_id: UUID,
        code: str,
        expires_minutes: int = 60
    ) -> PasswordResetToken:
        """Create password reset token"""
        token = PasswordResetToken(
            user_id=user_id,
            code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes),
            used=False
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token
    
    def get_password_reset_token(
        self,
        user_id: UUID,
        code: str
    ) -> Optional[PasswordResetToken]:
        """Get valid password reset token by user_id and code"""
        return self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.code == code,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
    
    def mark_password_reset_token_used(self, token: PasswordResetToken) -> None:
        """Mark password reset token as used"""
        token.used = True
        self.db.add(token)
        self.db.commit()
    
    # Refresh token operations
    
    def create_refresh_token(
        self,
        user_id: UUID,
        token: str,
        expires_days: int = 30
    ) -> RefreshToken:
        """Create refresh token"""
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=expires_days),
            revoked=False
        )
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token
    
    def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """Get valid refresh token"""
        return self.db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
    
    def revoke_refresh_token(self, token: RefreshToken) -> None:
        """Revoke refresh token"""
        token.revoked = True
        self.db.add(token)
        self.db.commit()
    
    def revoke_all_user_refresh_tokens(self, user_id: UUID) -> None:
        """Revoke all refresh tokens for a user"""
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        ).update({"revoked": True})
        self.db.commit()

