# SPDX-License-Identifier: MIT
"""URI - Vlju representable as a URI."""

import re

from typing import Any, Self

from fnattr.util import escape
from fnattr.util.repr import mkrepr
from fnattr.util.typecheck import needtype
from fnattr.vlju import Vlju

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
                 password: str | None = None) -> None:

        if isinstance(host, Authority):
            self.username = host.username
            self.password = host.password
            self.host = host.host
            self.port = host.port
        elif isinstance(host, str):
            if host.startswith('//'):
                host = host[2 :]
            if '@' in host:
                up, host = host.split('@', 1)
                if ':' in up:
                    u, p = up.split(':', 1)
                else:
                    u = up
                    p = None
                if username is not None and username != u:
                    message = f'username={username} conflicts with {up}@'
                    raise ValueError(message)
                if password is not None and password != p:
                    message = f'password={password} conflicts with {up}@'
                    raise ValueError(message)
                self.username = u
                self.password = p
            if ':' in host:
                host, pstr = host.split(':', 1)
                pn = int(pstr)
                if port is not None and port != pn:
                    message = f'port={port} conflicts with {host}'
                    raise ValueError(message)
                self.port = pn
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
        return mkrepr(self, ['host'], ['port', 'username', 'password'])

    def __str__(self) -> str:
        r = ''
        if self.username:
            r += escape.auth.encode(self.username)
            if self.password:
                r += ':' + escape.auth.encode(self.password)
            r += '@'
        r += escape.auth.encode(self.host)
        if self.port:
            r += f':{self.port}'
        return r

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Authority):
            return (self.host == other.host and self.port == other.port
                    and self.username == other.username
                    and self.password == other.password)
        return False

AuthorityArg = Authority | str | None

def auth(a: AuthorityArg) -> Authority | None:
    if a is None:
        return None
    if isinstance(a, Authority):
        return a
    return Authority(a)

class URI(Vlju):
    """
    Represents a URI.

    short:  uri
    long:   uri
    where:
        uri   → `scheme()` `_sa` `sauthority()` `_ap` `spath()`
                `squery()` `sfragment()` `sr()` `sq()`
    """

    def __init__(self, s: str | object, **kwargs) -> None:
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
        sa = kwargs.get('sa')   # scheme/authority separator
        if sa is None:
            sa = ':' if self._scheme else ''
            sa += '//' if self._authority else ''
        self._sa: str = needtype(sa, str)
        ap = kwargs.get('ap')   # authority/path separator
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
        return f'{escape.path.encode(self.path())}'

    def sauthority(self) -> str:
        a = self.authority()
        return str(a) if a else ''

    def squery(self) -> str:
        s = self.query()
        return f'?{escape.query.encode(s)}' if s else ''

    def sq(self) -> str:
        s = self.q()
        return f'?={escape.query.encode(s)}' if s else ''

    def sr(self) -> str:
        s = self.r()
        return f'?+{escape.query.encode(s)}' if s else ''

    def sfragment(self) -> str:
        s = self.fragment()
        return f'#{escape.fragment.encode(s)}' if s else ''

    def uri(self, path: str | None = None) -> str:
        return (self.scheme() + self._sa + self.sauthority() + self._ap +
                (self.spath() if path is None else escape.path.encode(path))
                + self.squery() + self.sfragment() + self.sr() + self.sq())

    def cast_params(self, t: object) -> tuple[str, dict]:
        if t is URI:
            return (self.path(),
                    {
                        'scheme': self._scheme,
                        'authority': self._authority,
                        'query': self._query,
                        'fragment': self._fragment,
                        'urnq': self._urnq,
                        'urnr': self._urnr,
                        'sa': self._sa,
                        'ap': self._ap,
                    })
        raise self.cast_param_error(t)

    # Vlju overrides:

    def __str__(self) -> str:
        return self.uri()

    def lv(self) -> str:
        return self.uri()

    def __getitem__(self, key: str | None) -> str:
        if key in ('scheme',
                   'path',
                   'authority',
                   'query',
                   'fragment',
                   'spath',
                   'sscheme',
                   'sauthority',
                   'squery',
                   'sfragment'):
            return getattr(self, key)()
        return super().__getitem__(key)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, URI):
            return (self._value == other._value                 # noqa: SLF001
                    and self._scheme == other._scheme           # noqa: SLF001
                    and self._authority == other._authority     # noqa: SLF001
                    and self._query == other._query             # noqa: SLF001
                    and self._fragment == other._fragment       # noqa: SLF001
                    and self._urnq == other._urnq               # noqa: SLF001
                    and self._urnr == other._urnr               # noqa: SLF001
                    and self._sa == other._sa                   # noqa: SLF001
                    and self._ap == other._ap)                  # noqa: SLF001
        return False

    def __repr__(self) -> str:
        return mkrepr(          # pragma: no cover
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
