'''
@create_time: 2026/3/27 下午1:56
@Author: GeChao
@File: llm.py
'''
from backend.app.config import logger
from backend.app.database import get_db_instance
from backend.app.models.db_sys_conf import SysConf
from backend.app.models.constants import DataEnable, LLMType
from backend.app.utils.qwen_utils import ai_chat_qwen
from langsmith import traceable


def _get_enabled_conf_value(db, key: str):
    record = db.query(SysConf).filter_by(key=key, enable=DataEnable.ON.value).first()
    return record.value if record else None


def _get_route_model(db, task_type: str, scene: str = 'default'):
    """按任务分配路由"""
    try:
        from backend.app.models.db_ai_model_route import DbAiModelRoute

        route = db.query(DbAiModelRoute).filter_by(
            task_type=task_type,
            scene=scene,
            enable=DataEnable.ON.value
        ).first()

        if not route and scene != 'default':
            route = db.query(DbAiModelRoute).filter_by(
                task_type=task_type,
                scene='default',
                enable=DataEnable.ON.value
            ).first()

        if route:
            return {
                'llm_type': route.llm_type,
                'model_name': route.model_name,
            }
    except Exception as error:
        logger.info(f'route model unavailable, fallback to sys_conf: {error}')

    llm_type = _get_enabled_conf_value(db, 'LLM_TYPE') or LLMType.QWEN.value
    model_name = _get_enabled_conf_value(db, 'AI_MODEL_QWEN') if llm_type == LLMType.QWEN.value else None
    if not model_name:
        model_name = _get_enabled_conf_value(db, 'AI_MODEL_GEMINI')
    return {
        'llm_type': llm_type,
        'model_name': model_name or 'unknown-model',
    }


@traceable(name="chat_with_llm", run_type="chain")
def chat_with_llm(image_url_list, user_prompt, system_prompt=None, task_type='general', scene='default'):
    db = None
    try:
        db = next(get_db_instance())
        route_conf = _get_route_model(db, task_type=task_type, scene=scene)

        if route_conf.get('llm_type') == LLMType.QWEN.value:
            return ai_chat_qwen(
                image_url_list=image_url_list,
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                model_override=route_conf.get('model_name')
            )

        return ai_chat_qwen(
            image_url_list=image_url_list,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            model_override=route_conf.get('model_name')
        )
    except Exception as error:
        logger.error(error)
        return ai_chat_qwen(image_url_list=image_url_list, user_prompt=user_prompt, system_prompt=system_prompt)
    finally:
        if db:
            db.close()


def get_model_used(task_type='general', scene='default'):
    db = None
    try:
        db = next(get_db_instance())
        route_conf = _get_route_model(db, task_type=task_type, scene=scene)
        return route_conf.get('model_name', 'unknown-model')
    except Exception as error:
        logger.error(error)
    finally:
        if db:
            db.close()

    return 'unknown-model'
