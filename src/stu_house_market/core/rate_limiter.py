from starlette.middleware.base import BaseHTTPMiddleware
from limits.aio.storage import RedisStorage
from limits.aio.strategies import (
    SlidingWindowCounterRateLimiter,
    MovingWindowRateLimiter,
)
from limits import RateLimitItemPerSecond
from fastapi import Request, status, FastAPI
from hashlib import sha256
from typing import Optional


from src.stu_house_market.core.config import settings
from src.stu_house_market.core.exc import TooManyRequestException


def get_redis_uri() -> str:
    if settings.ENV == "PROD":
        return (
            f"async+redis://{settings.REDIS_USERNAME}:{settings.REDIS_PASSWORD}"
            f"@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        )
    return (
        f"async+redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
    )


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        storage: RedisStorage,
        rate: Optional[int] = settings.DEFAULT_MIDDLEWARE_RATE_LIMIT,
    ):
        super().__init__(app)
        self.rate_limiter = SlidingWindowCounterRateLimiter(storage)
        self.rate = RateLimitItemPerSecond(rate)

    async def dispatch(self, request: Request, call_next):
        user_id = user_identifier(request)
        is_allowed = await self.rate_limiter.hit(self.rate, user_id)
        if not is_allowed:
            raise TooManyRequestException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests -- User exceeded limit",
            )

        return await call_next(request)


def user_identifier(request: Request) -> str:
    payload = getattr(request.state, "payload", None)

    if payload and payload.get("sub"):
        raw_id = f"usr:{payload['sub']}"
    else:
        client = request.client
        raw_id = f"usr:ip:{client.host if client else 'unknown'}"

    return f"usr_{sha256(raw_id.encode()).hexdigest()}"


def standalone_rate_limiter(
    rate: Optional[int] = settings.DEFAULT_MIDDLEWARE_RATE_LIMIT // 2,
):
    async def limiter(request: Request):
        user_id = user_identifier(request)
        moving_window_limiter = MovingWindowRateLimiter(
            rate_limit_storage.get_storage()
        )
        is_allowed = await moving_window_limiter.hit(
            RateLimitItemPerSecond(rate), user_id
        )
        if not is_allowed:
            raise TooManyRequestException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests -- User exceeded limit",
            )

    return limiter


class RateLimitStorage:
    def __init__(self):
        self.storage: Optional[RedisStorage] = None

    def init_storage(self):
        if self.storage:
            return

        redis_uri = get_redis_uri()

        self.storage = RedisStorage(redis_uri, implementation="redispy")

    def get_storage(self) -> RedisStorage:
        if not self.storage:
            self.init_storage()
        return self.storage


rate_limit_storage = RateLimitStorage()
