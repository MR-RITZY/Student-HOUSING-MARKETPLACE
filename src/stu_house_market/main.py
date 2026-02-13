from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager, AsyncExitStack


from src.stu_house_market.db.db import db_lifespan
from src.stu_house_market.core.exc import register_exceptions
from src.stu_house_market.db.redis_manager import redis_lifespan
from src.stu_house_market.router.auth import router as auth_router
from src.stu_house_market.router.user import router as user_router
from src.stu_house_market.router.house import router as house_router
from src.stu_house_market.router.google_oauth2 import router as google_oauth_router
from src.stu_house_market.core.config import settings
from src.stu_house_market.core.rate_limiter import (
    RateLimiterMiddleware,
    rate_limit_storage,
)
from src.stu_house_market.core.server_logging import app_info

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_info.info("Setting up Start-Ups")
   
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(db_lifespan())
        await stack.enter_async_context(redis_lifespan())
        rate_limit_storage.init_storage()
        app_info.info("Start-Ups set up Completely")
        yield
        app_info.info("Application Shutting Down: Closing App's Resources")


app = FastAPI(lifespan=lifespan, root_path="/api/v1/student-housing")


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    session_cookie="session",
    max_age=3600,
    same_site="lax",
    https_only=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimiterMiddleware, storage=rate_limit_storage.get_storage())

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(house_router)
app.include_router(google_oauth_router)
register_exceptions(app)


@app.get("/")
async def get_root():
    return RedirectResponse(settings.FRONTEND_HOST, status_code=status.HTTP_301_MOVED_PERMANENTLY)




