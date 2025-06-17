from bs4 import BeautifulSoup
from loguru import logger as log
import requests

base_url = 'https://www.legifrance.gouv.fr'


def get_links(index):
    # 假设这是你的网页URL，这里需要替换为实际的URL
    url = base_url + ('/search/cnil?tab_selection=cnil&searchField=ALL'
                      '&query=&searchProximity=&searchType=ALL&isAdvancedResult='
                      '&isAdvancedResult=&timeInterval=&typePagination=DEFAULT'
                      '&sortValue=DATE_DECISION_DESC&pageSize=10&tab_selection=cnil#cnil&page=') + str(index)

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

        # 查找所有 article 标签下的 a 标签
        article_links = soup.select('article a')

        # 提取所有 a 标签的 href 属性
        href_links = [link.get('href') for link in article_links if link.get('href')]

        # 打印所有 href 链接
        for link in href_links:
            print(link)

    except requests.RequestException as e:
        log.warning(f"请求发生错误: {e}")
    except Exception as e:
        log.warning(f"发生未知错误: {e}")
    return resp


if __name__ == '__main__':
    get_links(1)
    # for i in range(0, 20):
    #     links = get_links(i)
    #     for e in links:
    #         tmp = base_url + e
    #         print(f'insert into todo_url(url, source) value ("{tmp}", 4);')
