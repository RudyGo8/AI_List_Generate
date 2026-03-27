'''
@create_time: 2026/3/27 下午1:25
@Author: GeChao
@File: constants.py
'''
from enum import Enum


class DataEnable(Enum):
    ON = 1
    OFF = 0


class LLMType(Enum):
    QWEN = 'QWEN'
    GEMINI = 'GEMINI'