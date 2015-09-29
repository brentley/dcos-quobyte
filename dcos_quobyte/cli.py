"""DCOS Quobyte Subcommand

Usage:
    dcos-quobyte info
    dcos-quobyte start [--host=<url>] [--release=<rel>]
    dcos-quobyte stop
    dcos-quobyte upgrade
    dcos-quobyte (-h | --help)

Options:
    --help           Show this screen
    --host=<url>     URL of the Quobyte framework host (including port number)
    --release=<rel>  Quobyte release number to be used
    --version        Show version
"""

from __future__ import print_function
from __future__ import unicode_literals

import requests

import docopt
from dcos import mesos
from dcos_quobyte import constants
from requests.exceptions import ConnectionError


__copyright__ = "Quobyte Inc. 2015"
__license__ = "Apache License 2.0"
__author__ = "Silvan Kaiser"

INFO_STRING = ("\ndcos-quobyte starts a Quobyte storage backend"
               "on your cluster:\n")
API_STRING = "/v1/version"
QUOBYTE_FRAMEWORK_NAME = "quobyte"


def find_quobyte_framework():
    dcos_client = mesos.DCOSClient()
    active_frameworks = mesos.get_master(dcos_client).frameworks()
    # print("Active frameworks found are: " + str(active_frameworks))
    quobyte_fw = None
    for framework in active_frameworks:
        if framework['name'] == QUOBYTE_FRAMEWORK_NAME:
            return framework['webui_url']
    return None


def build_url(host=None):
    if host is None:
        host = find_quobyte_framework()
    if host is None:
        raise ValueError("Unable to retrieve URL for framework, please provide"
                         " --master=<http://a.b.c:xyz> option.")
    else:
        print("Located Quobyte famework web interface at " + str(host))

    if host.endswith('/'):
        host = host.rstrip('/')

    return str(host) + API_STRING


def info(args):
    print(INFO_STRING)
    return 0


def start(host=None, release=None):
    if release is None:
        raise ValueError("No framework release specified, please provide"
                         " --release=<a.b.c> option.")
    request_url = build_url(host)
    try:
        r = requests.get(request_url, data=str(release))
        print("start request result is " + str(r))
        status_code = r.status_code
        if status_code is requests.codes.ok:
            print("Framework accepted start command.")
            return 0
        else:
            print("Error! Framework returned status code: " + str(status_code))
            return status_code
    except ConnectionError as e:
        print('Unable to connect to framework at ' + str(host))
        print(str(e))
        return 2


def stop(host=None):
    request_url = build_url(host)
    try:
        r = requests.get(request_url)
        status_code = r.status_code
        if status_code is requests.codes.ok:
            print("Framework accepted stop command.")
            return 0
        else:
            print("Error! Framework returned status code: " + str(status_code))
            return status_code
    except ConnectionError:
        print('Unable to connect to framework at ' + str(host) + "\n"
              'Reason was: ' + str(ConnectionError))
        return 2


def upgrade(host=None, release=None):
    return start(host, release)


def main():
    args = docopt.docopt(
        __doc__,
        help=False,
        version='dcos-quobyte version {}'.format(constants.version))

    if args['--help'] or args['-h']:
        return print(__doc__)  # Prints the whole docstring
    elif args['info']:
        return info(args)
    elif args['start']:
        return start(host=args['--host'], release=args['--release'])
    elif args['stop']:
        return stop(host=args['--host'])
    elif args['upgrade']:
        return upgrade(host=args['--host'], release=args['--release'])
    else:
        print(__doc__)  # Prints usage (only)
        return 1

    return 0

if __name__ == "__main__":
    main()
