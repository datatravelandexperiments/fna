# SPDX-License-Identifier: MIT

import argparse
import hashlib
import logging
import os
import re
import sys

from pathlib import Path
from typing import Any

from fnattr.util.config import read_cmd_configs_and_merge_options
from fnattr.util.sqlite import SQLite
from fnattr.vlju.types.all import DOI
from fnattr.vljum.m import M
from fnattr.vljumap import enc

COLUMNS = [
    'Title',
    'Subtitle',
    'Author',
    'Editor',
    'Edition',
    'Copyright Year',
    'Publication Year',
    'ISBN#',
    'LCCN#',
    'ISSN#',
    'DOI',
    'Series Number',
    'LoC Classification',
]

def destination(p: Path, row, options: dict[str, Any]) -> Path | None:
    logging.debug('row=%s', repr(row))
    m = M()

    for k in ('Title', 'Subtitle'):
        if t := row.get(k):
            m.add('title', fix_title(t, options))

    for k, f in (('Author', 'a'), ('Editor', 'ed')):
        if t := row.get(k):
            for a in t.split(';'):
                m.add(f, a.strip().strip(','))

    for k, f in (('ISBN#', 'isbn'), ('LCCN#', 'lccn'), ('DOI', 'doi'),
                 ('ISSN#', 'issn'), ('Edition', 'edition'),
                 ('LoC Classification', 'loc'), ('Series Number', 'v')):
        if t := row.get(k):
            m.add(f, t)

    for k in ('Publication Date', 'Copyright Year'):
        if t := row.get(k):
            m.add('date', fix_date(t))

    subdir = destination_dir(m)
    dstdir = options['destination'] / subdir
    maxlen = min(options['PATH_MAX'] - len(str(dstdir)) - 1,
                 options['FILE_MAX']) - len(p.suffix)
    logging.debug("DIR:  '%s'", dstdir)
    file = destination_file(m, maxlen)
    if file is None:
        return None
    file += p.suffix
    logging.debug("FILE: '%s'", file)
    dst = Path(dstdir) / Path(file)
    logging.debug("DST:  '%s'", dst)
    return dst

def fix_title(s: str, options: dict[str, Any]) -> str:
    if options['the'] == 'start' and s.endswith(', The'):
        s = 'The ' + s[:-5]
    elif options['the'] == 'end' and s.startswith('The '):
        s = s[4 :] + ', The'
    return smarten_up(s)

def fix_date(s: str) -> str:
    y, n = re.subn(r'.*\b([12]\d{3})\b.*', r'\1', s)
    if n:
        s = y
    return s

def smarten_up(s: str) -> str:
    if '--' in s:
        s = s.replace('--', ' — ')
    return ' '.join(s.split())

def destination_dir(m: M) -> str:
    if 'loc' in m:
        t = str(m['loc'][0])
        b, n = re.subn(r'CPB Box no. (\d+).*', r'\1', t)
        if n:
            b = f'{int(b):04}'
            return f'lc/_CPB_Box_/{b[:2]}xx'
        r = ''
        while t and t[0].isalpha():
            r += t[0]
            t = t[1 :]
        r = r[: 2].upper()
        if r:
            return f'lc/{r}'

    if 'isbn' in m:
        t = str(m['isbn'][0])
        return f'isbn/{(int(t[:6]) - 978000):03}'

    if 'doi' in m:
        t = m['doi'][0]
        assert isinstance(t, DOI)
        return f'doi/{t.prefix()}'

    return 'other'

def destination_file(m: M, maxlen: int) -> str | None:
    keys = [
        k for k in ('title', 'a', 'ed', 'v', 'isbn', 'doi', 'lccn', 'issn',
                    'edition', 'date') if k in m
    ]
    m = m.submap(keys)

    encoder = m.encoder.get()
    s = encoder.encode(m)
    if len(s) <= maxlen:
        return s
    logging.debug('long: %d>%d %s', len(s), maxlen, s)

    for k in ('date', 'edition', 'ed'):
        if k in keys:
            m.remove(k)
            s = encoder.encode(m)
            if len(s) <= maxlen:
                return s
            logging.debug('long: %d>%d %s', len(s), maxlen, s)

    for k in ('title', 'a'):
        while len(m[k]) > 1:
            m[k].pop()
            s = encoder.encode(m)
            if len(s) <= maxlen:
                return s
            logging.debug('long: %d>%d %s', len(s), maxlen, s)

    return None

def sha1(p: Path) -> str | None:
    if p.is_file():
        try:
            with p.open('rb') as f:
                return hashlib.file_digest(f, hashlib.sha1).hexdigest()
        except OSError as e:
            logging.error(e)
            return None

    if p.is_dir():
        files = []
        for dirpath, _, filenames in os.walk(p):
            for file in filenames:
                if file == '.DS_Store':
                    continue
                files.append(f'{dirpath}/{file}')
        files.sort()
        h = hashlib.sha1()
        for file in files:
            with Path(file).open('rb') as f:
                h = hashlib.file_digest(f, lambda: h)
        return h.hexdigest()

    logging.error('%s not found', p)
    return None

def dict_factory(cursor, row) -> dict:
    return dict(zip((column[0] for column in cursor.description), row))

def main(argv):
    cmd = Path(argv[0]).stem
    r = 0

    parser = argparse.ArgumentParser(prog=cmd, description='TODO')
    parser.add_argument(
        '--config',
        '-c',
        metavar='FILE',
        type=str,
        action='append',
        help='Configuration file.')
    parser.add_argument(
        '--db',
        '--database',
        '-d',
        metavar='DB',
        type=str,
        help='SQLite database file.')
    parser.add_argument(
        '--table',
        '-t',
        metavar='TABLE',
        type=str,
        help='SQLite database table.')
    parser.add_argument(
        '--dedup',
        action='store_true',
        help='Remove if destination is identical.')
    parser.add_argument(
        '--destination',
        '--root',
        '-r',
        metavar='DIR',
        type=str,
        help='Destination root.')
    parser.add_argument('--dryrun', '-n', action='store_true')
    parser.add_argument(
        '--encoder',
        '-e',
        metavar='ENCODER',
        type=str,
        choices=enc.encoder.keys(),
        help='Filename encoder.')
    parser.add_argument(
        '--ignore-hash-collision',
        '-I',
        action='store_true',
        help='Ignore hash collisions; use first entry.')
    parser.add_argument(
        '--log-level',
        '-L',
        metavar='LEVEL',
        type=str,
        choices=[c for c in logging.getLevelNamesMapping() if c != 'NOTSET'],
        default='INFO')
    parser.add_argument('--sha', action='store_true', help='Print SHA1 only.')
    parser.add_argument(
        '--the',
        choices=('start', 'end', 'none'),
        help='Move ‘The’ in titles.',
    )
    parser.add_argument(
        'files',
        metavar='FILE',
        type=str,
        nargs='+',
        help='Files to rename',
    )
    args = parser.parse_args(argv[1 :])

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format=f'{cmd}: %(levelname)s: %(message)s')

    _config, options = read_cmd_configs_and_merge_options(
        cmd,
        args.config,
        args,
        db=None,
        table='ebooks',
        destination='.',
        the='start',
    )

    if not args.sha and not args.db:
        logging.error('--db is required')
        return 1

    options['destination'] = Path(options['destination'])
    options['PATH_MAX'] = os.pathconf(options['destination'], 'PC_PATH_MAX')
    options['FILE_MAX'] = os.pathconf(options['destination'], 'PC_NAME_MAX')

    M.configure_options(options)

    if args.db:
        db = SQLite(args.db).connect()
        db.connection().row_factory = dict_factory
    else:
        db = None

    for file in args.files:

        logging.debug('From: %s', file)
        src = Path(file)

        sha = sha1(src)
        if sha is None:
            r = 1
            continue
        if args.sha:
            print(f'{sha} {file}')
            continue
        logging.debug('sha=%s', sha)
        if not db:
            continue

        cursor = db.load(options['table'], *COLUMNS, SHA1=sha)
        rows = cursor.fetchall()
        if len(rows) == 0:
            logging.error("%s: No entry for '%s'", cmd, src)
            r = 1
            continue
        if len(rows) > 1:
            if args.ignore_hash_collision:
                logging.warning("Hash collision for '%s': %s", src, sha)
            else:
                logging.error("Hash collision for '%s': %s", src, sha)
                logging.debug('%s', rows[0])
                logging.debug('%s', rows[1])
                r = 1
                continue

        dst = destination(src, rows[0], options)
        if dst is None:
            logging.error("%s: Failed to build a new name for '%s'", cmd, src)
            r = 1
            continue

        if dst.exists():
            if src.samefile(dst):
                continue
            if args.dedup:
                dstsha = sha1(dst)
                if dstsha == sha:
                    logging.info('%s: destination is identical: %s', cmd, dst)
                    if not args.dryrun and src.is_file():
                        src.unlink()
                    continue
                logging.debug('%s %s', sha, src)
                logging.debug('%s %s', dstsha, dst)
            logging.error('destination exists: %s', dst)
            r = 1
            continue

        if not args.dryrun:
            if not dst.parent.is_dir():
                dst.parent.mkdir(parents=True)
            src.rename(dst)

        logging.info('To:   %s', dst)

    if db:
        db.close()
    return r

if __name__ == '__main__':
    sys.exit(main(sys.argv))
