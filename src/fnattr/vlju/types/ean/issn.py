# SPDX-License-Identifier: MIT
"""ISSN - International Standard Serial Number."""

from fnattr.util import checksum
from fnattr.vlju.types.ean import EAN13, as13

class ISSN(EAN13):
    """Represents an ISSN (International Standard Serial Number)."""

    def __init__(self, s: str) -> None:
        # self._value contains an unsplit ISSN-13 string.
        v = as13(s, 'issn')
        if v is None:
            raise ValueError(s)
        super().__init__(v, 'issn')

    def lv(self) -> str:
        if (v := self.split8()) is None:    # pragma: no branch
            raise ValueError(v)             # pragma: no cover
        return v

    def path(self) -> str:
        return self.lv()

    def issn13(self) -> str:
        """Return an unsplit ISSN-13."""
        return self._value

    def issn8(self) -> str | None:
        """Return an unsplit ISSN-8, or None if not representable."""
        if self._value and self._value.startswith('977'):
            s = self._value[3 : 10]
            return s + checksum.mod11(s)
        return None

    def split13(self) -> str:
        v = self._value
        return f'{v[0:3]}-{v[3:7]}-{v[7:10]}-{v[10:12]}-{v[12]}'

    def split8(self) -> str | None:
        if (s := self.issn8()) is None:
            return None
        return f'{s[0:4]}-{s[4:8]}'
