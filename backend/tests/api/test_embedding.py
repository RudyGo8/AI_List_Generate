# -*- coding: utf-8 -*-
"""
测试 Embedding 类目匹配功能
"""
from backend.app.utils.similar_utils import get_category_exchange
from backend.app.services.embedding_generator import get_shop_my_categories


def test_get_category_exchange():
    print("=" * 50)
    print("=" * 50)
    
    # 测试英文类目匹配
    result = get_category_exchange(
        category_path_content="Electronics > Mobile Phones",
        site="shop"
    )
    print(f"输入: Electronics > Mobile Phones, site=shop")
    print(f"输出: {result[:3]}")
    
    # 测试中文类目匹配
    result2 = get_category_exchange(
        category_path_content="电子 > 手机 > 智能手机",
        site="tiktok"
    )
    print(f"\n输入: 电子 > 手机 > 智能手机, site=shop")
    print(f"输出: {result2[:3]}")
    
    return result


def test_get_shop_my_categories():

    result = get_shop_my_categories(
        query_text="手机 > 智能手机",
        site="tiktok",
        top_k=3
    )
    print(f"输入: 手机 > 智能手机, site=tiktok, top_k=3")
    print(f"输出: {result}")
    
    return result


if __name__ == "__main__":
    try:
        test_get_category_exchange()
        test_get_shop_my_categories()
        print("\n" + "=" * 50)
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
