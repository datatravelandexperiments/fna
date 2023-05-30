# SPDX-License-Identifier: MIT
"""Duration."""

# Why not just timedelta? I wanted nanosecond resolution like `struct timespec`.

import re

from datetime import timedelta
from typing import Self

NANOSECONDS_PER_DAY = 24 * 60 * 60 * 1_000_000_000
NANOSECONDS_PER_HOUR = 60 * 60 * 1_000_000_000
NANOSECONDS_PER_MINUTE = 60 * 1_000_000_000
NANOSECONDS_PER_SECOND = 1_000_000_000
NANOSECONDS_PER_MILLISECOND = 1_000_000
NANOSECONDS_PER_MICROSECOND = 1_000
NANOSECONDS_PER_NANOSECOND = 1

class Duration:
    """Duration."""

    def __init__(self,
                 *,
                 days: int | float = 0,
                 hours: int | float = 0,
                 minutes: int | float = 0,
                 seconds: int | float = 0,
                 milliseconds: int | float = 0,
                 microseconds: int | float = 0,
                 nanoseconds: int = 0) -> None:
        # Python has arbitrary-precision integers but not abritrary-precision
        # floats, so we convert each term to integer nanoseconds separately.
        self.ns: int = (
            nanoseconds + int(microseconds * NANOSECONDS_PER_MICROSECOND)
            + int(milliseconds * NANOSECONDS_PER_MILLISECOND)
            + int(seconds * NANOSECONDS_PER_SECOND)
            + int(minutes * NANOSECONDS_PER_MINUTE)
            + int(hours * NANOSECONDS_PER_HOUR)
            + int(days * NANOSECONDS_PER_DAY))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Duration):
            return self.ns == other.ns
        if isinstance(other, int):
            return self.ns == other
        return False

    def to_nanoseconds(self) -> int:
        return self.ns

    def to_seconds(self) -> float:
        return self.ns / NANOSECONDS_PER_SECOND

    def to_dhmsn(self) -> tuple[int, int, int, int, int]:
        return nanoseconds_to_dhmsn(self.ns)

    def to_timedelta(self) -> timedelta:
        return timedelta(microseconds=self.ns / NANOSECONDS_PER_MICROSECOND)

    def __repr__(self) -> str:
        return f'{type(self).__name__}(nanoseconds={self.ns})'

    def __str__(self) -> str:
        return self.fmt(':::.')

    def fmt(self, p: str = 'dhms') -> str:
        """Minimally format a duration."""
        return fmt_nanoseconds(self.ns, p)

    @classmethod
    def parse(cls, s: str) -> Self:
        return cls(nanoseconds=parse_to_nanoseconds(s))

    @classmethod
    def from_timedelta(cls, t: timedelta) -> Self:
        return cls(days=t.days, seconds=t.seconds, microseconds=t.microseconds)

def nanoseconds_to_dhmsn(ns: int) -> tuple[int, int, int, int, int]:
    s, n = divmod(ns, NANOSECONDS_PER_SECOND)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return d, h, m, s, n

def fmt_nanoseconds(nanoseconds: int, p: str = 'dhms') -> str:
    """Minimally format a duration."""
    if nanoseconds < 0:
        sign = '-'
        nanoseconds = -nanoseconds
    else:
        sign = ''
    d, h, m, s, n = nanoseconds_to_dhmsn(nanoseconds)
    r = (
        f'{d}{p[0]}{h:02}{p[1]}{m:02}{p[2]}{s:02}'  #
        .removeprefix(f'0{p[0]}')                   # if no days
        .removeprefix('0')                          # if hours < 10
        .removeprefix(f'0{p[1]}')                   # if no hours
        .removeprefix('0')                          # if minutes < 10
        .removeprefix(f'0{p[2]}')                   # if no minutes
        .removeprefix('0')                          # if seconds < 10
    )
    ns = ''
    if n:
        ns = f'{n:09}'
        while (t := ns.removesuffix('000')) != ns:
            ns = t
    return f'{sign}{r}{p[3]}{ns}'.removesuffix('.')

__UNIT_TO_NANOSECONDS = {
    'd': NANOSECONDS_PER_DAY,
    'day': NANOSECONDS_PER_DAY,
    'days': NANOSECONDS_PER_DAY,
    'h': NANOSECONDS_PER_HOUR,
    'hour': NANOSECONDS_PER_HOUR,
    'hours': NANOSECONDS_PER_HOUR,
    'm': NANOSECONDS_PER_MINUTE,
    'minute': NANOSECONDS_PER_MINUTE,
    'minutes': NANOSECONDS_PER_MINUTE,
    '′': NANOSECONDS_PER_MINUTE,
    "'": NANOSECONDS_PER_MINUTE,
    's': NANOSECONDS_PER_SECOND,
    'second': NANOSECONDS_PER_SECOND,
    'seconds': NANOSECONDS_PER_SECOND,
    '″': NANOSECONDS_PER_SECOND,
    '"': NANOSECONDS_PER_SECOND,
    'ms': NANOSECONDS_PER_MILLISECOND,
    'millisecond': NANOSECONDS_PER_MILLISECOND,
    'milliseconds': NANOSECONDS_PER_MILLISECOND,
    'µs': NANOSECONDS_PER_MICROSECOND,
    'us': NANOSECONDS_PER_MICROSECOND,
    'microsecond': NANOSECONDS_PER_MICROSECOND,
    'microseconds': NANOSECONDS_PER_MICROSECOND,
    'ns': 1,
    'nanosecond': 1,
    'nanoseconds': 1,
}

__NANOSECONDS_TO_UNIT = {
    NANOSECONDS_PER_DAY: 'day',
    NANOSECONDS_PER_HOUR: 'hour',
    NANOSECONDS_PER_MINUTE: 'minute',
    NANOSECONDS_PER_SECOND: 'second',
    NANOSECONDS_PER_MILLISECOND: 'millisecond',
    NANOSECONDS_PER_MICROSECOND: 'microsecond',
    NANOSECONDS_PER_NANOSECOND: 'nanosecond',
}

__UU = [
    NANOSECONDS_PER_DAY,
    NANOSECONDS_PER_HOUR,
    NANOSECONDS_PER_MINUTE,
    NANOSECONDS_PER_SECOND,
]

__SPLIT_RE = re.compile(r'(?P<number>[.\d]+)(?P<unit>[^.\d]*)(?P<rest>.*)')

def parse_to_nanoseconds(s: str) -> int:
    """
    Parse a timestamp, returning nanoseconds.

    Some examples of accepted strings:

      123 days 5′ 10.3″
      1:23:45:57.39
      99
      99:59
      99:59.99
      99:59:59.999
      99:23:59:59.999
      123 Hours 5:10.3
      123 hours 10.25
      123 hours 99s1024
      1d 23 59 59
      1 23H 59 59
      1d 23 59 59s
      1 day 14 µs
    """
    s = s.strip()
    if not s:
        message = f'not a number: {s!r}'
        raise ValueError(message)

    # Split into parallel lists of number and unit.
    numbers: list[str] = []
    units: list[int] = []
    t = s
    while (m := __SPLIT_RE.fullmatch(t)):
        number, unit, t = m.group('number', 'unit', 'rest')
        numbers.append(number)
        units.append(parse_unit(unit))

    if t:
        message = f'not a number: {t!r}'
        raise ValueError(message)

    if all(units):
        pass
    elif any(units):
        units = __reconcile_units(s, numbers, units)
    else:
        units = __assign_units(s, numbers)

    total: float = 0
    for number, unit in zip(numbers, units, strict=True):
        total += float(number) * unit
    return int(total)

def __reconcile_units(s: str, numbers: list[str],
                      units: list[int]) -> list[int]:
    """Handle mixed cases."""
    units = list(units)
    length = len(units)

    # Find the rightmost unit.
    ri = -1
    for ri in range(length - 1, -1, -1):    # pragma: no branch
        if units[ri]:
            break
    if ri < 0:                              # pragma: no branch
        message = f'internal error: {s!r}'  # pragma: no coverage
        raise ValueError(message)           # pragma: no coverage

    if ri != length - 1:
        # There are units to the right to be filled in.
        u = units[ri]
        if ri == length - 2 and u == NANOSECONDS_PER_SECOND:
            # Special case: handle the use of ‘s’ as a decimal point.
            n = numbers[-1]
            if '.' in n:
                message = f'ambiguous decimal: {s!r}'
                raise ValueError(message)
            units[-1] = 10**(9 - len(n))
        else:
            fi = ri + 1
            try:
                ui = __UU.index(u) + 1
            except ValueError as e:
                message = f'ambiguous units: {s!r}'
                raise ValueError(message) from e
            ulength = len(__UU)
            while fi < length and ui < ulength:
                units[fi] = __UU[ui]
                fi += 1
                ui += 1
            if fi < length:
                message = f'too many numbers after {__NANOSECONDS_TO_UNIT[u]}s'
                raise ValueError(message)

    # Now work left.
    for i in range(ri, -1, -1):
        if units[i] == 0:
            u = units[ri]
            try:
                ui = __UU.index(u)
            except ValueError as e:
                message = f'ambiguous units: {s!r}'
                raise ValueError(message) from e
            if ui == 0:
                message = (f'no units larger than {__NANOSECONDS_TO_UNIT[u]}'
                           f'for {numbers[i]}')
                raise ValueError(message)
            units[i] = __UU[ui - 1]
        ri = i

    return units

def __assign_units(s: str, numbers: list[str]) -> list[int]:
    """Handle a colon-separated sequence."""
    if (length := len(numbers)) > 4:
        message = f'too many components: {s!r}'
        raise ValueError(message)
    if any('.' in n for n in numbers[:-1]):
        message = f'unexpected decimal: {s!r}'
        raise ValueError(message)
    for i, u, m in [(1, 'seconds', 60), (2, 'minutes', 60), (3, 'hours', 24)]:
        if length > i and float(numbers[-i]) >= m:
            message = f'{u} too large: {numbers[-i]!r}'
            raise ValueError(message)
    return __UU[-length :]

def parse_unit(s: str) -> int:
    s = s.strip().lower()
    if not s or s == ':':
        return 0
    if s in __UNIT_TO_NANOSECONDS:
        return __UNIT_TO_NANOSECONDS[s]
    message = f'not a unit: {s!r}'
    raise ValueError(message)
