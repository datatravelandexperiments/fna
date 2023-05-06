# SPDX-License-Identifier: MIT
"""EAN13 - Vlju representing a EAN13"""

import util.checksum

from vlju.types.urn import URN

def is_valid_ean13(s: str) -> bool:
    """Checks for 13-digit-only form."""
    return (len(s) == 13 and s.isdigit()
            and util.checksum.alt13(s[0 : 12]) == s[12])

def to13(s: str) -> str | None:
    """Convert other forms to E-13."""
    s = s.replace('-', '')
    s = s.replace('.', '')
    if len(s) == 8:
        s = '977' + s[: 7] + '000'  # ISSN → EAN13
    if len(s) == 9:
        s = '0' + s                 # SBN → ISBN
    if len(s) == 10:
        if s[0].lower() == 'm':
            s = '9790' + s[1 :]     # ISMN → EAN13
        else:
            s = '978' + s           # ISBN → EAN13
    if len(s) == 12:
        s = '0' + s                 # UPC-A → EAN13
    if len(s) == 13 and s[0 : 12].isdigit():
        return s[0 : 12] + util.checksum.alt13(s[0 : 12])
    return None

def key13(s: str) -> str:
    """Classify an E-13."""
    t = s[: 3]
    if t == '977':
        return 'issn'
    if t == '978':
        return 'isbn'
    if t == '979':
        if s[3] == '0':
            return 'ismn'
        return 'isbn'
    return 'ean13'

def as13(s: str, key: str) -> str | None:
    if (e := to13(s)) and (key13(e) == key):
        return e
    return None

class EAN13(URN):
    """Represents an EAN-13 article number."""

    def __init__(self, v: str, k: str = 'ean13'):
        u = to13(v)
        if u is None:
            raise ValueError(v)
        super().__init__(u, k)

    def __str__(self) -> str:
        return self._value

    def __int__(self) -> int:
        return int(self._value)
