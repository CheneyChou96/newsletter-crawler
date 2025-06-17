import json

from bs4 import BeautifulSoup
from loguru import logger as log
import requests

base_url = 'https://www.autoritedelaconcurrence.fr/'


def get_total_page():
    resp = requests.get('https://www.autoritedelaconcurrence.fr/fr/'
                        'communiques-de-presse?field_sector_target_id=All&year=All&page=0')

    # 创建 BeautifulSoup 对象
    soup = BeautifulSoup(resp.text, 'html.parser')

    # 查找带有类名 pager__item pager__item--last 的标签下的 a 标签
    last_page_link = soup.find('li', class_='pager__item pager__item--last')
    if last_page_link:
        a_tag = last_page_link.find('a')
        if a_tag:
            href_value = a_tag.get('href')
            if href_value:
                # 提取 page 参数的值
                import urllib.parse
                parsed_url = urllib.parse.urlparse(href_value)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                page_value = query_params.get('page')
                if page_value:
                    return page_value[0]
                else:
                    log.warning("未找到 page 参数的值。")
            else:
                log.warning("未找到 a 标签的 href 属性。")
        else:
            log.warning("未找到带有类名 pager__item pager__item--last 的标签下的 a 标签。")
    else:
        log.warning("未找到带有类名 pager__item pager__item--last 的标签。")
    return None


def get_links(page):
    url = ('https://www.autoritedelaconcurrence.fr/fr'
           '/communiques-de-presse?field_sector_target_id=All&year=All&page=' + str(page))

    resp = []

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找所有带有 views-row 类的元素
        views_rows = soup.find_all(class_='views-row')

        # 用于存储所有 a 标签的 href 值
        href_values = []

        # 遍历每个 views-row 元素
        for row in views_rows:
            # 在每个 views-row 元素中查找 h2 标签
            h2_tags = row.find_all('h2')
            for h2 in h2_tags:
                # 在每个 h2 标签中查找 a 标签
                a_tags = h2.find_all('a')
                for a in a_tags:
                    # 获取 a 标签的 href 属性值
                    href = a.get('href')
                    if href:
                        href_values.append(href)

        # 打印所有获取到的 href 值
        for href in href_values:
            resp.append(base_url + href)

    return resp


if __name__ == '__main__':
    total_page = get_total_page()
    links_list = set()
    for i in range(int(total_page)):
        print(f'#第{i + 1}页')
        links = get_links(i)
        for link in links:
            links_list.add(link)

    for link in links_list:
        print(f'insert into todo_url(url, source) values("{link}", 1);')

