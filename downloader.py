from logging import Logger
import re
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError
from datetime import datetime


class Downloader():
    ARCHIVE_PAGE_URL = 'https://xkcd.com/archive/'
    COMIC_BASE_URL = 'https://imgs.xkcd.com/comics/'

    def _get_comic_slugs(self) -> dict:
        response = self._get_request_archive_page()
        if response.status_code != 200:
            self._show_logger(
                f'[Warning] Error {response.status_code} getting Archive page')
            exit()
        return self._get_dict_slugs(response.content)

    def _get_request_archive_page(self) -> requests.models.Response:
        try:
            return requests.get(Downloader.ARCHIVE_PAGE_URL, timeout=10)
        except HTTPError:
            self._show_logger(
                f'[Warning] HTTPError {Downloader.ARCHIVE_PAGE_URL}')
        except Timeout:
            self._show_logger(
                f'[Warning] Timeout {Downloader.ARCHIVE_PAGE_URL}')
        except ConnectionError:
            self._show_logger(
                f'[Warning] ConnectionError {Downloader.ARCHIVE_PAGE_URL}')
        exit()

    def _get_dict_slugs(self, html_page: bytes) -> dict:
        html_page = BeautifulSoup(html_page, 'html.parser')
        middleContainer = html_page.find('div', id='middleContainer')
        anchors = middleContainer.select('a')
        slug_dict = {}
        for anchor in anchors:
            slug_dict.update(
                {f'{anchor.attrs.get("href")}':
                 (self._clean_slug(anchor.string))}
            )
        return slug_dict

    def _clean_slug(self, title: str) -> str:
        if re.match('^[\W -]*$', title):
            return re.sub(r'[ -]+', '_', re.sub(
                r'[/]+', '', title.strip().lower()))
        else:
            return re.sub(r'[ -]+', '_', re.sub(
                r'[^A-z\d -]+', '', title.strip().lower()))

    def _get_requests(self, url: str) -> bytes:
        try:
            return requests.get(Downloader.ARCHIVE_PAGE_URL)
        except HTTPError:
            return HTTPError

    def _show_logger(self, message_log: str) -> None:
        hour = datetime.now().strftime('[%y/%m/%d %H:%M]')
        print(hour, f'{message_log}')


instance = Downloader()
instance._get_comic_slug()
