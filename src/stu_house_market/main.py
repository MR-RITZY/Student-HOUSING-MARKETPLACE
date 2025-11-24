from fastapi import FastAPI
from contextlib import asynccontextmanager, AsyncExitStack

from src.stu_house_market.db import db_lifespan
from src.stu_house_market.exc import register_exceptions
from src.stu_house_market.redis_manager import redis_lifespan
from src.stu_house_market.router.auth import router as auth_router
from src.stu_house_market.router.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(db_lifespan())
        await stack.enter_async_context(redis_lifespan())
        yield



app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(auth_router)
register_exceptions(app)


