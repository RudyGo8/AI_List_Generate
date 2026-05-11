import json
import redis
from typing import Any, Optional
from backend.app.config import logger, REDIS_URL

_redis_client = None

def _build_client():
    if redis is None:
        return None
    if not REDIS_URL:
        return None
    try:
        # 创建redis
        client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        # 测试redis
        client.ping()
        logger.info("redis cache enabled")
        return client
    except Exception as error:
        logger.info(f"redis unavailable, cache disabled: {error}")
        return None

# 懒加载：避免重复创建连接
def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = _build_client()
    return _redis_client

# 读取缓存
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

# 写入缓存
def set_json(key: str, value: Any, ttl_seconds: int = 21600) -> bool:
    client = get_redis_client()
    if not client:
        return False
    try:
        # 设置期限
        client.setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False))
        return True
    except Exception as error:
        logger.info(f"redis set failed key={key} error={error}")
        return False
