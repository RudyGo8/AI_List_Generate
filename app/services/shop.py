'''
@create_time: 2026/3/28 下午2:00
@Author: GeChao
@File: shop.py
'''
import json

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
                image_url_list=None,
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


def _extract_json_payload(raw_text):
    if not raw_text:
        return None
    if isinstance(raw_text, dict):
        return raw_text

    text = str(raw_text).strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        try:
            return json.loads(text[start_idx:end_idx + 1])
        except Exception:
            return None
    return None


def shop_product_bundle_text_only(product_title, category_name, attributes, des_lang_type, db_instance, scene='default'):
    """
    One-call generation for title/description/attributes.
    Text-only by design to reduce latency and image-token cost.
    """
    try:
        system_prompt = _get_prompt(
            db_instance,
            ['SYSTEM_SHOP_PRODUCT_BUNDLE', 'SYSTEM_TIKTOKSHOP_PRODUCT_BUNDLE'],
            "You are an ecommerce listing expert. Generate title, description and attributes in JSON only.",
            scene=scene
        )
        user_prompt_tpl = _get_prompt(
            db_instance,
            ['USER_SHOP_PRODUCT_BUNDLE', 'USER_TIKTOKSHOP_PRODUCT_BUNDLE'],
            (
                "Original title: %s\nCategory: %s\nLanguage: %s\nOriginal attributes: %s\n\n"
                "Return strict JSON with keys: product_title, product_desc, attributes."
            ),
            scene=scene
        )

        title = product_title or ""
        cat = category_name or ""
        lang = des_lang_type or "English"
        attrs = str(attributes or "")
        try:
            user_prompt = user_prompt_tpl % (title, cat, lang, attrs)
        except Exception:
            user_prompt = (
                f"Original title: {title}\nCategory: {cat}\nLanguage: {lang}\nOriginal attributes: {attrs}\n"
                "Return strict JSON with keys: product_title, product_desc, attributes."
            )

        raw_text, usage = chat_with_llm(
            image_url_list=None,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            task_type='shop_desc',
            scene=scene,
        )

        data = _extract_json_payload(raw_text) or {}
        product_title_out = data.get('product_title') or data.get('title') or "Generated Title"
        product_desc_out = data.get('product_desc') or data.get('description') or "Generated Description"
        attributes_out = data.get('attributes')
        if attributes_out is None:
            attributes_out = "{}"

        if isinstance(attributes_out, (dict, list)):
            attributes_out = json.dumps(attributes_out, ensure_ascii=False)
        else:
            attributes_out = str(attributes_out)

        return {
            "product_title": str(product_title_out),
            "product_desc": str(product_desc_out),
            "attributes": attributes_out,
        }, usage
    except Exception as error:
        logger.error(error)
        return None, None
