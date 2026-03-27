'''
@create_time: 2026/3/27 下午4:30
@Author: GeChao
@File: ocr.py
'''
from fastapi import APIRouter, Depends, Request

from app.schemas.common import CommonResponse
from app.schemas.ocr import OcrRequest
from app.services.multimodel_generator import common_image_ocr
from app.utils.dependencies import api_key_check

router_r1 = APIRouter(
    prefix="/api/r1/c",
    dependencies=[Depends(api_key_check)],
    tags=["ocr"],
)


@router_r1.post("/ocr")
async def route_image_ocr(request: Request, ocr_req: OcrRequest):
    clientId = (request.headers.get('accesskey'))

    image_url_list = ocr_req.image_url_list

    word_list, usage = common_image_ocr(image_url_list=image_url_list)
    ret_data = {'word_list': word_list}
    return CommonResponse(success=True, msg='success', data=ret_data, usage=usage)
