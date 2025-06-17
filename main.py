from fastapi import FastAPI, Request, HTTPException
from ai_information_data.api import api_aid
from tortoise.contrib.fastapi import register_tortoise
from settings.settings import TORTOISE_ORM
from loguru import logger as log
from job.job_register import init_job
from constants import token_value, header_token
from fastapi.responses import JSONResponse

app = FastAPI()


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # 获取自定义请求头的值
    token_key = request.headers.get(header_token)

    if token_key is None or token_key != token_value:
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "登录失效"}
        )

    response = await call_next(request)
    return response

log.info("Starting FastAPI application...")


app.include_router(api_aid, prefix='/aid', tags=['information_data'])

register_tortoise(app, config=TORTOISE_ORM)


@app.on_event("startup")
async def startup_event():
    log.info("Starting up init job...")
    init_job()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3001)

