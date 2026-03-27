'''
@create_time: 2026/3/25 下午7:38
@Author: GeChao
@File: main.py
'''
from fastapi import FastAPI, Request
from app.routes.common.translate import router_r1 as translate_router_r1
from app.routes.common.ocr import router_r1 as ocr_router_r1
from app.config import logger

app = FastAPI()


@app.middleware('http')
async def log_request(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code} {request.url}")
    return response


app.include_router(translate_router_r1)
app.include_router(ocr_router_r1)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=1235)
