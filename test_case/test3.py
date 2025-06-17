from bs4 import BeautifulSoup
from loguru import logger as log
import requests

base_url = 'https://noyb.eu'


def get_links(index):
    # 假设这是你的网页URL，这里需要替换为实际的URL
    url = base_url + '/en/news?page=' + str(index)

    resp = []

    try:
        # 发送HTTP请求获取网页内容
        response = requests.get(url)
        # 检查请求是否成功
        response.raise_for_status()

        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找具有 item-list-top 类名的 ul 元素
        ul_elements = soup.find_all('ul', class_=['item-list-top', 'item-list-bottom'])

        # 遍历每个 ul 元素
        for ul in ul_elements:
            # 查找 ul 元素下的所有 li 元素
            li_elements = ul.find_all('li')
            # 遍历每个 li 元素
            for li in li_elements:
                # 查找 li 元素下的 a 标签
                a_tag = li.find('a')
                if a_tag:
                    # 获取 a 标签的 href 属性
                    href = a_tag.get('href')
                    if href:
                        resp.append(href)

    except requests.RequestException as e:
        log.warning(f"请求发生错误: {e}")
    except Exception as e:
        log.warning(f"发生未知错误: {e}")
    return resp


if __name__ == '__main__':
    for i in range(0, 20):
        links = get_links(i)
        for e in links:
            tmp = base_url + e
            print(f'insert into todo_url(url, source) value ("{tmp}", 3);')
