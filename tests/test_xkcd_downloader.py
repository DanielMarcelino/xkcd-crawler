from ast import Raise
from typing import Type
import unittest
import os

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
    def test_displays_especific_log_msg_when_directory_alredy_exists(self,mock_mkdir):
        mock_mkdir.side_effect = FileExistsError
        self.instance._create_directory()
        with self.assertLogs() as captured_log:
            self.instance._create_directory()
        self.assertEqual(captured_log.output[0], f'INFO:root:The directory: "{self.instance.DIRECTORY}/" '
                                                 'alredy exists')

    @patch('os.mkdir')
    def test_displays_especific_log_msg_and_trigger_sytem_exit_when_permission_error_occurs(self, mock_mkdir):
        mock_mkdir.side_effect = PermissionError
        with self.assertLogs() as captured_log:
            with self.assertRaises(SystemExit):
                self.instance._create_directory()
        self.assertEqual(captured_log.output[0], f'ERROR:root:PermissionError when create directory '
                                                 f'"{self.instance.DIRECTORY}/"')


class TestCreateFileInLocalStorageMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.instance.DIRECTORY = 'directory_test'
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
    def test_display_especific_log_msg_when_is_adirectory_error_occurs(self, mock_open):
        mock_open.side_effect = IsADirectoryError
        with self.assertLogs() as captured_log:
            self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                    self.info_log_msg, self.error_log_msg)
        self.assertEqual(captured_log.output[0], f'ERROR:root:IsADirectoryError {self.error_log_msg}')
    
    @patch('builtins.open', new_callable=mock_open())
    def test_display_especific_log_msg_when_permission_error_occurs(self, mock_open):
        mock_open.side_effect = PermissionError
        with self.assertLogs() as captured_log:
            self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                    self.info_log_msg, self.error_log_msg)
        self.assertEqual(captured_log.output[0], f'ERROR:root:PermissionError {self.error_log_msg}')

    @patch('builtins.open', new_callable=mock_open())
    def test_display_especific_log_msg_when_file_not_found_error_occurs(self, mock_open):
        mock_open.side_effect = FileNotFoundError
        with self.assertLogs() as captured_log:
            self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                    self.info_log_msg, self.error_log_msg)
        self.assertEqual(captured_log.output[0], f'ERROR:root:FileNotFoundError {self.error_log_msg}')


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
    def test_display_especific_log_msg_when_known_exceptions_are_raised(self, mock_requests):
        known_exeptions = [HTTPError, Timeout, ConnectionError, InvalidURL]
        for exception in known_exeptions:
            mock_requests.side_effect = exception
            with self.assertLogs() as captured_log:
                self.instance._make_request(self.test_url, self.except_log_msg)
            self.assertEqual(captured_log.output[0], f'ERROR:root:{exception.__name__} '
                                                     f'{self.except_log_msg}')

    @patch('requests.get', return_value = requests.models.Response())
    def test_display_especific_log_msg_when_unknown_exceptions_are_raised(self, mock_requests):
        mock_requests.side_effect = Exception
        with self.assertLogs() as captured_log:
            self.instance._make_request(self.test_url, self.except_log_msg)
        self.assertEqual(captured_log.output[0], f'ERROR:root:Some error ocurred {self.except_log_msg}')



if __name__ == '__main__':
    unittest.main()