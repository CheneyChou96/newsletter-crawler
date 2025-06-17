import requests
import json

base_url = 'http://47.79.23.160:3002'


def scrape(url: str, formats=None, config_params: dict = None):
    if formats is None:
        formats = ['markdown']

    body_data = {
        'url': url,
        'formats': formats,
        'timeout': 360000
    }

    if config_params:
        body_data.update(config_params)

    resp = requests.post(base_url + '/v1/scrape', headers={
        'content-type': 'application/json',
    }, data=json.dumps(body_data))

    if resp.status_code == 200:
        return resp.json()
    else:
        raise Exception(f"Error: {resp.status_code} - {resp.text}")
