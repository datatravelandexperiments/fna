# SPDX-License-Identifier: MIT
"""LCCN - Library of Congress Control Number."""

# http://info-uri.info/registry/OAIHandler?verb=GetRecord&metadataPrefix=reg&identifier=info:lccn/

from fnattr.vlju.types.info import Info
from fnattr.vlju.types.uri import Authority
from fnattr.vlju.types.url import URL

def normalize(s: str) -> str:
    """Normalize according to info:lccn."""
    s = s.replace(' ', '')
    if (n := s.find('/')) > 0:
        s = s[: n]
    if (n := s.find('-')) > 0:
        s = f'{s[:n]}{int(s[n + 1:]):06}'
    return s.lower()

class LCCN(Info):
    """
    Represents an LCCN (Library of Congress Control Number).

    short:  value
    long:   uri
    """

    _lc = Authority('lccn.loc.gov')

    def __init__(self, s: str) -> None:
        super().__init__(normalize(s), authority='lccn')

    def cast_params(self, t: object) -> tuple[str, dict]:
        if t is URL:
            return (self.spath(),
                    {
                        'scheme': 'https',
                        'authority': self._lc,
                        'query': self.query(),
                        'fragment': self.fragment(),
                    })
        return super().cast_params(t)

    # Vlju overrides

    def __str__(self) -> str:
        return self._value
