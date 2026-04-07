"""
Embedding utilities with optional Redis cache.
"""

import hashlib
from typing import Any, Dict, List

import numpy as np

from app.config import EMBEDDING_CACHE_TTL_SECONDS, logger
from app.database import get_db_instance
from app.models.constants import DataEnable
from app.models.db_sys_conf import SysConf
from app.utils.cache_utils import get_json, set_json


def _norm_text(text: str) -> str:
    return (text or "").strip().lower()


def _build_embedding_cache_key(model_name: str, text: str) -> str:
    payload = f"{_norm_text(model_name)}|{_norm_text(text)}"
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
    return f"ailist:emb:v1:{digest}"


def _get_embedding_conf(db):
    api_key_obj = db.query(SysConf).filter_by(key="EMBEDDING_API_KEY", enable=DataEnable.ON.value).first()
    base_url_obj = db.query(SysConf).filter_by(key="EMBEDDING_BASE_URL", enable=DataEnable.ON.value).first()
    model_obj = db.query(SysConf).filter_by(key="EMBEDDING_MODEL", enable=DataEnable.ON.value).first()

    api_key = api_key_obj.value if api_key_obj else None
    base_url = base_url_obj.value if base_url_obj else None
    model_name = model_obj.value if model_obj else None
    return api_key, base_url, model_name


def get_embedding(text: str) -> List[float]:
    """Generate one embedding vector."""
    db = next(get_db_instance())
    try:
        embedding_api_key, embedding_base_url, embedding_model = _get_embedding_conf(db)
        if not embedding_base_url or not embedding_api_key or not embedding_model:
            raise ValueError("Embedding API not configured")

        cache_key = _build_embedding_cache_key(embedding_model, text)
        cached_embedding = get_json(cache_key)
        if isinstance(cached_embedding, list) and cached_embedding:
            logger.info(f"embedding_cache_hit key={cache_key}")
            return cached_embedding
        logger.info(f"embedding_cache_miss key={cache_key}")

        from openai import OpenAI

        client = OpenAI(api_key=embedding_api_key, base_url=embedding_base_url)
        response = client.embeddings.create(model=embedding_model, input=text)
        embedding = response.data[0].embedding

        set_json(cache_key, embedding, ttl_seconds=EMBEDDING_CACHE_TTL_SECONDS)
        return embedding
    except Exception as error:
        logger.error(f"Embedding error: {error}")
        return None
    finally:
        db.close()


# 相似度计算
def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    arr1 = np.array(vec1)
    arr2 = np.array(vec2)
    dot_product = np.dot(arr1, arr2)
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))


# 向量库
def batch_get_embeddings(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []

    db = next(get_db_instance())
    try:
        embedding_api_key, embedding_base_url, embedding_model = _get_embedding_conf(db)
        if not embedding_base_url or not embedding_api_key or not embedding_model:
            raise ValueError("Embedding API not configured")

        result_embeddings: List[List[float]] = [None] * len(texts)
        miss_texts: List[str] = []
        miss_indices: List[int] = []

        for idx, text in enumerate(texts):
            cache_key = _build_embedding_cache_key(embedding_model, text)
            cached_embedding = get_json(cache_key)
            if isinstance(cached_embedding, list) and cached_embedding:
                result_embeddings[idx] = cached_embedding
            else:
                miss_texts.append(text)
                miss_indices.append(idx)

        if not miss_texts:
            logger.info(f"embedding_batch_cache_hit_all count={len(texts)}")
            return result_embeddings

        logger.info(f"embedding_batch_cache_partial total={len(texts)} miss={len(miss_texts)}")

        from openai import OpenAI

        client = OpenAI(api_key=embedding_api_key, base_url=embedding_base_url)
        response = client.embeddings.create(model=embedding_model, input=miss_texts)
        miss_embeddings = [item.embedding for item in response.data]

        for miss_i, embedding in enumerate(miss_embeddings):
            original_idx = miss_indices[miss_i]
            original_text = texts[original_idx]
            result_embeddings[original_idx] = embedding
            cache_key = _build_embedding_cache_key(embedding_model, original_text)
            set_json(cache_key, embedding, ttl_seconds=EMBEDDING_CACHE_TTL_SECONDS)

        return result_embeddings
    except Exception as error:
        logger.error(f"Batch embedding error: {error}")
        return []
    finally:
        db.close()


def find_similar_categories(query_text: str, category_list: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """Find similar categories by embedding similarity."""
    if not category_list:
        return []

    try:
        query_embedding = get_embedding(query_text)
        if not query_embedding:
            return category_list[:top_k]

        category_texts = [cat.get("category_path", "") for cat in category_list]
        category_embeddings = batch_get_embeddings(category_texts)
        if not category_embeddings:
            return category_list[:top_k]

        similarities = []
        for i, category in enumerate(category_list):
            category_embedding = category_embeddings[i] if i < len(category_embeddings) else None
            if category_embedding:
                sim = cosine_similarity(query_embedding, category_embedding)
                similarities.append({**category, "similarity": sim})

        similarities.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        return similarities[:top_k]
    except Exception as error:
        logger.error(f"Find similar categories error: {error}")
        return category_list[:top_k]
