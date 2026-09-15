"""
Token revocation store backed by Redis.
Compatible with Python 3.7 (32-bit).
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.infra.redis.client import get_redis

logger = logging.getLogger(__name__)


# ---------- Key prefixes ----------
_K_JTI = "revoked:jti:{jti}"
_K_USER_TOKENS = "user:tokens:{user_id}"
_K_USER_CUTOFF = "user:revoked_before:{user_id}"
_K_REFRESH_USED = "refresh:used:{jti}"


# ---------- Internal helpers ----------
def _ttl_from_exp(exp: datetime) -> int:
    """Seconds until `exp`, min 1 (Redis rejects TTL<=0)."""
    now = datetime.now(timezone.utc)
    delta = int((exp - now).total_seconds())
    return max(delta, 1)


class RevocationStore:
    """
    High-level API for token revocation.
    Instantiate once (FastAPI dependency) or use module-level helpers.
    """

    def __init__(self, client: Optional[redis.Redis] = None) -> None:
        self._client = client

    @property
    def client(self) -> redis.Redis:
        return self._client or get_redis()

    async def _healthy(self) -> bool:
        try:
            await self.client.ping()
            return True
        except (RedisError, OSError) as exc:
            logger.error("Redis unavailable: %s", exc)
            return not settings.REVOCATION_FAIL_CLOSED

    # ========================================================
    # 1) Revoke a single token by jti
    # ========================================================
    async def revoke(
        self,
        jti: str,
        exp: datetime,
        user_id: Optional[str] = None,
    ) -> None:
        if not await self._healthy():
            return

        ttl = _ttl_from_exp(exp)
        try:
            pipe = self.client.pipeline()
            pipe.set(_K_JTI.format(jti=jti), "1", ex=ttl)
            if user_id:
                pipe.srem(_K_USER_TOKENS.format(user_id=user_id), jti)
            await pipe.execute()
        except RedisError as exc:
            logger.error("revoke() failed for jti=%s: %s", jti, exc)

    # ========================================================
    # 2) Check if a token is revoked
    # ========================================================
    async def is_revoked(
        self,
        jti: str,
        user_id: Optional[str] = None,
        issued_at: Optional[datetime] = None,
    ) -> bool:
        if not await self._healthy():
            return not settings.REVOCATION_FAIL_CLOSED

        try:
            pipe = self.client.pipeline()
            pipe.exists(_K_JTI.format(jti=jti))

            if user_id:
                pipe.get(_K_USER_CUTOFF.format(user_id=user_id))

            results = await pipe.execute()
            individually_revoked = bool(results[0])

            if individually_revoked:
                return True

            if user_id and issued_at is not None:
                cutoff = results[1]
                if cutoff and int(issued_at.timestamp()) < int(cutoff):
                    return True

            return False

        except RedisError as exc:
            logger.error("is_revoked() failed for jti=%s: %s", jti, exc)
            return not settings.REVOCATION_FAIL_CLOSED

    # ========================================================
    # 3) Revoke ALL tokens for a user (cutoff approach)
    # ========================================================
    async def revoke_all_for_user(self, user_id: str) -> None:
        if not await self._healthy():
            return

        now = int(time.time())
        try:
            ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400 + 60
            await self.client.set(
                _K_USER_CUTOFF.format(user_id=user_id),
                now,
                ex=ttl,
            )
            await self.client.delete(_K_USER_TOKENS.format(user_id=user_id))
        except RedisError as exc:
            logger.error("revoke_all_for_user(%s) failed: %s", user_id, exc)

    # ========================================================
    # 4) Track active refresh tokens (for rotation)
    # ========================================================
    async def register_refresh(
        self,
        user_id: str,
        jti: str,
        exp: datetime,
    ) -> None:
        if not await self._healthy():
            return

        ttl = _ttl_from_exp(exp)
        key = _K_USER_TOKENS.format(user_id=user_id)
        try:
            pipe = self.client.pipeline()
            pipe.sadd(key, jti)
            pipe.expire(key, ttl)
            await pipe.execute()
        except RedisError as exc:
            logger.error("register_refresh(%s) failed: %s", user_id, exc)

    # ========================================================
    # 5) Refresh token rotation — reuse detection
    # ========================================================
    async def mark_refresh_used(
        self,
        jti: str,
        user_id: str,
        exp: datetime,
    ) -> bool:
        if not await self._healthy():
            return True

        key = _K_REFRESH_USED.format(jti=jti)
        ttl = _ttl_from_exp(exp)

        try:
            was_set = await self.client.set(key, user_id, ex=ttl, nx=True)

            if was_set:
                return True

            existing = await self.client.get(key)
            if existing == user_id:
                logger.warning(
                    "Refresh token reuse detected (same user) jti=%s user=%s",
                    jti, user_id,
                )
                await self.revoke_all_for_user(user_id)
                return False

            logger.critical(
                "Refresh token STOLEN? jti=%s expected=%s got=%s",
                jti, existing, user_id,
            )
            await self.revoke_all_for_user(user_id)
            return False

        except RedisError as exc:
            logger.error("mark_refresh_used(%s) failed: %s", jti, exc)
            return True


# ---------- Module-level singleton ----------
_store = None  # type: Optional[RevocationStore]


def get_revocation_store() -> RevocationStore:
    global _store
    if _store is None:
        _store = RevocationStore()
    return _store