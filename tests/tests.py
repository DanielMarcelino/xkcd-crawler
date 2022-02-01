import mock
import unittest

from requests.exceptions import Timeout
from xkcd_downloader import XkcdDownloader

requests = Mock()

class TestRequest(unittest.TestCase):

    def test_get_xkcd_timeout(self):
        requests.get.side_effect = Timeout
        with self.assertRaises(Timeout):
            _make_request()

if __name__ == '__main__':
    unittest.main()
