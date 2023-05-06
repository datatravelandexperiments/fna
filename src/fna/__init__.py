#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
import pathlib
import sys

import util.io
import util.config
import vljum.m
import vljum.runner
import vljumap.enc

def main(argv: list[str] | None = None):
    if argv is None:
        argv = sys.argv
    cmd = pathlib.Path(argv[0]).stem
    parser = argparse.ArgumentParser(
        prog=cmd,
        description='Manage key/value attributes in file names',
        epilog=(f'For a list of subcommands, run `{cmd} help`. '
                f'For information on a specific subcommand, '
                f'run `{cmd} help ‹subcommand›`'))
    parser.add_argument(
        '--config',
        '-c',
        metavar='FILE',
        type=str,
        action='append',
        help='Configuration file.')
    parser.add_argument(
        '--decoder',
        '-d',
        metavar='DECODER',
        type=str,
        choices=vljumap.enc.decoder.keys(),
        help='Default string decoder.')
    parser.add_argument(
        '--encoder',
        '-e',
        metavar='ENCODER',
        type=str,
        choices=vljumap.enc.encoder.keys(),
        help='Default string encoder.')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        '--dsl',
        '-D',
        dest='mode',
        default='dsl',
        const='dsl',
        action='store_const',
        help='Positional arguments are subcommands (default).')
    mode.add_argument(
        '--evaluate',
        '-E',
        dest='mode',
        const='evaluate',
        action='store_const',
        help='Positional arguments are expressions to evaluate.')
    mode.add_argument(
        '--execute',
        '-x',
        dest='mode',
        const='execute',
        action='store_const',
        help='Positional arguments are statements to execute.')
    mode.add_argument(
        '--file',
        '-f',
        dest='mode',
        const='file',
        action='store_const',
        help='Positional arguments are program files.')
    parser.add_argument(
        'argument',
        metavar='ARGUMENT',
        type=str,
        nargs=argparse.REMAINDER,
        default=[],
        help='Part of a subcommand, or an expression or statement.')
    args = parser.parse_args(argv[1 :])

    config = util.config.read_cmd_configs(cmd, args.config)
    options = config.get('option', {})
    if args.decoder:
        options['decoder'] = args.decoder
    if args.encoder:
        options['encoder'] = args.encoder
    vljum.m.M.configure_options(options)
    vljum.m.M.configure_sites(config.get('site', {}))

    try:
        match args.mode:
            case 'dsl':
                vljum.runner.Runner().run(args.argument)
            case 'evaluate':
                for i in args.argument:
                    r = vljum.m.M.evaluate(i)
                    if r is not None:
                        print(r)
            case 'execute':
                for i in args.argument:
                    vljum.m.M.execute(i)
            case 'file':
                for i in args.argument:
                    with util.io.open_input(i) as f:
                        vljum.m.M.execute(f.read())
            case _:
                print(f'{cmd}: Unknown mode: {args.mode}')
        return 0
    except Exception as e:
        print(f'{cmd}: Unhandled exception: {type(e).__name__}{e.args}')
        raise e

if __name__ == "__main__":
    sys.exit(main())
