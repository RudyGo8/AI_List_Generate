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


# 分词：字符串转列表
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


def _rank_by_score(scores: List[float | None]) -> Dict[int, int]:
    ranked_items = [
        (index, score) for index, score in enumerate(scores) if score is not None
    ]
    ranked_items.sort(key=lambda item: item[1], reverse=True)
    return {index: rank for rank, (index, _) in enumerate(ranked_items, start=1)}


def _rrf_score(ranks: List[int | None], k: int = 60) -> float:
    return sum(1.0 / (k + rank) for rank in ranks if rank is not None)


# 混合检索
def rank_categories_hybrid(query_text: str, category_list: List[Dict], top_k: int = 3) -> List[Dict]:
    if not category_list:
        return []

    query_tokens = _tokenize(query_text)
    doc_tokens_list = [_tokenize(item.get('category_path', '')) for item in category_list]

    n_docs = len(doc_tokens_list)
    # 平均每个分类路径分词后的长度
    avg_doc_len = sum(len(toks) for toks in doc_tokens_list) / max(n_docs, 1)

    # DF 文档频率：一个词出现在多少个分类里
    df_map = {}
    for toks in doc_tokens_list:
        for tok in set(toks):
            df_map[tok] = df_map.get(tok, 0) + 1

    # BM25 分数
    bm25_raw_scores = []
    for toks in doc_tokens_list:
        # 统计词频
        tf = Counter(toks)
        bm25_raw_scores.append(
            _bm25_score(
                query_tokens=query_tokens,
                tf=tf,
                doc_len=len(toks),
                avgdl=avg_doc_len,
                n_docs=n_docs,
                df_map=df_map,
            )
        )

    query_embedding = get_embedding(query_text)
    category_texts = [item.get('category_path', '') for item in category_list]
    category_embeddings = batch_get_embeddings(category_texts)

    embedding_raw_scores = []
    for index, _category in enumerate(category_list):
        emb_score = None
        if query_embedding and index < len(category_embeddings) and category_embeddings[index]:
            emb_score = cosine_similarity(query_embedding, category_embeddings[index])
        embedding_raw_scores.append(emb_score)

    bm25_ranks = _rank_by_score(bm25_raw_scores)
    embedding_ranks = _rank_by_score(embedding_raw_scores)

    ranked = []
    for index, category in enumerate(category_list):
        emb_score = embedding_raw_scores[index]

        # key_score = _keyword_overlap_score(query_text, path)
        # score = emb_score * 0.8 + key_score * 0.2

        bm25_raw = bm25_raw_scores[index]
        emb_norm = (emb_score + 1.0) / 2.0 if emb_score is not None else 0.0

        bm25_rank = bm25_ranks.get(index)
        embedding_rank = embedding_ranks.get(index)
        score = _rrf_score([embedding_rank, bm25_rank])

        ranked.append({
            **category,
            'embedding_similarity': emb_norm,
            'keyword_score': bm25_raw,
            'embedding_rank': embedding_rank,
            'keyword_rank': bm25_rank,
            'score': score,
        })

    ranked.sort(key=lambda x: x.get('score', 0), reverse=True)
    return ranked[:top_k]


if __name__ == '__main__':
    list = "abcd>1,1/,2//"
    print(f"list: {list}")
    new_list =_tokenize(list)
    print(f"new_list: {new_list}")
