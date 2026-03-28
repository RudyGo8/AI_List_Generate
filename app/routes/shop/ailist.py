'''
@create_time: 2026/3/28 上午10:27
@Author: GeChao
@File: ailist.py
'''
from fastapi import APIRouter, Depends
from fastapi import Request
from app.utils.dependencies import api_key_check
from app.schemas.list import ListGenerateRequest
from app.utils.get_data_utils import get_product

router_r1 = APIRouter(
    prefix="/api/r1/shop",
    dependencies=[Depends(api_key_check)],
    tags=["shop"]
)


@router_r1.post("/ailist")
async def routes_shop_ailist(request: Request, list_generate_req: ListGenerateRequest):
    clientId = (request.headers.get('accesskey'))

    site = list_generate_req.site
    notice_url = list_generate_req.notice_url
    tag_type = list_generate_req.tag_type
    des_lang_type = list_generate_req.des_lang_type

    product_url = list_generate_req.product_url
    if product_url:
        product_data = get_product(product_url=product_url)
        spu_image_url = product_data.get('spu_image_url', None)
        sku_image_url_list = product_data.get('sku_image_url_list', None)
        product_title = product_data.get('product_title', None)
        category_name = product_data.get('category_name', None)
        category_id = product_data.get('category_id', None)
        attributes = product_data.get('attributes', None)
        supplier_name = product_data.get('supplier_name', None)
        custom_data = product_data.get('custom_data', None)
    else:

        spu_image_url = list_generate_req.spu_image_url
        sku_image_url_list = list_generate_req.sku_image_url_list
        product_title = list_generate_req.product_title
        category_name = list_generate_req.category_name
        category_id = list_generate_req.category_id
        attributes = list_generate_req.attributes
        supplier_name = list_generate_req.supplier_name
        custom_data = list_generate_req.custom_data

    if not spu_image_url:
        return fail_api("spu_image_url must be provided!")
    if not site:
        return fail_api("site must be provided!")
