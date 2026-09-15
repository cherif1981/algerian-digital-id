from datetime import datetime, timedelta, timezone
import pytest
import fakeredis.aioredis

from app.core.revocation import RevocationStore


@pytest.fixture
async def store():
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    s = RevocationStore(client=client)
    yield s
    # fakeredis القديم مش عنده aclose → استخدم close
    await client.close()


@pytest.mark.asyncio
async def test_revoke_single_token(store):
    exp = datetime.now(timezone.utc) + timedelta(minutes=5)
    await store.revoke("jti-1", exp=exp, user_id="u1")

    assert await store.is_revoked("jti-1") is True
    assert await store.is_revoked("jti-2") is False


@pytest.mark.asyncio
async def test_revoke_all_for_user(store):
    now = datetime.now(timezone.utc)
    past = now - timedelta(minutes=1)

    await store.revoke_all_for_user("u1")

    assert await store.is_revoked("any", user_id="u1", issued_at=past) is True


@pytest.mark.asyncio
async def test_refresh_reuse_detection(store):
    exp = datetime.now(timezone.utc) + timedelta(days=7)

    first = await store.mark_refresh_used("jti-r1", "u1", exp)
    assert first is True

    second = await store.mark_refresh_used("jti-r1", "u1", exp)
    assert second is False