from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.security import create_access_token, get_current_active_user
from src.schemas.auth import Token
from src.schemas.user import UserCreate, UserRead
from src.services.user_service import authenticate_user, create_user
from src.models.user import User

router = APIRouter(tags=["Auth"])


@router.post(
    "/register",
    response_model=UserRead,
    summary="Register a new user",
    description="Create a new user account.",
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a user with email and password."""
    try:
        user = await create_user(db, email=user_in.email, password=user_in.password, full_name=user_in.full_name)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/token",
    response_model=Token,
    summary="Obtain JWT token",
    description="Login and obtain a JWT access token.",
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Login with email and password to receive a JWT token."""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.email, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserRead,
    summary="Validate token and get current user",
    description="Returns the authenticated user's profile if the provided bearer token is valid.",
)
async def auth_me(current_user: User = Depends(get_current_active_user)):
    """Token validation endpoint returning the current authenticated user profile."""
    return current_user
