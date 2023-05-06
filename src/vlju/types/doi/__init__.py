# SPDX-License-Identifier: MIT
"""DOI - Document Object Identifier"""

import re
import urllib.parse

from collections.abc import Sequence
from typing import Self

from util import escape
from util.typecheck import needtype
from vlju.types.info import Info
from vlju.types.uri import Authority, URI
from vlju.types.url import URL

class Prefix(list[int]):
    """Represents a DOI (or Handle) prefix."""

    def __init__(self, p: Self | Sequence | str):
        if isinstance(p, str):
            p = list(map(int, p.split('.')))
        super().__init__(p)

    def is_doi(self) -> bool:
        return self[0] == 10

    def __str__(self) -> str:
        return '.'.join(map(str, self))

    @property
    def prefix(self) -> 'Prefix':
        # Implement prefix so that a Prefix can quack like a DOI.
        return self

class DOI(Info):
    """Represents a DOI (Document Object Identifier) or Handle.

    short:  sdoi
    long:   doi | uri
    where:
        sdoi    → `_prefix` ‘,’ `_suffix`
        doi     → ‘doi:’ `_prefix` ‘/’ `_suffix`ᵖ
    """
    _i = {'doi': Authority('doi'), 'hdl': Authority('hdl')}
    _u = {'doi': Authority('doi.org'), 'hdl': Authority('hdl.handle.net')}

    _matcher = re.compile(
        r"""
            (?P<scheme>
            |https?://((dx.)?doi.org|hdl.handle.net)/
            |(info:)?(hdl|doi)/
            |doi:/*
            )
            (?P<prefix>\d[\d.]*)
            [/,]
            (?P<suffix>.+)
            """, re.VERBOSE)

    def __init__(self, s: str | None = None, **kwargs):
        if s is None:
            prefix = Prefix(kwargs['prefix'])
            suffix = needtype(kwargs['suffix'], str)
        else:
            m = self._matcher.fullmatch(s)
            if not m:
                raise ValueError(s)
            scheme, p, suffix = m.group('scheme', 'prefix', 'suffix')
            prefix = Prefix(p)
            if scheme.startswith('http') or scheme.startswith('info'):
                suffix = urllib.parse.unquote(suffix)
        # Note that DOI does not use Info path or authority.
        super().__init__('')
        self._prefix = prefix
        self._suffix = suffix.lower()
        self._kind = 'doi' if self._prefix.is_doi() else 'hdl'

    def prefix(self) -> Prefix:
        return self._prefix

    def suffix(self) -> str:
        return self._suffix

    def hdl(self, hdl: str = 'hdl') -> str:
        return f'info:{hdl}/{self.spath()}'

    def doi(self):
        if self._prefix.is_doi():
            return f'doi:{self._prefix}/{escape.path.encode(self._suffix)}'
        return super().lv()

    def cast_params(self, t) -> tuple[str, dict]:
        if t is URI:
            return (self.spath(), {
                'scheme': 'info',
                'sa': ':',
                'authority': self._kind,
                'query': self.query(),
                'fragment': self.fragment(),
            })
        if t is URL:
            return (self.spath(), {
                'scheme': 'https',
                'authority': self._u[self._kind],
                'query': self.query(),
                'fragment': self.fragment()
            })
        raise self.cast_param_error(t)

    # URI overrides:

    def __eq__(self, other):
        try:
            return (self._prefix == other._prefix
                    and self._suffix == other._suffix)
        except AttributeError:
            return False

    def authority(self) -> Authority:
        return self._i[self._kind]

    def sauthority(self) -> str:
        return self._kind

    def spath(self) -> str:
        return f'{self._prefix}/{self._suffix}'

    # Vlju overrides:

    def __str__(self) -> str:
        return f'{self._prefix},{self._suffix}'

    def lv(self) -> str:
        return self.doi()

    def __repr__(self):
        return f'DOI(prefix={repr(self._prefix)},suffix={repr(self._suffix)})'
