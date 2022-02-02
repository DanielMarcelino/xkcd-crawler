from ast import Raise
import builtins
from typing import Type
import unittest
import os
import logging
from unittest import mock

from unittest.mock import MagicMock, Mock, patch, mock_open
from xkcd_downloader import XkcdDownloader


class TesteCreateDirectoryMethod(unittest.TestCase):
    def setUp(self):
        self.instance = XkcdDownloader()
        self.instance.DIRECTORY = 'directory_test'

    @patch('os.mkdir')
    def test_call_mkdir_with_correct_argument(self, mock_mkdir):
        self.instance._create_directory()
        mock_mkdir.assert_called_once_with(self.instance.DIRECTORY)


    def test_create_directory_when_not_exists(self):
        self.instance._create_directory()
        self.assertTrue(os.path.isdir(f'./{self.instance.DIRECTORY}'))
        os.rmdir(self.instance.DIRECTORY)

    @patch('os.mkdir')
    def test_displays_log_msg_when_directory_has_been_created(self, mock_mkdir):
        mock_mkdir.side_effect = None
        with self.assertLogs() as captured_log:
            self.instance._create_directory()
        self.assertEqual(captured_log.output[0], f'INFO:root:The directory: "{self.instance.DIRECTORY}/" '
                                                 'has been created')

    @patch('os.mkdir')
    def test_displays_log_msg_when_directory_alredy_exists(self,mock_mkdir):
        mock_mkdir.side_effect = FileExistsError
        self.instance._create_directory()
        with self.assertLogs() as captured_log:
            self.instance._create_directory()
        self.assertEqual(captured_log.output[0], f'INFO:root:The directory: "{self.instance.DIRECTORY}/" '
                                                'alredy exists')

    @patch('os.mkdir')
    def test_displays_log_msg_and_trigger_sytem_exit_when_permission_error_occurs(self, mock_mkdir):
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
        self.file_content = b'teste binary content'
        self.info_log_msg = 'Lorem ipsum'
        self.error_log_msg = 'Dolor sit amet'


    @patch('builtins.open', new_callable=mock_open())
    def test_call_open_and_write_with_corect_arguments(self, mock_open):
        self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                    self.info_log_msg, self.error_log_msg)
        mock_open.assert_called_once_with(f'{self.instance.DIRECTORY}/teste_file.bin' , 'wb')
        mock_open.return_value.__enter__().write.assert_called_once_with(self.file_content)

    def test_create_file_local_storage(self):
        self.instance.DIRECTORY = ''
        self.instance._create_file_in_local_storage(self.file_name, self.file_content,
                                                    self.info_log_msg, self.error_log_msg)
        self.assertTrue(os.path.isfile(f'{self.instance.DIRECTORY}/{self.file_name}'))
        os.remove(f'{self.instance.DIRECTORY}/{self.file_name}')
        os.rmdir(self.instance.DIRECTORY)


if __name__ == '__main__':
    unittest.main()