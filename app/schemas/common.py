'''
@create_time: 2026/3/27 下午4:51
@Author: GeChao
@File: common.py
'''

from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class CommonResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = Field(..., description="Request Was Successful Or Not")
    msg: str = Field(..., description="Return Message Content")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Interface Data Fields")
    usage: Optional[Dict[str, Any]] = Field(default=None, description="Usage-related Information")



