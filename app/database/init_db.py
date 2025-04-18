import asyncio
from app.database.db import Base, engine
from app.utils.storage import configure_lifecycle_policy


async def init_db():
    """
    Initialize the database by creating all tables.
    """
    async with engine.begin() as conn:
        # Drop all tables if they exist
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database initialized!")


async def configure_storage():
    """
    Configure storage settings, like S3 lifecycle policies.
    """
    # Configure S3 lifecycle policy
    if configure_lifecycle_policy():
        print("S3 lifecycle policy configured successfully")
    else:
        print("Failed to configure S3 lifecycle policy")


# Run this file directly to initialize the database
if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(configure_storage()) 