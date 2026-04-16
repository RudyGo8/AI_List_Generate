from sqlalchemy import Column, BigInteger, String, DateTime, Text, Index, Integer, Float
from sqlalchemy.sql import func
from backend.app.database import Base


class DbNoticeDetail(Base):
    __tablename__ = "db_notice_detail"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    gid = Column(String(24, collation="utf8mb4_bin"), nullable=False, comment="组ID")
    task_type = Column(String(4, collation="utf8mb4_bin"), nullable=False, comment="任务类型")
    biz_id = Column(String(128, collation="utf8mb4_bin"), nullable=False, comment="业务ID")
    notice_url = Column(String(512, collation="utf8mb4_bin"), nullable=True, comment="通知地址")
    notice_content = Column(Text(collation="utf8mb4_bin"), nullable=True, comment="通知内容")
    next_notice_time = Column(DateTime, server_default=func.now(), comment="下次通知时间")
    custom_data = Column(Text, nullable=True, comment="用户自定义数据")
    notice_counts = Column(Integer, default=0.0, comment="执行时长")
    status = Column(String(2, collation="utf8mb4_bin"), nullable=False,
                    comment="数据状态，02:ready,03:处理中,00:成功,01:失败")
    batch_no = Column(String(128, collation="utf8mb4_bin"), nullable=True, comment="批处理编号")
    remark = Column(String(512, collation="utf8mb4_bin"), default=None, comment="描述")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    create_user = Column(String(128, collation="utf8mb4_bin"), nullable=False, server_default="system",
                         comment="创建人")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="修改时间")
    update_user = Column(String(128, collation="utf8mb4_bin"), server_default="system", comment="修改人")

    __table_args__ = (
        Index("idx_nd_gid", "gid"),
        Index("idx_nd_status", "status"),
        Index("idx_nd_next_notice_time", "next_notice_time"),
        Index("idx_nd_task_type_biz_id", "task_type", "biz_id"),
        Index("idx_nd_update_time", "update_time"),
        Index("idx_nd_create_time", "create_time"),
    )
