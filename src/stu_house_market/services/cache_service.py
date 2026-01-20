from src.stu_house_market.db.redis_manager import redis_client

class CacheService:
    def __init__(self):
        self.redis_client = redis_client

    
    async def get_or_set(self, query: dict, ttl: int, db_fn, *arg, **kwargs):
        key = self.get_cache_key(query)
        cached = await redis_client.get_from_json(key)
        if cached:
            return cached

        value = await db_fn(*arg, **kwargs)
        await redis_client.setex_to_json(key, ttl, value)
        return value
    
    @classmethod
    def get_cache_key(query: dict):
        cache_key = "cache"
        for key, value in query.items():
            if value:
                cache_key += f":{key}={value}"
        return cache_key
        


def get_cache():
    return CacheService()