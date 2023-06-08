# SPDX-License-Identifier: MIT

import argparse
import hashlib
import logging
import os
import re
import sys

from pathlib import Path
from typing import Any

from fnattr.util.config import read_cmd_configs, merge_options
from fnattr.util.sqlite import SQLite
from fnattr.vljum.m import M
from fnattr.vljumap import enc

COLUMNS = [
    'Title',
    'Subtitle',
    'Author',
    'Editor',
    'Edition',
    'Copyright Year',
    'Publication Date',
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
                m.add(f, a.strip())

    for k, f in (('ISBN#', 'isbn'), ('LCCN#', 'lccn'), ('DOI', 'doi'),
                 ('ISSN#', 'issn'), ('Edition',
                                     'edition'), ('LoC Classification', 'loc')):
        if t := row.get(k):
            m.add(f, t)

    for k in ('Publication Date', 'Copyright Year'):
        if t := row.get(k):
            m.add('date', fix_date(t, options))

    subdir = destination_dir(options, m)
    dstdir = options['destination'] / subdir
    maxlen = min(options['PATH_MAX'] - len(str(dstdir)) - 1,
                 options['FILE_MAX']) - len(p.suffix)
    file = destination_file(options, maxlen, m)
    if file is None:
        return None
    file += p.suffix
    logging.debug('DIR:  ‘%s’', dstdir)
    logging.debug('FILE: ‘%s’', file)
    dst = Path(dstdir) / Path(file)
    logging.debug('DST:  ‘%s’', dst)
    return dst

def fix_title(s: str, options) -> str:
    if options['the'] == 'start' and s.endswith(', The'):
        s = 'The ' + s[:-5]
    elif options['the'] == 'end' and s.startswith('The '):
        s = s[4 :] + ', The'
    return smarten_up(s, options)

def fix_date(s: str, options) -> str:
    y, n = re.subn(r'.*\b([12]\d{3})\b.*', r'\1', s)
    if n:
        s = y
    return s

def smarten_up(s: str, options) -> str:
    if '--' in s:
        s = s.replace('--', ' — ')
    return ' '.join(s.split())

def destination_dir(options, v: M) -> str:
    if 'loc' in v:
        t = str(v['loc'][0])
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
            return r

    if 'isbn' in v:
        t = str(v['isbn'][0])
        return f'isbn/{(int(t[:6]) - 978000):03}'

    if 'doi' in v:
        t = str(v['doi'][0])
        assert isinstance(t, vlju.types.all.DOI)
        return f'doi/{str(t.prefix())}'

    return 'other'

def destination_file(options, maxlen: int, m: M) -> str | None:
    keys = []
    if 'title' in m:
        keys.append('title')
    for k in ('a', 'ed'):
        if k in m:
            keys.append(k)
            break
    for k in ('isbn', 'doi', 'lccn', 'issn'):
        if k in m:
            keys.append(k)
            break
    for k in ('edition', 'date'):
        if k in m:
            keys.append(k)
    if 'date' in m:
        keys.append('date')
    m = m.submap(keys)

    encoder = m.encoder.get()
    s = encoder.encode(m)
    if len(s) <= maxlen:
        return s

    for k in ('date', 'edition', 'ed'):
        if k in keys:
            keys.remove(k)
            s = encoder.encode(m)
            if len(s) <= maxlen:
                return s

    for k in ('title', 'a'):
        while len(m[k]) > 1:
            m[k].pop()
            s = encoder.encode(m)
            if len(s) <= maxlen:
                return s

    return None

def sha1(p: Path) -> str | None:
    if p.is_file():
        try:
            with open(p, 'rb', buffering=0) as f:
                return hashlib.file_digest(f, hashlib.sha1).hexdigest()
        except IOError as e:
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
            with open(file, 'rb', buffering=0) as f:
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
        '--db',
        '--database',
        '-d',
        metavar='DB',
        type=str,
        help='SQLite database file.')
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

    config = read_cmd_configs(cmd, args.config)
    options = merge_options(
        config.get('option'), args, {
            'db': {},
            'decoder': {'default': 'v3'},
            'encoder': {'default': 'v3'},
            'destination': {'default': '.'},
            'the': {'default': 'start'},
        })

    if not args.sha and not args.db:
        logging.error('--db is required')
        return 1

    options['PATH_MAX'] = os.pathconf(args.destination, 'PC_PATH_MAX')
    options['FILE_MAX'] = os.pathconf(args.destination, 'PC_NAME_MAX')
    options['destination'] = Path(options['destination'])

    M.configure_options(options)

    db = SQLite(args.db).connect()
    db.connection().row_factory = dict_factory

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

        cursor = db.load('tellico', *COLUMNS, SHA1=sha)
        rows = cursor.fetchall()
        if len(rows) == 0:
            logging.error('%s: No entry for ‘%s’', cmd, src)
            r = 1
            continue
        if len(rows) > 1:
            if args.ignore_hash_collision:
                logging.warning('%s: Hash collision for ‘%s’: %s', cmd, src,
                                sha)
            else:
                logging.error('%s: Hash collision for ‘%s’: %s', cmd, src, sha)
                logging.debug('%s', rows[0])
                logging.debug('%s', rows[1])
                r = 1
                continue

        dst = destination(src, rows[0], options)
        if dst is None:
            logging.error('%s: Failed to build a new name for ‘%s’', cmd, src)
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
                        # TODO: dirs
                        src.unlink()
                    continue
            logging.error('%s: destination exists: %s', cmd, dst)
            r = 1
            continue

        if not args.dryrun:
            if not dst.parent.is_dir():
                dst.parent.mkdir(parents=True)
            src.rename(dst)

        logging.info('To:   %s', dst)

    db.close()
    return r

if __name__ == '__main__':
    sys.exit(main(sys.argv))
