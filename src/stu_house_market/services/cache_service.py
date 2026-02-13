from src.stu_house_market.db.redis_manager import redis_client

class CacheService:
    def __init__(self):
        self.redis_client = redis_client

    
    async def get_or_set(self, query: dict | str, tag:str, db_fn, ttl: int = 3600, *arg, **kwargs):
        key = self.get_cache_key(query, tag)
        cached = await redis_client.get_from_json(key)
        if cached:
            return cached

        value = await db_fn(*arg, **kwargs)
        await redis_client.setex_to_json(key, ttl, value)
        return value
    
    @classmethod
    def get_cache_key(query: dict | str, tag:str):
        if isinstance(query, str):
            return f"cache:{tag}:{query}"
        cache_key = f"cache:{tag}"
        for key, value in query.items():
            if value:
                cache_key += f":{key}={value}"
        return cache_key
        


def get_cache():
    return CacheService()