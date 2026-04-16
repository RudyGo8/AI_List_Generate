from sqlalchemy import Column, BigInteger, String, DateTime, Index, Integer, Float
from sqlalchemy.sql import func
from backend.app.database import Base


class DbAiModelRoute(Base):
    __tablename__ = "db_ai_model_route"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True, comment="主键")
    task_type = Column(String(64, collation="utf8mb4_bin"), nullable=False, comment="任务类型，如 shop_category/translate/ocr")
    scene = Column(String(64, collation="utf8mb4_bin"), nullable=False, default="default", comment="场景标识")
    model_name = Column(String(128, collation="utf8mb4_bin"), nullable=False, comment="模型名称")
    llm_type = Column(String(32, collation="utf8mb4_bin"), nullable=False, default="QWEN", comment="模型供应商类型")
    temperature = Column(Float, nullable=True, default=None, comment="采样温度")
    max_tokens = Column(Integer, nullable=True, default=None, comment="最大输出token")
    timeout = Column(Integer, nullable=True, default=None, comment="超时时间（秒）")
    enable = Column(Integer, nullable=False, default=1, comment="0停用,1启用")
    remark = Column(String(512, collation="utf8mb4_bin"), default=None, comment="描述")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    create_user = Column(String(128, collation="utf8mb4_bin"), nullable=False, server_default="system", comment="创建人")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="修改时间")
    update_user = Column(String(128, collation="utf8mb4_bin"), server_default="system", comment="修改人")

    __table_args__ = (
        Index("uniq_ai_route_task_scene_enable", "task_type", "scene", "enable", unique=True),
        Index("idx_ai_route_task_type", "task_type"),
    )
