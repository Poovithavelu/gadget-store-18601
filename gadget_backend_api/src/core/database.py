from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import OperationalError  # Catch DB connectivity issues gracefully

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
    """
    Initialize database connection.

    On environments where MySQL is not available during startup, this should not prevent the API from starting.
    We attempt to create tables (demo/dev only). If the DB is unreachable, we log a warning and continue.
    """
    # Import models here to register with Base metadata.
    from src.models.user import User  # noqa: F401
    from src.models.product import Product  # noqa: F401
    from src.models.order import Order, OrderItem  # noqa: F401

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except OperationalError as exc:
        # Startup should not fail solely due to DB being unavailable; routes that hit DB will still error at runtime.
        # Using print to avoid requiring a logger setup; container logs will capture this.
        print(f"[startup][warning] Database is not reachable, skipping init_db table creation: {exc}")
    except Exception as exc:
        # Any other unexpected exception should also not block startup, but we emit a clear warning.
        print(f"[startup][warning] Unexpected error during init_db; continuing startup: {exc}")
