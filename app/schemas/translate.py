'''
@create_time: 2026/3/27 下午1:38
@Author: GeChao
@File: translate.py
'''
from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    des_lang_type: str = Field(..., description="目标语言")
    content: str = Field(..., descrption="翻译内容")
