from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.core.security import get_current_active_user, get_current_admin_user
from src.models.user import User
from src.schemas.user import UserRead

router = APIRouter(tags=["Users"])


@router.get("/me", response_model=UserRead, summary="Get current user", description="Get the profile of the authenticated user.")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Return current user profile."""
    return current_user


@router.get("", response_model=List[UserRead], summary="List users", description="Admin: List all users.", dependencies=[Depends(get_current_admin_user)])
async def list_users(db: AsyncSession = Depends(get_db)):
    """List all users (admin only)."""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()
