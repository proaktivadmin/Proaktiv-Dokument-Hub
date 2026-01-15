"""
Database Configuration and Session Management

Provides async SQLAlchemy engine and session factory for database operations.
Supports both PostgreSQL (production) and SQLite (development/low-cost).
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from typing import AsyncGenerator
import logging
import os

from app.config import settings

logger = logging.getLogger(__name__)


def is_sqlite(url: str) -> bool:
    """Check if the database URL is for SQLite."""
    return url.startswith("sqlite")


def get_async_database_url(url: str) -> str:
    """
    Convert database URL to async format.
    
    - postgresql:// -> postgresql+asyncpg://
    - sqlite:// -> sqlite+aiosqlite://
    """
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url


def get_sync_database_url(url: str) -> str:
    """
    Ensure URL uses sync driver for Alembic migrations.
    
    - postgresql+asyncpg:// -> postgresql://
    - sqlite+aiosqlite:// -> sqlite://
    """
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "")
    if "+aiosqlite" in url:
        return url.replace("+aiosqlite", "")
    return url


def ensure_sqlite_directory(url: str) -> None:
    """
    Ensure the directory for SQLite database file exists.
    
    For URLs like sqlite:////data/prod.db, creates /data if needed.
    """
    if is_sqlite(url):
        # Extract path from sqlite:////path/to/db.db
        path = url.replace("sqlite:///", "").replace("sqlite://", "")
        if path.startswith("/"):
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created SQLite database directory: {directory}")


# Ensure SQLite directory exists before creating engines
ensure_sqlite_directory(settings.DATABASE_URL)

# Engine configuration based on database type
if is_sqlite(settings.DATABASE_URL):
    # SQLite configuration - simpler, no connection pooling
    async_engine = create_async_engine(
        get_async_database_url(settings.DATABASE_URL),
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
    )
    
    sync_engine = create_engine(
        get_sync_database_url(settings.DATABASE_URL),
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL configuration - with connection pooling
    async_engine = create_async_engine(
        get_async_database_url(settings.DATABASE_URL),
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    
    sync_engine = create_engine(
        get_sync_database_url(settings.DATABASE_URL),
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )


# Async session factory
async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    
    Yields:
        AsyncSession: Database session that auto-closes after request.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database connection.
    
    Called on application startup to verify database connectivity.
    For SQLite, also creates tables if they don't exist.
    """
    from sqlalchemy import text
    
    # Import models to ensure they're registered with Base
    from app.models import Base
    from app.models import template, category, tag  # noqa: F401
    
    try:
        async with async_engine.connect() as conn:
            # Test connection
            await conn.execute(text("SELECT 1"))
        
        db_type = "SQLite" if is_sqlite(settings.DATABASE_URL) else "PostgreSQL"
        logger.info(f"Database connection established successfully ({db_type})")
        
        # For SQLite (ephemeral), automatically create all tables on startup
        if is_sqlite(settings.DATABASE_URL):
            logger.info("SQLite detected - creating tables if they don't exist...")
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created/verified successfully")
            
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


async def close_db() -> None:
    """
    Close database connections.
    
    Called on application shutdown.
    """
    await async_engine.dispose()
    logger.info("Database connections closed")
