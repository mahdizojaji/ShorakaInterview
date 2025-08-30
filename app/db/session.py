from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.setting import settings

PG_DSN = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DBNAME}"

# Create engine with connection pooling configuration
# Note: For async engines, SQLAlchemy automatically uses the appropriate pool class
engine = create_async_engine(
    url=PG_DSN,
    echo=settings.DB_ECHO,
    # Connection pooling configuration
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    # Connection configuration
    connect_args={"server_settings": {"application_name": "bimahbazar_app"}},
)

# Create session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session with proper connection pooling.
    This function yields a session from the connection pool.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


def get_session_sync():
    """
    Synchronous function to get session factory for manual session management.
    Useful for background tasks or non-async contexts.
    """
    return async_session_factory
