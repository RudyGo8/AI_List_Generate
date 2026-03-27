'''
@create_time: 2026/3/27 下午4:51
@Author: GeChao
@File: common.py
'''

from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class CommonResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = Field(..., description="表示请求是否成功")
    msg: str = Field(..., description="返回的消息内容")
    data: Optional[Dict[str, Any]] = Field(default=None, description="包含接口数据字段")
    usage: Optional[Dict[str, Any]] = Field(default=None, description="使用情况的相关信息")



