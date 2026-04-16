'''
@create_time: 2026/3/28 上午11:13
@Author: GeChao
@File: db_product_src_detail.py
'''
from sqlalchemy import Column, String, BigInteger, Text, DateTime, func, Index

from backend.app.database import Base


class ProductSrcDetail(Base):
    __tablename__ = "db_product_src_detail"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键，可以理解为任务ID")
    gid = Column(String(24, collation="utf8mb4_bin"), nullable=False, comment="组ID")
    product_title = Column(String(256, collation="utf8mb4_bin"), nullable=True, comment="原始商品标题")
    product_url = Column(String(2048, collation="utf8mb4_bin"), nullable=True, comment="原始商品链接")
    category_name = Column(String(128, collation="utf8mb4_bin"), nullable=True, comment="原始商品类目")
    category_id = Column(String(24, collation="utf8mb4_bin"), nullable=True, comment="原始商品类目ID")
    spu_image_url = Column(String(256, collation="utf8mb4_bin"), nullable=False, comment="原始spu图片链接")
    sku_image_url_list = Column(Text(collation="utf8mb4_bin"), nullable=True, comment="原始sku图片链接")
    attributes = Column(Text(collation="utf8mb4_bin"), nullable=True, comment="原始商品属性")
    remark = Column(String(512, collation="utf8mb4_bin"), nullable=True, comment="描述")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    create_user = Column(String(128, collation="utf8mb4_bin"), nullable=False, default="system", comment="创建人")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="修改时间")
    update_user = Column(String(128, collation="utf8mb4_bin"), nullable=False, default="system", comment="修改人")

    __table_args__ = (
        Index("idx_spd_gid", "gid"),
        Index("idx_spd_create_time", "create_time"),
        Index("idx_spd_update_time", "update_time"),
        Index("idx_spd_product_title", "product_title"),
    )