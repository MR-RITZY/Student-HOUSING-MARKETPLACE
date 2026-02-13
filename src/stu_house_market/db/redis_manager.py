from redis.asyncio import Redis, ConnectionPool, Connection, SSLConnection
from redis.exceptions import ConnectionError
from typing import Optional, Any
from contextlib import asynccontextmanager
import json

from src.stu_house_market.core.config import settings
from src.stu_house_market.core.server_logging import app_info, app_error

connection_kwargs = dict(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    socket_timeout=30.0,
    socket_connect_timeout=5.0,
    socket_keepalive=True,
    retry_on_timeout=True,
    health_check_interval=30.0,
    decode_responses=True,
    client_name=settings.APP_NAME,
)


if settings.REDIS_USERNAME:
    connection_kwargs["username"] = settings.REDIS_USERNAME

if settings.REDIS_PASSWORD:
    connection_kwargs["password"] = settings.REDIS_PASSWORD


class RedisManager:
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.redis: Optional[Redis] = None

    def initialize_redis(self):
        if self.redis:
            return
        self.pool = ConnectionPool(
            connection_class = SSLConnection if settings.ENV == "PROD" else Connection,
            max_connections=10,
            **connection_kwargs,
        )
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

    async def setex_to_json(self, key: str, ttl: int, value: Any):
        return await self.redis.setex(key, ttl, json.dumps(value))

    async def get_from_json(self, key: str):
        value = await self.redis.get(key)
        return json.loads(value) if value else None


redis_client = RedisManager()


@asynccontextmanager
async def redis_lifespan():
    try:
        app_info.info("Connecting to Redis")
        redis_client.initialize_redis()
        await redis_client.ping()
        app_info.info("Redis Connection Successfully")
        yield redis_client
    except ConnectionError as e:
        app_error.error(f"Error Encounter While Connecting to Redis:\n{e}")
        raise
    finally:
        await redis_client.terminate()
        app_info.info("Closing Redis Connection")
