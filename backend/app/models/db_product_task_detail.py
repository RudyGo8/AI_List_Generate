'''
@create_time: 2026/3/28 上午11:17
@Author: GeChao
@File: db_product_task_detail.py
'''
from sqlalchemy import Column, BigInteger, String, DateTime, Text, Index, Integer, Float
from sqlalchemy.sql import func
from backend.app.database import Base


class DbProductTaskDetail(Base):
    __tablename__ = "db_product_task_detail"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    gid = Column(String(24, collation="utf8mb4_bin"), nullable=False, comment="组ID")
    product_src_id = Column(BigInteger, nullable=True, comment="原始商品表主键ID")
    product_des_id = Column(BigInteger, nullable=True, comment="目标商品表主键ID")
    platform_id = Column(Integer, nullable=False, comment="平台ID")
    site = Column(String(12, collation="utf8mb4_bin"), nullable=True, comment="站点")
    status = Column(String(2, collation="utf8mb4_bin"), nullable=False,
                    comment="数据状态，02:ready,03:处理中,00:成功,01:失败")
    custom_data = Column(Text, nullable=True, comment="用户自定义数据")
    des_lang_type = Column(String(24, collation="utf8mb4_bin"), nullable=False, default='中文', comment="目标语言")
    tag_type = Column(String(4, collation="utf8mb4_bin"), default=None, comment="标签类型")
    batch_no = Column(String(128, collation="utf8mb4_bin"), nullable=True, comment="批处理编号")
    model_name = Column(String(128, collation="utf8mb4_bin"), nullable=True, comment="模型名")
    duration = Column(Float, default=0.0, comment="执行时长")
    usage = Column(String(128, collation="utf8mb4_bin"), nullable=True, comment="消耗")
    notice_url = Column(String(512, collation="utf8mb4_bin"), nullable=True, comment="通知地址")
    remark = Column(String(512, collation="utf8mb4_bin"), default=None, comment="描述")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    create_user = Column(String(128, collation="utf8mb4_bin"), nullable=False, server_default="system",
                         comment="创建人")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="修改时间")
    update_user = Column(String(128, collation="utf8mb4_bin"), server_default="system", comment="修改人")

    __table_args__ = (
        Index("idx_ptd_product_src_id", "product_src_id"),
        Index("idx_ptd_product_des_id", "product_des_id"),
        Index("idx_ptd_platform_id", "platform_id", "site"),
        Index("idx_ptd_gid", "gid"),
        Index("idx_ptd_create_time", "create_time"),
        Index("idx_ptd_status", "status"),
    )
