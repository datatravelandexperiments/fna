# SPDX-License-Identifier: MIT
"""URI - Vlju representable as a URI"""

import re

from typing import Any, Self

import util.repr
import util.escape

from util.typecheck import needtype
from vlju import Vlju

class Authority:
    """Authority represents a URI authority."""
    host: str
    port: int | None = None
    username: str | None = None
    password: str | None = None

    def __init__(self,
                 host: str | Self,
                 port: int | None = None,
                 username: str | None = None,
                 password: str | None = None):

        if isinstance(host, Authority):
            self.username = host.username
            self.password = host.password
            self.host = host.host
            self.port = host.port
        elif isinstance(host, str):
            if host.startswith('//'):
                host = host[2 :]
            if '@' in host:
                assert username is None
                up, host = host.split('@', 1)
                if ':' in up:
                    assert password is None
                    self.username, self.password = up.split(':', 1)
                else:
                    self.username = up
            if ':' in host:
                assert port is None
                host, p = host.split(':', 1)
                self.port = int(p)
            self.host = host.lower()
        else:
            raise TypeError

        if port is not None:
            self.port = port
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password

    def __repr__(self) -> str:
        return util.repr.mkrepr(self, ['host'],
                                ['port', 'username', 'password'])

    def __str__(self) -> str:
        r = ''
        if self.username:
            r += util.escape.auth.encode(self.username)
            if self.password:
                r += ':' + util.escape.auth.encode(self.password)
            r += '@'
        r += util.escape.auth.encode(self.host)
        if self.port:
            r += f':{self.port}'
        return r

    def __eq__(self, other) -> bool:
        try:
            return (self.host == other.host and self.port == other.port
                    and self.username == other.username
                    and self.password == other.password)
        except AttributeError:
            return False

AuthorityArg = Authority | str | None

def auth(a: AuthorityArg) -> Authority | None:
    if a is None:
        return None
    if isinstance(a, Authority):
        return a
    return Authority(a)

class URI(Vlju):
    """Represents a URI.

    short:  uri
    long:   uri
    where:
        uri   → `scheme()` `_sa` `sauthority()` `_ap` `spath()`
                `squery()` `sfragment()` `sr()` `sq()`
    """

    def __init__(self, s, **kwargs):
        if isinstance(s, str):
            if kwargs:
                v: str = s
            else:
                v, kwargs = split_uri(s)
        elif hasattr(s, 'cast_params'):
            v, d = s.cast_params(type(self))
            kwargs = d | kwargs
        else:
            raise TypeError(s)
        super().__init__(v)
        self._scheme: str = needtype(kwargs.get('scheme', ''), str)
        self._authority: Authority | None = auth(kwargs.get('authority'))
        self._query: str | None = needtype(kwargs.get('query'), str, None)
        self._fragment: str | None = needtype(kwargs.get('fragment'), str, None)
        self._urnq: str | None = needtype(kwargs.get('urnq'), str, None)
        self._urnr: str | None = needtype(kwargs.get('urnr'), str, None)
        sa = kwargs.get('sa')  # scheme/authority separator
        if sa is None:
            sa = ':' if self._scheme else ''
            sa += '//' if self._authority else ''
        self._sa: str = needtype(sa, str)
        ap = kwargs.get('ap')  # authority/path separator
        if ap is None:
            ap = '/' if (self._authority and self._value[0].isalnum()) else ''
        self._ap: str = needtype(ap, str)

    def scheme(self) -> str:
        return self._scheme

    def path(self) -> str:
        return self._value

    def authority(self) -> Authority | None:
        return self._authority

    def query(self) -> str | None:
        return self._query

    def q(self) -> str | None:
        return self._urnq

    def r(self) -> str | None:
        return self._urnr

    def fragment(self) -> str | None:
        return self._fragment

    def spath(self) -> str:
        return f'{util.escape.path.encode(self.path())}'

    def sauthority(self) -> str:
        a = self.authority()
        return str(a) if a else ''

    def squery(self) -> str:
        s = self.query()
        return f'?{util.escape.query.encode(s)}' if s else ''

    def sq(self) -> str:
        s = self.q()
        return f'?={util.escape.query.encode(s)}' if s else ''

    def sr(self) -> str:
        s = self.r()
        return f'?+{util.escape.query.encode(s)}' if s else ''

    def sfragment(self) -> str:
        s = self.fragment()
        return f'#{util.escape.fragment.encode(s)}' if s else ''

    def uri(self, path: str | None = None) -> str:
        return (
            self.scheme() + self._sa + self.sauthority() + self._ap +
            (self.spath() if path is None else util.escape.path.encode(path))
            + self.squery() + self.sfragment() + self.sr() + self.sq())

    def cast_params(self, t) -> tuple[str, dict]:
        if t is URI:
            return (self.path(), {
                'scheme': self._scheme,
                'authority': self._authority,
                'query': self._query,
                'fragment': self._fragment,
                'urnq': self._urnq,
                'urnr': self._urnr,
                'sa': self._sa,
                'ap': self._ap
            })
        raise self.cast_param_error(t)

    # Vlju overrides:

    def __str__(self) -> str:
        return self.uri()

    def lv(self) -> str:
        return self.uri()

    def __getitem__(self, key):
        if key in ('scheme', 'path', 'authority', 'query', 'fragment', 'spath',
                   'sscheme', 'sauthority', 'squery', 'sfragment'):
            return getattr(self, key)()
        return super().__getitem__(key)

    def __eq__(self, other):
        try:
            return (self._value == other._value
                    and self._scheme == other._scheme
                    and self._authority == other._authority
                    and self._query == other._query
                    and self._fragment == other._fragment
                    and self._urnq == other._urnq and self._urnr == other._urnr
                    and self._sa == other._sa and self._ap == other._ap)
        except AttributeError:
            return False

    def __repr__(self) -> str:
        return util.repr.mkrepr(    # pragma: no cover
            self, ['_value'],
            ['_scheme', '_sa', '_authority', '_query', '_fragment'])

SCHEME_RE = re.compile(r'(?P<scheme>\w+):(?P<rest>.+)')

def split_uri(s: str) -> tuple[str, dict[str, Any]]:
    """Split a URI string."""
    d = {}

    # scheme
    if m := SCHEME_RE.fullmatch(s):
        d['scheme'], s = m.group('scheme', 'rest')

    # authority
    if s.startswith('//') and (i := s.find('/', 2)) > 0:
        d['authority'] = Authority(s[2 : i])
        s = s[i :]

    # fragment
    if (i := s.find('#')) > 0:
        d['fragment'] = s[i + 1 :]
        s = s[: i]

    # query
    if (i := s.find('?')) > 0:
        d['query'] = s[i + 1 :]
        s = s[: i]

    return (s, d)
