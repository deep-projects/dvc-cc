import sys
from argparse import ArgumentParser


def cli_modes(script_name, title, description, modes, version=None):
    sys.argv[0] = script_name

    parser = ArgumentParser(description=description)
    if version:
        parser.add_argument(
            '-v', '--version', action='version', version=version
        )
    subparsers = parser.add_subparsers(title=title)

    sub_parser = None
    for key, val in modes.items():
        sub_parser = subparsers.add_parser(key, help=val['description'], add_help=False)

    if len(sys.argv) < 2:
        parser.print_help()
        exit()

    _ = parser.parse_known_args()
    sub_args = sub_parser.parse_known_args()

    mode = modes[sub_args[1][0]]['main']
    sys.argv[0] = '{} {}'.format(script_name, sys.argv[1])
    del sys.argv[1]
    exit(mode())
