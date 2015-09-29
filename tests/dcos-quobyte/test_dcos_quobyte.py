""" Unit tests for dcos-quobyte cli """

from __future__ import print_function
from __future__ import unicode_literals
import unittest
import mock
from mock.mock import PropertyMock, sentinel

from dcos_quobyte import cli
from dcos import mesos
import requests
from requests.exceptions import ConnectionError
from requests import status_codes


class dcos_quobyte_cli_test (unittest.TestCase):

    def setUp(self):
        print("\n------- Testing method " + self._testMethodName)

    @mock.patch.object(cli, 'print')
    def test_info(self, mock_cli):

        cli.info(None)
        mock_cli.assert_called_once_with(cli.INFO_STRING)

    @mock.patch.object(requests, 'get')
    def test_start(self, mock_requests):
        test_url = "http://test.master.adr:1234"
        test_release = "0.0.0"
        mock_requests.return_value.status_code = requests.codes.ok

        result_code = cli.start(test_url, test_release)
        print ("Test result is " + str(result_code))

        mock_requests.assert_called_once_with("http://test.master.adr:1234"
                                              "/v1/version?0.0.0")
        self.assertEquals(0, result_code)

    @mock.patch.object(requests, 'get')
    def test_start_trailing_backslash(self, mock_requests):
        test_url = "http://test.master.adr:1234/"
        test_release = "0.0.0"
        mock_requests.return_value.status_code = requests.codes.ok

        cli.start(test_url, test_release)

        # mock_requests.assert_called_once_with(test_url + "/v1/version?0.0.0")
        mock_requests.assert_called_once_with("http://test.master.adr:1234"
                                              "/v1/version?0.0.0")

    def test_start_no_host(self):
        test_url = None
        test_release = "0.0.0"

        self.assertRaises(ValueError, cli.start, test_url, test_release)

    def test_start_no_release(self):
        test_url = "http://test.master.adr:1234"
        test_release = None

        self.assertRaises(ValueError, cli.start, test_url, test_release)

    @mock.patch.object(requests, 'get', side_effect=ConnectionError)
    def test_start_connection_error(self, mock_requests):
        test_url = "http://test.master.adr:1234"
        test_release = "0.0.0"

        self.assertEqual(2, cli.start(test_url, test_release),
                         "Wrong exit value on ConnectionError test.")

    @mock.patch.object(requests, 'get')
    def test_start_bad_status(self, mock_requests):
        test_url = "http://test.master.adr:1234"
        test_release = "0.0.0"
        mock_requests.return_value.status_code = 500

        result_code = cli.start(test_url, test_release)

        mock_requests.assert_called_once_with("http://test.master.adr:1234"
                                              "/v1/version?0.0.0")
        self.assertEquals(500, result_code)

    @mock.patch.object(requests, 'get')
    def test_stop(self, mock_requests):
        test_url = "http://test.master.adr:1234"
        mock_requests.return_value.status_code = requests.codes.ok

        cli.stop(test_url)

        mock_requests.assert_called_once_with(test_url + "/v1/version")

    @mock.patch.object(requests, 'get')
    def test_stop_no_host(self, mock_requests):
        test_url = None

        self.assertRaises(ValueError, cli.stop)

    @mock.patch.object(requests, 'get', side_effect=ConnectionError)
    def test_stop_connection_error(self, mock_requests):
        test_url = "http://test.master.adr:1234"
        mock_requests.return_value.status_code = 500

        self.assertEqual(2, cli.stop(test_url),
                         "Wrong exit value on ConnectionError test.")

    @mock.patch.object(requests, 'get')
    def test_stop_bad_status(self, mock_requests):
        test_url = "http://test.master.adr:1234"
        mock_requests.return_value.status_code = 500

        result_code = cli.stop(test_url)

        mock_requests.assert_called_once_with("http://test.master.adr:1234"
                                              "/v1/version")
        self.assertEquals(500, result_code16)

    @mock.patch.object(cli, 'start')
    def test_upgrade(self, mock_cli_start):
        test_url = "http://test.master.adr:1234"
        test_release = "0.0.0"
        mock_cli_start.return_value = 0

        self.assertEquals(0, cli.upgrade(test_url, test_release))
        mock_cli_start.assert_called_once_with(test_url, test_release)


if __name__ == '__main__':
    unittest.main()
