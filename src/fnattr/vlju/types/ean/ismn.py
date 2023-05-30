# SPDX-License-Identifier: MIT
"""ISMN (International Standard Music Number)."""

from fnattr.vlju.types.ean import EAN13, as13

class ISMN(EAN13):
    """Represents an ISMN (International Standard Music Number)."""

    def __init__(self, s: str) -> None:
        v = as13(s, 'ismn')
        if v is None:
            msg = f'value {s} is not an ISMN'
            raise ValueError(msg)
        super().__init__(v, 'ismn')

    def lv(self) -> str:
        if self._value[: 4] != '9790':      # pragma: no branch
            raise ValueError(self._value)   # pragma: no cover
        return f'M{self._value[4:]}'

    def path(self) -> str:
        return self.lv()
