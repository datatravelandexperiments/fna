# SPDX-License-Identifier: MIT
"""ISBN (International Standard Book Number)."""

import array
import bisect
import warnings

from fnattr.util import checksum
from fnattr.vlju.types.ean import EAN13, as13, is_valid_ean13, isbn_ranges

def constraint(t: object, s: str) -> None:
    if not t:                   # pragma: no branch
        raise RuntimeError(s)   # pragma: no cover

RangeAgencies = dict[tuple[str, str], str]

class Ranges:
    """Provides ISBN splitting."""

    def __init__(self, start: array.array, split: array.array) -> None:
        # SoA: _start is sorted lower bounds, _split is corresponding split.
        self._start = start
        self._split = split

    def split(self, s: str) -> tuple[str, ...]:
        """Split a string isbn1, with no separators."""
        constraint(len(s) == 13, 'length not 13')
        constraint(s.isdigit(), 'non-digit')
        i = bisect.bisect_right(self._start, int(s))
        if i <= 0:
            warnings.warn(f'ISBN {s} not found in split table', stacklevel=0)
            return (s, )
        return self._isplit(s, self._split[i - 1])

    @staticmethod
    def _isplit(s: str, i: int) -> tuple[str, ...]:
        """Split a string according to the integer pattern."""
        r = []
        while i:
            d = int(i % 10)
            i = i // 10
            constraint(d != 0, 'zero segment')
            r.append(s[-d :])
            s = s[:-d]
        r.append(s)
        return tuple(reversed(r))

class ISBN(EAN13):
    """Represents an ISBN (International Standard Book Number)."""

    _ranges = Ranges(isbn_ranges.START, isbn_ranges.SPLIT)
    split_all = False

    def __init__(self, s: str, *, split: bool = False) -> None:
        # self._value contains an unsplit ISBN-13 string.
        v = as13(s, 'isbn')
        if v is None:
            raise ValueError(s)
        super().__init__(v, 'isbn')
        self._parts: tuple[str, ...] | None = None
        if split or self.split_all:
            self.split()

    def isbn13(self) -> str:
        """Return an unsplit ISBN-13."""
        return self._value

    def isbn10(self) -> str | None:
        """Return an unsplit ISBN-10, or None if not representable."""
        if self._value and self._value.startswith('978'):
            s = self._value[3 : 12]
            return s + checksum.mod11(s)
        return None

    def split(self) -> tuple[str, ...]:
        if self._parts is None:
            self._parts = self._ranges.split(self._value)
        return self._parts

    def split13(self) -> str:
        """Return a canonically split ISBN-13."""
        return '-'.join(map(str, self.split()))

    def split10(self) -> str | None:
        """Return a canonically split ISBN-10."""
        parts = self.split()
        if parts[0] == '978':
            check = checksum.mod11(self._value[3 : 12])
            return '-'.join(parts[1 :-1]) + '-' + check
        return None

def is_valid_isbn10(s: str) -> bool:
    """Check for 10-character-only form."""
    return (len(s) == 10 and s[0 : 8].isdigit()
            and checksum.mod11(s[0 : 8]) == s[9])

def is_valid_isbn13(s: str) -> bool:
    """Check for 13-digit-only form."""
    return is_valid_ean13(s)
