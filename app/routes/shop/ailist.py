'''
@create_time: 2026/3/28 上午10:27
@Author: GeChao
@File: ailist.py
'''
from fastapi import APIRouter, Depends
from fastapi import Request
from pydantic import json

from app.schemas.common import CommonResponse
from app.services.tasks import set_product_src_to_db, shop_product_generate_wrapper, get_product_des_by_task
from app.utils.dependencies import api_key_check
from app.schemas.list import ListGenerateRequest
from app.utils.get_data_utils import get_product
from app.utils.param_utils import filter_product_response
from app.utils.response_utils import fail_api

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
        custom_data = product_data.get('custom_data', None)
    else:
        spu_image_url = list_generate_req.spu_image_url
        sku_image_url_list = list_generate_req.sku_image_url_list
        product_title = list_generate_req.product_title
        category_name = list_generate_req.category_name
        category_id = list_generate_req.category_id
        attributes = list_generate_req.attributes
        custom_data = list_generate_req.custom_data

    if not spu_image_url:
        return fail_api("spu_image_url must be provided!")
    if not site:
        return fail_api("site must be provided!")

    res, task_id = set_product_src_to_db(clientId=clientId,
                                         site=site,
                                         spu_image_url=spu_image_url, notice_url=notice_url,
                                         sku_image_url_list=sku_image_url_list,
                                         product_title=product_title,
                                         category_id=category_id, category_name=category_name,
                                         attributes=attributes,
                                         tag_type=tag_type, custom_data=custom_data, des_lang_type=des_lang_type)

    if res:
        ret_data = {'task_id': task_id}
        if notice_url:
            return CommonResponse(success=True, msg='task created success', data=ret_data)
        else:
            res = shop_product_generate_wrapper(task_record_id=task_id, batch_no=None)
            if res:
                task_status, product_des_record, usage = get_product_des_by_task(task_id=task_id)
                if product_des_record:
                    notice_content = filter_product_response(response_content=product_des_record.to_dict())
                else:
                    notice_content = {}
                notice_content["status"] = task_status
                notice_content["task_id"] = task_id

                return CommonResponse(success=True, msg='success', data=notice_content, usage=json.loads(usage))
            return CommonResponse(success=False, msg='fail')

    else:
        return CommonResponse(success=False, msg='task create fail')

