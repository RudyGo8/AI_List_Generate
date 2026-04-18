import math
import re
from collections import Counter
from typing import List, Dict

from backend.app.utils.embedding_utils import get_embedding, batch_get_embeddings, cosine_similarity


# 关键词重叠度
def _keyword_overlap_score(query: str, text: str) -> float:
    q_terms = set((query or '').lower().replace('>', ' ').split())
    t_terms = set((text or '').lower().replace('>', ' ').split())
    if not q_terms or not t_terms:
        return 0.0
    return len(q_terms & t_terms) / max(len(q_terms), 1)


# 改为BM25
def _tokenize(text: str) -> list[str]:
    text = (text or "").lower().replace(">", " ").replace("/", " ")
    return re.findall(r"[a-z0-9\u4e00-\u9fff]+", text)


def _bm25_score(query_tokens, tf, doc_len, avgdl, n_docs, df_map, k1=1.2, b=0.75):
    score = 0.0
    for t in query_tokens:
        f = tf.get(t, 0)
        if f <= 0:
            continue
        df = df_map.get(t, 0)
        idf = math.log(1.0 + (n_docs - df + 0.5) / (df + 0.5))
        denom = f + k1 * (1 - b + b * doc_len / max(avgdl, 1e-9))
        score += idf * (f * (k1 + 1) / max(denom, 1e-9))
    return score


# 类目混合排序，返回top3
def rank_categories_hybrid(query_text: str, category_list: List[Dict], top_k: int = 3) -> List[Dict]:
    if not category_list:
        return []

    query_tokens = _tokenize(query_text)
    doc_tokens_list = [_tokenize(item.get('category_path', '')) for item in category_list]

    n_docs = len(doc_tokens_list)
    avgdl = sum(len(toks) for toks in doc_tokens_list) / max(n_docs, 1)

    df_map = {}
    for toks in doc_tokens_list:
        for tok in set(toks):
            df_map[tok] = df_map.get(tok, 0) + 1

    bm25_raw_scores = []
    for toks in doc_tokens_list:
        tf = Counter(toks)
        bm25_raw_scores.append(
            _bm25_score(
                query_tokens=query_tokens,
                tf=tf,
                doc_len=len(toks),
                avgdl=avgdl,
                n_docs=n_docs,
                df_map=df_map,
            )
        )

    bm25_min = min(bm25_raw_scores) if bm25_raw_scores else 0.0
    bm25_max = max(bm25_raw_scores) if bm25_raw_scores else 0.0

    def _bm25_norm(v: float) -> float:
        if bm25_max - bm25_min < 1e-12:
            return 0.0
        return (v - bm25_min) / (bm25_max - bm25_min)


    query_embedding = get_embedding(query_text)
    category_texts = [item.get('category_path', '') for item in category_list]
    category_embeddings = batch_get_embeddings(category_texts)

    ranked = []
    for index, category in enumerate(category_list):
        path = category.get('category_path', '')
        emb_score = 0.0
        if query_embedding and index < len(category_embeddings) and category_embeddings[index]:
            emb_score = cosine_similarity(query_embedding, category_embeddings[index])

        # key_score = _keyword_overlap_score(query_text, path)
        # score = emb_score * 0.8 + key_score * 0.2

        bm25_raw = bm25_raw_scores[index]
        bm25_norm = _bm25_norm(bm25_raw)
        emb_norm = (emb_score + 1.0) / 2.0

        score = emb_score * 0.7 + bm25_norm * 0.3
        ranked.append({
            **category,
            'embedding_similarity': emb_norm,
            'keyword_score': bm25_raw,
            'score': score,
        })

    ranked.sort(key=lambda x: x.get('score', 0), reverse=True)
    return ranked[:top_k]
