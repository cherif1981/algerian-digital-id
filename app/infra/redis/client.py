"""
Async Redis client with connection pooling.
Used for: token revocation, rate limiting, session cache.
"""

from __future__ import annotations

from typing import AsyncGenerator

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings


_pool: Redis | None = None


def get_redis() -> Redis:
    """
    Return a singleton Redis client backed by a connection pool.
    Safe to call from anywhere; connection is lazy.
    """
    global _pool
    if _pool is None:
        _pool = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT,
            retry_on_timeout=True,
            health_check_interval=30,
        )
    return _pool


async def get_redis_dep() -> AsyncGenerator[Redis, None]:
    """FastAPI dependency variant."""
    yield get_redis()


async def close_redis() -> None:
    """Call on app shutdown."""
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None


async def ping_redis() -> bool:
    """Health check for /health endpoint."""
    try:
        return await get_redis().ping()
    except Exception:
        return False