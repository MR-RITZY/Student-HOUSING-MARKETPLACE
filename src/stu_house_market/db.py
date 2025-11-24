from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from contextlib import asynccontextmanager

from src.stu_house_market.model import Base
from src.stu_house_market.config import settings

db_url = (
    f"postgresql+asyncpg://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
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
    async with async_engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all, async_engine)
            await conn.commit()
            yield
        except Exception as e:
            print(e)
            yield
        finally:
            await async_engine.dispose()
