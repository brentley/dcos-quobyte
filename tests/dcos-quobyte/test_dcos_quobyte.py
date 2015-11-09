""" Unit tests for dcos-quobyte cli """

from __future__ import print_function
from __future__ import unicode_literals
import unittest
import mock
from mock.mock import ANY
import six

from dcos_quobyte import cli
from dcos_quobyte.cli import docopt
from dcos_quobyte import constants
from dcos import mesos
import requests
from requests.exceptions import ConnectionError


class dcos_quobyte_cli_test (unittest.TestCase):

    def setUp(self):
        print("\n------- Testing method " + self._testMethodName)

    @mock.patch.object(cli, 'print')
    def test_info(self, mock_cli):

        cli.info()
        mock_cli.assert_called_once_with(cli.INFO_STRING)

    @mock.patch.object(requests, 'get')
    def test_start(self, mock_requests):
        test_url = "http://test.master.adr:1234"
        test_release = "0.0.0"
        mock_requests.return_value.status_code = requests.codes.ok

        result_code = cli.start(test_url, test_release)
        print ("Test result is " + str(result_code))

        mock_requests.assert_called_once_with("http://test.master.adr:1234"
                                              "/v1/version",
                                              data='0.0.0')
        self.assertEquals(0, result_code)

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
                                              "/v1/version",
                                              data='0.0.0')
        self.assertEquals(500, result_code)

    @mock.patch.object(requests, 'get')
    def test_stop(self, mock_requests):
        test_url = "http://test.master.adr:1234"
        mock_requests.return_value.status_code = requests.codes.ok

        cli.stop(test_url)

        mock_requests.assert_called_once_with(test_url + "/v1/version")

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
        self.assertEquals(500, result_code)

    @mock.patch.object(cli, 'start')
    def test_upgrade(self, mock_cli_start):
        test_url = "http://test.master.adr:1234"
        test_release = "0.0.0"
        mock_cli_start.return_value = 0

        self.assertEquals(0, cli.upgrade(test_url, test_release))
        mock_cli_start.assert_called_once_with(test_url, test_release)

    @mock.patch.object(mesos, 'DCOSClient', return_value=mock.Mock())
    @mock.patch.object(mesos, 'get_master')
    def test_find_quobyte_framework(self,
                                    mock_mesos_get_master,
                                    mock_mesos_dcosclient):
        fw_mock = mock.Mock()
        fw_mock.frameworks.return_value = [
            {'name': 'other_framework',
             'webui_url': 'http://wrong.host.adr:4321'},
            {'name': 'quobyte',
             'webui_url': 'http://test.webui_url.adr:1234'}]
        mock_mesos_get_master.return_value = fw_mock

        self.assertEquals("http://test.webui_url.adr:1234",
                          cli.find_quobyte_framework())
        mock_mesos_get_master.assert_called_once_with(ANY)

    @mock.patch.object(mesos, 'DCOSClient', return_value=mock.Mock())
    @mock.patch.object(mesos, 'get_master')
    def test_find_quobyte_framework_none(self,
                                    mock_mesos_get_master,
                                    mock_mesos_dcosclient):
        fw_mock = mock.Mock()
        fw_mock.frameworks.return_value = [
            {'name': 'other_framework',
             'webui_url': 'http://wrong.host.adr:4321'}]
        mock_mesos_get_master.return_value = fw_mock

        self.assertEquals(None, cli.find_quobyte_framework())
        mock_mesos_get_master.assert_called_once_with(ANY)

    def test_build_url(self):
        self.assertEquals("http://test.webui_url.adr:1234" + cli.API_STRING,
                          cli.build_url("http://test.webui_url.adr:1234"))

    @mock.patch.object(cli, 'find_quobyte_framework',
                       return_value='http://autodetected.quobyte.mesos:2323')
    def test_build_url_no_host_autodetect(self, mock_cli_fqf):
        self.assertEquals("http://autodetected.quobyte.mesos:2323/v1/version",
                          cli.build_url(None))

    @mock.patch.object(cli, 'find_quobyte_framework')
    def test_build_url_no_host_error(self, mock_cli_fqf):
        test_url = None
        test_release = "0.0.0"
        mock_cli_fqf.return_value = None

        self.assertRaises(ValueError, cli.build_url, test_url)
        mock_cli_fqf.assert_called_once_with()

    def test_build_url_trailing_backslash(self):
        test_url = "http://test.master.adr:1234/"

        self.assertEquals("http://test.master.adr:1234/v1/version",
                          cli.build_url(test_url))

    @mock.patch.object(cli, 'print')
    def test_config_schema(self, mock_cli_print):
        cli.config_schema()

        mock_cli_print.assert_called_once_with(cli.SCHEMA)

    @mock.patch.object(cli, 'print')
    @mock.patch("dcos_quobyte.cli.docopt",
                return_value={'-h': False,
                              '--help': False,
                              '--info': False,
                              'start': False,
                              'stop': False,
                              'upgrade': False,
                              '--config-schema': False})
    def test_main(self, mock_docopt_docopt, mock_cli_print):
        self.assertEquals(1, cli.main())
        version_string = (six.text_type
                          ("dcos quobyte version " + constants.version))
        mock_docopt_docopt.assert_called_once_with(cli.__doc__,
                                                   help=False,
                                                   version=version_string)
        mock_cli_print.assert_called_once_with(cli.__doc__)

    @mock.patch.object(cli, 'print', return_value=0)
    @mock.patch("dcos_quobyte.cli.docopt",
                return_value={'-h': False,
                              '--help': True,
                              '--info': False,
                              'start': False,
                              'stop': False,
                              'upgrade': False,
                              '--config-schema': False})
    def test_main_help(self, mock_docopt_docopt, mock_cli_print):
        self.assertEquals(0, cli.main())
        mock_docopt_docopt.assert_called_once_with(cli.__doc__,
                                                   help=False,
                                                   version=ANY)
        mock_cli_print.assert_called_once_with(cli.__doc__)

    @mock.patch.object(cli, 'print', return_value=0)
    @mock.patch("dcos_quobyte.cli.docopt",
                return_value={'-h': True,
                              '--help': False,
                              '--info': False,
                              'start': False,
                              'stop': False,
                              'upgrade': False,
                              '--config-schema': False})
    def test_main_h(self, mock_docopt_docopt, mock_cli_print):
        self.assertEquals(0, cli.main())
        mock_docopt_docopt.assert_called_once_with(cli.__doc__,
                                                   help=False,
                                                   version=ANY)
        mock_cli_print.assert_called_once_with(cli.__doc__)

    @mock.patch.object(cli, 'info', return_value=0)
    @mock.patch("dcos_quobyte.cli.docopt",
                return_value={'-h': False,
                              '--help': False,
                              '--info': True,
                              'start': False,
                              'stop': False,
                              'upgrade': False,
                              '--config-schema': False})
    def test_main_info(self, mock_docopt_docopt, mock_cli_info):
        self.assertEquals(0, cli.main())
        mock_docopt_docopt.assert_called_once_with(cli.__doc__,
                                                   help=False,
                                                   version=ANY)
        mock_cli_info.assert_called_once_with()

    @mock.patch.object(cli, 'start', return_value=0)
    @mock.patch("dcos_quobyte.cli.docopt",
                return_value={'-h': False,
                              '--help': False,
                              '--info': False,
                              'start': True,
                              'stop': False,
                              'upgrade': False,
                              '--config-schema': False,
                              '--host': 'fake_host',
                              '--release': 'fake_release'})
    def test_main_start(self, mock_docopt_docopt, mock_cli_start):
        self.assertEquals(0, cli.main())
        mock_docopt_docopt.assert_called_once_with(cli.__doc__,
                                                   help=False,
                                                   version=ANY)
        mock_cli_start.assert_called_once_with(host='fake_host',
                                               release='fake_release')

    @mock.patch.object(cli, 'stop', return_value=0)
    @mock.patch("dcos_quobyte.cli.docopt",
                return_value={'-h': False,
                              '--help': False,
                              '--info': False,
                              'start': False,
                              'stop': True,
                              'upgrade': False,
                              '--config-schema': False,
                              '--host': 'fake_host',
                              '--release': 'fake_release'})
    def test_main_stop(self, mock_docopt_docopt, mock_cli_stop):
        self.assertEquals(0, cli.main())
        mock_docopt_docopt.assert_called_once_with(cli.__doc__,
                                                   help=False,
                                                   version=ANY)
        mock_cli_stop.assert_called_once_with(host='fake_host')

    @mock.patch.object(cli, 'upgrade', return_value=0)
    @mock.patch("dcos_quobyte.cli.docopt",
                return_value={'-h': False,
                              '--help': False,
                              '--info': False,
                              'start': False,
                              'stop': False,
                              'upgrade': True,
                              '--config-schema': False,
                              '--host': 'fake_host',
                              '--release': 'fake_release'})
    def test_main_upgrade(self, mock_docopt_docopt, mock_cli_upgrade):
        self.assertEquals(0, cli.main())
        mock_docopt_docopt.assert_called_once_with(cli.__doc__,
                                                   help=False,
                                                   version=ANY)
        mock_cli_upgrade.assert_called_once_with(host='fake_host',
                                               release='fake_release')

    @mock.patch.object(cli, 'config_schema', return_value=0)
    @mock.patch("dcos_quobyte.cli.docopt",
                return_value={'-h': False,
                              '--help': False,
                              '--info': False,
                              'start': False,
                              'stop': False,
                              'upgrade': False,
                              '--config-schema': True})
    def test_main_config_schema(self, mock_docopt_docopt, mock_cli_cschema):
        self.assertEquals(0, cli.main())
        mock_docopt_docopt.assert_called_once_with(cli.__doc__,
                                                   help=False,
                                                   version=ANY)
        mock_cli_cschema.assert_called_once_with()

if __name__ == '__main__':
    unittest.main()
