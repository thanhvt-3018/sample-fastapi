from __future__ import annotations

from datetime import timedelta

# Sử dụng aioredis để hỗ trợ Redis bất đồng bộ, phù hợp với FastAPI, giúp cải thiện hiệu suất khi làm việc với Redis trong các endpoint async
import redis.asyncio as aioredis

from app.core.config import settings

_redis: aioredis.Redis | None = None

REVOKED_PREFIX = "revoked_token:"


async def init_redis() -> None:
    global _redis
    # Sử dụng decode_responses=True để tự động giải mã giá trị trả về từ Redis thành chuỗi, giúp dễ dàng làm việc với dữ liệu
    _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialised")
    return _redis


async def revoke_token(token: str, ttl: timedelta) -> None:
    await get_redis().setex(f"{REVOKED_PREFIX}{token}", int(ttl.total_seconds()), "")


async def is_token_revoked(token: str) -> bool:
    result = await get_redis().exists(f"{REVOKED_PREFIX}{token}")
    return result == 1
