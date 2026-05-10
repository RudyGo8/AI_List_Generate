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
import time

app = FastAPI(
    title="ai-list-generate-backend",
    version=APP_VERSION,
)

# 跨域 CORS 中间件
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

# 请求日志中间件
@app.middleware('http')
async def log_request(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    start_time = time.time()
    # 将请求传给下一个中间件
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} {request.url} {process_time:.3f}s")
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
