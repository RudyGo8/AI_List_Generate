'''
@create_time: 2026/4/17 下午4:21
@Author: GeChao
@File: langsmith_shop_step2.py.py
'''
import json
from langsmith import evaluate
from backend.app.database import get_db_instance
from backend.app.services.shop import shop_product_category_step2

DATASET_NAME = "ai_list_generate_shop_step2_eval"

def _to_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return [x.strip() for x in text.split(",") if x.strip()]
    return []


def _norm_text(text: str) -> str:
    return str(text or "").strip().lower()


def _norm_path(path: str) -> str:
    # 统一分隔符、空格、大小写
    text = str(path or "").strip().lower()
    text = text.replace(" / ", ">").replace("/", ">")
    parts = [p.strip() for p in text.split(">") if p.strip()]
    return " > ".join(parts)


def target_step2(inputs: dict) -> dict:
    db = next(get_db_instance())
    try:
        result, raw_path, _usage = shop_product_category_step2(
            site=inputs.get("site", ""),
            product_title=inputs.get("product_title", ""),
            candidate_category_paths=_to_list(inputs.get("candidate_category_paths")),
            db_instance=db,
            scene=inputs.get("scene", "default"),
        )
        return {
            "pred_category_id": str(result.get("category_id", "DEFAULT")),
            "pred_category_path": result.get("category_path", "General"),
            "raw_step2_category_path": raw_path or "",
            "top3_candidates": result.get("top3_candidates", []),
        }
    finally:
        db.close()


# 匹配id
def category_id_exact_match(outputs: dict, reference_outputs: dict) -> dict:
    pred_id = _norm_text(outputs.get("pred_category_id"))
    ref_id = _norm_text(reference_outputs.get("ref_step2_category_id"))
    score = 1 if pred_id and ref_id and pred_id == ref_id else 0
    return {"key": "category_id_exact_match", "score": score}


# 比较预测路径和标准路径是否文本完全一致
def category_path_exact_match(outputs: dict, reference_outputs: dict) -> dict:
    pred_path = _norm_text(outputs.get("pred_category_path"))
    gold_path = _norm_text(reference_outputs.get("ref_step2_category_path"))
    score = 1 if pred_path and gold_path and pred_path == gold_path else 0
    return {"key": "category_path_exact_match", "score": score}


# 归一化对比
def category_path_normalized_match(outputs: dict, reference_outputs: dict) -> dict:
    pred_path = _norm_path(outputs.get("pred_category_path"))
    gold_path = _norm_path(reference_outputs.get("ref_step2_category_path"))
    score = 1 if pred_path and gold_path and pred_path == gold_path else 0
    return {"key": "category_path_normalized_match", "score": score}


# 召回率
def step2_recall_at_3(outputs: dict, reference_outputs: dict) -> dict:
    ref_id = _norm_text(reference_outputs.get("ref_step2_category_id"))
    top3 = outputs.get("top3_candidates") or []

    top3_ids = [str(item.get("category_id", "")).strip().lower() for item in top3[:3]]
    score = 1 if ref_id and ref_id in top3_ids else 0
    return {"key": "step2_recall_at_3", "score": score}


# 分差对比
def step2_top1_top2_margin(outputs: dict, reference_outputs: dict = None) -> dict:
    top3 = outputs.get("top3_candidates") or []
    if len(top3) < 2:
        return {"key": "step2_top1_top2_margin", "score": 0.0}

    def _to_float(v):
        try:
            return float(v)
        except Exception:
            return 0.0

    s1 = _to_float(top3[0].get("score"))
    s2 = _to_float(top3[1].get("score"))
    margin = s1 - s2
    return {"key": "step2_top1_top2_margin", "score": margin}


if __name__ == "__main__":
    evaluate(
        target_step2,
        data=DATASET_NAME,
        evaluators=[
            category_id_exact_match,
            category_path_exact_match,
            category_path_normalized_match,
            step2_recall_at_3,
            step2_top1_top2_margin,
        ],
        experiment_prefix="ai_list_generate_shop_step2_eval_experiment",
        metadata={"task": "shop_category", "step": "step2"},
        max_concurrency=4,
        blocking=True,
    )
