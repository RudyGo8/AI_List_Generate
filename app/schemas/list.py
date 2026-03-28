'''
@create_time: 2026/3/28 上午10:33
@Author: GeChao
@File: list.py
'''
from pydantic import BaseModel, HttpUrl, Field, model_validator
from typing import Optional, List, Dict, Any


class ListGenerateRequest(BaseModel):
    site: str = Field(None, description="Site ID")
    notice_url: Optional[HttpUrl] = Field(None, description="Notice URL")
    product_url: Optional[HttpUrl] = Field(None, description="Product URL")
    spu_image_url: Optional[HttpUrl] = Field(None, description="SPU Image URL")
    sku_image_url_list: Optional[List[HttpUrl]] = Field(None, description="SKU Image URL List")
    product_title: Optional[str] = Field(None, description="Product Title")
    category_name: Optional[str] = Field(None, description="Category Name")
    category_id: Optional[int] = Field(None, description="Category ID")
    attributes: Optional[list] = Field(None, description="Product Attributes")
    supplier_name: Optional[str] = Field(None, description="Supplier Name")
    custom_data: Optional[str] = Field(None, description="Custom Data")
    tag_type: Optional[str] = Field(None, description="Product Tag Type")
    des_lang_type: Optional[str] = Field("中文", description="Target Language")

    @model_validator(mode='after')
    def check_product_url_or_spu_image_url(self) -> 'ListGenerateRequest':
        if not self.product_url and not self.spu_image_url:
            raise ValueError('product_url and  spu_image_url must be provided one!')
        return self