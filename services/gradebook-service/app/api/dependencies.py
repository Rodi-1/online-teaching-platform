"""API dependencies"""
from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status, Header
from jose import JWTError, jwt

class CurrentUser:
    def __init__(self, user_id: UUID, role: str, email: str):
        self.id = user_id
        self.role = role
        self.email = email

def get_current_user(authorization: str = Header(...)) -> CurrentUser:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])  # Should match JWT_SECRET
        user_id = UUID(payload.get("sub"))
        return CurrentUser(user_id=user_id, role=payload.get("role"), email=payload.get("email"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def require_teacher(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers can perform this action")
    return current_user

