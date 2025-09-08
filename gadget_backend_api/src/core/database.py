from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import OperationalError  # Catch DB connectivity issues gracefully

from src.core.config import settings


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy models."""
    pass


# Lazy engine/session initialization to avoid import-time failures impacting OpenAPI generation
_engine = None  # type: Optional[object]
_SessionLocal = None  # type: Optional[async_sessionmaker[AsyncSession]]


def _ensure_engine_and_session() -> None:
    """
    Ensure the async engine and session factory are created.

    This avoids importing the DB dialect and creating an engine at module import time,
    which can cause /openapi.json to fail if the driver isn't available/configured.
    """
    global _engine, _SessionLocal
    if _engine is None:
        try:
            _engine = create_async_engine(
                settings.sqlalchemy_database_uri(),
                echo=settings.DEBUG,
                pool_pre_ping=True,
            )
            _SessionLocal = async_sessionmaker(bind=_engine, expire_on_commit=False, class_=AsyncSession)
        except Exception as exc:
            # Do not raise during schema generation; defer errors until actual DB access.
            # Log a clear warning and leave _engine/_SessionLocal as None.
            print(f"[db][warning] Failed to create async engine lazily: {exc}")
            _engine = None
            _SessionLocal = None


def get_engine():
    """
    Get or create the async SQLAlchemy engine.

    Returns:
        The async engine instance (or None if initialization failed).
    """
    _ensure_engine_and_session()
    return _engine


def get_session_factory():
    """
    Get or create the async sessionmaker.

    Returns:
        async_sessionmaker[AsyncSession] | None
    """
    _ensure_engine_and_session()
    return _SessionLocal


# PUBLIC_INTERFACE
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to provide an async database session."""
    session_factory = get_session_factory()
    if session_factory is None:
        # Surface a clear runtime error when a route actually needs the DB.
        raise RuntimeError("Database is not initialized. Check database driver and configuration.")
    async with session_factory() as session:
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

    engine = get_engine()
    if engine is None:
        print("[startup][warning] Database engine not available; skipping init_db table creation.")
        return

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
