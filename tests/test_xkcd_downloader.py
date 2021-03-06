import os
import requests
import unittest

from requests.exceptions import HTTPError, Timeout, ConnectionError, InvalidURL
from src.xkcd_downloader import XkcdDownloader
from unittest.mock import patch, mock_open


class DubleRequests:
    def __init__(self, status_code: int, text: str = '', headers: dict = {}, content: bytes = b'',
                 json: dict = {}):
        self.status_code = status_code
        self.text = text
        self.headers = headers
        self.content = content
        self._json = json

    def json(self):
        return self._json


class TesteCreateDirectoryMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.instance.DIRECTORY = 'directory_name_test'

    @patch('os.mkdir')
    def test_call_mkdir_with_correct_arguments(self, mock_mkdir):
        self.instance._create_directory()
        mock_mkdir.assert_called_once_with(self.instance.DIRECTORY)

    def test_create_directory_when_not_exists(self):
        self.instance._create_directory()
        self.assertTrue(os.path.isdir(f'./{self.instance.DIRECTORY}'))
        os.rmdir(self.instance.DIRECTORY)

    @patch('os.mkdir')
    def test_displays_especific_log_msg_when_directory_has_been_created(self, mock_mkdir):
        mock_mkdir.side_effect = None
        with self.assertLogs() as captured_log:
            self.instance._create_directory()
        self.assertEqual(captured_log.output[0], f'INFO:root:The directory: "{self.instance.DIRECTORY}/" '
                                                 'has been created')

    @patch('os.mkdir')
    def test_displays_especific_log_msg_when_directory_alredy_exists(self, mock_mkdir):
        mock_mkdir.side_effect = FileExistsError
        self.instance._create_directory()
        with self.assertLogs() as captured_log:
            self.instance._create_directory()
        self.assertEqual(captured_log.output[0], f'INFO:root:The directory: "{self.instance.DIRECTORY}/" '
                                                 'alredy exists')

    @patch('os.mkdir')
    def test_displays_especific_log_msg_and_trigger_sytem_exit_when_exceptions_are_raised(self, mock_mkdir):
        exceptions = [OSError, PermissionError, FileNotFoundError]
        for expt in exceptions:
            mock_mkdir.side_effect = expt
            with self.assertLogs() as captured_log:
                with self.assertRaises(SystemExit):
                    self.instance._create_directory()
            self.assertEqual(captured_log.output[0], f'ERROR:root:{expt.__name__} when create directory '
                                                     f'"{self.instance.DIRECTORY}/"')


class TestCreateFileInLocalStorageMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.file_name = 'test_file.bin'
        self.file_content = b'test binary content'
        self.info_log_msg = 'Lorem ipsum'
        self.error_log_msg = 'Dolor sit amet'

    @patch('builtins.open', new_callable=mock_open())
    def test_call_open_and_write_with_correct_arguments(self, mock_open):
        self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                    self.info_log_msg, self.error_log_msg)
        mock_open.assert_called_once_with(f'{self.instance.DIRECTORY}/test_file.bin', 'wb')
        mock_open.return_value.__enter__().write.assert_called_once_with(self.file_content)

    def test_create_file_in_local_storage(self):
        self.instance.DIRECTORY = '.'
        self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                    self.info_log_msg, self.error_log_msg)
        self.assertTrue(os.path.isfile(self.file_name))
        os.remove(f'{self.instance.DIRECTORY}/{self.file_name}')

    @patch('builtins.open', new_callable=mock_open())
    def test_display_especific_log_msg_when_file_has_been_created(self, mock_open):
        mock_open.side_effect = None
        with self.assertLogs() as captured_log:
            self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                        self.info_log_msg, self.error_log_msg)
        self.assertEqual(captured_log.output[0], f'INFO:root:{self.info_log_msg}')

    @patch('builtins.open', new_callable=mock_open())
    def test_display_especific_log_msg_when_exceptions_are_raised(self, mock_open):
        known_execptions = [IsADirectoryError, PermissionError, FileNotFoundError]
        for exeption in known_execptions:
            mock_open.side_effect = exeption
            with self.assertLogs() as captured_log:
                self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                            self.info_log_msg, self.error_log_msg)
            self.assertEqual(captured_log.output[0], f'ERROR:root:{exeption.__name__} {self.error_log_msg}')

    @patch('builtins.open', new_callable=mock_open())
    def test_increment_count_of_comic_downloads_attribute_when_file_has_been_saved(self, mock_open):
        mock_open.side_effect = None
        self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                    self.info_log_msg, self.error_log_msg)
        self.assertEqual(1, self.instance._count_of_comic_downloads)

    @patch('builtins.open', new_callable=mock_open())
    def test_not_increment_count_of_comic_downloads_attribute_when_to_save_file_fails(self, mock_open):
        mock_open.side_effect = Exception
        self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                    self.info_log_msg, self.error_log_msg)
        self.assertEqual(0, self.instance._count_of_comic_downloads)


class TestMakeRequestMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.test_url = 'https://www.xkcd.com'
        self.except_log_msg = 'Lorem ipsum'

    @patch('requests.get')
    def test_call_requests_get_with_correct_arguments(self, mock_requests):
        self.instance._make_request(self.test_url, self.except_log_msg)
        mock_requests.assert_called_once_with(self.test_url, headers=self.instance.HEADERS,
                                              timeout=self.instance.TIMEOUT)

    @patch('requests.get', return_value=requests.models.Response())
    def test_returns_requests_instance_when_http_response_is_sucesful(self, mock_requests):
        response = self.instance._make_request(self.test_url, self.except_log_msg)
        self.assertIsInstance(response, requests.models.Response)

    @patch('requests.get', return_value=requests.models.Response())
    def test_display_especific_log_msg_when_exceptions_are_raised(self, mock_requests):
        known_exeptions = [HTTPError, Timeout, ConnectionError, InvalidURL]
        for exception in known_exeptions:
            mock_requests.side_effect = exception
            with self.assertLogs() as captured_log:
                self.instance._make_request(self.test_url, self.except_log_msg)
            self.assertEqual(captured_log.output[0], f'ERROR:root:{exception.__name__} '
                                                     f'{self.except_log_msg}')


class TestGetMd5FromFileMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.content_to_md5 = [[b'phrase to test MD5 generator method', 'ebdda56737bb8d7e5c1e056a48c4aacc'],
                               [b'xkcd comics', '733050eabfd65f2120a5ec201273a369']]

    def test_returns_md5_from_binary_content(self):
        for content in self.content_to_md5:
            self.assertEqual(self.instance._get_md5_from_file(content[0]), content[1])


class TestSaveComicImgFileInLocalStorageMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.name_img_file = 'img_test.png'
        self.img_file_content = b'content img file'
        self.comic_id = 136

    @patch('src.xkcd_downloader.XkcdDownloader._create_directory')
    @patch('os.path.isfile', return_value=True)
    def test_call_isfile_with_correct_argument(self, mock_isfile, mock_create_directory):
        self.instance._save_comic_img_file_in_local_storage(self.name_img_file, self.img_file_content,
                                                            self.comic_id)
        mock_isfile.assert_called_once_with(f'{self.instance.DIRECTORY}/{self.name_img_file}')

    @patch('src.xkcd_downloader.XkcdDownloader._create_file_in_local_storage')
    @patch('os.path.isfile', return_value=False)
    def test_call_create_directory_with_correct_argument(self, mock_isfile, mock_create_directory):
        info_log_msg = f'Comic id: {self.comic_id} has been saved with name: {self.name_img_file}'
        error_log_msg = (f'when save file image for comic id: {self.comic_id} '
                         f'with name: {self.name_img_file}')
        self.instance._save_comic_img_file_in_local_storage(self.name_img_file, self.img_file_content,
                                                            self.comic_id)
        mock_create_directory.assert_called_once_with(file_name=self.name_img_file,
                                                      file_content=self.img_file_content,
                                                      info_log_msg=info_log_msg, error_log_msg=error_log_msg)

    @patch('src.xkcd_downloader.XkcdDownloader._create_file_in_local_storage')
    @patch('os.path.isfile', return_value=True)
    def test_display_log_message_when_file_returns_true(self, mock_isfile, mock_create_file_in_local):
        with self.assertLogs() as captured_log:
            self.instance._save_comic_img_file_in_local_storage(self.name_img_file, self.img_file_content,
                                                                self.comic_id)
        self.assertEqual(captured_log.output[0], f'INFO:root:File of Comic id: {self.comic_id} alredy exits '
                                                 f'with name: {self.name_img_file}')


class TestContentIsAImageMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.headers_html = {"Content-Type": "text/"}
        self.headers_image = {"Content-Type": "image/"}

    def test_returns_false_when_content_type_is_not_image(self):
        self.assertFalse(self.instance._content_is_a_image(self.headers_html))

    def test_returns_true_when_content_type_is_not_image(self):
        self.assertTrue(self.instance._content_is_a_image(self.headers_image))


class TestGetImageComicUrlMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.comic_id = 123
        self.url = f'{self.instance.API_URL[0]}{self.comic_id}{self.instance.API_URL[1]}'
        self.log_message = f'in request comic id: {self.comic_id} from xkcd API'
        self.json = {"img": "https://imgs.xkcd.com/comics/centrifugal_force.png",
                     "title": "Centrifugal Force"}

    @patch('src.xkcd_downloader.XkcdDownloader._make_request', return_value=None)
    def test_call_make_request_with_correct_arguments(self, mock_make_request):
        self.instance._get_image_comic_url(self.comic_id)
        mock_make_request.assert_called_once_with(url=self.url, except_log_message=self.log_message)

    @patch('src.xkcd_downloader.XkcdDownloader._make_request')
    def test_returns_url_when_request_http_sucessful(self, mock_make_request):
        mock_make_request.return_value = DubleRequests(200, json=self.json)
        url_returned = self.instance._get_image_comic_url(self.comic_id)
        self.assertEqual(url_returned, 'https://imgs.xkcd.com/comics/centrifugal_force.png')

    @patch('src.xkcd_downloader.XkcdDownloader._make_request')
    def test_display_especific_log_msg_when_status_code_is_not_200(self, mock_make_request):
        list_status_code = [403, 404, 500]
        for status_code in list_status_code:
            expected_log_msg = (f'WARNING:root:Error {status_code} in xkcd API request from '
                                f'comic id: {self.comic_id}')
            with self.assertLogs() as captured_log:
                mock_make_request.return_value = DubleRequests(status_code)
                self.instance._get_image_comic_url(self.comic_id)
                self.assertEqual(captured_log.output[0], expected_log_msg)


class TesteDownloadImageFileForComicMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.comic_id = 123
        self.comic_img_url = 'https://imgs.xkcd.com/comics/centrifugal_force.png'
        self.headers_not_img = {"Content-Type": "text/"}
        self.headers_img = {"Content-Type": "image/png"}
        self.except_log_msg = f'in request for comic id image file: {self.comic_id}'
        self.file_content = b'xkcd comics'
        self.file_md5 = '733050eabfd65f2120a5ec201273a369'
        extencion = self.headers_img['Content-Type'][6:]
        self.file_name = f'{self.file_md5}.{extencion}'

    @patch('src.xkcd_downloader.XkcdDownloader._get_image_comic_url', return_value=None)
    def test_call_get_comic_id_with_correct_arguments(self, mock_get_image_comic_url):
        self.instance._download_image_file_for_comic(self.comic_id)
        mock_get_image_comic_url.assert_called_once_with(self.comic_id)

    @patch('src.xkcd_downloader.XkcdDownloader._make_request', return_value=None)
    @patch('src.xkcd_downloader.XkcdDownloader._get_image_comic_url')
    def test_call_make_request_with_correct_arguments(self, mock_get_image_comic_url, mock_make_request):
        mock_get_image_comic_url.return_value = self.comic_img_url
        self.instance._download_image_file_for_comic(self.comic_id)
        mock_make_request.assert_called_once_with(url=self.comic_img_url,
                                                  except_log_message=self.except_log_msg)

    @patch('src.xkcd_downloader.XkcdDownloader._content_is_a_image', return_value=False)
    @patch('src.xkcd_downloader.XkcdDownloader._make_request')
    @patch('src.xkcd_downloader.XkcdDownloader._get_image_comic_url')
    def test_call_content_is_a_image_with_correct_arguments(self, mock_get_image_comic_url,
                                                            moc_make_request, mock_content_is_a_image):
        mock_get_image_comic_url.return_value = self.comic_img_url
        moc_make_request.return_value = DubleRequests(status_code=200, headers=self.headers_not_img)
        self.instance._download_image_file_for_comic(self.comic_id)
        mock_content_is_a_image.assert_called_once_with(self.headers_not_img)

    @patch('src.xkcd_downloader.XkcdDownloader._save_comic_img_file_in_local_storage')
    @patch('src.xkcd_downloader.XkcdDownloader._content_is_a_image', return_value=True)
    @patch('src.xkcd_downloader.XkcdDownloader._make_request')
    @patch('src.xkcd_downloader.XkcdDownloader._get_image_comic_url')
    def test_call__save_comic_img_file_in_local_storage_with_correct_arguments(
        self, mock_get_image_comic_url, moc_make_request, mock_content_is_a_image,
        mock_save_comic_img_file_in_local_storage
       ):
        mock_get_image_comic_url.return_value = self.comic_img_url
        moc_make_request.return_value = DubleRequests(status_code=200, headers=self.headers_img,
                                                      content=self.file_content)
        self.instance._download_image_file_for_comic(self.comic_id)
        mock_save_comic_img_file_in_local_storage.assert_called_once_with(self.file_name, self.file_content,
                                                                          self.comic_id)

    @patch('src.xkcd_downloader.XkcdDownloader._content_is_a_image', return_value=False)
    @patch('src.xkcd_downloader.XkcdDownloader._make_request')
    @patch('src.xkcd_downloader.XkcdDownloader._get_image_comic_url')
    def test_display_specific_log_msg_when_response_is_not_a_image(self, mock_get_image_comic_url,
                                                                   moc_make_request, mock_content_is_a_image):
        expected_log_msg = f'INFO:root:The file for comic id: {self.comic_id} is not a image'
        mock_get_image_comic_url.return_value = self.comic_img_url
        moc_make_request.return_value = DubleRequests(status_code=200, headers=self.headers_not_img)
        self.instance._download_image_file_for_comic(self.comic_id)
        with self.assertLogs() as captured_log:
            self.instance._download_image_file_for_comic(self.comic_id)
        self.assertEqual(captured_log.output[0], expected_log_msg)

    @patch('src.xkcd_downloader.XkcdDownloader._make_request')
    @patch('src.xkcd_downloader.XkcdDownloader._get_image_comic_url')
    def test_display_specific_log_msg_when_response_not_get_status_code_200(self, mock_get_image_comic_url,
                                                                            mock_make_request):
        list_status_code = [403, 404, 500]
        for status_code in list_status_code:
            mock_make_request.return_value = DubleRequests(status_code=status_code)
            expected_log_msg = f'WARNING:root:Error {status_code} in request for comic id: {self.comic_id}'
            mock_get_image_comic_url.return_value = self.comic_img_url
            with self.assertLogs() as captured_log:
                self.instance._download_image_file_for_comic(self.comic_id)
            self.assertEqual(captured_log.output[0], expected_log_msg)


class TesteGetLastIndexFromApiMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.json = {"num": 123}

    @patch('src.xkcd_downloader.XkcdDownloader._make_request', return_value=None)
    def test_call_make_request_with_correct_arguments(self, mock_make_request):
        url = ''.join(self.instance.API_URL)
        except_log_message = 'in request last comic index from xkcd API'
        self.instance._get_last_index_from_api()
        mock_make_request.assert_called_once_with(url=url, except_log_message=except_log_message)

    @patch('src.xkcd_downloader.XkcdDownloader._make_request')
    def test_returns_last_index_when_response_is_sucessful(self, mock_make_request):
        mock_make_request.return_value = DubleRequests(status_code=200, json=self.json)
        last_index_returned = self.instance._get_last_index_from_api()
        self.assertEqual(last_index_returned, 123)

    @patch('src.xkcd_downloader.XkcdDownloader._make_request', return_value=None)
    def test_display_specific_log_msg_when_response_get_status_code_200(self, mock_make_request):
        mock_make_request.return_value = DubleRequests(status_code=200, json=self.json)
        expected_log_msg = 'INFO:root:Last comic index (comic id): 123'
        with self.assertLogs() as captured_log:
            self.instance._get_last_index_from_api()
        self.assertEqual(captured_log.output[0], expected_log_msg)

    @patch('src.xkcd_downloader.XkcdDownloader._make_request', return_value=None)
    def test_display_specific_log_msg_when_response_not_get_status_code_200(self, mock_make_request):
        list_status_code = [403, 404, 500]
        for status_code in list_status_code:
            mock_make_request.return_value = DubleRequests(status_code=status_code)
            expected_log_msg = (f'WARNING:root:Error {status_code} when getting last comic index '
                                'from xkcd API')
            with self.assertLogs() as captured_log:
                with self.assertRaises(SystemExit):
                    self.instance._get_last_index_from_api()
            self.assertEqual(captured_log.output[0], expected_log_msg)


class TestMakeDownloadMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.max_index = 10
        self.args_list = [i for i in range(1, self.max_index + 1)]

    @patch('src.xkcd_downloader.XkcdDownloader._download_image_file_for_comic')
    @patch('src.xkcd_downloader.XkcdDownloader._get_last_index_from_api')
    def test_call_download_image_file_for_comic_with_correct_indexes(self, mock_get_last_index,
                                                                     mock_download_img_file):
        mock_get_last_index.return_value = self.max_index
        self.instance.make_download()
        mock_download_img_file.call_args_list == self.args_list


class TestGetCountOfComicDownloadsMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.instance._count_of_comic_downloads = 10

    def test_get_correct_amount_of_downloads(self):
        self.assertEqual(self.instance._count_of_comic_downloads, self.instance.get_count_of_comic_downloads)


if __name__ == '__main__':
    unittest.main()
