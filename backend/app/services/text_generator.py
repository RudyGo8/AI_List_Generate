'''
@create_time: 2026/3/27 下午1:43
@Author: GeChao
@File: text_generator.py
'''
from backend.app.config import logger
from backend.app.database import get_db_instance
from backend.app.models.db_sys_ai_prompt import SysAiPrompt
from backend.app.models.constants import DataEnable
from backend.app.services.llm import chat_with_llm
from backend.app.utils.param_utils import extract_list
from langsmith import traceable


def _build_prompt_keys(prompt_key: str, scene: str = 'default'):
    if scene and scene != 'default':
        return [f"{prompt_key}__{scene.upper()}", prompt_key]
    return [prompt_key]


def _get_prompt_value(db_instance, prompt_key: str, scene: str = 'default'):
    for key in _build_prompt_keys(prompt_key, scene=scene):
        prompt_obj = db_instance.query(SysAiPrompt).filter_by(
            prompt_key=key,
            enable=DataEnable.ON.value
        ).first()
        if prompt_obj and prompt_obj.prompt_value:
            return prompt_obj.prompt_value
    return None


@traceable(name="service_text_translate", run_type="chain")
def service_text_translate(des_lang_type, content, scene='default') -> (str, dict):
    db_instance = next(get_db_instance())

    try:
        user_text_translate = _get_prompt_value(db_instance, 'USER_TEXT_TRANSLATE', scene=scene)
        system_text_translate = _get_prompt_value(db_instance, 'SYSTEM_TEXT_TRANSLATE', scene=scene)

        if not user_text_translate or not system_text_translate:
            logger.error('translate prompt not found in db_sys_ai_prompt')
            return None, None

        user_prompt = user_text_translate % (des_lang_type, content)

        return chat_with_llm(
            image_url_list=None,
            user_prompt=user_prompt,
            system_prompt=system_text_translate,
            task_type='translate',
            scene=scene,
        )
    except Exception as error:
        logger.error(error)
        return None, None
    finally:
        db_instance.close()


@traceable(name="service_batch_text_translate", run_type="chain")
def service_batch_text_translate(des_lang_type, content_list, scene='default') -> (list, dict):
    db_instance = next(get_db_instance())

    try:
        user_batch_text_translate = _get_prompt_value(db_instance, 'USER_BATCH_TEXT_TRANSLATE', scene=scene)
        system_text_translate = _get_prompt_value(db_instance, 'SYSTEM_BATCH_TEXT_TRANSLATE', scene=scene)

        if not user_batch_text_translate or not system_text_translate:
            logger.error('batch translate prompt not found in db_sys_ai_prompt')
            return None, None

        cleaned_list = [str(item).replace(',', '') for item in content_list]
        content_list_to_ai = '["' + '","'.join(cleaned_list) + '"]'

        user_prompt = user_batch_text_translate % (des_lang_type, content_list_to_ai)

        data_translated_str, usage = chat_with_llm(
            image_url_list=None,
            user_prompt=user_prompt,
            system_prompt=system_text_translate,
            task_type='batch_translate',
            scene=scene,
        )
        list_data = extract_list(data_translated_str) if data_translated_str else None
        return list_data, usage
    except Exception as error:
        logger.error(error)
        return None, None
    finally:
        db_instance.close()
