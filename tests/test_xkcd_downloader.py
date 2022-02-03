import os
import unittest

import requests

from unittest.mock import patch, mock_open
from requests.exceptions import HTTPError, Timeout, ConnectionError, InvalidURL
from xkcd_downloader import XkcdDownloader


class TesteCreateDirectoryMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.instance.DIRECTORY = 'directory_name_test'

    @patch('os.mkdir')
    def test_call_mkdir_with_correct_argument(self, mock_mkdir):
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
        self.file_name = 'teste_file.bin'
        self.file_content = b'test binary content'
        self.info_log_msg = 'Lorem ipsum'
        self.error_log_msg = 'Dolor sit amet'

    @patch('builtins.open', new_callable=mock_open())
    def test_call_open_and_write_with_corect_arguments(self, mock_open):
        self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                    self.info_log_msg, self.error_log_msg)
        mock_open.assert_called_once_with(f'{self.instance.DIRECTORY}/teste_file.bin' , 'wb')
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


class TestMakeRequestMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.test_url = 'https://www.xkcd.com'
        self.except_log_msg = 'Lorem ipsum' 

    @patch('requests.get')
    def test_call_requests_get_with_corect_arguments(self, mock_requests):
        self.instance._make_request(self.test_url, self.except_log_msg)
        mock_requests.assert_called_once_with(self.test_url, headers=self.instance.HEADERS,
                                              timeout=self.instance.TIMEOUT)

    @patch('requests.get', return_value = requests.models.Response())
    def test_return_requests_instance_when_http_response_is_sucesful(self, mock_requests):
        response = self.instance._make_request(self.test_url, self.except_log_msg)
        self.assertIsInstance(response, requests.models.Response)
    
    @patch('requests.get', return_value = requests.models.Response())
    def test_display_especific_log_msg_when_exceptions_are_raised(self, mock_requests):
        known_exeptions = [HTTPError, Timeout, ConnectionError, InvalidURL]
        for exception in known_exeptions:
            mock_requests.side_effect = exception
            with self.assertLogs() as captured_log:
                self.instance._make_request(self.test_url, self.except_log_msg)
            self.assertEqual(captured_log.output[0], f'ERROR:root:{exception.__name__} '
                                                     f'{self.except_log_msg}')


class TestGetMd5FromFile(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.content_to_md5 = [[b'phrase to test MD5 generator method', 'ebdda56737bb8d7e5c1e056a48c4aacc'],
                              [b'xkcd comics', '733050eabfd65f2120a5ec201273a369']]
    
    def test_return_md5_from_binary_content(self):
        for content in self.content_to_md5:
            self.assertEqual(self.instance._get_md5_from_file(content[0]),content[1])


class TestSaveComicImgFileInLocalStorage(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.name_img_file = 'img_test.png'
        self.img_file_content = b'content img file'
        self.comic_id = '136'
        
    
    @patch('xkcd_downloader.XkcdDownloader._create_directory')
    @patch('os.path.isfile', return_value = True)
    def teste_call_isfile_with_corect_argument(self, mock_isfile, mock_create_directory):
        self.instance._save_comic_img_file_in_local_storage(self.name_img_file, self.img_file_content,
                                                            self.comic_id)
        mock_isfile.assert_called_once_with(f'{self.instance.DIRECTORY}/{self.name_img_file}')

    @patch('xkcd_downloader.XkcdDownloader._create_file_in_local_storage')
    @patch('os.path.isfile', return_value = False)
    def teste_call_isfile_with_corect_argument(self, mock_isfile, mock_create_directory):
        info_log_msg = f'Comic id: {self.comic_id} has been downloaded with name: {self.name_img_file}'
        error_log_msg=(f'when save file image for comic id: {self.comic_id} with name: {self.name_img_file}')
        self.instance._save_comic_img_file_in_local_storage(self.name_img_file, self.img_file_content,
                                                            self.comic_id)
        mock_create_directory.assert_called_once_with(file_name=self.name_img_file,file_content=self.img_file_content,
                                                      info_log_msg=info_log_msg, error_log_msg=error_log_msg)


if __name__ == '__main__':
    unittest.main()
