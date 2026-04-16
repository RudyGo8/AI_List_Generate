from backend.app.database import get_db_instance
from backend.app.models.db_sys_ai_prompt import SysAiPrompt
from backend.app.models.db_category import Category
from backend.app.services.llm import chat_with_llm
from backend.app.utils.embedding_utils import find_similar_categories


def get_shop_my_categories(query_text: str, site: str = 'tiktok', top_k: int = 5):
    """Return top-k similar categories for a site by embedding similarity."""
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
