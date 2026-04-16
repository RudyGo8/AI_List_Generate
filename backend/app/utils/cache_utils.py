import json
from typing import Any, Optional

from backend.app.config import logger, REDIS_URL

try:
    import redis
except Exception:  # pragma: no cover
    redis = None


_redis_client = None


def _build_client():
    if redis is None:
        return None

    if not REDIS_URL:
        return None

    try:
        client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        client.ping()
        logger.info("redis cache enabled")
        return client
    except Exception as error:
        logger.info(f"redis unavailable, cache disabled: {error}")
        return None


def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = _build_client()
    return _redis_client


def get_json(key: str) -> Optional[Any]:
    client = get_redis_client()
    if not client:
        return None
    try:
        payload = client.get(key)
        if not payload:
            return None
        return json.loads(payload)
    except Exception as error:
        logger.info(f"redis get failed key={key} error={error}")
        return None


def set_json(key: str, value: Any, ttl_seconds: int = 21600) -> bool:
    client = get_redis_client()
    if not client:
        return False
    try:
        client.setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False))
        return True
    except Exception as error:
        logger.info(f"redis set failed key={key} error={error}")
        return False
