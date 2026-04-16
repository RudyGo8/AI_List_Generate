'''
@create_time: 2026/3/27 下午4:30
@Author: GeChao
@File: ocr.py
'''
from fastapi import APIRouter, Depends, Request

from backend.app.schemas.common import CommonResponse
from backend.app.schemas.ocr import OcrRequest
from backend.app.services.multimodel_generator import common_image_ocr
from backend.app.utils.dependencies import api_key_check

router_r1 = APIRouter(
    prefix="/api/r1/c",
    dependencies=[Depends(api_key_check)],
    tags=["ocr"],
)


@router_r1.post("/ocr")
async def route_image_ocr(request: Request, ocr_req: OcrRequest):
    clientId = (request.headers.get('accesskey'))
    scene = request.headers.get('x-ai-scene', 'default')

    image_url_list = ocr_req.image_url_list

    word_list, usage = common_image_ocr(image_url_list=image_url_list, scene=scene)
    ret_data = {'word_list': word_list}
    return CommonResponse(success=True, msg='success', data=ret_data, usage=usage)
