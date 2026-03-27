'''
@create_time: 2026/3/27 下午1:13
@Author: GeChao
@File: translate.py
'''

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.schemas.translate import TranslateRequest, BatchTranslateRequest
from app.utils.dependencies import api_key_check
from app.services.text_generator import service_text_translate, service_batch_text_translate

router_r1 = APIRouter(
    prefix="/api/r1/c",
    dependencies=[Depends(api_key_check)],
    tags=["translate"]
)


@router_r1.post("/translate")
async def route_text_translate(request: Request, translate_req: TranslateRequest) -> JSONResponse:
    clientId = (request.headers.get('accesskey'))

    des_lang_type = translate_req.des_lang_type
    content = translate_req.content

    ret_data, usage = service_text_translate(des_lang_type, content)

    if ret_data is None:
        return JSONResponse(content={"success": False, "msg": "Translation failed", "data": {}, "usage": usage})

    ret_data_dict = {'translated_content': ret_data.rstrip("\\n")}
    return JSONResponse(content={"success": True, "msg": "success", "data": ret_data_dict, "usage": usage})


@router_r1.post("/batchtranslate")
async def route_batch_text_translate(request: Request, batch_translate_req: BatchTranslateRequest) -> JSONResponse:
    from app.config import logger
    clientId = (request.headers.get('accesskey'))
    des_lang_type = batch_translate_req.des_lang_type.upper()
    content_list = batch_translate_req.content_list

    
    ret_data, usage = service_batch_text_translate(des_lang_type=des_lang_type, content_list=content_list)
    logger.info(f"batch_translate result: ret_data={ret_data}, usage={usage}")
    
    if not ret_data:
        return JSONResponse(content={"success": False, "msg": "Translation failed", "data": {}, "usage": usage})

    translated_data_list = []
    for index in range(len(content_list)):
        translated_data_list.append({'content': content_list[index], 'translated': ret_data[index]})

    ret_data_dict = {'translated_content_list': translated_data_list}
    return JSONResponse(content={"success": True, "msg": "success", "data": ret_data_dict, "usage": usage})
