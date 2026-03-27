'''
@create_time: 2026/3/27 下午4:44
@Author: GeChao
@File: multimodel_generator.py
'''
from app.config import logger
from app.database import get_db_instance
from app.models.db_sys_ai_prompt import SysAiPrompt
from app.models.constants import DataEnable
from app.services.llm import chat_with_llm


def common_image_ocr(image_url_list):
    logger.info(f"OCR called with {len(image_url_list) if image_url_list else 0} images")
    db_instance = next(get_db_instance())
    try:
        prompt_record = db_instance.query(SysAiPrompt).filter_by(
            prompt_key='SYSTEM_IMAGE_OCR',
            enable=DataEnable.ON.value).first()

        if not prompt_record:
            logger.error("OCR prompt not found in database: SYSTEM_IMAGE_OCR")
            return None, None
        system_image_ocr = prompt_record.prompt_value
        logger.info(f"Using OCR prompt: {system_image_ocr}")

        logger.info(f"Calling chat_with_llm with image_url_list: {image_url_list}")
        res, usage = chat_with_llm(image_url_list=image_url_list, user_prompt='',
                                   system_prompt=system_image_ocr)
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