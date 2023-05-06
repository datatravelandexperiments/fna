#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

from collections.abc import Iterable

import argparse
import sys

from pathlib import Path

from util.config import read_cmd_configs, xdg_config
from vlju import Vlju
from vljum.m import M
from vljumap import enc

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
    with open(file, 'rt', encoding='utf-8') as f:
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

def compare_sorted_lists(a: list, b: list):
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
    }.get(op, (op,))
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

def main(argv: list[str] | None = None):
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
        '--verbose',
        '-v',
        default=False,
        action='store_true',
        help='Report renaming.')
    parser.add_argument(
        'file',
        metavar='FILENAME',
        type=str,
        nargs=argparse.REMAINDER,
        default=[],
        help='File name(s).')
    args = parser.parse_args(argv[1 :])

    config = read_cmd_configs(cmd, args.config)
    options = config.get('option', {})
    if args.decoder:
        options['decoder'] = args.decoder
    M.configure_options(options)
    M.configure_sites(config.get('site', {}))

    try:
        if not args.map:
            args.map = find_map_files(cmd)
        if not args.map:
            print(f'{cmd}: no map file.')
            return 1
        maps = read_map_files(args.map)
        for file in args.file:
            m = M().file(file)
            if dst := match_maps(maps, m):
                if not dst.exists():
                    if not args.dryrun:
                        dst.mkdir(parents=True)
                    if args.dryrun or args.verbose:
                        print(f'{dst}: created')
                if not args.dryrun:
                    try:
                        m.dir(dst).rename()
                    except FileExistsError as e:
                        print(f'{cmd}: file exists: {e}')
                if args.dryrun or args.verbose:
                    print(f'{dst}: {file}')
            elif args.verbose:
                print(f'no match for {file}')
        return 0
    except Exception as e:
        print(f'{cmd}: Unhandled exception: {type(e).__name__}{e.args}')
        raise e

if __name__ == "__main__":
    sys.exit(main())
