'''
@create_time: 2026/3/27 下午4:44
@Author: GeChao
@File: multimodel_generator.py
'''
from backend.app.config import logger
from backend.app.database import get_db_instance
from backend.app.models.db_sys_ai_prompt import SysAiPrompt
from backend.app.models.constants import DataEnable
from backend.app.services.llm import chat_with_llm


def _get_ocr_prompt(db_instance, scene='default'):
    prompt_keys = ['SYSTEM_IMAGE_OCR']
    if scene and scene != 'default':
        prompt_keys = [f"SYSTEM_IMAGE_OCR__{scene.upper()}"] + prompt_keys

    for key in prompt_keys:
        prompt_record = db_instance.query(SysAiPrompt).filter_by(
            prompt_key=key,
            enable=DataEnable.ON.value
        ).first()
        if prompt_record and prompt_record.prompt_value:
            return prompt_record.prompt_value

    return None


def common_image_ocr(image_url_list, scene='default'):
    logger.info(f"OCR called with {len(image_url_list) if image_url_list else 0} images")
    db_instance = next(get_db_instance())
    try:
        system_image_ocr = _get_ocr_prompt(db_instance, scene=scene)

        if not system_image_ocr:
            logger.error("OCR prompt not found in database: SYSTEM_IMAGE_OCR")
            return None, None
        logger.info(f"Using OCR prompt: {system_image_ocr}")

        logger.info(f"Calling chat_with_llm with image_url_list: {image_url_list}")
        res, usage = chat_with_llm(
            image_url_list=image_url_list,
            user_prompt='',
            system_prompt=system_image_ocr,
            task_type='ocr',
            scene=scene,
        )
        logger.info(f"chat_with_llm returned: res={type(res)}, usage={usage}")

        if res is None:
            logger.error("OCR call returned None")
        else:
            logger.info(f"OCR result length: {len(res) if res else 0}")

        return res, usage

    except Exception as error:
        logger.error(f"OCR error: {error}")
        import traceback

        logger.error(traceback.format_exc())
        return None, None
    finally:
        db_instance.close()
