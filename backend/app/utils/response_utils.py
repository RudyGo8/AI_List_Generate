'''
@create_time: 2026/3/28 上午11:06
@Author: GeChao
@File: response_utils.py
'''

from fastapi.responses import JSONResponse


def fail_api(msg: str = "失败"):

    return JSONResponse(content={"success": False, "msg": msg})
