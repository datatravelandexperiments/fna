# SPDX-License-Identifier: MIT
"""Rename files using Danbooru metadata."""

import argparse
import hashlib
import logging
import sys

from collections.abc import Callable, Generator, Mapping
from pathlib import Path

import pybooru  # type: ignore[import]

from fnattr.extra.fnaffle import Destinations, rename
from fnattr.util import log, nested
from fnattr.util.config import read_cmd_configs_and_merge_options
from fnattr.vljum.m import M
from fnattr.vljumap import enc

def split_tags(tags: str) -> Generator[str, None, None]:
    return (s.replace('_', ' ') for s in tags.split())

def add_tags(m: M,
             key: str,
             tags: str,
             cmap: Mapping,
             cf: Callable[[str], str] | None = None) -> None:
    if not tags:
        return
    for tag in split_tags(tags):
        if cmap and tag in cmap:
            v = cmap[tag]
        elif cf:
            v = cf(tag)
        else:
            v = tag
        m.add(key, v)

def capitalize_tag(s: str) -> str:
    if (n := s.find('(')) > 0:
        s = s[: n].strip()
    return ' '.join(t.capitalize() for t in s.split())

def file_md5(file: str | Path) -> str | None:
    try:
        with Path(file).open('rb') as f:
            return hashlib.file_digest(f, hashlib.md5).hexdigest()
    except OSError as e:
        logging.error(e)
        return None

def dan_fetch_md5(d: pybooru.Danbooru, md5: str) -> dict | None:
    try:
        return d.post_list(md5=md5)
    except pybooru.exceptions.PybooruHTTPError:
        return None

def danboorize(m: M, p: dict, defs: Mapping) -> None:
    if 'id' in p:
        m.reset('dan', str(p['id']))
    add_tags(m, 'c', str(p.get('tag_string_character', '')),
             nested.nget(defs, ['tag', 'c'], []), capitalize_tag)
    add_tags(m, 'a', str(p.get('tag_string_artist', '')),
             nested.nget(defs, ['tag', 'a'], []), capitalize_tag)
    if (tags := defs.get('tag')):
        for tag in split_tags(p.get('tag_string', '')):
            if tag in tags and isinstance((kv := tags[tag]), str):
                kv = tags[tag]
                if '=' in kv:
                    k, v = kv.split('=', 1)
                else:
                    k = kv
                    v = ''
                m.add(k, v)
    if (source := p.get('source')):
        k, v = m.from_site_url(source)
        if k:
            m.add(k, v)
    if (pixiv := p.get('pixiv_id')) and 'pixiv' not in m:
        m.add('pixiv', str(pixiv))
    m.order()

def run(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv
    cmd = Path(argv[0]).stem
    parser = argparse.ArgumentParser(
        prog=cmd, description='Rename files according to Danbooru metadata')
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
        help='File name decoder.')
    parser.add_argument(
        '--encoder',
        '-e',
        metavar='DECODER',
        type=str,
        choices=enc.encoder.keys(),
        help='File name encoder.')
    parser.add_argument(
        '--dryrun',
        '-n',
        default=False,
        action='store_true',
        help='Do not actually rename.')
    parser.add_argument(
        '--md5',
        default=False,
        action='store_true',
        help='Arguments are MD5 hashes rather than file names.')
    parser.add_argument(
        '--merge',
        '-m',
        default=True,
        action=argparse.BooleanOptionalAction,
        help='Merge with existing attributes.')
    parser.add_argument(
        '--log-level',
        '-L',
        metavar='LEVEL',
        type=str,
        choices=log.CHOICES,
        default='info')
    parser.add_argument(
        '--url',
        '-u',
        metavar='URL',
        type=str,
        default='https://danbooru.donmai.us/')
    parser.add_argument('--user', '-U', metavar='USER', type=str)
    parser.add_argument(
        '--token', '-T', metavar='TOKEN', type=str, help='API token.')

    parser.add_argument(
        '-Q', default=False, action='store_true', help='Quit early.')

    parser.add_argument(
        'file',
        metavar='FILENAME',
        type=str,
        nargs=argparse.REMAINDER,
        default=[],
        help='File name(s).')
    args = parser.parse_args(argv[1 :])

    log.level(cmd, args.log_level, dryrun=args.dryrun)
    config, options = read_cmd_configs_and_merge_options(
        ['fnaffle', cmd],
        args.config,
        args,
        decoder='v3',
        encoder='v3',
        user={'option': 'provider.danbooru.user'},
        token={'option': 'provider.danbooru.token'},
    )
    M.configure_options(options)
    #   M.configure_sites(config.get('site', {}))

    tags: dict[str, str] = {}
    for k in (['global'], ['provider', 'danbooru']):
        if (m := nested.ngetor(config, [*k, 'tag'])):
            tags = nested.nupdate(tags, m)

    d = Destinations.from_config(config)
    d.values['tag'] = tags

    s = pybooru.Danbooru(
        site_url=args.url,
        username=nested.nget(options, ['provider', 'danbooru', 'user'], ''),
        api_key=nested.nget(options, ['provider', 'danbooru', 'token'], ''))
    for file in args.file:
        m = M()
        if args.merge:
            m.file(file)
        else:
            m.set_path(file)
        if args.md5:
            md5 = file
        elif not (md5 := file_md5(file)):
            continue
        logging.debug('MD5 %s %s', md5, file)

        if not (p := dan_fetch_md5(s, md5)):
            logging.error('No match for: %s', file)
            continue

        danboorize(m, p, d.values)
        if dst := d.match(m):
            m.with_dir(dst)
        rename(m, dryrun=args.dryrun or args.md5)

    return 0

def main(argv: list[str] | None = None) -> int:
    try:
        return run(argv)
    except Exception as e:
        logging.error('Unhandled exception: %s%s', type(e).__name__, e.args)
        if logging.getLogger().getEffectiveLevel() < logging.INFO:
            raise
        return 1

if __name__ == '__main__':
    sys.exit(main())
