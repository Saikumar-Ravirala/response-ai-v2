import redis.asyncio as aioredis
from app.core.config import settings

# Single shared async Redis connection
redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def add_to_denylist(jti: str, ttl_seconds: int):
    """
    Called on logout.
    Blocks this JWT immediately even though it hasn't expired yet.
    Auto-removed from Redis after ttl_seconds (when token would have expired anyway).
    """
    await redis.setex(f"denylist:{jti}", ttl_seconds, "1")


async def is_denylisted(jti: str) -> bool:
    """
    Called on every protected request.
    Returns True if this token was revoked (user logged out).
    """
    return await redis.exists(f"denylist:{jti}") > 0