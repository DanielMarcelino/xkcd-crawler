import re
import requests
import json
import os
import hashlib

from  concurrent.futures import ThreadPoolExecutor
from logging import Logger
from datetime import datetime
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, Timeout, ConnectionError


class Downloader():
    def __init__(self) -> None:
        self._create_directory()
        self.setlist_files_in_directory = {file_name for file_name in os.listdir(f'{self.DIRECTORY}/')}
        self.counts = {'.png': 0, '.jpg': 0, '.gif': 0, 'other': 0, 'total': 0}
        
    ARCHIVE_PAGE_URL = 'https://xkcd.com/archive/'
    COMIC_BASE_URL = 'https://imgs.xkcd.com/comics/'
    URL_API = ['https://xkcd.com/', '/info.0.json']
    DIRECTORY = 'comics'

    def _create_directory(self) -> None:
        try:
            os.mkdir(self.DIRECTORY)
        except FileExistsError:
            pass
        except PermissionError:
            pass


    def comics_download(self) -> None:
        data_info_comics = self._get_data_info_slugs()
        with ThreadPoolExecutor(max_workers=8) as executor:
            for key in data_info_comics.keys():
                executor.submit(self._img_download, data_info_comics[key], key[1:-1])


    def _img_download(self, slug: str, img_id: str) -> None:
        response = self._request_img_file(slug, img_id)
        if response.status_code == 200:
            if not response.content.startswith(b'<html>'):
                extension = ''
                if response.content.startswith(b'\x89PNG'):
                    extension = 'png'
                elif response.content.startswith(b'GIF'):
                    extension = 'gif'
                elif response.content.startswith(b'\xff'):
                    extension = 'jpg'
                else:
                    extension = 'NULL' #para teste

                if self._save_img_file_in_disk(f'{self._get_md5_from_file(response.content)}.{extension}', response.content):
                    self._show_logger(f'[Info] Comic title: {slug} id:  {img_id} has been downloaded.')
                else:
                    self._show_logger(f'[Info] Comic title: {slug} id:  {img_id} alredy exists.')
                
        else:
            self._show_logger(f'[Error] {response.status_code} during the comic download  title: {slug} id:  {img_id}.')
    
    def _get_md5_from_file(self, file_content: bytes) -> str:
        md5_from_file = hashlib.md5()
        md5_from_file.update(file_content)
        md5_from_file = str(md5_from_file.hexdigest())
        return md5_from_file

    def _save_img_file_in_disk(self, file_name: str, file_content: bytes) -> bool:
        self.counts[f'{file_name[-4:]}'] += 1
        self.counts['total'] += 1
        print(self.counts)
        try:
            if file_name not in self.setlist_files_in_directory:
                with open(f'{self.DIRECTORY}/{file_name}', 'wb') as img_file:
                    img_file.write(file_content)
                return True 
        except PermissionError:
            return False
            pass

    def _request_img_from_slug(self, comic_slug:str) -> requests.models.Response:
        extensions_list = ['.png', '.jpg']
        for extension in extensions_list:
            response = requests.get(self.COMIC_BASE_URL + comic_slug + extension, timeout=10)
            if response.status_code == 200:
                self.arquive_counts[extension] += 1
                return response
        return None
    
    def _request_img_from_api(self, comic_id:str) -> requests.models.Response:
        api_response = requests.get(self.URL_API[0] + comic_id + self.URL_API[1] , timeout=10)
        if api_response.status_code != 200:
            self._show_logger(
                f'[Warning] Error {api_response.status_code} in API request from comic id {comic_id}')
            return None
        comic_img_url = json.loads(api_response.content)['img']
        return requests.get(comic_img_url , timeout=10)

    def _request_img_file(self, comic_slug:str, comic_id:str) -> requests.models.Response:
        try:
            response_from_slug_request = self._request_img_from_slug(comic_slug)
            if response_from_slug_request:
                return response_from_slug_request
            
            return self._request_img_from_api(comic_id)
        except HTTPError:
            self._show_logger(
                f'[Warning] HTTPError {self.ARCHIVE_PAGE_URL}')
        except Timeout:
            self._show_logger(
                f'[Warning] Timeout {self.ARCHIVE_PAGE_URL}')
        except ConnectionError:
            self._show_logger(
                f'[Warning] ConnectionError {self.ARCHIVE_PAGE_URL}')
        return None

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
instance.comics_download()

"""
verificar arquivos com extenção .false
"""