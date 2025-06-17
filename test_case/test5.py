import json

from bs4 import BeautifulSoup
from loguru import logger as log
import requests

base_url = 'https://cnil.fr'


def get_total_page():
    resp = requests.get('https://cnil.fr/fr/actualite')

    # 创建 BeautifulSoup 对象
    soup = BeautifulSoup(resp.text, 'html.parser')

    # 查找带有类名 pager__item pager__item--last 的 li 元素
    li_element = soup.find('li', class_='pager__item pager__item--last')

    if li_element:
        # 查找 li 元素下的 a 标签
        a_element = li_element.find('a')
        if a_element:
            # 获取 a 标签的 href 属性值
            href_value = a_element.get('href')
            return href_value.split('=')[1]
        else:
            print("未找到 li 元素下的 a 标签。")
    else:
        print("未找到带有类名 pager__item pager__item--last 的 li 元素。")


def get_links(page):

    url = ('https://cnil.fr/fr/views/ajax?_wrapper_format=drupal_ajax&view_name=type_d_article'
           '&view_display_id=block&view_args=41&view_path=%2Ftaxonomy%2Fterm%2F41&view_base_path='
           '&pager_element=0&_drupal_ajax=1&page=' + str(page))

    resp = []

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'priority': 'u=1, i',
        'referer': 'https://cnil.fr/fr/actualite',
        'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        'x-requested-with': 'XMLHttpRequest',
        'Cookie': 'SERVERID=dvs12649.eva.produhost.net'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        resp_json = response.json()
        for one_json in resp_json:
            if one_json['command'] == 'insert':
                data = one_json['data']
                data_soup = BeautifulSoup(data, 'html.parser')
                # 获取所有h3标签下a标签的href
                a_tags = data_soup.find_all('h3')
                for a_tag in a_tags:
                    href = a_tag.find('a')
                    if href:
                        resp.append(base_url + href.get('href'))
                return resp

    except requests.exceptions.HTTPError as http_err:
        log.warning(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as req_err:
        log.warning(f'Request error occurred: {req_err}')
    except ValueError as json_err:
        log.warning(f'JSON decoding error occurred: {json_err}')

    return resp


if __name__ == '__main__':
    # total_page = get_total_page()
    # # 19
    # print(f'total page is: {total_page}')
    # for i in range(0, int(total_page) + 1):
    #     links = set(get_links(i))
    #     for e in links:
    #         print(f'insert into todo_url(url, source) value ("{e}", 5);')
    links = set(get_links(85))
    for e in links:
        print(f'insert into todo_url(url, source) value ("{e}", 5);')
