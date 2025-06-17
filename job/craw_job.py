import requests
from loguru import logger as log
from constants import hongkong_newsletter_host, token_value, header_token
from datetime import datetime
import json


def check_todo():
    log.info('🤔start execute check_todo job ...')
    current_date = datetime.now()
    # # 计算前一天的日期
    # previous_date = current_date - timedelta(days=1)
    # # 提取年、月、日并转换为整数
    # year = int(previous_date.year)
    # month = int(previous_date.month)
    # day = int(previous_date.day)
    # log.info(f'容错处理前一天数据，{year}{month}{day}')
    # data = {
    #     "year": year,
    #     "month": month,
    #     "day": day
    # }
    # resp = requests. post(url=f'{hongkong_newsletter_host}/aid/test_check_todo', data=json.dumps(data))
    # if resp.status_code != 200:
    #     log.warning('❌请求失败，返回状态码: {}'.format(resp.status_code))
    #
    year = int(current_date.year)
    month = int(current_date.month)
    day = int(current_date.day)
    log.info('处理当天数据，{}{}{}'.format(year, month, day))
    data = {
        "year": year,
        "month": month,
        "day": day
    }
    headers = {
        header_token: token_value
    }
    resp = requests.post(url=f'{hongkong_newsletter_host}/aid/test_check_todo', data=json.dumps(data), headers=headers)
    if resp.status_code != 200:
        log.warning('❌请求失败，返回状态码: {}'.format(resp.status_code))
    log.info('✅check_todo job executed successfully')
