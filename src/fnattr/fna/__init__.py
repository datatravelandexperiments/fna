# SPDX-License-Identifier: MIT
"""`fna` command."""

import argparse
import logging
import pathlib
import sys

import fnattr.util.config
import fnattr.util.io
import fnattr.util.log
import fnattr.vljum.m
import fnattr.vljum.runner
import fnattr.vljumap.enc

def main(argv: list[str] | None = None) -> int:
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
        choices=fnattr.vljumap.enc.decoder.keys(),
        help='Default string decoder.')
    parser.add_argument(
        '--encoder',
        '-e',
        metavar='ENCODER',
        type=str,
        choices=fnattr.vljumap.enc.encoder.keys(),
        help='Default string encoder.')
    parser.add_argument(
        '--log-level',
        '-L',
        metavar='LEVEL',
        type=str,
        choices=fnattr.util.log.CHOICES,
        default='WARNING')
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

    log.level(cmd, args.log_level)

    config, options = fnattr.util.config.read_cmd_configs_and_merge_options(
        cmd,
        args.config,
        args,
        decoder='v3',
        encoder='v3',
    )
    fnattr.vljum.m.M.configure_options(options)
    fnattr.vljum.m.M.configure_sites(config.get('site', {}))

    try:
        match args.mode:
            case 'dsl':
                fnattr.vljum.runner.Runner().run(args.argument)
            case 'evaluate':
                for i in args.argument:
                    r = fnattr.vljum.m.M.evaluate(i)
                    if r is not None:
                        print(r)
            case 'execute':
                for i in args.argument:
                    fnattr.vljum.m.M.execute(i)
            case 'file':
                for i in args.argument:
                    with fnattr.util.io.open_input(i) as f:
                        fnattr.vljum.m.M.execute(f.read())
            case _:
                logging.error('Unknown mode: %s', args.mode)
    except Exception as e:
        logging.error('Unhandled exception: %s%s', type(e).__name__, e.args)
        if logging.getLogger().getEffectiveLevel() < logging.INFO:
            raise

    return 0

if __name__ == '__main__':
    sys.exit(main())
