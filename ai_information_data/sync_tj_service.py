from db.models import TodoCleanData
from loguru import logger as log
from utils.fire_crawl_utils import scrape
import ai_information_data.dao as aid_dao
from urllib.parse import urlparse
from datetime import datetime
import json
import uuid
import pytz
from ai_information_data.tj_cos import upload_file


async def sync_tj_service():
    todo_data = await TodoCleanData.filter(status=0)
    for index, item in enumerate(todo_data, start=1):
        log.info(f"当前进度：{index}/{len(todo_data)}")
        todo_url = item.url
        # 提取 domain
        parsed_url = urlparse(todo_url)
        # 获取域名（包括子域名）
        domain = parsed_url.netloc
        # 根据 domain 获取 fire_crawl 配置
        config = await aid_dao.get_fire_crawl_config(domain)
        scrape_resp = scrape(todo_url, config_params=config)
        content = scrape_resp.get('data')['markdown'] if scrape_resp.get('data') else ''
        await TodoCleanData.filter(id=item.id).update(status=1, content=content, pull_time=datetime.now())

    log.info('开始推送天境数据...')
    # 获取今天的开始和结束时间
    today = datetime.now().date()
    start_of_today = datetime.combine(today, datetime.min.time())
    end_of_today = datetime.combine(today, datetime.max.time())

    # 查询pull_time在今天范围内的数据
    today_data = await TodoCleanData.filter(
        pull_time__gte=start_of_today,
        pull_time__lte=end_of_today,
        status=1
    ).all()
    list_data = []
    for today_datum in today_data:
        data_dic = {
            'content': today_datum.content,
            'id': today_datum.id,
            'publishTime': int(today_datum.publish_time.timestamp()) if today_datum.publish_time else None,
            'lawViolatedReason': '',
            'lawViolatedValue': '',
            'siteArticleCategory': today_datum.article_category or '',
            'siteCountry': today_datum.country or '',
            'siteIdentificationSource': today_datum.identification_source or '',
            'siteLanguage': today_datum.lang or '',
            'siteNotificationAgency': today_datum.notification_agency or '',
            'siteOrganizationType': today_datum.organization_type or '',
            'siteRegion': today_datum.region or '',
            'siteSubjectType': today_datum.subject_type or '',
            'siteRegionalScope': today_datum.regional_scope or '',
            'title': today_datum.title or '',
            'url': today_datum.url or ''
        }
        list_data.append(data_dic)

    result = {
        'list': list_data,
    }
    # 写入到本地
    file_name = str(uuid.uuid4()) + '_data.json'
    local_path = '/tmp/' + file_name
    with open(local_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    log.info('写入到本地完成，开始上传 cos')
    now = datetime.now()
    # 设置时区为中国标准时间
    tz = pytz.timezone('Asia/Shanghai')
    # 将当前时间转换为中国标准时间
    now = now.astimezone(tz)
    formated_time = now.strftime('%Y%m%d')
    key = f'/newsletter_data/{formated_time}/data.json'
    upload_file(local_path, key)
    log.info("上传完成, 上传数据{}条".format(len(list_data)))
