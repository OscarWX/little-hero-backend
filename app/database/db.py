from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite URL for database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./little_hero.db"

# Create async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create async session factory
async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Create a Base class for declarative models
Base = declarative_base()

# Database dependency for FastAPI endpoints
async def get_db():
    """
    Dependency function that provides a database session for FastAPI endpoints.
    Ensures the session is closed after the request is processed.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close() 