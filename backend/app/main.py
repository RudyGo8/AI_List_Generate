'''
@create_time: 2026/3/25 下午7:38
@Author: GeChao
@File: main.py
'''
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes.common.translate import router_r1 as translate_router_r1
from backend.app.routes.common.ocr import router_r1 as ocr_router_r1
from backend.app.routes.shop.ailist import router_r1 as shop_router_r1
from backend.app.config import logger, APP_VERSION

app = FastAPI(
    title="ai-list-generate-backend",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:4173',
        'http://127.0.0.1:4173'
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.middleware('http')
async def log_request(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code} {request.url}")
    return response


@app.get("/api/r1/meta/version", tags=["meta"])
async def route_version():
    return {"success": True, "msg": "success", "data": {"version": APP_VERSION}}


app.include_router(shop_router_r1)
app.include_router(translate_router_r1)
app.include_router(ocr_router_r1)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=1235)
