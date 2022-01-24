import re
import requests
import json

from logging import Logger
from datetime import datetime
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, Timeout, ConnectionError



class Downloader():
    ARCHIVE_PAGE_URL = 'https://xkcd.com/archive/'
    COMIC_BASE_URL = 'https://imgs.xkcd.com/comics/'
    URL_API = ['https://xkcd.com/', '/info.0.json']

    def comics_downolad(self) -> None:
        data_info_comics = self._get_data_info_slugs()
        response = ''
        key = ''
        for key in data_info_comics.keys():
            response = self._request_img_file(f'{self.COMIC_BASE_URL}{data_info_comics[key]}')
            if response.status_code == 200:
                self._show_logger(f'[Info] Comic title {data_info_comics[key]} id:  {key[1:-1]} has been downloaded.')
            else:
                pass

    def _request_img_in_api(self, comic_id: str) -> None:
        try:
            api_response = requests.get(self.URL_API[0] + comic_id + self.URL_API[1] , timeout=10)
            if api_response.status_code != 200:
                self._show_logger(
                   f'[Warning] Error {api_response.status_code} in API request from comic id {comic_id}')
                return
            comic_img_url = json.loads(api_response.content)['img']
            if comic_img_url[-1:] == '/':
                return

            img_response = requests.get(comic_img_url , timeout=10)
            if img_response.status_code == 200:
                comic_title = comic_img_url[::-1].split('/')[0][:3:-1]
                self._show_logger(f'[Info] Comic title {comic_title} id:  {comic_id} has been downloaded.')
                return
            else:
                self._show_logger(
                    f'[Warning] Error {api_response.status_code} in API request from comic id {comic_id}')
                return
        
        except HTTPError:
            self._show_logger(
                f'[Warning] HTTPError {self.ARCHIVE_PAGE_URL}')
        except Timeout:
            self._show_logger(
                f'[Warning] Timeout {self.ARCHIVE_PAGE_URL}')
        except ConnectionError:
            self._show_logger(
                f'[Warning] ConnectionError {self.ARCHIVE_PAGE_URL}')
        exit()
             
    def _request_img_file(self, url:str) -> requests.models.Response:
        extencions_list = ['.png', '.jpg']
        for extencion in extencions_list:
            try:
                return requests.get(url + extencion, timeout=10)
            except HTTPError:
                self._show_logger(
                    f'[Warning] HTTPError {self.ARCHIVE_PAGE_URL}')
            except Timeout:
                self._show_logger(
                    f'[Warning] Timeout {self.ARCHIVE_PAGE_URL}')
            except ConnectionError:
                self._show_logger(
                    f'[Warning] ConnectionError {self.ARCHIVE_PAGE_URL}')
            exit()



    def _get_data_info_slugs(self) -> dict:
        response = self._get_request_archive_page()
        if response.status_code != 200:
            self._show_logger(
                f'[Warning] Error {response.status_code} getting Archive page')
            exit()
        data_info_comics = self._parser_html_page(response.content)
        self._show_logger(f'[Info] {len(data_info_comics)} comics found.')
        return data_info_comics

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

    def _parser_html_page(self, html_page: bytes) -> dict:
        html_page = BeautifulSoup(html_page, 'html.parser')
        middleContainer = html_page.find('div', id='middleContainer')
        anchors = middleContainer.select('a')
        data_info_comics = {}
        for anchor in anchors:
            data_info_comics.update(
                {f'{anchor.attrs.get("href")}':
                 (self._clean_slug(str(anchor.string)))}
            )
        return data_info_comics

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
instance._request_img_in_api('1663')
