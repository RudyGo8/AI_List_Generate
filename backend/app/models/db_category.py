'''
@create_time: 2026/3/28
@Author: GeChao
@File: db_category.py
'''
from sqlalchemy import Column, BigInteger, String, DateTime, Index, Integer
from sqlalchemy.sql import func
from backend.app.database import Base


class Category(Base):
    __tablename__ = "db_category"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    site = Column(String(64, collation="utf8mb4_bin"), nullable=False, comment="站点标识，如 shopee_vn, tiktok_id")
    category_path = Column(String(512, collation="utf8mb4_bin"), nullable=False, comment="类目路径，如 电子 > 手机")
    category_id = Column(String(64, collation="utf8mb4_bin"), nullable=False, comment="平台类目ID")
    parent_id = Column(String(64, collation="utf8mb4_bin"), default=None, comment="父类目ID")
    level = Column(Integer, nullable=False, default=1, comment="类目层级")
    enable = Column(Integer, nullable=False, default=1, comment="0停用,1启用")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    create_user = Column(String(128, collation="utf8mb4_bin"), nullable=False, server_default="system", comment="创建人")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="修改时间")
    update_user = Column(String(128, collation="utf8mb4_bin"), server_default="system", comment="修改人")

    __table_args__ = (
        Index("idx_site", "site"),
        Index("idx_category_id", "site", "category_id", unique=True),
    )
