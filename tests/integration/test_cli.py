from common import exec_command


def test_help():
    returncode, stdout, stderr = exec_command(
        ['dcos-quobyte', 'quobyte', '--help'])

    assert returncode == 0
    assert stdout == b"""DCOS Quobyte Example Subcommand

Usage:
    dcos quobyte info

Options:
    --help           Show this screen
    --version        Show version
"""
    assert stderr == b''
