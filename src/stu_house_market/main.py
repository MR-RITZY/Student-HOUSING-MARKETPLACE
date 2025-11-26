from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager, AsyncExitStack


from src.stu_house_market.db import db_lifespan
from src.stu_house_market.exc import register_exceptions
from src.stu_house_market.redis_manager import redis_lifespan
from src.stu_house_market.router.auth import router as auth_router
from src.stu_house_market.router.user import router as user_router
from src.stu_house_market.config import settings



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(db_lifespan())
        await stack.enter_async_context(redis_lifespan())
        yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)
app.include_router(auth_router)
register_exceptions(app)



@app.get("/")
async def get_root():
    return RedirectResponse(settings.FRONTEND_HOST, status_code=status.HTTP_302_FOUND)

