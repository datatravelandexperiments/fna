# SPDX-License-Identifier: MIT
"""ISMN (International Standard Music Number)."""

from vlju.types.ean import EAN13, as13

class ISMN(EAN13):
    """Represents an ISMN (International Standard Music Number)."""

    def __init__(self, s: str):
        v = as13(s, 'ismn')
        if v is None:
            raise ValueError(f"value {s} is not an ISMN")
        super().__init__(v, 'ismn')

    def lv(self) -> str:
        assert self._value[:4] == '9790'
        return f'M{self._value[4:]}'

    def path(self) -> str:
        return self.lv()
