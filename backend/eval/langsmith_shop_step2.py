'''
@create_time: 2026/4/17 下午4:21
@Author: GeChao
@File: langsmith_shop_step2.py.py
'''
from langsmith import evaluate
from backend.app.database import get_db_instance
from backend.app.services.shop import shop_product_category_step2
from backend.app.utils.str_text_utils import to_list, norm_text, norm_path, to_float

DATASET_NAME = "ai_list_generate_shop_step2_eval"


def target_step2(inputs: dict) -> dict:
    db = next(get_db_instance())
    try:
        result, raw_path, _usage = shop_product_category_step2(
            site=inputs.get("site", ""),
            product_title=inputs.get("product_title", ""),
            candidate_category_paths=to_list(inputs.get("candidate_category_paths")),
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


# id 匹配
def category_id_exact_match(outputs: dict, reference_outputs: dict) -> dict:
    pred_id = norm_text(outputs.get("pred_category_id"))
    ref_id = norm_text(reference_outputs.get("ref_step2_category_id"))
    score = 1 if pred_id and ref_id and pred_id == ref_id else 0
    return {"key": "category_id_exact_match", "score": score}


# 归一化对比
def category_path_normalized_match(outputs: dict, reference_outputs: dict) -> dict:
    pred_path = norm_path(outputs.get("pred_category_path"))
    gold_path = norm_path(reference_outputs.get("ref_step2_category_path"))
    score = 1 if pred_path and gold_path and pred_path == gold_path else 0
    return {"key": "category_path_normalized_match", "score": score}


# 召回率
def step2_recall_at_3(outputs: dict, reference_outputs: dict) -> dict:
    ref_id = norm_text(reference_outputs.get("ref_step2_category_id"))
    top3 = outputs.get("top3_candidates") or []

    top3_ids = [str(item.get("category_id", "")).strip().lower() for item in top3[:3]]
    score = 1 if ref_id and ref_id in top3_ids else 0
    return {"key": "step2_recall_at_3", "score": score}


if __name__ == "__main__":
    evaluate(
        target_step2,
        data=DATASET_NAME,
        evaluators=[
            category_id_exact_match,
            category_path_normalized_match,
            step2_recall_at_3,
        ],
        experiment_prefix="ai_list_generate_shop_step2_eval_experiment",
        metadata={"task": "shop_category", "step": "step2"},
        max_concurrency=4,
        blocking=True,
    )
