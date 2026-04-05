'''
@create_time: 2026/3/28 下午2:06
@Author: GeChao
@File: similar_utils.py
'''
from app.database import get_db_instance
from app.models.db_category import Category
from app.services.category_matcher import rank_categories_hybrid


def get_category_exchange(category_path_content, platform_id=None, site='shop_test'):

    """Get similar categories for the given category path content"""

    db = next(get_db_instance())
    try:
        all_categories = db.query(Category).filter(
            Category.site == site,
            Category.enable == 1
        ).all()

        if not all_categories:
            return [{"category_path": category_path_content, "category_id": "DEFAULT"}]

        category_list = [
            {'category_path': cat.category_path, 'category_id': cat.category_id}
            for cat in all_categories
        ]

        similar_categories = rank_categories_hybrid(
            query_text=category_path_content,
            category_list=category_list,
            top_k=3
        )

        if not similar_categories:
            return [{"category_path": category_path_content, "category_id": "DEFAULT"}]

        return similar_categories

    except Exception as e:
        print(f"get_category_exchange error: {e}")
        return [{"category_path": category_path_content, "category_id": "DEFAULT"}]
    finally:
        db.close()
