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
    SFT_LOCAL = 'SFT_LOCAL'


class DataStatus(Enum):
    SUCCESS = '00'
    FAIL = '01'
    READY = '02'
    PROCESSING = '03'


class SpecialID(Enum):
    NOTHING = -1

class BatchType(Enum):
    NOTICE = '0000'
    PRODUCT_GENERATE = '0001'
    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class NoticeStatus(Enum):
    READY = '02'  # 数据准备好
    PROCESSING = '03'  # 数据处理中
    SUCCESS = '00'  # 数据成功
    FAIL = '01'  # 数据失败
