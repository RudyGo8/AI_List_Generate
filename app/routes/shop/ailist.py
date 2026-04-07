'''
@create_time: 2026/3/28 上午10:27
@Author: GeChao
@File: ailist.py
'''
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi import Request
import json

from app.schemas.common import CommonResponse
from app.services.tasks import set_product_src_to_db, shop_product_generate_wrapper, get_product_des_by_task
from app.utils.dependencies import api_key_check
from app.schemas.list import ListGenerateRequest
from app.utils.get_data_utils import get_product
from app.utils.param_utils import filter_product_response
from app.utils.response_utils import fail_api
from app.models.constants import DataStatus

router_r1 = APIRouter(
    prefix="/api/r1/shop",
    dependencies=[Depends(api_key_check)],
    tags=["shop"]
)


# 场景标记
def _merge_scene_to_custom_data(custom_data, scene):
    if not scene or scene == 'default':
        return custom_data

    payload = {}
    if custom_data:
        try:
            if isinstance(custom_data, str):
                payload = json.loads(custom_data)
            elif isinstance(custom_data, dict):
                payload = custom_data
            else:
                payload = {"raw_custom_data": str(custom_data)}
        except Exception:
            payload = {"raw_custom_data": str(custom_data)}

    payload['ai_scene'] = scene
    return json.dumps(payload, ensure_ascii=False)


@router_r1.post("/ailist")
async def routes_shop_ailist(request: Request, list_generate_req: ListGenerateRequest, background_tasks: BackgroundTasks):
    clientId = (request.headers.get('accesskey'))
    ai_scene = request.headers.get('x-ai-scene', 'default')
    site = list_generate_req.site
    platform_id = list_generate_req.platform_id
    notice_url = list_generate_req.notice_url
    tag_type = list_generate_req.tag_type
    des_lang_type = list_generate_req.des_lang_type

    product_url = list_generate_req.product_url
    if product_url:
        product_data = get_product(product_url=product_url)
        if not product_data:
            return fail_api("get product data fail!")
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

    custom_data = _merge_scene_to_custom_data(custom_data, ai_scene)

    if not spu_image_url:
        return fail_api("spu_image_url must be provided!")
    if not site:
        return fail_api("site must be provided!")

    res, task_id = set_product_src_to_db(clientId=clientId,
                                         platform_id=platform_id,
                                         site=site,
                                         spu_image_url=spu_image_url, notice_url=notice_url,
                                         sku_image_url_list=sku_image_url_list,
                                         product_title=product_title,
                                         category_id=category_id, category_name=category_name,
                                         attributes=attributes,
                                         tag_type=tag_type, custom_data=custom_data, des_lang_type=des_lang_type)

    if not res:
        return CommonResponse(success=False, msg='task create fail')

    # 异步执行
    background_tasks.add_task(shop_product_generate_wrapper, task_id, None)
    ret_data = {
        'task_id': task_id,
        'status': DataStatus.READY.value,
        'polling_url': f'/api/r1/shop/ailist/task/{task_id}'
    }
    return CommonResponse(success=True, msg='task created success', data=ret_data)


@router_r1.get("/ailist/task/{task_id}")
async def routes_shop_ailist_task(task_id: int):
    task_status, product_des_record, usage, model_name = get_product_des_by_task(task_id=task_id)

    data = {
        "task_id": task_id,
        "status": task_status,
        "model_name": model_name
    }

    if product_des_record:
        data.update(filter_product_response(response_content=product_des_record.to_dict()) or {})

    usage_dict = json.loads(usage) if usage else None

    if task_status == DataStatus.FAIL.value:
        return CommonResponse(success=False, msg='task failed', data=data, usage=usage_dict)

    if task_status in (DataStatus.READY.value, DataStatus.PROCESSING.value):
        return CommonResponse(success=True, msg='task processing', data=data, usage=usage_dict)

    return CommonResponse(success=True, msg='success', data=data, usage=usage_dict)
