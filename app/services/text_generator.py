'''
@create_time: 2026/3/27 下午1:43
@Author: GeChao
@File: text_generator.py
'''
import json
from app.config import logger
from app.database import get_db_instance
from app.models.db_sys_ai_prompt import SysAiPrompt
from app.models.constants import DataEnable
from app.services.llm import chat_with_llm
from app.utils.param_utils import extract_list


def service_text_translate(des_lang_type, content) -> (str, dict):
    db_instance = next(get_db_instance())

    try:
        user_text_translate = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='USER_TEXT_TRANSLATE',
            enable=DataEnable.ON.value).first().prompt_value

        system_text_translate = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='SYSTEM_TEXT_TRANSLATE',
            enable=DataEnable.ON.value).first().prompt_value

        user_category_tiktok = user_text_translate % (des_lang_type, content)

        return chat_with_llm(image_url_list=None,
                             user_prompt=user_category_tiktok,
                             system_prompt=system_text_translate)
    except Exception as error:
        logger.error(error)
        return None, None
    finally:
        db_instance.close()


def service_batch_text_translate(des_lang_type, content_list) -> (list, dict):
    db_instance = next(get_db_instance())

    try:
        user_batch_text_translate = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='USER_BATCH_TEXT_TRANSLATE',
            enable=DataEnable.ON.value).first().prompt_value

        system_text_translate = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='SYSTEM_BATCH_TEXT_TRANSLATE',
            enable=DataEnable.ON.value).first().prompt_value

        # 处理内容格式
        cleaned_list = [item.replace(',', '') for item in content_list]
        content_list_to_ai = ",".join(cleaned_list)
        content_list_to_ai = "[\"" + content_list_to_ai.replace(",", "\",\"") + "\"]"

        user_batch_text_translate = user_batch_text_translate % (des_lang_type, content_list_to_ai)

        data_translated_str, usage = chat_with_llm(image_url_list=None,
                                                   user_prompt=user_batch_text_translate,
                                                   system_prompt=system_text_translate)
        list_data = extract_list(data_translated_str)
        return list_data, usage
    except Exception as error:
        logger.error(error)
        return None, None
    finally:
        db_instance.close()
