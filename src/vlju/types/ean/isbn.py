# SPDX-License-Identifier: MIT
"""ISBN (International Standard Book Number)."""

import array
import bisect
import logging
import warnings
import xml.etree.ElementTree as ElT

from pathlib import Path

import util.checksum

from vlju.types.ean import EAN13, as13, is_valid_ean13

# logging.getLogger().setLevel(level=logging.DEBUG)

def constraint(t: object, s: str) -> None:
    # We don't currently test against a malformed range file.
    if not t:  # pragma: no branch
        raise RuntimeError(s)  # pragma: no cover

class Ranges:
    """Provides ISBN splitting."""

    _ranges_xml = Path(__file__).parent / 'RangeMessage.xml'

    def __init__(self):
        self._initialized = False
        self._agency = {}
        # SoA: _start is sorted lower bounds, _split is corresponding split.
        self._start = None
        self._split = None

    def init(self) -> None:
        """Lazy initialization."""
        if not self._initialized:
            self._load_ranges(self._ranges_xml)

    def _load_ranges(self, f: Path):
        """Load ISBN ranges from a file."""
        root = ElT.parse(f).getroot()
        constraint(root.tag == 'ISBNRangeMessage',
                   'root is not ISBNRangeMessage')

        starts: list[int] = []
        lengths: list[int] = []
        for rg in root.iter('RegistrationGroups'):
            for g in rg.iter('Group'):
                self._load_group(g, starts, lengths)
        self._start = array.array('Q', starts)
        self._split = array.array('I', lengths)
        self._initialized = True

    def _load_group(self, g, starts, lengths):
        s_prefix = g.findtext('Prefix')
        constraint(s_prefix is not None, 'missing Prefix')
        s_compact_prefix = s_prefix.replace('-', '')
        ts_prefix: tuple[str, ...] = tuple(s_prefix.split('-'))
        self._agency[ts_prefix] = g.findtext('Agency')
        ti_prefix_length: tuple[int, ...] = tuple(map(len, ts_prefix))
        remaining = 12 - sum(ti_prefix_length)
        logging.debug('prefix %s %s + %d', s_prefix, ti_prefix_length,
                      remaining)

        for r in g.iter('Rule'):
            s_range = r.findtext('Range')
            constraint(s_range is not None, 'missing Range')
            s_length = r.findtext('Length')
            constraint(s_length is not None, 'missing Length')
            length = int(s_length)

            s_first, s_last = s_range.split('-')
            pad = '0' * (remaining - len(s_first))
            s_first = (s_first + pad)[: remaining]
            s_last = (s_last + pad)[: remaining]

            if length:
                ti_lengths = (*ti_prefix_length, length, remaining - length, 1)
            else:
                ti_lengths = (*ti_prefix_length, remaining, 1)
            constraint(sum(ti_lengths) == 13, 'lengths not 13')
            s_lengths = ''.join(map(str, ti_lengths))
            # Assert that each segment length is at most 9.
            constraint(len(s_lengths) == len(ti_lengths), 'length mismatch')
            i_lengths = int(s_lengths[1 :])

            s_compact_first = s_compact_prefix + s_first + '0'
            s_compact_last = s_compact_prefix + s_last + '9'

            i_first = int(s_compact_first)
            i_last = int(s_compact_last)

            logging.debug('B %d to %d : %s to %s : %s %d', i_first, i_last,
                          '-'.join(_isplit(s_compact_first, i_lengths)),
                          '-'.join(_isplit(s_compact_last,
                                           i_lengths)), ti_lengths, i_lengths)

            starts.append(i_first)
            lengths.append(i_lengths)

    def split(self, s: str) -> tuple[str, ...]:
        """Split a string isbn1, with no separators."""
        constraint(len(s) == 13, 'length not 13')
        constraint(s.isdigit(), 'non-digit')
        self.init()
        if self._start is None or self._split is None:  # pragma: no branch
            message = 'missing _start or _split'  # pragma: no cover
            raise RuntimeError(message)  # pragma: no cover
        i = bisect.bisect_right(self._start, int(s))
        if i <= 0:
            warnings.warn(f'ISBN {s} not found in split table', stacklevel=0)
            return (s, )
        return _isplit(s, self._split[i - 1])

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

    _ranges = Ranges()
    split_all = False

    def __init__(self, s: str, *, split: bool = False):
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
            return s + util.checksum.mod11(s)
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
            check = util.checksum.mod11(self._value[3 : 12])
            return '-'.join(parts[1 :-1]) + '-' + check
        return None

def is_valid_isbn10(s: str) -> bool:
    """Check for 10-character-only form."""
    return (len(s) == 10 and s[0 : 8].isdigit()
            and util.checksum.mod11(s[0 : 8]) == s[9])

def is_valid_isbn13(s: str) -> bool:
    """Check for 13-digit-only form."""
    return is_valid_ean13(s)
