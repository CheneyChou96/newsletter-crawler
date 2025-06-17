from utils.ai_consumer_utils import *
from loguru import logger as log
from db.models import TodoCleanData, TjPushLog, FireCrawlConfig
from datetime import datetime


def get_todo_urls(source: int):
    return todo_urls(source)


def update_status(data_id):
    complete(data_id)


def get_failed_urls(deep: int, source: int, ge_create_date: str):
    return failed_urls(deep, source, ge_create_date)


def get_monitor_site():
    return monitor_site_list()


def update_site(db_id, latest_url):
    return update_site_db(db_id, latest_url)


def save_scraped_data(data, url, deep: 0, source, pid, path, ext, force_title=False):
    req = AiInformationDataReq()
    req.deep = deep
    req.source = source
    req.pid = pid
    req.path = path
    req.publishTime = data.get('publishTime', None)
    temp_data = data.get('data', None)
    if data.get('success'):
        metadata = temp_data.get('metadata')
        if ext is not None:
            metadata.update(json.loads(ext))
        req.metadata = json.dumps(metadata, ensure_ascii=False)
        req.title = data.get('tempTitle', None) if force_title else metadata.get('title', data.get('tempTitle', None))
        req.sourceUrl = metadata.get('sourceURL')
        req.lang = metadata.get('language', data.get('tempLang', None))
        req.markdown = temp_data['markdown']
        req.status = 'success'
    else:
        log.warning('scrape is failed, resp: {}'.format(data))
        if 'metadata' in data:
            metadata = temp_data['metadata']
            req.metadata = json.dumps(metadata, ensure_ascii=False)
            if 'statusCode' in metadata:
                req.status = metadata['statusCode']
            else:
                req.status = 'failed'
        else:
            req.status = 'failed'
            req.sourceUrl = url
    return save(req)


async def get_un_todo_urls():
    # 大于重试次数 10的不再爬取
    return await TodoCleanData.filter(status=0, retry_num__lte=10).order_by('-create_time')


async def complete_un_todo_url(url_id):
    await TodoCleanData.filter(id=url_id).update(status=1)


async def mark_exception_status(url_id, retry_num):
    await TodoCleanData.filter(id=url_id).update(retry_num=retry_num)


async def get_filtered_data(year: int, month: int, day: int):
    # start_date = datetime(year, month, day)
    return await TodoCleanData.filter(status=0, retry_num__lte=10)


async def today_has_data(year: int, month: int, day: int):
    start_date = datetime(year, month, day)
    return await TodoCleanData.filter(create_time__gte=start_date)


async def get_today_push_log():
    today = datetime.today().replace(hour=0, minute=0, second=0)
    return await TjPushLog.filter(push_time=today).first()


async def get_todo_url_by_urls(urls: list):
    return await TodoCleanData.filter(url__in=urls)


async def get_fire_crawl_config(domain: str):
    # 查询未删除且域名匹配的配置
    return await FireCrawlConfig.filter(
        domain=domain,
        is_delete=False  # 对应SQL中的is_delete=0
    ).first().values_list('config', flat=True)  # 只返回config字段
