# SPDX-License-Identifier: MIT
"""Move files to directories based on matching attributes."""

import argparse
import logging
import operator
import sys

from collections.abc import Iterable
from pathlib import Path

from fnattr.util.config import merge_options, read_cmd_configs, xdg_config
from fnattr.vljum.m import M
from fnattr.vljumap import enc

def find_map_files(cmd: str) -> list[Path]:
    return [
        f for f in (xdg_config('vlju/fnaffle.map'),
                    xdg_config(f'{cmd}/fnaffle.map'), Path('fnaffle.map'),
                    Path('.fnaffle')) if f is not None and f.exists()
    ]

StringListDict = dict[str, frozenset[str]]

def sets(m: M) -> StringListDict:
    return {k: frozenset(str(a) for a in v) for k, v in m.lists()}

Maps = list[tuple[Path, str, StringListDict]]

def read_map_files(files: Iterable[Path | str]) -> Maps:
    maps: Maps = []
    for file in files:
        maps += read_map_file(file)
    return maps

def read_map_file(file: Path | str) -> Maps:
    maps = []
    with Path(file).open(encoding='utf-8') as f:
        while line := f.readline():
            dst, op, encoding = line.strip().split(None, 2)
            m = M().decode(encoding, 'v3')
            target = sets(m)
            maps.append((Path(dst), op, target))
    return maps

def compare_sets(a: frozenset[str], b: frozenset[str]) -> str:
    if a == b:
        return '='
    if a < b:
        return '⊂'
    if b > a:
        return '⊃'
    return '≠'

def match_map(candidate: StringListDict, condition_op: str,
              condition_values: StringListDict) -> bool:
    oper = {
        '=': operator.eq,
        '≠': operator.ne,
        '⊆': lambda a, b: a == b or a <= b,
        '⊂': frozenset.issubset,
        '⊇': lambda a, b: a == b or b <= a,
        '⊃': frozenset.issuperset,
    }[condition_op]
    for k, v in condition_values.items():
        s = candidate.get(k) or frozenset()
        if not oper(s, v):
            return False
    return True

def find_match(maps: Maps, m: M) -> Path | None:
    ms = sets(m)
    for dst, op, values in maps:
        if match_map(ms, op, values):
            return dst
    return None

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv
    cmd = Path(argv[0]).stem
    parser = argparse.ArgumentParser(
        prog=cmd, description='Move files according to file name attributes')
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
        choices=enc.decoder.keys(),
        help='Default string decoder.')
    parser.add_argument(
        '--dryrun',
        '-n',
        default=False,
        action='store_true',
        help='Do not actually rename.')
    parser.add_argument(
        '--map',
        '-m',
        metavar='FILE',
        type=str,
        action='append',
        help='Renaming map file.')
    parser.add_argument(
        '--log-level',
        '-L',
        metavar='LEVEL',
        type=str,
        choices=[c for c in logging.getLevelNamesMapping() if c != 'NOTSET'],
        default='WARNING')
    parser.add_argument(
        'file',
        metavar='FILENAME',
        type=str,
        nargs=argparse.REMAINDER,
        default=[],
        help='File name(s).')
    args = parser.parse_args(argv[1 :])

    log_level = getattr(logging, args.log_level.upper())
    if args.dryrun and log_level > logging.INFO:
        log_level = logging.INFO
    logging.basicConfig(
        level=log_level, format=f'{cmd}: %(levelname)s: %(message)s')

    config = read_cmd_configs(cmd, args.config)
    options = merge_options(
        config.get('option'),
        args,
        {'decoder': {'default': 'v3'}})
    M.configure_options(options)
    M.configure_sites(config.get('site', {}))

    try:
        if not args.map:
            args.map = find_map_files(cmd)
        if not args.map:
            logging.error('no map file')
            return 1
        maps = read_map_files(args.map)

        for file in args.file:
            m = M().file(file)
            if not (dst := find_match(maps, m)):
                logging.info('no match: %s', file)
                continue
            if not dst.exists():
                if not args.dryrun:
                    dst.mkdir(parents=True)
                logging.info('created directory: %s', dst)
            logging.info('to %s: %s', dst, file)
            if not args.dryrun:
                try:
                    m.with_dir(dst).rename()
                except FileExistsError:
                    logging.error('file exists: %s', file)

    except Exception as e:
        logging.error('Unhandled exception: %s%s', type(e).__name__, e.args)
        if logging.getLogger().getEffectiveLevel() < logging.INFO:
            raise
    return 0

if __name__ == '__main__':
    sys.exit(main())
