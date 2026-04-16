from app.database import get_db_instance
from app.models.db_sys_ai_prompt import SysAiPrompt
from app.models.db_category import Category
from app.services.llm import chat_with_llm
from app.utils.embedding_utils import find_similar_categories


def get_shop_my_categories(query_text: str, site: str = 'tiktok', top_k: int = 5):
    """
    通过 embedding 相似度匹配获取目标站点的类目

    Args:
        query_text: 查询文本（如 AI 识别的类目路径）
        site: 站点标识，如 'tiktok', 'shopee_vn', 'shopee_id' 等
        top_k: 返回前 k 个最相似的类目

    Returns:
        List[Dict]: 相似类目列表，包含 category_path, category_id, similarity
    """
    db = next(get_db_instance())
    try:
        all_categories = db.query(Category).filter(
            Category.site == site,
            Category.enable == 1
        ).all()

        if not all_categories:
            return []

        category_list = [
            {'category_path': cat.category_path, 'category_id': cat.category_id}
            for cat in all_categories
        ]

        similar_categories = find_similar_categories(query_text, category_list, top_k=top_k)

        return similar_categories
    except Exception as e:
        print(f"get_tiktokshop_my_categories error: {e}")
        return []
    finally:
        db.close()
