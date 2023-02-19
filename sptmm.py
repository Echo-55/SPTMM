import webbrowser

import requests
from bs4 import BeautifulSoup

from spt_utils import Config, Utils


class ModManager:
    def __init__(self, cfg: Config):
        cfg.read_config()

    def parse_urls(self, url):
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, features="html.parser")
        dl_button = soup.find_all(attrs={"itemprop": "downloadUrl"})
        dl_link = dl_button[0].get("href")
        self.open_browser(dl_link)

    def open_browser(self, url):
        webbrowser.open_new_tab(url)
