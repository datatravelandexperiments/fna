# SPDX-License-Identifier: MIT
"""Generic web site items."""

from typing import Type

from vlju.types.uri import Authority, URI
from vlju.types.url import URL

import util.fearmat

Template = str | None

class SiteBase(URL):
    """Base class for SiteFactory-generated Vljus."""
    _scheme: str
    _authority: Authority | None = None
    path_template: Template = None
    query_template: Template = None
    fragment_template: Template = None
    normalize_template: Template = None

    def __init__(self, s: str):
        if self.normalize_template:
            s = util.fearmat.fearmat(self.normalize_template, {'x': s})
        super().__init__(s, scheme=self._scheme, authority=self._authority)

    def __str__(self) -> str:
        return self._value

    def path(self) -> str:
        if self.path_template:
            return util.fearmat.fearmat(self.path_template, {'x': self._value})
        return self._value

    def query(self) -> str:
        if self.query_template:
            return util.fearmat.fearmat(self.query_template, {'x': self._value})
        return ''

    def fragment(self) -> str:
        if self.fragment_template:
            return util.fearmat.fearmat(self.fragment_template,
                                        {'x': self._value})
        return ''

    def cast_params(self, t) -> tuple[str, dict]:
        if t is URI or t is URL:
            return (self.path(), {
                'scheme': self._scheme,
                'authority': self._authority,
                'query': self.query(),
                'fragment': self.fragment()
            })
        raise self.cast_param_error(t)

def site_class(name: str,
               host: Authority | str,
               path: Template,
               scheme: str | None = None,
               query: Template = None,
               fragment: Template = None,
               normalize: Template = None) -> Type[SiteBase]:
    return type(
        name, (SiteBase, ), {
            '_scheme': scheme if scheme is not None else 'https',
            '_authority': Authority(host),
            'path_template': path,
            'query_template': query,
            'fragment_template': fragment,
            'normalize_template': normalize,
        })
