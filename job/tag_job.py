import time

from loguru import logger as log

from utils import redis_utils as redis
from utils.ai_consumer_utils import run_tag, count_tag_num, update_failed_data
from utils.date_util import get_now


def tag_job():
    # old_num = redis.get_value('tag_num')
    # log.info('old_num is: {}'.format(old_num))

    # log.info('update_failed_data...')
    # update_failed_data({'createDate': get_now().strftime('%Y-%m-%d')})

    # log.info('开始执行count')
    count_req_retry_count = 0
    count = count_request()
    while count is None and count_req_retry_count < 10:
        log.warning(f'count_request失败，重试次数: {count_req_retry_count}')
        time.sleep(1)
        count = count_request()
        count_req_retry_count += 1
    if count is None:
        log.error('count_request重试失败，无法获取标签数量')
        return
    log.info('count is {}'.format(count))
    # redis.set_value('tag_num', count)
    # if old_num is not None and int(old_num) != int(count):
    #     log.info('打标进行中，不进行重试')
    #     return

    log.info('开始执行打标job')
    tag_req_retry_count = 0
    try:
        tag = tag_request()
        while not tag and tag_req_retry_count < 10:
            log.warning(f'tag_request失败，重试次数: {tag_req_retry_count}')
            time.sleep(1)
            tag = tag_request()
            tag_req_retry_count += 1
        if not tag:
            log.error('tag_request重试失败，无法执行打标')
            return
    except Exception as e:
        log.error(f'打标请求失败: {e}')
    log.info('打标执行完成✅')


def count_request():
    result = count_tag_num()
    return len(result)


def tag_request():
    source = int(redis.get_value('source')) if redis.get_value('source') is not None else -1
    limit = int(redis.get_value('limit')) if redis.get_value('limit') is not None else 15
    data = {
        "source": source,
        "limit": limit
    }
    return run_tag(data) is not None
