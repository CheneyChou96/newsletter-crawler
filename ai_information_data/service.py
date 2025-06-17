import json

import ai_information_data.dao as aid_dao
from utils.fire_crawl_utils import scrape
from urllib.parse import urlparse
from loguru import logger as log
import utils.ai_consumer_utils as ai_sdk
import utils.redis_utils as redis
from tortoise import Tortoise
import datetime
from sql.todo_data_sql import insert_sql, update_sql_1, update_sql_2


def todo_urls(source: int):
    urls = aid_dao.todo_urls(source)
    if urls is None:
        log.info('no urls')
        return None

    log.info('todo_urls size is {}'.format(len(urls)))

    for i, item in enumerate(urls):
        log.info('todo_url: 当前进度{}/{}'.format(i, len(urls)))
        try:
            scrape_resp = scrape(item['url'])
            aid_dao.save_scraped_data(scrape_resp, item['url'], 0, item['source'], None, None, item['ext'])
            if scrape_resp.get('success'):
                data = scrape_resp.get('data')
                metadata = data.get('metadata')
                if metadata is not None and metadata.get('statusCode') and metadata.get('statusCode') == 200:
                    aid_dao.complete(item['id'])
        except Exception as e:
            log.warning('爬取失败: {}'.format(e))
            aid_dao.save_scraped_data({}, item['url'], 0, source,
                                      None, None, item['ext'])
    return True


async def retry(deep: int, source: int, ge_create_date: str):
    failed_data = aid_dao.get_failed_urls(deep, source, ge_create_date)
    log.info('failed_urls size is {}'.format(len(failed_data)))

    if len(failed_data) == 0:
        log.info('没有失败的url')
        return None

    source_url_list = []
    for item in failed_data:
        source_url_list.append(item['sourceUrl'])

    todo_list = await aid_dao.get_todo_url_by_urls(source_url_list)
    log.info('todo_list size is {}', len(todo_list))
    if todo_list is not None and len(todo_list) > 0:
        await fire_crawl_url(todo_list)
    log.info('finish retry')
    return True
    # ext = None
    # for item in aid_dao.get_monitor_site():
    #     if item['id'] == source:
    #         ext = item['ext']
    #         break

    # for i, item in enumerate(failed_data):
    #     log.info('failed_url: {}/{}'.format(i, len(failed_data)))
    #     try:
    #         scrape_resp = scrape(item['sourceUrl'])
    #         aid_dao.save_scraped_data(scrape_resp, item['sourceUrl'], item['deep'], item['source'], item['pid'],
    #                                   item['path'], ext)
    #     except Exception as e:
    #         log.warning('爬取失败: {}'.format(e))
    #         aid_dao.save_scraped_data({}, item['sourceUrl'], int(item['deep']), item['source'],
    #                                   item['id'], item['path'], ext)


def deep(req):
    ext = None
    for item in aid_dao.get_monitor_site():
        if item['id'] == req['source']:
            ext = item['ext']
            break
    # 根据条件获取要爬取的urls
    data_array = ai_sdk.deep_urls(req)
    log.info('data_array size is {}'.format(len(data_array)))
    for i, item in enumerate(data_array):
        item_urls = item['urls']
        log.info('deep_url: {}/{}, item_urls: {}'.format(i, len(data_array), len(item_urls)))
        if len(item_urls) == 0:
            log.info('没有要爬取的url')
            continue

        for j, url in enumerate(item_urls):
            log.info('deep_url: {}/{}, url: {}'.format(j, len(item_urls), url))
            try:
                scrape_resp = scrape(url)
                aid_dao.save_scraped_data(scrape_resp, url, int(item['deep'] + 1), item['source'],
                                          item['id'], item['path'], ext)
            except Exception as e:
                log.warning('爬取失败: {}'.format(e))
                aid_dao.save_scraped_data({}, url, int(item['deep'] + 1), item['source'],
                                          item['id'], item['path'], ext)

    log.info('finish deep')


async def job_retry():
    # sites = aid_dao.get_monitor_site()
    # for one_site in sites:
    await retry(0, -1)


async def todo_clean_data(req):
    un_todo_url = await aid_dao.get_un_todo_urls()
    # un_todo_url = await aid_dao.get_filtered_data(2025, 4, 23)
    await fire_crawl_url(un_todo_url)


async def fire_crawl_url(todo_url_list):
    log.info('un_todo_url size is {}'.format(len(todo_url_list)))
    redis.set_value('un_todo_url', len(todo_url_list))
    for i, item in enumerate(todo_url_list):
        log.info('un_todo_url: 当前进度{}/{}'.format(i + 1, len(todo_url_list)))
        ext = {
            'region': item.region,
            'countryOrAreas': item.country,
            'subjectType': item.subject_type,
            'orgType': item.organization_type,
            'notificationAgency': item.notification_agency,
            'articleClass': item.article_category,
            'identifySource': item.identification_source,
            'siteLang': item.lang,
            'regionalScope': item.regional_scope
        }
        try:
            todo_url = item.url if item.attachment is None else item.attachment
            # 提取 domain
            parsed_url = urlparse(todo_url)
            # 获取域名（包括子域名）
            domain = parsed_url.netloc
            # 根据 domain 获取 fire_crawl 配置
            config = await aid_dao.get_fire_crawl_config(domain)
            scrape_resp = scrape(todo_url, config_params=config)
            if item.publish_time is not None:
                scrape_resp['publishTime'] = item.publish_time.strftime('%Y-%m-%d %H:%M:%S')
            scrape_resp['tempTitle'] = item.title
            scrape_resp['tempLang'] = item.lang_site
            scrape_resp['data']['metadata']['sourceURL'] = item.url
            aid_dao.save_scraped_data(scrape_resp, item.url, 0, -1, None, None,
                                      json.dumps(ext, ensure_ascii=False), True)
            await aid_dao.complete_un_todo_url(item.id)
        except Exception as e:
            log.warning('爬取失败: {}, url {}'.format(e, item.url))
            await aid_dao.mark_exception_status(item.id, item.retry_num + 1)

        redis.set_value('un_todo_url', len(todo_url_list) - (i + 1))

    return None


async def pull_today_data():
    conn = Tortoise.get_connection('default')

    log.info('execute insert_sql')
    await conn.execute_script(insert_sql)

    log.info('execute update_sql_1')
    await conn.execute_script(update_sql_1)

    log.info('execute update_sql_2')
    await conn.execute_script(update_sql_2)

    return None


async def execute_fire_crawl_job():
    now = datetime.datetime.now()

    # 获取年、月、日
    year = now.year
    month = now.month
    day = now.day
    # 执行未完成的
    un_todo_url = await aid_dao.get_filtered_data(year, month, day)
    await fire_crawl_url(un_todo_url)


async def check_todo(year: int, month: int, day: int):
    log.info('check_todo_and_push start')
    undo_list = await aid_dao.get_filtered_data(year, month, day)

    check_todo_redis = redis.get_value('check_todo')
    if check_todo_redis is not None:
        log.warning('当前有任务在进行')
        return
    redis.set_value('check_todo', '1')

    await fire_crawl_url(undo_list)

    log.info('开始推送 cos')
    ai_sdk.push_tj_cos({'source': -1})

    redis.del_value('check_todo')
