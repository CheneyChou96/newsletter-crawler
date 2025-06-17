import json

import requests
from ai_information_data.models import AiInformationDataReq
from loguru import logger as log

base_url = 'https://testai.ilaw.law/consumer-gateway/consumer-ai-server'
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzeXN0ZW1JZCI6IkNPTlNVTUVSX0FJIiwicGhvbmUiOiIxNTUyMzMxMjgzMSIsImV4cCI6MTc0NjY5NjQ3NywidXNlcklkIjoiMTg4OTUxMzg0NzUwOTcwMDYxMCJ9.M1Ws4GdaXQ13SBiTqaqV4_Cv1YGRtR0RR3e9u0iHf5M'


def get_data(response, api, print_result: bool = True):
    if response.status_code == 200:
        if response.json()['code'] == 0:
            result_data = response.json()['data']
            if print_result:
                log.success(f'{api} is request success and result is {response.json()}')
            else:
                log.success(f'{api} is request success')
            return result_data
        else:
            log.error(f'failed, error: {response.json()}')
    else:
        log.error('request failed, status code: {}'.format(response.status_code))
    return None


def post_request(api: str, data: dict, print_result: bool = True):
    log.info('post request: {}, and param is {}'.format(api, data))
    resp = requests.post(base_url + api, headers={
        'content-type': 'application/json; charset=utf-8',
        'token': token
    }, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))

    return get_data(resp, api, print_result)


def get_request(api: str, data: dict):
    resp = requests.get(base_url + api, headers={
        'token': token,
    })
    return get_data(resp, api)


def save(data: AiInformationDataReq):
    api = '/api/v1/crawl/data/save'
    return post_request(api, data.__dict__)


def todo_urls(source: int):
    api = '/api/v1/todoUrl/get'
    return post_request(api, {'source': source, 'status': 0})


def complete(data_id):
    api = '/api/v1/todoUrl/complete/' + str(data_id)
    return post_request(api, {})


def failed_urls(deep: int, source: int, ge_create_date: str):
    api = '/api/v1/crawl/data/get'
    return post_request(api, {'deep': deep, 'source': source, 'failed': True, 'geCreateDate': ge_create_date})

def count_tag_num():
    api = '/api/v1/crawl/data/get'
    return post_request(api, {'tagStatus': 1}, False)

def monitor_site_list():
    api = '/api/v1/monitorSite/list'
    return get_request(api, {})


def update_site_db(db_id, latest_url):
    pass


#
# {
#             "id": "1909520778638151681",
#             "title": "Comment faire la une des journaux grâce au RGPD et une violation de données ? | CNIL",
#             "continent": null,
#             "country": null,
#             "publishColumns": null,
#             "lang": "fr",
#             "sourceUrl": "",
#             "metadata": "{\"title\":\"",\"favicon\":\"",\"language\":\"fr\",\"ogTitle\":\"Comment faire la une des journaux grâce au RGPD et une violation de données ?\",\"ogLocaleAlternate\":[],\"scrapeId\":\"c4add4f6-1702-483b-89b0-553439525f88\",\"viewport\":[\"width=device-width, initial-scale=1.0\",\"width=device-width, initial-scale=1.0\"],\"og:title\":\"Comment faire la une des journaux grâce au RGPD et une violation de données ?\",\"MobileOptimized\":\"width\",\"HandheldFriendly\":\"true\",\"sourceURL\":\"https://cnil.fr/fr/comment-faire-la-une-des-journaux-grace-au-rgpd-et-une-violation-de-donnees\",\"url\":\"https://cnil.fr/fr/comment-faire-la-une-des-journaux-grace-au-rgpd-et-une-violation-de-donnees\",\"statusCode\":200,\"region\":\"欧盟\",\"countryOrAreas\":\"法国\",\"subjectType\":\"官方机构\",\"orgType\":\"政府\",\"notificationAgency\":\"Commission Nationale de l''Informatique et des Libertés - CNIL\",\"articleClass\":\"监管资讯\",\"identifySource\":\"数据保护\",\"siteLang\":\"法语\",\"cCountry\":\"全国\"}",
#             "status": "success",
#             "deep": 0,
#             "markdown": "",
#             "pid": null,
#             "path": "1909520757829939200",
#             "source": 5,
#             "urls": [
#                 "https://www.cnil.fr/sites/cnil/files/2024-03/cnil_guide_securite_personnelle_2024.pdf",
#                 "https://www.cnil.fr/sites/cnil/files/2025-04/infog-une-journaux.pdf",
#                 "https://cnil.fr/sites/cnil/files/2025-04/infog-une-journaux.pdf"
#             ]
#         }
def deep_urls(data: dict):
    api = '/api/v1/crawl/data/deep'
    return post_request(api, data)


def run_tag(data: dict):
    api = '/api/v1/crawl/data/runTag'
    return post_request(api, data)


def push_tj_cos(data: dict):
    api = '/api/v1/crawl/data/pushTj'
    return post_request(api, data)


def update_failed_data(data: dict):
    api = '/api/v1/crawl/data/updateFailData'
    return post_request(api, data)
