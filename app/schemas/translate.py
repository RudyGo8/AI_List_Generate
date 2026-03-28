'''
@create_time: 2026/3/27 下午1:38
@Author: GeChao
@File: translate.py
'''
from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    des_lang_type: str = Field(..., description="Language Type")
    content: str = Field(..., description="Translated Text")


class BatchTranslateRequest(BaseModel):
    des_lang_type: str = Field(..., description="Language Type")
    content_list: list = Field(..., description="Translated Text List")
