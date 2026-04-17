'''
@create_time: 2026/4/16 下午10:01
@Author: GeChao
@File: langsmith_translate.py
'''
from langsmith import Client
from backend.app.services.text_generator import service_text_translate

client = Client()


def translate_target(inputs: dict) -> dict:
    text, usage = service_text_translate(
        des_lang_type=inputs["des_lang_type"],
        content=inputs["content"],
        scene=inputs.get("scene", "default"),
    )
    return {
        "translated_text": text or "",
        "usage": usage or {}
    }


if __name__ == "__main__":
    result = client.evaluate(
        translate_target,
        data="ai_list_generate_translate",
        experiment_prefix="translate-eval-v1",
    )
    print(result)
