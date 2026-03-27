'''
@create_time: 2026/3/27 下午1:43
@Author: GeChao
@File: text_generator.py
'''
from app.config import logger
from app.database import get_db_instance
from app.models.db_sys_ai_prompt import SysAiPrompt
from app.models.constants import DataEnable
from app.services.llm import chat_with_llm


def service_text_translate(des_lang_type, content):
    db_instance = next(get_db_instance())

    try:
        user_text_translate = db_instance.query(SysAiPrompt).filter_by(
            prompt_key = 'USER_TEXT_TRANSLATE',
            enable=DataEnable.ON.value).first().prompt_value

        system_text_translate = db_instance.query(SysAiPrompt).filter_by(
            prompt_key = 'SYSTEM_TEXT_TRANSLATE',
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


