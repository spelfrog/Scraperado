import os
import time

import graphyte
import requests
from bs4 import BeautifulSoup


def get_body() -> str:
    r = requests.get(
        'https://www.boulderado.de/boulderadoweb/gym-clientcounter/index.php',
        params={
            'mode': 'get',
            'token': os.environ['boulderado_token']
        })
    if r.status_code == 200:
        return r.text
    else:
        raise ConnectionError(f"boulderado request failed with code {r.status_code}")


def scrape_data(body: str) -> dict[str, int]:
    soup = BeautifulSoup(body, 'html.parser')
    keywords = ['act', 'free']

    return {key: int(soup.find(class_=f'{key}counter')['data-value']) for key in keywords}


def send_to_graphite(data: dict[str, int]):
    graphyte.init(os.environ['graphite_host'], prefix=os.environ['graphite_path'])
    for key, value in data.items():
        graphyte.send(key, value)


if __name__ == "__main__":
    while True:
        send_to_graphite(scrape_data(get_body()))
        time.sleep(os.environ.get("sleep_time", 300))
