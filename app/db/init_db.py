import asyncio
import logging
from app.db.base import engine, Base
from app.models.sql import * # Import all models to register them

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    async with engine.begin() as conn:
        # In production, we use Alembic for this. 
        # But for dev/testing, we can sometimes use create_all
        # However, since we set up Alembic, we should use that.
        # This script can be used to create initial data if needed.
        # For now, let's just check connection.
        logger.info("Checking database connection...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created (if not exist).")

    await engine.dispose()

if __name__ == "__main__":
    logger.info("Initializing database...")
    asyncio.run(init_db())
    logger.info("Database initialization complete.")
