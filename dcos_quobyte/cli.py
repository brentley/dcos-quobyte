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


def info(args):
    print(INFO_STRING)
    return 0


def start(host=None, release=None):
    if host is None:
        raise ValueError("No framework host specified, please provide"
                         " --host=<hosturl> option.")
    elif release is None:
        raise ValueError("No framework release specified, please provide"
                         " --release=<a.b.c> option.")

    if host.endswith('/'):
        host = host.rstrip('/')

    try:
        r = requests.get(str(host) + API_STRING + "?" + str(release))
        # print("start request result is " + str(r))
        status_code = r.status_code
        if status_code is requests.codes.ok:
            print("Framework accepted start command.")
            return 0
        else:
            print("Error! Framework returned status code: " + str(status_code))
            return status_code
    except ConnectionError:
        print('Unable to connect to framework at ' + str(host))
        return 2


def stop(host=None):
    if host is None:
        raise ValueError("No framework host specified, please provide"
                         " --host=<hosturl> option.")
    try:
        r = requests.get(str(host) + API_STRING)
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

    print(args)

    if args['--help'] or args['-h']:
        return print(__doc__)  # Prints the whole docstring
    elif args['info']:
        return info(args)
    elif args['start']:
        return start(host=args['--host'], release=args['--release'])
    elif args['stop']:
        return start(host=args['--host'])
    elif args['upgrade']:
        return upgrade(host=args['--host'], release=args['--release'])
    else:
        print(__doc__)  # Prints usage (only)
        return 1

    return 0

if __name__ == "__main__":
    main()
