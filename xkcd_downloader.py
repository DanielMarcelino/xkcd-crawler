import hashlib
import json
import logging
import os

import requests

from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import HTTPError, Timeout, ConnectionError, InvalidURL

class XkcdDownloader:
    
    URL_API = ['https://xkcd.com/', '/info.0.json']
    DIRECTORY = 'comics'
    TIMEOUT = 10
    HEADERS = {}
    
    def __init__(self) -> None:
        logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.INFO)
        self._create_directory()
        self._setlist_files_in_directory = {file_name for file_name in os.listdir(f'{self.DIRECTORY}/')}

    def make_download(self):
        last_comic_index = self._get_last_index_from_api()
        if last_comic_index:
            with ThreadPoolExecutor(max_workers=8) as executor:
                executor.map(self._download_image_file_for_comic, range(1, last_comic_index + 1))
            # for index in range(1, last_comic_index + 1):
            #     self._download_image_file_for_comic(index)
            pass
   
    def _get_last_index_from_api(self) -> int:
        api_response = self._make_request(
            url=''.join(self.URL_API),
            except_log_message='in request last comic index from API'
        )
        if isinstance(api_response, requests.models.Response):
            if api_response.status_code == 200:
                json_from_api = json.loads(api_response.content)
                last_comic_index = json_from_api['num']
                logging.info(f'Last comic index (comic id): {last_comic_index}')
                return last_comic_index
            else:
                logging.warning(f'Error {api_response.status_code} when getting last comic index from API')
        
        
    def _get_comic_url_img_from_api(self, comic_id: int) -> str:
        api_response = self._make_request(
            url=f'{self.URL_API[0]}{comic_id}{self.URL_API[1]}',
            except_log_message=f'in request comic id: {comic_id} from API'
        )
        if isinstance(api_response, requests.models.Response):
            if api_response.status_code == 200:
                json_from_api = json.loads(api_response.content)
                comic_img_url = json_from_api['img']
                comic_title = json_from_api['title']
                logging.info(f'URL from image comic id: {comic_id}, title: {comic_title}, has been obtained from API')
                return comic_img_url
            else:
                logging.warning(f'Error {api_response.status_code} in API request from comic id: {comic_id}')

    def _download_image_file_for_comic(self, comic_id: int) -> None:
        comic_img_url = self._get_comic_url_img_from_api(comic_id)
        if comic_img_url:
            response_for_image_file = self._make_request(
                url=comic_img_url,
                except_log_message=f'in request for comic id image file: {comic_id}'
            )
            if isinstance(response_for_image_file, requests.models.Response):
                if response_for_image_file.status_code == 200:
                    md5 = self._get_md5_from_file(response_for_image_file.content)
                    extension_file = comic_img_url[-4:]
                    name_img_file = md5 + extension_file 
                    self._save_img_file_in_disk(name_img_file, response_for_image_file.content)
                    logging.info(f'Comic id: {comic_id} has been downloaded with name: {name_img_file}')
                else:
                    logging.warning(f'Error {response_for_image_file.status_code} in request for comic id: {comic_id}')
                    return None
    
    def _make_request(self, url: str, except_log_message: str) -> requests.models.Response:
        try:
            return requests.get(url, headers=self.HEADERS, timeout=self.TIMEOUT)
        except (HTTPError, Timeout, ConnectionError, InvalidURL) as error:
            logging.error(f'{type(error).__name__} {except_log_message}')
        except:
            logging.error(f'Some error ocurred {except_log_message}')

    def _create_directory(self) -> None:
        try:
            os.mkdir(self.DIRECTORY)
            logging.info(f'The directory:"{self.DIRECTORY}/" has been created')
        except FileExistsError:
            logging.info(f'The directory:"{self.DIRECTORY}/" alredy exists')
        except PermissionError as error:
            logging.error(f'{type(error).__name__} when create directory "{self.DIRECTORY}/"')

    def _get_md5_from_file(self, file_content: bytes) -> str:
        md5_from_file = hashlib.md5()
        md5_from_file.update(file_content)
        return  md5_from_file.hexdigest()

    def _save_img_file_in_disk(self, file_name: str, file_content: bytes):
        if file_name not in self._setlist_files_in_directory:
            try:
                with open(f'{self.DIRECTORY}/{file_name}', 'wb') as img_file:
                    img_file.write(file_content)
            except:
                print(f"Erro {file_name}")

instance = XkcdDownloader()
instance.make_download()