from loguru import logger as log
from utils import redis_utils as redis
import requests
from constants import hongkong_newsletter_host, token_value, header_token
import json
from utils.date_util import get_now


def retry_failed_job():
    v = redis.get_value('retry:jobs')
    if v is not None:
        log.warning('当前有未完成的任务')
        return
    redis.set_value('retry:jobs', '1')
    log.info('开始执行job')

    headers = {
        'Content-Type': 'application/json',
        header_token: token_value
    }
    data = {
        "deep": 0,
        "source": -1,
        "geCreateDate": get_now().strftime('%Y-%m-%d')
    }

    try:
        response = requests.post(f'{hongkong_newsletter_host}/aid/retry', headers=headers, data=json.dumps(data))
        response.raise_for_status()
        if response.status_code == 200:
            log.info('✅job执行成功')
        else:
            log.warning(f'❌请求失败，返回状态码: {response.status_code}')
    except requests.exceptions.HTTPError as http_err:
        log.warning(f'❌HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as req_err:
        log.warning(f'❌Request error occurred: {req_err}')

    log.info('job执行完成')
    redis.del_value('retry:jobs')



