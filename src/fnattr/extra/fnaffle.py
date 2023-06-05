# SPDX-License-Identifier: MIT
"""Move files to directories based on matching attributes."""

import argparse
import builtins
import logging
import os
import re
import sys

from collections.abc import (
    Generator,
    Iterable,
    Mapping,
    MutableMapping,
    MutableSequence,
    Set,
)
from pathlib import Path
from typing import Any, Generic, Self, TypeVar

from fnattr.util import log, nested
from fnattr.util.config import read_cmd_configs_and_merge_options
from fnattr.util.typecheck import needtype
from fnattr.vljum.m import M
from fnattr.vljumap import enc

T = TypeVar('T')
V = TypeVar('V')

class Lazy(Generic[T]):
    """Holds a value."""

    def __init__(self, v: T) -> None:
        self.value: T = v

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.value!r})'

def lazify(a: Any) -> dict | list | set | Lazy:  # noqa: any-type
    if isinstance(a, Mapping):
        return {k: lazify(v) for k, v in a.items()}
    if isinstance(a, Set):
        # Pyright doesn't understand that lazify(v) is hashable if v is.
        return {lazify(v) for v in a}
    if isinstance(a, Iterable) and not isinstance(a, str):
        return [lazify(v) for v in a]
    return Lazy(a)

def zalify(
        a: Lazy[T] | T,
        values: Mapping) -> MutableMapping | MutableSequence | list | set | T:
    """Evaluate Lazy values in place."""
    if isinstance(a, Lazy):
        return zalify(a.value, values)
    if isinstance(a, MutableMapping):
        for k, v in a.items():
            a[k] = zalify(v, values)
        return a
    if isinstance(a, Set):
        return {zalify(v, values) for v in a}
    if isinstance(a, str):
        return zalify_str(a, values)
    if isinstance(a, MutableSequence):
        for i, v in enumerate(a):
            a[i] = zalify(v, values)
        return a
    if isinstance(a, Iterable):
        return [zalify(v, values) for v in a]
    return a

def zalify_str(s: str, values: Mapping) -> Any:
    # print(f'zalify_str {s=}')
    xl, xr = ('«', '»')
    if xl not in s:
        return s
    if s[0] == xl and s[-1] == xr:
        return zalify(nested.dget(values, s[1 :-1], None), values)
    r = []
    while xl in s:
        i = s.index(xl)
        j = s.index(xr, i)
        k = s[i + 1 : j]
        # print(f'     inner {k=}')
        v = nested.dget(values, k, '')
        # print(f'         ↦ {v=}')
        v = zalify(v, values)
        # print(f'         ↦ {v=}')
        r.append(s[: i])
        r.append(str(v))
        s = s[j + 1 :]
    r.append(s)
    return ''.join(r)

def flatten_list(a: Any) -> Generator:
    if isinstance(a, list | set | frozenset):
        for i in a:
            yield from flatten_list(i)
        return
    yield a

def zalify_to_frozenset(v: Any, values: Mapping) -> frozenset:
    t = list(flatten_list(zalify(v, values)))
    return frozenset(list(t))

FrozenSets = dict[str, frozenset]

class Destinations:
    """Record of target directories and associated conditions."""

    builtins = {
        k: getattr(builtins, k)
        for k in (
            'False',
            'None',
            'True',
            'all',
            'any',
            'frozenset',
            'len',
        )
    } | {
        'set': frozenset,
    }
    sets_re = re.compile('‹([^"›]+)›')

    def __init__(self, dests: list, defs: dict, sets: dict) -> None:
        self.values = {
            'def': defs,
            'set': sets,
            'env': os.environ,
        }
        self.singleset: dict[str, dict[frozenset, str]] = {}
        self.conditionals: list[dict] = []
        for k, v in sets.items():
            sets[k] = zalify_to_frozenset(v, self.values)
        for dest in dests:
            directory = zalify(dest['directory'], self.values)
            dest['directory'] = directory
            if 'set' in dest:
                sets = {
                    k: zalify_to_frozenset(v, self.values)
                    for k, v in dest['set'].items()
                }
                if len(sets) == 1 and 'condition' not in dest:
                    # Pure single set match.
                    k, v = list(sets.items())[0]
                    nested.nset(self.singleset, [k, frozenset(v)], directory)
                    continue
                dest['set'] = sets
            self.conditionals.append(dest)

    @classmethod
    def from_config(cls, config: Mapping) -> Self:
        defs: dict = needtype(lazify(config.get('def', {})), dict)
        sets: dict = needtype(lazify(config.get('set', {})), dict)
        dests: list = needtype(lazify(config.get('destination', [])), list)
        return cls(dests, defs, sets)

    def match(self, m: M) -> Path | None:
        msets: FrozenSets = {}
        if dst := self._match_single_set(m, msets):
            return dst
        if dst := self._match_conditionals(m, msets):
            return dst
        return None

    def _match_single_set(self, m: M, msets: FrozenSets) -> Path | None:
        for k, s in self.singleset.items():
            mset = mget(m, msets, k)
            if mset in s:
                return Path(s[mset])
        return None

    def _match_conditionals(self, m: M, msets: FrozenSets) -> Path | None:
        for c in self.conditionals:
            if dst := self._match_condition(m, msets, c):
                return dst
        return None

    def _match_condition(self, m: M, msets: FrozenSets, c: dict) -> Path | None:
        if 'set' in c:
            for k, s in c['set'].items():
                # Attribute must be a nonempty subset.
                mset = mget(m, msets, k)
                if not (mset and mset.issubset(s)):
                    return None
        condition = c['condition']
        if isinstance(condition, Lazy):
            condition = zalify(condition, self.values)
            if isinstance(condition, str):
                condition = self.sets_re.sub('(sets["\\1"])', condition)
            c['condition'] = condition
        if isinstance(condition, str):
            for k in m:
                mget(m, msets, k)
            logging.debug('condition: %s', condition)
            r = eval(condition, {'sets': msets, '__builtins__': self.builtins})
        else:
            r = condition
        if bool(r):
            return Path(c['directory'])
        return None

def mget(m: M, msets: FrozenSets, key: str) -> frozenset:
    if key not in msets:
        msets[key] = frozenset(str(a) for a in m.get(key, []))
    return msets[key]

def rename(m: M, *, dryrun: bool = False) -> bool:
    try:
        m.rename(dryrun=dryrun, dedup=True)
    except FileExistsError:
        logging.error('file exists: %s', m.filename())
        return False
    return True

def run(argv: list[str] | None = None) -> int:
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
        choices=log.CHOICES,
        default='WARNING')
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
        cmd, args.config, args, decoder='v3')
    M.configure_options(options)
    #   M.configure_sites(config.get('site', {}))

    d = Destinations.from_config(config)
    for file in args.file:
        m = M().file(file)
        if not (dst := d.match(m)):
            logging.info('no match: %s', file)
            continue
        rename(m.with_dir(dst), dryrun=args.dryrun)

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
