'''
@create_time: 2026/4/17 上午10:48
@Author: GeChao
@File: langsmith_shop_step1.py
'''
from langsmith import evaluate, Client
from backend.app.database import get_db_instance
from backend.app.services.shop import shop_product_category_step1

client = Client()
dataset_name = "ai_list_generate_shop_step1_eval"


# 数据集里的字段传给你的一级类目预测函数，得到 3 个返回值
def target_step1(inputs: dict) -> dict:
    db = next(get_db_instance())
    try:
        candidates, raw_path, usage = shop_product_category_step1(
            site=inputs.get("site", ""),
            spu_image_url=inputs.get("spu_image_url"),
            sku_image_url_list=inputs.get("sku_image_url_list"),
            product_title=inputs.get("product_title", ""),
            category_name="",
            db_instance=db,
            scene=inputs.get("scene", "default"),
        )
        top1 = candidates[0] if candidates else {"category_id": "DEFAULT", "category_path": "General"}
        return {
            "pred_category_id": str(top1.get("category_id", "DEFAULT")),
            "pred_category_path": top1.get("category_path", "General"),
            "candidate_ids": [str(c.get("category_id", "")) for c in candidates[:3]],
            "raw_step1_category_path": raw_path or "",
        }
    finally:
        db.close()


# 预测路径是否和标注路径完全一致
def exact_match(inputs, outputs, reference_outputs):
    pred = (outputs.get("pred_category_path") or "").strip().lower()
    ref = (reference_outputs.get("ref_step1_category_path") or "").strip().lower()
    return pred == ref


# 按层级比较，算前缀命中率
def level_score(inputs, outputs, reference_outputs):
    pred = [x.strip().lower() for x in (outputs.get("pred_category_path") or "").split(">") if x.strip()]
    ref = [x.strip().lower() for x in (reference_outputs.get("ref_step1_category_path") or "").split(">") if x.strip()]
    if not ref:
        return 0.0
    hit = 0
    for p, r in zip(pred, ref):
        if p == r:
            hit += 1
        else:
            break
    return hit / len(ref)


# Top1 准确率
def top1_id_exact_match(inputs, outputs, reference_outputs):
    pred_id = str(outputs.get("pred_category_id") or "").strip().lower()
    ref_id = str(reference_outputs.get("ref_step1_category_id") or "").strip().lower()
    return bool(pred_id and ref_id and pred_id == ref_id)


# 正确答案的类目 ID 有没有出现在 Top3 候选里
def top3_hit(inputs, outputs, reference_outputs):
    ref_id = str(reference_outputs.get("ref_step1_category_id") or "").strip()
    candidate_ids = [str(x).strip() for x in (outputs.get("candidate_ids") or [])]
    if not ref_id:
        return False
    return ref_id in candidate_ids


# 原始生成路径不为空
def raw_path_non_empty(inputs, outputs, reference_outputs):
    return bool((outputs.get("raw_step1_category_path") or "").strip())


if __name__ == "__main__":
    results = evaluate(
        target_step1,
        data=dataset_name,
        evaluators=[exact_match, level_score, top3_hit,
                    raw_path_non_empty,
                    top1_id_exact_match],
        experiment_prefix="ai_list_generate_shop_step1_eval_experiment",
        max_concurrency=10,
        blocking=True,
    )
    print(results)
# evaluate(
#     target_step1,
#     data=dataset_name,
#     evaluators=[exact_match, level_score],
#     experiment_prefix="ai_list_generate_shop_step1_eval experiment"
# )
