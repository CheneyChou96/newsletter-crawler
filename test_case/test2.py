import requests
from bs4 import BeautifulSoup
from loguru import logger


def get_links_from_page(index: str):
    # 假设这是你的网页URL，这里需要替换为实际的URL
    url = 'https://www.edps.europa.eu/press-publications/press-news/news_en' + index

    resp = []

    try:
        # 发送HTTP请求获取网页内容
        response = requests.get(url)
        # 检查请求是否成功
        response.raise_for_status()

        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找类名为view-content的元素
        view_content = soup.find(class_='view-content')
        if view_content:
            # 查找类名为node__content clearfix的元素
            node_contents = view_content.find_all(class_='node node--type-edpsweb-news node--promoted clearfix')
            for node_content in node_contents:
                data = {
                    'url': None,
                    'news_id': None,
                }
                # 查找所有的a标签
                a_tags = node_content.find_all('a')
                for a_tag in a_tags:
                    # 获取a标签的href属性
                    link = a_tag.get('href')
                    news_id = a_tag.get('id')
                    if news_id:
                        # 获取id值
                        data['news_id'] = news_id
                    if link:
                        if not link.startswith('http'):
                            link = 'https://www.edps.europa.eu' + link
                        data['url'] = link
                resp.append(data)
        else:
            logger.warning("未找到类名为view-content的元素。")

    except requests.RequestException as e:
        logger.warning(f"请求发生错误: {e}")
    except Exception as e:
        logger.warning(f"发生未知错误: {e}")
    return resp


if __name__ == '__main__':

    # for i in range(0, 57):
    get_links_from_page('?page=31')


