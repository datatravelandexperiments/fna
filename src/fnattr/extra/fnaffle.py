# SPDX-License-Identifier: MIT
"""Move files to directories based on matching attributes."""

import argparse
import logging
import sys

from collections.abc import Iterable, MutableMapping
from pathlib import Path

from fnattr.util.config import read_cmd_configs, merge_options, xdg_config
from fnattr.vljum.m import M
from fnattr.vljumap import enc

def find_map_files(cmd: str) -> list[Path]:
    return [
        f for f in (xdg_config('vlju/fnaffle.map'),
                    xdg_config(f'{cmd}/fnaffle.map'), Path('fnaffle.map'),
                    Path('.fnaffle')) if f is not None and f.exists()
    ]

Maps = list[tuple[Path, str, dict]]

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
            target = sorted_strings(m)
            maps.append((Path(dst), op, target))
    return maps

StringListDict = dict[str, list[str]]

def sorted_strings(m: M) -> StringListDict:
    d = {}
    for k in sorted(m.keys()):
        d[k] = sorted(str(v) for v in m[k])
    return d

def compare_sorted_lists(a: list, b: list) -> str:
    r = 3
    an = len(a)
    bn = len(b)
    ai = 0
    bi = 0
    while ai < an and bi < bn and r:
        if a[ai] < b[bi]:
            r &= ~1
            ai += 1
            continue
        if a[ai] > b[bi]:
            r &= ~2
            bi += 1
            continue
        ai += 1
        bi += 1
    if (r & 1) and ai < an:
        r &= ~1
    if (r & 2) and bi < bn:
        r &= ~2
    return ['≠', '⊂', '⊃', '='][r]

def match_map(op: str, source: StringListDict, target: StringListDict) -> bool:
    ok = {
        '⊆': ('⊂', '='),
        '⊇': ('⊃', '='),
    }.get(op, (op, ))
    for k, v in target.items():
        if not (s := source.get(k)):
            return False
        r = compare_sorted_lists(s, v)
        if r not in ok:
            return False
    return True

def match_maps(maps: Maps, m: M) -> Path | None:
    source = sorted_strings(m)
    for dst, op, target in maps:
        if match_map(op, source, target):
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
        default='INFO')
    parser.add_argument(
        'file',
        metavar='FILENAME',
        type=str,
        nargs=argparse.REMAINDER,
        default=[],
        help='File name(s).')
    args = parser.parse_args(argv[1 :])

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format=f'{cmd}: %(levelname)s: %(message)s')

    config = read_cmd_configs(cmd, args.config)
    options = merge_options(
        config.get('option'), args, {'decoder': {'default': 'v3'}})
    M.configure_options(options)
    M.configure_sites(config.get('site', {}))

    try:
        if not args.map:
            args.map = find_map_files(cmd)
        if not args.map:
            logging.error('%s: no map file', cmd)
            return 1
        maps = read_map_files(args.map)
        for file in args.file:
            m = M().file(file)
            if dst := match_maps(maps, m):
                if not dst.exists():
                    if not args.dryrun:
                        dst.mkdir(parents=True)
                    logging.info('%s: created', dst)
                if not args.dryrun:
                    try:
                        m.with_dir(dst).rename()
                    except FileExistsError:
                        logging.error('file exists: %s', file)
                if args.dryrun or args.verbose:
                    print(f'{dst}: {file}')
            elif args.verbose:
                print(f'no match for {file}')
    except Exception as e:
        logging.error('Unhandled exception: %s%s', type(e).__name__, e.args)
        if logging.getLogger().getEffectiveLevel() < logging.INFO:
            raise
    return 0

if __name__ == '__main__':
    sys.exit(main())
