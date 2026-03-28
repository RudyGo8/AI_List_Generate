'''
@create_time: 2026/3/28
@Author: GeChao
@File: embedding_utils.py
'''
import numpy as np
from typing import List, Dict, Any
from app.database import get_db_instance
from app.models.db_sys_conf import SysConf
from app.models.constants import DataEnable


def get_embedding(text: str) -> List[float]:
    """get """
    db = next(get_db_instance())
    try:
        embedding_api_key = db.query(SysConf).filter_by(key='EMBEDDING_API_KEY', enable=DataEnable.ON.value).first().value
        embedding_base_url = db.query(SysConf).filter_by(key='EMBEDDING_BASE_URL', enable=DataEnable.ON.value).first().value
        embedding_model = db.query(SysConf).filter_by(key='EMBEDDING_MODEL', enable=DataEnable.ON.value).first().value

        if not embedding_base_url or not embedding_api_key:
            raise ValueError("Embedding API not configured")

        from openai import OpenAI
        client = OpenAI(api_key=embedding_api_key, base_url=embedding_base_url)

        response = client.embeddings.create(
            model=embedding_model,
            input=text
        )

        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return None
    finally:
        db.close()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """calculate cosine similarity between two vectors"""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))


def batch_get_embeddings(texts: List[str]) -> List[List[float]]:
    """batch get embedding"""
    db = next(get_db_instance())
    try:
        embedding_api_key = db.query(SysConf).filter_by(key='EMBEDDING_API_KEY', enable=DataEnable.ON.value).first().value
        embedding_base_url = db.query(SysConf).filter_by(key='EMBEDDING_BASE_URL', enable=DataEnable.ON.value).first().value
        embedding_model = db.query(SysConf).filter_by(key='EMBEDDING_MODEL', enable=DataEnable.ON.value).first().value

        if not embedding_base_url or not embedding_api_key:
            raise ValueError("Embedding API not configured")

        from openai import OpenAI
        client = OpenAI(api_key=embedding_api_key, base_url=embedding_base_url)

        response = client.embeddings.create(
            model=embedding_model,
            input=texts
        )

        return [item.embedding for item in response.data]
    except Exception as e:
        print(f"Batch embedding error: {e}")
        return []
    finally:
        db.close()


def find_similar_categories(query_text: str, category_list: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """Find similar categories for the given query text and category list"""
    if not category_list:
        return []

    try:
        query_embedding = get_embedding(query_text)
        if not query_embedding:
            return category_list[:top_k]

        category_texts = [cat.get('category_path', '') for cat in category_list]
        category_embeddings = batch_get_embeddings(category_texts)

        if not category_embeddings:
            return category_list[:top_k]

        similarities = []
        for i, cat in enumerate(category_list):
            cat_embedding = category_embeddings[i] if i < len(category_embeddings) else None
            if cat_embedding:
                sim = cosine_similarity(query_embedding, cat_embedding)
                similarities.append({
                    **cat,
                    'similarity': sim
                })

        similarities.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        return similarities[:top_k]

    except Exception as e:
        print(f"Find similar categories error: {e}")
        return category_list[:top_k]
