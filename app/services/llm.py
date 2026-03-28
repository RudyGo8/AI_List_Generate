'''
@create_time: 2026/3/27 下午1:56
@Author: GeChao
@File: llm.py
'''
from app.config import logger
from app.database import get_db_instance
from app.models.db_sys_conf import SysConf
from app.models.constants import DataEnable, LLMType
from app.utils.qwen_utils import ai_chat_qwen


def chat_with_llm(image_url_list, user_prompt, system_prompt=None):
    db = next(get_db_instance())

    try:
        LLM_Model = db.query(SysConf).filter_by(key='LLM_TYPE', enable=DataEnable.ON.value).first().value

        if LLM_Model == LLMType.QWEN.value:
            return ai_chat_qwen(image_url_list=image_url_list, user_prompt=user_prompt, system_prompt=system_prompt)
        ''' else model '''
    except Exception as e:
        logger.error(e)
        return ai_chat_qwen(image_url_list=image_url_list, user_prompt=user_prompt, system_prompt=system_prompt)
    finally:
        db.close()


def get_model_used():
    db = next(get_db_instance())
    try:
        LLM_MODEL = db.query(SysConf).filter_by(key='LLM_TYPE', enable=DataEnable.ON.value).first().value
        if LLM_MODEL == LLMType.QWEN.value:
            return db.query(SysConf).filter_by(key='AI_MODEL_QWEN', enable=1).first().value

    except Exception as error:
        logger.error(error)
        return db.query(SysConf).filter_by(key='AI_MODEL_GEMINI', enable=1).first().value
    finally:
        db.close()
