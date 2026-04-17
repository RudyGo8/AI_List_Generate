'''
@create_time: 2026/3/27 下午4:52
@Author: GeChao
@File: ocr.py
'''
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List


class OcrRequest(BaseModel):
    image_url_list: Optional[List[HttpUrl]] = Field(None, description="Picture URL List")
