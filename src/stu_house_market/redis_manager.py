from redis.asyncio import Redis, ConnectionPool, Connection
from src.stu_house_market.config import settings
from typing import Optional, Any
from contextlib import asynccontextmanager


connection_kwargs = dict(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    max_connections=3,
    socket_timeout=30.0,
    socket_connect_timeout=5.0,
    socket_keepalive=True,
    retry_on_timeout=True,
    health_check_interval=30.0,
    decode_responses=True,
    client_name=settings.APP_NAME,
    connection_class=Connection,
)


if settings.ENV == "PROD":
    connection_kwargs.update(
        {
            "username": settings.REDIS_USERNAME,
            "password": settings.REDIS_PASSWORD,
        }
    )


class RedisManager:
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.redis: Optional[Redis] = None

    def initialize_redis(self):
        if not self.pool or not self.redis:
            self.pool = ConnectionPool(**connection_kwargs)
            self.redis = Redis(connection_pool=self.pool)

    async def terminate(self):
        if self.redis:
            await self.redis.close()
        if self.pool:
            await self.pool.disconnect()

    async def ping(self):
        return await self.redis.ping()

    async def setex(self, key: str, ttl: int, value: Any):
        return await self.redis.setex(key, ttl, value)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def ttl(self, key: str):
        return await self.redis.ttl(key)

    async def delete(self, key: str):
        return await self.redis.delete(key)


redis_client = RedisManager()


@asynccontextmanager
async def redis_lifespan():
    try:
        redis_client.initialize_redis()
        await redis_client.ping()
        yield redis_client
    except Exception as e:
        raise
    finally:
        await redis_client.terminate()
