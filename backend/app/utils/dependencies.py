'''
@create_time: 2026/3/27 下午1:19
@Author: GeChao
@File: dependencies.py
'''

from fastapi import Header, HTTPException
from backend.app.database import get_db_instance
from backend.app.models.db_sys_client_conf import SysClientConf
from backend.app.models.constants import DataEnable


def api_key_check(accesskey: str = Header(...), accesssecret: str = Header(...)):
    db = next(get_db_instance())

    try:
        client = db.query(SysClientConf).filter(
            SysClientConf.api_key == accesskey,
            SysClientConf.api_secret == accesssecret,
            SysClientConf.enable == DataEnable.ON.value
        ).first()

        if not client:
            raise HTTPException(status_code=401, detail="Unauthorized")
    finally:
        db.close()
