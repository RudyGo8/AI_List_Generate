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


def shop_product_category(site, spu_image_url, sku_image_url_list, product_title, category_name, db_instance):
    try:
        system_obj = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='SYSTEM_COMMON_CATEGORY_STEP_ONE',
            enable=DataEnable.ON.value).first()

        system_shop_product_category = system_obj.prompt_value if system_obj else ""

        user_obj = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='USER_COMMON_CATEGORY_STEP_ONE',
            enable=DataEnable.ON.value).first()

        user_shop_product_category = user_obj.prompt_value if user_obj else "商品标题：%s\n原始类目：%s\n\n请根据图片和标题分析商品类型，给出最合适的类目路径。"

        title = product_title if product_title else ""
        cat = category_name if category_name else ""
        user_shop_product_category = user_shop_product_category % (title, cat)

        image_url_list = [spu_image_url]

        '''one step category'''
        category_path_by_ai, usage = chat_with_llm(image_url_list=image_url_list,
                                                   user_prompt=user_shop_product_category,
                                                   system_prompt=system_shop_product_category)

        if category_path_by_ai is not None:
            category_list = get_category_exchange(category_path_content=category_path_by_ai, site=site)

        else:
            category_list = [{"category_path": "General", "category_id": "DEFAULT"}]

        system_obj2 = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='SYSTEM_COMMON_CATEGORY_STEP_TWO',
            enable=DataEnable.ON.value).first()
        system_shop_product_category = system_obj2.prompt_value if system_obj2 else "你是一个电商类目分析专家。从候选类目列表中选择最合适的类目。"
        user_obj2 = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='USER_COMMON_CATEGORY_STEP_TWO',
            enable=DataEnable.ON.value).first()
        user_shop_product_category = user_obj2.prompt_value if user_obj2 else "商品标题：%s\n候选类目列表：%s\n\n请从以上候选类目中选择最合适的类目。"

        category_list_str = ""
        if category_list:
            for category in category_list:
                if not category_list_str:
                    category_list_str = category.get('category_path', '')
                else:
                    category_list_str = category_list_str + ', ' + category.get('category_path', '')

        '''two step category'''
        if category_list_str:
            try:
                system_shop_product_category = system_shop_product_category % (title, category_list_str)
            except:
                system_shop_product_category = f"商品标题：{title}\n候选类目：{category_list_str}\n请选择最合适的类目。"

            category_path_by_ai, usage = chat_with_llm(image_url_list=image_url_list,
                                                       user_prompt=user_shop_product_category,
                                                       system_prompt=system_shop_product_category)
            if category_path_by_ai is not None:
                category_list = get_category_exchange(category_path_content=category_path_by_ai, site=site)

        if not category_list:
            category_list = [{"category_path": "General", "category_id": "DEFAULT"}]

        logger.info(category_list)
        if category_list and len(category_list) > 0:
            return category_list[0], usage
        else:
            return {"category_path": "General", "category_id": "DEFAULT"}, usage
    except Exception as error:
        logger.error(error)
        return {"category_path": "General", "category_id": "DEFAULT"}, None


def shop_product_title(spu_image_url, sku_image_url_list, product_title, category_name, des_lang_type, db_instance):
    try:
        system_prompt_obj = db_instance.query(SysAiPrompt).filter_by(prompt_key='SYSTEM_SHOP_PRODUCT_TITLE',
                                                                     enable=DataEnable.ON.value).first()
        system_product_title = system_prompt_obj.prompt_value if system_prompt_obj else "你是一个Shop商品标题优化专家。根据商品图片和信息，生成符合Shop平台规范的优质商品标题。标题应该简洁、有吸引力，包含关键词。"

        user_prompt_obj = db_instance.query(SysAiPrompt).filter_by(prompt_key='USER_SHOP_PRODUCT_TITLE',
                                                                   enable=DataEnable.ON.value).first()
        user_product_title = user_prompt_obj.prompt_value if user_prompt_obj else "商品原标题：%s\n商品类目：%s\n目标语言：%s\n\n请根据图片和商品信息生成Shop商品标题。"

        # 处理 product_title 可能为 None 的情况
        title = product_title if product_title else ""
        cat = category_name if category_name else ""
        lang = des_lang_type if des_lang_type else "English"

        try:
            user_product_title = user_product_title % (title, cat, lang)
        except:
            user_product_title = f"商品标题：{title}\n类目：{cat}\n语言：{lang}\n请生成标题。"

        image_url_list = [spu_image_url]
        if sku_image_url_list and isinstance(sku_image_url_list, str):
            image_url_list.extend(sku_image_url_list.split(','))

        res, usage = chat_with_llm(image_url_list=image_url_list, user_prompt=user_product_title,
                                   system_prompt=system_product_title)
        return (res if res else "Generated Title"), usage
    except Exception as error:
        logger.error(error)
        return None, None


def shop_product_desc(spu_image_url, sku_image_url_list, product_title, category_name, des_lang_type, db_instance):
    try:
        system_prompt_obj = db_instance.query(SysAiPrompt).filter_by(prompt_key='SYSTEM_SHOP_PRODUCT_DESC',
                                                                     enable=DataEnable.ON.value).first()
        system_product_desc = system_prompt_obj.prompt_value if system_prompt_obj else "你是一个Shop商品描述撰写专家。根据商品图片和信息，生成详细、吸引人的商品描述，突出产品特点和卖点。"

        user_prompt_obj = db_instance.query(SysAiPrompt).filter_by(prompt_key='USER_SHOP_PRODUCT_DESC',
                                                                   enable=DataEnable.ON.value).first()
        user_product_desc = user_prompt_obj.prompt_value if user_prompt_obj else "商品标题：%s\n商品类目：%s\n目标语言：%s\n\n请根据图片和商品信息生成TikTokShop商品描述。"

        title = product_title if product_title else ""
        cat = category_name if category_name else ""
        lang = des_lang_type if des_lang_type else "English"

        try:
            user_product_desc = user_product_desc % (title, cat, lang)
        except:
            user_product_desc = f"商品标题：{title}\n类目：{cat}\n语言：{lang}\n请生成描述。"

        image_url_list = [spu_image_url]
        if sku_image_url_list and isinstance(sku_image_url_list, str):
            image_url_list.extend(sku_image_url_list.split(','))

        res, usage = chat_with_llm(image_url_list=image_url_list, user_prompt=user_product_desc,
                                   system_prompt=system_product_desc)
        return res if res else "Generated Description", usage
    except Exception as error:
        logger.error(error)
        return None, None


def shop_product_attributes(site, spu_image_url, sku_image_url_list, product_title,
                            category_id, category_name, product_desc, attributes, des_lang_type, db_instance):
    try:
        system_obj = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='SYSTEM_TIKTOKSHOP_PRODUCT_ATTRIBUTE',
            enable=DataEnable.ON.value).first()
        system_product_attributes = system_obj.prompt_value if system_obj else "你是一个电商属性专家。根据商品信息生成符合平台要求的商品属性。"

        user_obj = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='USER_TIKTOKSHOP_PRODUCT_ATTRIBUTE',
            enable=DataEnable.ON.value).first()
        user_product_attributes = user_obj.prompt_value if user_obj else "商品标题：%s\n商品类目：%s\n商品描述：%s\n原始属性：%s\n\n请生成商品属性。"

        # 简化处理，不依赖数据库类目属性配置
        try:
            user_product_attributes = user_product_attributes % (product_title or "", category_name or "", product_desc or "", str(attributes or ""))
        except Exception as e:
            user_product_attributes = f"商品标题：{product_title}\n商品类目：{category_name}\n请生成商品属性。"

        image_url_list = [spu_image_url]
        if sku_image_url_list and isinstance(sku_image_url_list, str):
            image_url_list.extend(sku_image_url_list.split(','))

        res, usage = chat_with_llm(image_url_list=image_url_list, user_prompt=user_product_attributes,
                                   system_prompt=system_product_attributes)
        return res, usage
    except Exception as error:
        logger.error(error)
        return None, None
