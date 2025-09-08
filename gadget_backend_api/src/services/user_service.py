from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash, verify_password
from src.models.user import User


# PUBLIC_INTERFACE
async def create_user(db: AsyncSession, email: str, password: str, full_name: str | None = None, is_admin: bool = False) -> User:
    """Create a new user with hashed password."""
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise ValueError("User with this email already exists")
    user = User(email=email, full_name=full_name, hashed_password=get_password_hash(password), is_admin=is_admin)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# PUBLIC_INTERFACE
async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
