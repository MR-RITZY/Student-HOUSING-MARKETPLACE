from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from contextlib import asynccontextmanager

from src.stu_house_market.model import Base
from src.stu_house_market.core.config import settings
from src.stu_house_market.core.server_logging import app_info, app_error

db_url = (
    f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}/{settings.DB_NAME}"
)

async_engine = create_async_engine(db_url)

AsyncSessionMaker = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


async def get_db():
    async with AsyncSessionMaker() as session:
        yield session


@asynccontextmanager
async def db_lifespan():
    app_info.info("Connecting To Database")
    async with async_engine.begin() as conn:
        try:
            app_info.info("Checking For Tables and Creating Them If Not Present")
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()
            app_info.info("All Tables Present")
            yield
        except Exception as e:
            app_error.error(f"Encounter Error While Connecting To Database:\n{e}")
            yield
        finally:
            await async_engine.dispose()
            app_info.info("Closing Database Connections")