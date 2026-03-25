'''
@create_time: 2026/3/25 下午7:38
@Author: GeChao
@File: main.py
'''
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def read_item(name: str):
    return {"message": f"Hello {name}"}

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8001)
