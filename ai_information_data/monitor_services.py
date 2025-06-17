from ai_information_data.dao import get_monitor_site, update_site
from loguru import logger
import requests
from bs4 import BeautifulSoup
from utils.fire_crawl_utils import scrape
from test_case.test2 import get_links_from_page


async def monitor_service():
    sites = await get_monitor_site()
    # global_privacy_assembly_org()
    await edps_news(sites)
    logger.info('edps_news finish...')


def global_privacy_assembly_org():
    url = 'https://globalprivacyassembly.org/news-events/latest-news/'
    logger.info('global_privacy_assembly_org start...')

    scrape(url, formats=['markdown'])

    # 获取网页 类名 content 下第一个 类名views-row 下 article标签下带有id='news_xxxx'的id值
    # 例如：id='news_1234'
    # 发送GET请求获取网页内容
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
                  'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(response.text)
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP 错误发生: {http_err}')
        return None
    except Exception as err:
        print(f'其他错误发生: {err}')
        return None

    if response.status_code == 200:
        # 使用BeautifulSoup解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到类名为content的元素
        content_element = soup.find(class_='content')
        if content_element:
            # 在content元素下找到第一个类名为views-row的元素
            views_row_element = content_element.find(class_='views-row')
            if views_row_element:
                # 在views-row元素下找到article标签且带有id属性的元素
                article_element = views_row_element.find('article',
                                                         id=lambda value: value and value.startswith('news_'))
                if article_element:
                    # 获取id值
                    article_id = article_element['id']
                    print(article_id)
                else:
                    logger.warning("未找到符合条件的article标签")
            else:
                logger.warning("未找到类名为views-row的元素")
        else:
            logger.warning("未找到类名为content的元素")
    else:
        logger.warning(f"请求失败，状态码: {response.status_code}")


async def edps_news(sites):
    url = 'https://www.edps.europa.eu/press-publications/press-news/news_en'
    logger.info('edps_news start...')

    # 获取最新一条数据的id
    news_id = None
    response = requests.get(url)

    if response.status_code != 200:
        logger.warning(f"请求失败，状态码: {response.status_code}")
        return

        # 使用BeautifulSoup解析网页内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到类名为content的元素
    main_element = soup.find(id='main')
    if main_element:
        # 在content元素下找到第一个类名为views-row的元素
        views_row_element = main_element.find(class_='views-row')
        if views_row_element:
            # 在views-row元素下找到article标签且带有id属性的元素
            news_elements = views_row_element.find('a',
                                                   id=lambda value: value and value.startswith('news_'))
            if news_elements:
                # 获取id值
                news_id = news_elements['id']
            else:
                logger.warning("未找到符合条件的article标签")
        else:
            logger.warning("未找到类名为views-row的元素")
    else:
        logger.warning("未找到类名为content的元素")

    if news_id is None:
        logger.warning("未找到新闻id")
        return

    # 数据库对比最新的id
    db_data = None
    for item in sites:
        if item['url'] == url:
            db_data = item
            break
    if db_data.latest_url is not None and db_data.latest_url == news_id:
        logger.info("{},没有新的数据".format(url))
        return

    # 查找总页码
    # 查找第一个同时带有 page-item 和 page-item-last 类名的标签
    target_tag = soup.find(class_=" ".join(["page-item", "page-item-last"]))

    if target_tag:
        # 在该标签内查找 a 标签
        a_tag = target_tag.find('a')
        if a_tag:
            # 获取 a 标签的 href 属性值
            total_page = a_tag.get('href')
            logger.info("total_page: {}".format(total_page))
        else:
            logger.warning("未找到符合条件的a标签")
            return
    else:
        logger.warning("未找到同时带有 page-item 和 page-item-last 类名的标签。")
        return

    if db_data.latest_url is None:
        logger.warning('数据库未记录，需要爬取全量数据')

    # total_page：?page=1
    # 根据=号分割字符串，获取第二部分
    page_number = total_page.split('=')[1]
    for i in range(0, int(page_number) + 1):
        resp_data = get_links_from_page(f'?page={i}')
        for one_data in resp_data:
            if (one_data['news_id'] is not None and db_data.latest_url is not None
                    and one_data['news_id'] == db_data.latest_url):
                logger.info("找到上次爬取id，{}: url: {}, id: {},最新的id是："
                            "{}".format(url, one_data['url'], db_data.latest_url, news_id))
                # 更新数据库最新的id
                await update_site(db_data.id, news_id)
                return
            scrape_url = one_data['url']
            if scrape_url is not None:
                logger.info('开始爬取url: {}'.format(scrape_url))
                try:
                    scrape_resp = scrape(scrape_url, formats=['markdown'])
                    logger.info('scrape_resp: {}'.format(scrape_resp))
                except Exception as e:
                    logger.warning('爬取失败: {}'.format(e))
                    continue

    # 更新数据库最新的id
    await update_site(db_data.id, news_id)
