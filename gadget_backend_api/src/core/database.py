from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy models."""
    pass


# Create engine and session factory
engine = create_async_engine(settings.sqlalchemy_database_uri(), echo=settings.DEBUG, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


# PUBLIC_INTERFACE
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to provide an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


# PUBLIC_INTERFACE
async def init_db() -> None:
    """Initialize database connection. Intended for startup checks; models create handled via migrations or explicit call."""
    # For demo purposes, we can create tables automatically (not recommended for production).
    # Import models here to register with Base metadata.
    from src.models.user import User  # noqa: F401
    from src.models.product import Product  # noqa: F401
    from src.models.order import Order, OrderItem  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
