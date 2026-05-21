import os
import json
from typing import Iterable, Optional
from app.config import CACHE_DEFAULT_EXPIRE

try:
    import redis.asyncio as redis
except Exception:
    redis = None

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = None
async def get_redis_client():
    global redis_client
    if redis is None:
        return None
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

async def cache_get_set(key: str, fetch_fn, expire: Optional[int] = None):
    """Get from cache or call fetch_fn and set cache.

    If Redis is not available or connection fails, fetch_fn is called directly.
    """
    if expire is None:
        expire = CACHE_DEFAULT_EXPIRE

    r = await get_redis_client()
    if r is None:
        return await fetch_fn()

    try:
        val = await r.get(key)
        if val is not None:
            try:
                return json.loads(val)
            except Exception:
                return val

        result = await fetch_fn()
        try:
            await r.set(key, json.dumps(result), ex=expire)
        except Exception:
            pass
        return result
    except Exception:
        return await fetch_fn()

async def invalidate_prefix(prefix: str) -> int:
    """Delete keys matching prefix. Returns number of deleted keys.

    Returns 0 if Redis is not available.
    """
    r = await get_redis_client()
    if r is None:
        return 0

    deleted = 0
    keys = [k async for k in r.scan_iter(f"{prefix}*")]
    if keys:
        try:
            deleted = await r.delete(*keys)
        except Exception:
            for k in keys:
                try:
                    await r.delete(k)
                    deleted += 1
                except Exception:
                    pass
    return deleted

def invalidate_cache_after(prefixes: Iterable[str]):
    """Decorator to invalidate cache prefixes after an async write function completes."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            for prefix in prefixes:
                try:
                    await invalidate_prefix(prefix)
                except Exception:
                    pass
            return result

        return wrapper

    return decorator
