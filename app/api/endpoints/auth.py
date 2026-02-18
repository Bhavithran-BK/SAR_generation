from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.sql import User
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    role: str

@router.post("/login", response_model=UserResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Simplified login for demo.
    """
    query = select(User).where(User.username == request.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    # In a real app, we'd check hashed passwords.
    # For this hackathon demo, we check equality or assume seeded data.
    if not user or user.password_hash != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
        
    return UserResponse(username=user.username, role=user.role)
