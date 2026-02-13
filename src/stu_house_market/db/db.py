from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy import text

import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from src.stu_house_market.model import Base
from src.stu_house_market.core.config import settings
from src.stu_house_market.core.server_logging import app_info, app_error

db_url = (
    f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}/{settings.DB_NAME}"
)

async_engine = create_async_engine(
    db_url,
    pool_pre_ping=True,
)

AsyncSessionMaker = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionMaker() as session:
        yield session


@asynccontextmanager
async def db_lifespan():
    app_info.info("Connecting To Database")

    try:
        if settings.ENV == "PROD":
            await check_for_db()
            await verify_schema()

        else:

            async with async_engine.begin() as conn:
                app_info.info("Checking For Tables and Creating Them If Not Present")
                await conn.run_sync(Base.metadata.create_all)
                app_info.info("All Tables Present")
        
        app_info.info("Database ready")
        yield

    except (DBAPIError, SQLAlchemyError) as e:
        app_error.error(f"Database startup error:\n{e}")
        raise

    finally:

        await async_engine.dispose()
        app_info.info("Closing Database Connections")


async def check_for_db(retries=5, delay=2):
    for attempt in range(retries):
        try:
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            app_info.info("Database connection verified")
            return
        except (DBAPIError, SQLAlchemyError) as e:
            if attempt == retries - 1:
                app_error.error("Database unreachable after retries")
                raise
            app_info.warning(
                f"Database not ready (attempt {attempt+1}/{retries}), retrying..."
            )
            await asyncio.sleep(delay)


async def verify_schema():
    app_info.info("Verifying database schema")
    
    required_tables = set(Base.metadata.tables.keys())
    
    if not required_tables:
        app_info.warning("No tables defined in metadata")
        return
    
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            ))
            existing_tables = {row[0] for row in result}
        
        missing_tables = required_tables - existing_tables
        
        if missing_tables:
            app_error.error(
                f"Missing required tables in production database: {missing_tables}"
            )
            raise RuntimeError(
                f"Database schema incomplete. Missing tables: {', '.join(missing_tables)}"
            )
        
        app_info.info(f"Schema verified: {len(required_tables)} tables present")
        
    except (DBAPIError, SQLAlchemyError) as e:
        app_error.error(f"Schema verification failed: {e}")
        raise