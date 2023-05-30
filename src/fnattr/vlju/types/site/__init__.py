# SPDX-License-Identifier: MIT
"""Generic web site items."""

import re

from collections.abc import Iterable
from typing import Self

from fnattr.util import fearmat
from fnattr.util.error import Error
from fnattr.vlju.types.uri import URI, Authority
from fnattr.vlju.types.url import URL

Template = str | None

class SiteBase(URL):
    """Base class for SiteFactory-generated Vljus."""

    _scheme: str
    _authority: Authority | None = None
    path_template: Template = None
    query_template: Template = None
    fragment_template: Template = None
    normalize_template: Template = None
    url_patterns: list[tuple[re.Pattern, str]] = []

    def __init__(self, s: str) -> None:
        if (t := match_url(type(self).url_patterns, s)):
            s = t
        if self.normalize_template:
            s = fearmat.fearmat(self.normalize_template, {'id': s, 'x': s})
        super().__init__(s, scheme=self._scheme, authority=self._authority)

    def __str__(self) -> str:
        return self._value

    def path(self) -> str:
        if self.path_template:
            return fearmat.fearmat(self.path_template, {
                'id': self._value,
                'x': self._value,
            })
        return self._value

    def query(self) -> str:
        if self.query_template:
            return fearmat.fearmat(self.query_template, {
                'id': self._value,
                'x': self._value,
            })
        return ''

    def fragment(self) -> str:
        if self.fragment_template:
            return fearmat.fearmat(self.fragment_template, {
                'id': self._value,
                'x': self._value,
            })
        return ''

    def cast_params(self, t: object) -> tuple[str, dict]:
        if t is URI or t is URL:
            return (self.path(),
                    {
                        'scheme': self._scheme,
                        'authority': self._authority,
                        'query': self.query(),
                        'fragment': self.fragment(),
                    })
        raise self.cast_param_error(t)

    @classmethod
    def from_url(cls, url: str) -> Self:
        if (s := cls.match_url(url)):
            return cls(s)
        message = f'URL not recognized: {url!r}'
        raise Error(message)

    @classmethod
    def match_url(cls, url: str) -> str:
        return match_url(cls.url_patterns, url)

def site_class(name: str,
               host: Authority | str,
               path: Template,
               scheme: str | None = None,
               query: Template = None,
               fragment: Template = None,
               normalize: Template = None,
               url: Iterable[str | list[str]] | None = None) -> type[SiteBase]:
    return type(
        name, (SiteBase, ),
        {
            '_scheme': scheme if scheme is not None else 'https',
            '_authority': Authority(host),
            'path_template': unlistify(path),
            'query_template': unlistify(query),
            'fragment_template': unlistify(fragment),
            'normalize_template': unlistify(normalize),
            'url_patterns': site_url_patterns(url),
        })

def unlistify(s: str | list[str] | None) -> str | None:
    if s is None or isinstance(s, str):
        return s
    return ''.join(s)

def site_url_patterns(
    urls: Iterable[str | list[str]] | None = None,
) -> list[tuple[re.Pattern, str]]:
    if not urls:
        return []
    r = []
    for url in urls:
        if isinstance(url, list):
            pattern = url[0]
            replacement = url[1] if len(url) > 1 else r'\1'
        else:
            pattern = url
            replacement = r'\1'
        r.append((re.compile(pattern, re.ASCII | re.VERBOSE), replacement))
    return r

def match_url(patterns: list[tuple[re.Pattern, str]], url: str) -> str:
    for pattern, replacement in patterns:
        if (m := pattern.fullmatch(url)):
            return m.expand(replacement)
    return ''
