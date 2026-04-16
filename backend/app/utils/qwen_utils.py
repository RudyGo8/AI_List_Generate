'''
@create_time: 2026/3/27 下午2:05
@Author: GeChao
@File: qwen_utils.py
'''
from openai import OpenAI

from app.config import logger
from app.database import get_db_instance
from app.models.db_sys_conf import SysConf
from app.models.constants import DataEnable

''' 调用qwen模型 '''


def ai_chat_qwen(image_url_list, user_prompt, system_prompt=None, model_override=None) -> (str, dict):
    db = None
    try:
        db = next(get_db_instance())

        ai_model_qwen = model_override or db.query(SysConf).filter_by(
            key='AI_MODEL_QWEN',
            enable=DataEnable.ON.value
        ).first().value
        ai_base_url_qwen = db.query(SysConf).filter_by(key='AI_BASE_URL_QWEN', enable=DataEnable.ON.value).first().value
        ai_api_key_qwen = db.query(SysConf).filter_by(key='AI_APIKEY_QWEN', enable=DataEnable.ON.value).first().value

        client = OpenAI(
            api_key=ai_api_key_qwen,
            base_url=ai_base_url_qwen
        )

        user_content = []
        message = []

        if system_prompt:
            message.append({"role": "system", "content": [{"type": "text", "text": system_prompt}]})

        if image_url_list:
            for image_url in image_url_list:
                url_str = str(image_url) if not isinstance(image_url, str) else image_url
                user_content.append(
                    {"type": "image_url", "image_url": {"url": url_str}}
                )

        user_content.append({"type": "text", "text": user_prompt})
        message.append({"role": "user", "content": user_content})

        completion = client.chat.completions.create(
            model=ai_model_qwen,
            messages=message
        )

        usage_dict = {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens
        }

        return completion.choices[0].message.content, usage_dict

    except Exception as error:
        logger.error(f"ai_chat_qwen error: {error}")
        return None, None

    finally:
        if db:
            db.close()
