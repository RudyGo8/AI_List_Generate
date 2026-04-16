'''
@create_time: 2026/3/27 下午2:00
@Author: GeChao
@File: db_sys_conf.py
'''
from sqlalchemy import Column, BigInteger, String, DateTime, Text, Index, Integer
from sqlalchemy.sql import func
from backend.app.database import Base


class SysConf(Base):
    __tablename__ = "db_sys_conf"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    key = Column(String(256, collation="utf8mb4_bin"), nullable=False, comment="键")
    value = Column(String(256, collation="utf8mb4_bin"), nullable=False, comment="值")
    enable = Column(Integer, nullable=False, comment="0停用,1启用")
    remark = Column(String(512, collation="utf8mb4_bin"), default=None, comment="描述")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    create_user = Column(String(128, collation="utf8mb4_bin"), nullable=False, server_default="system",
                         comment="创建人")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="修改时间")
    update_user = Column(String(128, collation="utf8mb4_bin"), server_default="system", comment="修改人")

    __table_args__ = (
        Index("uniq_sc_key_enable", "key", "enable", unique=True),  # 联合唯一索引
    )
