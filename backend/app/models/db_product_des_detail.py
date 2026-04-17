from sqlalchemy import Column, BigInteger, String, Text, DateTime, Index, Integer
from sqlalchemy.sql import func
from backend.app.database import Base


class ProductDesDetail(Base):
    __tablename__ = "db_product_des_detail"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    gid = Column(String(24, collation="utf8mb4_bin"), nullable=False, comment="组ID")
    platform_id = Column(Integer, nullable=True, comment="平台编号")
    site = Column(String(12, collation="utf8mb4_bin"), nullable=True, comment="站点")
    product_src_id = Column(BigInteger, nullable=True, comment="原商品表主键ID")
    product_title = Column(String(256, collation="utf8mb4_bin"), nullable=True, comment="商品标题")
    product_desc = Column(Text(collation="utf8mb4_bin"), nullable=True, comment="商品描述")
    spu_image_url = Column(String(256, collation="utf8mb4_bin"), nullable=True, comment="spu图片链接")
    sku_image_url_list = Column(Text(collation="utf8mb4_bin"), nullable=True, comment="sku图片链接")
    category_name = Column(String(256, collation="utf8mb4_bin"), nullable=True, comment="类目名称")
    category_id = Column(String(128, collation="utf8mb4_bin"), nullable=True, comment="类目ID")
    sales_attr_value_list = Column(Text(collation="utf8mb4_bin"), nullable=True, comment="销售属性列表(sku)")
    attr_value_list = Column(Text(collation="utf8mb4_bin"), nullable=True, comment="属性列表")
    tag_value = Column(String(256, collation="utf8mb4_bin"), default=None, comment="标签值")
    version = Column(String(24, collation="utf8mb4_bin"), nullable=True, comment="版本号")
    remark = Column(String(512, collation="utf8mb4_bin"), nullable=True, comment="描述")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    create_user = Column(String(128, collation="utf8mb4_bin"), nullable=False, default="system", comment="创建人")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="修改时间")
    update_user = Column(String(128, collation="utf8mb4_bin"), nullable=False, default="system", comment="修改人")

    __table_args__ = (
        Index("idx_dpd_gid", "gid"),
        Index("idx_dpd_create_time", "create_time"),
        Index("idx_dpd_update_time", "update_time"),
        Index("idx_dpd_src_product_src_id", "product_src_id"),
        Index("idx_dpd_src_platform_id_site", "platform_id", "site"),
        Index("idx_dpd_product_title", "product_title"),
    )

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    #
    # def to_dict(self):
    #     model_dict = dict(self.__dict__)
    #     model_dict.pop('_sa_instance_state', None)
    #     return model_dict
