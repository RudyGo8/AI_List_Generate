from typing import List, Dict

from backend.app.utils.embedding_utils import get_embedding, batch_get_embeddings, cosine_similarity


# 关键词重叠度
def _keyword_overlap_score(query: str, text: str) -> float:
    q_terms = set((query or '').lower().replace('>', ' ').split())
    t_terms = set((text or '').lower().replace('>', ' ').split())
    if not q_terms or not t_terms:
        return 0.0
    return len(q_terms & t_terms) / max(len(q_terms), 1)


# 类目混合排序，返回top3
def rank_categories_hybrid(query_text: str, category_list: List[Dict], top_k: int = 3) -> List[Dict]:
    if not category_list:
        return []

    query_embedding = get_embedding(query_text)
    category_texts = [item.get('category_path', '') for item in category_list]
    category_embeddings = batch_get_embeddings(category_texts)

    ranked = []
    for index, category in enumerate(category_list):
        path = category.get('category_path', '')
        emb_score = 0.0
        if query_embedding and index < len(category_embeddings) and category_embeddings[index]:
            emb_score = cosine_similarity(query_embedding, category_embeddings[index])

        key_score = _keyword_overlap_score(query_text, path)
        score = emb_score * 0.8 + key_score * 0.2

        ranked.append({
            **category,
            'embedding_similarity': emb_score,
            'keyword_score': key_score,
            'score': score,
        })

    ranked.sort(key=lambda x: x.get('score', 0), reverse=True)
    return ranked[:top_k]
