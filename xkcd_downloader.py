import hashlib
import json
import logging
import os

import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError, InvalidURL


class XkcdDownloader:
    URL_API = ['https://xkcd.com/', '/info.0.json']
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
                logging.info(
                    f'Last comic index (comic id): {last_comic_index}')
                return last_comic_index
            else:
                logging.warning(
                    (f'Error {api_response.status_code}'
                        'when getting last comic index from API')
                )

    def _download_image_file_for_comic(self, comic_id: int) -> None:
        comic_img_url = self._get_comic_url_img_from_api(comic_id)
        if comic_img_url:
            response_for_image_file = self._make_request(
                url=comic_img_url,
                except_log_message=('in request for comic id '
                                    f'image file: {comic_id}')
            )
            if isinstance(response_for_image_file, requests.models.Response):
                if response_for_image_file.status_code == 200:
                    if (
                        response_for_image_file.headers
                        ['Content-Type'].startswith('image')
                    ):
                        md5 = self._get_md5_from_file(
                            response_for_image_file.content)
                        extension_file = comic_img_url[-4:]
                        name_img_file = md5 + extension_file
                        self._save_img_file_in_disk(
                            name_img_file,
                            response_for_image_file.content,
                            comic_id
                        )
                    else:
                        logging.info(
                            f'The file for comic id: {comic_id} is not a image'
                        )
                        return
                else:
                    logging.warning(
                        (f'Error {response_for_image_file.status_code} '
                            f'in request for comic id: {comic_id}')
                    )

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
                logging.info(
                    (f'URL from image comic id: {comic_id}, '
                        f'title: {comic_title}, has been obtained from API')
                )
                return comic_img_url
            else:
                logging.warning(
                    (f'Error {api_response.status_code} '
                        f'in API request from comic id: {comic_id}')
                )

    def _make_request(
        self, url: str, except_log_message: str
    ) -> requests.models.Response:
        try:
            return requests.get(
                url, headers=self.HEADERS, timeout=self.TIMEOUT
            )
        except (HTTPError, Timeout, ConnectionError, InvalidURL) as error:
            logging.error(f'{type(error).__name__} {except_log_message}')
        except Exception:
            logging.error(f'Some error ocurred {except_log_message}')


    def _save_img_file_in_disk(
        self, file_name: str, file_content: bytes, comic_id: int
    ) -> None:
        if not os.path.isfile(f'{self.DIRECTORY}/{file_name}'):
            try:
                with open(f'{self.DIRECTORY}/{file_name}', 'wb') as img_file:
                    img_file.write(file_content)
                self._count_of_comic_downloads += 1
                logging.info(
                    (f'Comic id: {comic_id} '
                        f'has been downloaded with name: {file_name}')
                )
            except (IsADirectoryError, PermissionError) as error:
                logging.error(
                    (f'{type(error).__name__} when save file image'
                        f' for comic id: {comic_id} with name: {file_name}')
                )
        else:
            logging.info(
                (f'File of Comic id: {comic_id} '
                    f'alredy exits with name: {file_name}')
            )

    def _get_md5_from_file(self, file_content: bytes) -> str:
        md5_from_file = hashlib.md5()
        md5_from_file.update(file_content)
        return md5_from_file.hexdigest()

    def _create_directory(self) -> None:
        try:
            os.mkdir(self.DIRECTORY)
            logging.info(f'The directory:"{self.DIRECTORY}/" has been created')
        except FileExistsError:
            logging.info(f'The directory:"{self.DIRECTORY}/" alredy exists')
        except PermissionError as error:
            logging.error(
                (f'{type(error).__name__} '
                    f'when create directory "{self.DIRECTORY}/"')
            )
            exit()
