from loguru import logger as log
from utils import redis_utils as redis
import requests
from constants import hongkong_newsletter_host, token_value, header_token


def tj_job():
    job_key = 'jobs:tj_job'
    v = redis.get_value(job_key)
    if v is not None:
        log.warning('当前有未完成的任务')
        return
    redis.set_value(job_key, '1')
    log.info('开始执行tj_job')

    headers = {
        'Content-Type': 'application/json',
        header_token: token_value
    }

    try:
        response = requests.get(f'{hongkong_newsletter_host}/aid/sync_tj', headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            log.info('✅tj_job执行成功')
        else:
            log.warning(f'❌请求失败，返回状态码: {response.status_code}')
    except requests.exceptions.HTTPError as http_err:
        log.warning(f'❌HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as req_err:
        log.warning(f'❌Request error occurred: {req_err}')

    redis.del_value(job_key)
