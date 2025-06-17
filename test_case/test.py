from utils.fire_crawl_utils import scrape
from ai_information_data.dao import save_scraped_data

if __name__ == '__main__':
    url = 'https://baijiahao.baidu.com/s?id=1666047746833809358&wfr=spider&for=pc'
    resp = scrape(url)
    save_scraped_data(resp, url, 0, 0, None, None, {'ext': 'test2232'})
