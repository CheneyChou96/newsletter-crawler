from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel
from ai_information_data.monitor_services import monitor_service
import ai_information_data.service as service
from utils import redis_utils as redis
from tortoise import Tortoise
from ai_information_data.sync_tj_service import sync_tj_service


class TodoUrlReq(BaseModel):
    source: int
    status: int


api_aid = APIRouter()


@api_aid.get("/hello")
async def hello():
    return {"message": "Hello World"}


@api_aid.post("/test")
async def test(req: TodoUrlReq):
    logger.info('req is: {}'.format(req))
    await monitor_service()
    return {"message": "Hello World"}


@api_aid.post("/todo_urls")
async def todo_urls(req: TodoUrlReq):
    v = redis.get_value('todo_urls')
    if v is not None:
        logger.warning('当前有未完成的任务')
        return {"message": "当前有未完成的任务"}
    redis.set_value('todo_urls', '1')
    logger.info('req is: {}'.format(req))
    service.todo_urls(req.source)
    redis.del_value('todo_urls')
    return {"message": "success"}


@api_aid.post("/retry")
async def retry(req: dict):
    v = redis.get_value('retry')
    if v is not None:
        logger.warning('当前有未完成的任务')
        return {"message": "当前有未完成的任务"}
    redis.set_value('retry', '1')
    logger.info('req is: {}'.format(req))
    await service.retry(req['deep'], req['source'], req['geCreateDate'])
    redis.del_value('retry')
    return {"message": "success"}


@api_aid.post("/deep")
async def deep(req: dict):
    v = redis.get_value('deep')
    if v is not None:
        logger.warning('当前有未完成的任务')
        return {"message": "当前有未完成的任务"}
    redis.set_value('deep', '1')
    logger.info('req is: {}'.format(req))
    service.deep(req)
    redis.del_value('deep')
    return {"message": "success"}


@api_aid.post("/todo_clean_data")
async def todo_clean_data(req: dict):
    v = redis.get_value('todo_clean_data')
    if v is not None:
        logger.warning('当前有未完成的任务')
        return {"message": "当前有未完成的任务"}
    redis.set_value('todo_clean_data', '1')
    logger.info('req is: {}'.format(req))
    await service.todo_clean_data(req)
    redis.del_value('todo_clean_data')
    return {"message": "success"}


@api_aid.get("/pull_today_data")
async def pull_today_data():
    logger.info('开始拉取今天的数据')
    v = redis.get_value('pull_today_data')
    if v is not None:
        logger.warning('当前有未完成的任务')
        return {"message": "当前有未完成的任务"}
    redis.set_value('pull_today_data', '1')
    await service.pull_today_data()
    redis.del_value('pull_today_data')
    return {"message": "success"}


@api_aid.post("/test_check_todo")
async def test_check_todo(req: dict):
    year = req.get('year')
    month = req.get('month')
    day = req.get('day')
    await service.check_todo(int(year), int(month), int(day))
    return {"message": "Hello World"}


@api_aid.post("/get")
async def get(req: dict):
    url = req.get('url')
    conn = Tortoise.get_connection('default')
    query = "SELECT content FROM crawler_ai_news_detail WHERE url = %s LIMIT 1"
    result = await conn.execute_query_dict(query, [url])

    if result:
        return result[0]['content']
    else:
        return None


@api_aid.get("/sync_tj")
async def sync_tj():
    await sync_tj_service()
    return {"message": "sync_tj completed successfully"}
