'''
@create_time: 2026/3/28 下午2:00
@Author: GeChao
@File: shop.py
'''
from app.config import logger
from app.models.constants import DataEnable
from app.models.db_sys_ai_prompt import SysAiPrompt
from app.services.llm import chat_with_llm
from app.utils.similar_utils import get_category_exchange


def _expand_prompt_keys(prompt_keys, scene='default'):
    if isinstance(prompt_keys, str):
        prompt_keys = [prompt_keys]

    if not scene or scene == 'default':
        return prompt_keys

    expanded = []
    for key in prompt_keys:
        expanded.append(f"{key}__{scene.upper()}")
        expanded.append(key)
    return expanded


def _get_prompt(db_instance, prompt_keys, default_value, scene='default'):
    resolved_keys = _expand_prompt_keys(prompt_keys, scene=scene)

    for key in resolved_keys:
        prompt_obj = db_instance.query(SysAiPrompt).filter_by(
            prompt_key=key,
            enable=DataEnable.ON.value
        ).first()
        if prompt_obj and prompt_obj.prompt_value:
            return prompt_obj.prompt_value

    return default_value


def _build_image_url_list(spu_image_url, sku_image_url_list):
    image_url_list = [spu_image_url]
    if sku_image_url_list and isinstance(sku_image_url_list, str):
        image_url_list.extend([url for url in sku_image_url_list.split(',') if url])
    return image_url_list


def shop_product_category(site, spu_image_url, sku_image_url_list, product_title, category_name, db_instance, scene='default'):
    try:
        system_step_one = _get_prompt(
            db_instance,
            'SYSTEM_COMMON_CATEGORY_STEP_ONE',
            "You are an ecommerce category expert. Identify the best category path for this product.",
            scene=scene
        )
        user_step_one_tpl = _get_prompt(
            db_instance,
            'USER_COMMON_CATEGORY_STEP_ONE',
            "Product title: %s\nOriginal category: %s\n\nReturn a category path only.",
            scene=scene
        )

        title = product_title or ""
        cat = category_name or ""
        try:
            user_step_one = user_step_one_tpl % (title, cat)
        except Exception:
            user_step_one = f"Product title: {title}\nOriginal category: {cat}\nReturn a category path only."

        image_url_list = _build_image_url_list(spu_image_url, sku_image_url_list)
        category_path_by_ai, usage = chat_with_llm(
            image_url_list=image_url_list,
            user_prompt=user_step_one,
            system_prompt=system_step_one,
            task_type='shop_category',
            scene=scene,
        )

        if category_path_by_ai:
            category_list = get_category_exchange(category_path_content=category_path_by_ai, site=site)
        else:
            category_list = [{"category_path": "General", "category_id": "DEFAULT"}]

        system_step_two = _get_prompt(
            db_instance,
            'SYSTEM_COMMON_CATEGORY_STEP_TWO',
            "You are an ecommerce category expert. Pick the best match from candidates.",
            scene=scene
        )
        user_step_two_tpl = _get_prompt(
            db_instance,
            'USER_COMMON_CATEGORY_STEP_TWO',
            "Product title: %s\nCandidate categories: %s\n\nReturn the best category path only.",
            scene=scene
        )

        category_list_str = ", ".join([item.get('category_path', '') for item in category_list if item.get('category_path')])
        if category_list_str:
            try:
                user_step_two = user_step_two_tpl % (title, category_list_str)
            except Exception:
                user_step_two = f"Product title: {title}\nCandidate categories: {category_list_str}\nReturn the best category path only."

            category_path_by_ai_step2, usage_step2 = chat_with_llm(
                image_url_list=image_url_list,
                user_prompt=user_step_two,
                system_prompt=system_step_two,
                task_type='shop_category',
                scene=scene,
            )
            usage = usage_step2 if usage_step2 else usage
            if category_path_by_ai_step2:
                category_list = get_category_exchange(category_path_content=category_path_by_ai_step2, site=site)

        if not category_list:
            category_list = [{"category_path": "General", "category_id": "DEFAULT"}]

        logger.info(category_list)
        return category_list[0], usage
    except Exception as error:
        logger.error(error)
        return {"category_path": "General", "category_id": "DEFAULT"}, None


def shop_product_title(spu_image_url, sku_image_url_list, product_title, category_name, des_lang_type, db_instance, scene='default'):
    try:
        system_product_title = _get_prompt(
            db_instance,
            ['SYSTEM_SHOP_PRODUCT_TITLE', 'SYSTEM_TIKTOKSHOP_PRODUCT_TITLE'],
            "You are an ecommerce title expert. Generate a concise and searchable product title.",
            scene=scene
        )
        user_product_title_tpl = _get_prompt(
            db_instance,
            ['USER_SHOP_PRODUCT_TITLE', 'USER_TIKTOKSHOP_PRODUCT_TITLE'],
            "Original title: %s\nCategory: %s\nLanguage: %s\n\nGenerate a product title.",
            scene=scene
        )

        title = product_title or ""
        cat = category_name or ""
        lang = des_lang_type or "English"

        try:
            user_product_title = user_product_title_tpl % (title, cat, lang)
        except Exception:
            user_product_title = f"Original title: {title}\nCategory: {cat}\nLanguage: {lang}\nGenerate a product title."

        image_url_list = _build_image_url_list(spu_image_url, sku_image_url_list)
        res, usage = chat_with_llm(
            image_url_list=image_url_list,
            user_prompt=user_product_title,
            system_prompt=system_product_title,
            task_type='shop_title',
            scene=scene,
        )
        return (res if res else "Generated Title"), usage
    except Exception as error:
        logger.error(error)
        return None, None


def shop_product_desc(spu_image_url, sku_image_url_list, product_title, category_name, des_lang_type, db_instance, scene='default'):
    try:
        system_product_desc = _get_prompt(
            db_instance,
            ['SYSTEM_SHOP_PRODUCT_DESC', 'SYSTEM_TIKTOKSHOP_PRODUCT_DESC'],
            "You are an ecommerce copywriter. Generate a detailed and persuasive product description.",
            scene=scene
        )
        user_product_desc_tpl = _get_prompt(
            db_instance,
            ['USER_SHOP_PRODUCT_DESC', 'USER_TIKTOKSHOP_PRODUCT_DESC'],
            "Product title: %s\nCategory: %s\nLanguage: %s\n\nGenerate a product description.",
            scene=scene
        )

        title = product_title or ""
        cat = category_name or ""
        lang = des_lang_type or "English"

        try:
            user_product_desc = user_product_desc_tpl % (title, cat, lang)
        except Exception:
            user_product_desc = f"Product title: {title}\nCategory: {cat}\nLanguage: {lang}\nGenerate a product description."

        image_url_list = _build_image_url_list(spu_image_url, sku_image_url_list)
        res, usage = chat_with_llm(
            image_url_list=image_url_list,
            user_prompt=user_product_desc,
            system_prompt=system_product_desc,
            task_type='shop_desc',
            scene=scene,
        )
        return (res if res else "Generated Description"), usage
    except Exception as error:
        logger.error(error)
        return None, None


def shop_product_attributes(site, spu_image_url, sku_image_url_list, product_title,
                            category_id, category_name, product_desc, attributes, des_lang_type, db_instance, scene='default'):
    try:
        system_product_attributes = _get_prompt(
            db_instance,
            ['SYSTEM_TIKTOKSHOP_PRODUCT_ATTRIBUTE', 'SYSTEM_SHOP_PRODUCT_ATTRIBUTE'],
            "You are an ecommerce attribute expert. Generate structured product attributes.",
            scene=scene
        )
        user_product_attributes_tpl = _get_prompt(
            db_instance,
            ['USER_TIKTOKSHOP_PRODUCT_ATTRIBUTE', 'USER_SHOP_PRODUCT_ATTRIBUTE'],
            "Product title: %s\nCategory: %s\nDescription: %s\nOriginal attributes: %s\n\nGenerate attributes.",
            scene=scene
        )

        try:
            user_product_attributes = user_product_attributes_tpl % (
                product_title or "",
                category_name or "",
                product_desc or "",
                str(attributes or "")
            )
        except Exception:
            user_product_attributes = (
                f"Product title: {product_title or ''}\nCategory: {category_name or ''}\n"
                f"Description: {product_desc or ''}\nOriginal attributes: {str(attributes or '')}\nGenerate attributes."
            )

        image_url_list = _build_image_url_list(spu_image_url, sku_image_url_list)
        res, usage = chat_with_llm(
            image_url_list=image_url_list,
            user_prompt=user_product_attributes,
            system_prompt=system_product_attributes,
            task_type='shop_attribute',
            scene=scene,
        )
        return res, usage
    except Exception as error:
        logger.error(error)
        return None, None
