import hashlib
import json
import logging
import os

import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError, InvalidURL


class XkcdDownloader:
    API_URL = ['https://xkcd.com/', '/info.0.json']
    DIRECTORY = 'comics'
    TIMEOUT = 10
    HEADERS = {}

    def __init__(self) -> None:
        logging.basicConfig(
            format='[%(asctime)s][%(levelname)s] %(message)s',
            level=logging.INFO
            )
        self._create_directory()
        self._count_of_comic_downloads = 0

    @property
    def get_count_of_comic_downloads(self) -> int:
        return self._count_of_comic_downloads

    def make_download(self) -> None:
        last_comic_index = self._get_last_index_from_api()
        if last_comic_index:
            for index in range(1, last_comic_index + 1):
                self._download_image_file_for_comic(index)

    def _get_last_index_from_api(self) -> int:
        api_response = self._make_request(
            url=''.join(self.API_URL),
            except_log_message='in request last comic index from xkcd API'
            )
        if self._verify_reponse(api_response):
            json_from_api = json.loads(api_response.content)
            last_comic_index = json_from_api['num']
            logging.info(
                f'Last comic index (comic id): {last_comic_index}')
            return last_comic_index
        else:
            logging.warning(
                (f'Error {api_response.status_code}'
                    'when getting last comic index from xkcd API')
                )

    def _verify_reponse(self, response):
        if (isinstance(response, requests.models.Response)
                and response.status_code == 200):
            return True
        else:
            return False

    def _download_image_file_for_comic(self, comic_id: int) -> None:
        comic_img_url = self._get_img_comic_url(comic_id)
        if comic_img_url:
            response_for_image_file = self._make_request(
                url=comic_img_url,
                except_log_message=('in request for comic id '
                                    f'image file: {comic_id}')
                )
            if self._verify_reponse(response_for_image_file):
                response_headers = response_for_image_file.headers
                if self._content_is_a_image(response_headers):
                    md5 = self._get_md5_from_file(
                        response_for_image_file.content)
                    file_extension = response_headers['Content-Type'][6:]
                    img_name_file = f'{md5}.{file_extension}'
                    self._save_comic_img_file_in_local_storage(
                        img_name_file, response_for_image_file.content,
                        comic_id
                        )
                else:
                    logging.info(f'The file for comic id: '
                                 f'{comic_id} is not a image')
                    return
            else:
                logging.warning(f'Error {response_for_image_file.status_code} '
                                f'in request for comic id: {comic_id}')

    def _get_img_comic_url(self, comic_id: int) -> str:
        api_response = self._make_request(
            url=f'{self.API_URL[0]}{comic_id}{self.API_URL[1]}',
            except_log_message=f'in request comic id: {comic_id} from xkcd API'
        )
        if self._verify_reponse(api_response):
            json_from_api = json.loads(api_response.text)
            comic_img_url = json_from_api['img']
            comic_title = json_from_api['title']
            logging.info(f'URL from image comic id: {comic_id}, '
                         f'title: {comic_title}, has been obtained from xkcd API')
            return comic_img_url
        else:
            logging.warning(f'Error {api_response.status_code} '
                            f'in xkcd API request from comic id: {comic_id}')

    def _make_request(self, url: str,
                      except_log_message: str) -> requests.models.Response:
        try:
            return requests.get(
                url, headers=self.HEADERS, timeout=self.TIMEOUT
            )
        except (HTTPError, Timeout, ConnectionError, InvalidURL) as error:
            logging.error(f'{type(error).__name__} {except_log_message}')
        except Exception:
            logging.error(f'Some error ocurred {except_log_message}')

    def _content_is_a_image(self, headers: dict) -> bool:
        if (headers['Content-Type'].startswith('image')):
            return True
        else:
            return False

    def _save_comic_img_file_in_local_storage(self, name_img_file: str,
                                              img_file_content: bytes,
                                              comic_id: int) -> None:
        if not self._file_alredy_exist(f'{self.DIRECTORY}/{name_img_file}'):
            self._create_file_in_local_storage(
                file_name=name_img_file,
                file_content=img_file_content,
                info_log_msg=(f'Comic id: {comic_id} '
                              'has been downloaded '
                              f'with name: {name_img_file}'),
                error_log_msg=('when save file image'
                               f' for comic id: {comic_id} '
                               f'with name: {name_img_file}')
                )
        else:
            logging.info(f'File of Comic id: {comic_id} '
                         f'alredy exits with name: {name_img_file}')

    def _get_md5_from_file(self, file_content: bytes) -> str:
        md5_from_file = hashlib.md5()
        md5_from_file.update(file_content)
        return md5_from_file.hexdigest()

    def _file_alredy_exist(self, file_name: str) -> bool:
        if os.path.isfile(file_name):
            return True
        else:
            return False

    def _create_file_in_local_storage(self, file_name: str,
                                      file_content: bytes,
                                      info_log_msg: str = '',
                                      error_log_msg: str = '') -> None:
        try:
            with open(f'{self.DIRECTORY}/{file_name}', 'wb') as img_file:
                img_file.write(file_content)
            self._count_of_comic_downloads += 1
            logging.info(info_log_msg)
        except (IsADirectoryError, PermissionError,
                FileNotFoundError) as error:
            logging.error(f'{type(error).__name__} {error_log_msg}')

    def _create_directory(self) -> None:
        try:
            os.mkdir(self.DIRECTORY)
            logging.info(f'The directory:"{self.DIRECTORY}/" has been created')
        except FileExistsError:
            logging.info(f'The directory:"{self.DIRECTORY}/" alredy exists')
        except PermissionError as error:
            logging.error(f'{type(error).__name__} '
                          f'when create directory "{self.DIRECTORY}/"')
            exit()
