# SPDX-License-Identifier: MIT

# flake8: noqa: E201

import collections
import datetime

import pytest

from fnattr.util.duration import Duration
from fnattr.util.pytestutil import it2p

def dhmsn(d: int | float = 0,
          h: int | float = 0,
          m: int | float = 0,
          s: int | float = 0,
          n: int = 0) -> int:
    return int(n + 1_000_000_000 * (s + 60 * (m + 60 * (h + 24 * d))))

def dns(**kwargs) -> int:
    u = {
        'days': 'd',
        'hours': 'h',
        'minutes': 'm',
        'seconds': 's',
        'nanoseconds': 'ns',
    }
    d = collections.defaultdict(int)
    for k, v in kwargs.items():
        d[u[k] if k in u else k] = v
    return dhmsn(d['d'], d['h'], d['m'], d['s'], d['ns'])

def test_duration_to_nanoseconds():
    d = Duration(nanoseconds=183_845_000_000_006)
    assert d.to_nanoseconds() == 183_845_000_000_006

def test_duration_to_seconds():
    d = Duration(nanoseconds=183_845_000_000_006)
    assert d.to_seconds() == 183_845.000_000_006

def test_duration_to_dhmsn():
    d = Duration(nanoseconds=183_845_000_000_006)
    assert d.to_dhmsn() == (2, 3, 4, 5, 6)

def test_duration_to_timedelta():
    d = Duration(nanoseconds=183_845_000_006_000)
    assert d.to_timedelta() == datetime.timedelta(
        days=2, hours=3, minutes=4, seconds=5, microseconds=6)

def test_duration_float():
    d = Duration(days=1.5, hours=1.5, minutes=1.5, seconds=1.5)
    assert d.to_seconds() == 135091.5

def test_duration_eq():
    d = Duration(days=1.5, hours=1.5, minutes=1.5, seconds=1.5)
    e = Duration(days=1.5, hours=1.5, minutes=1.5, seconds=1.5)
    assert d is not e
    assert d == e

def test_duration_eq_int():
    ns = 1234567890
    d = Duration(nanoseconds=ns)
    assert d == ns

def test_duration_ne():
    d = Duration(days=1.5, hours=1.5, minutes=1.5, seconds=1.5)
    e = Duration(days=1.5, hours=1.5, minutes=1.5, seconds=1.6)
    assert d != e

def test_duration_ne_type():
    d = Duration()
    assert d != Duration

def test_duration_from_timedelta():
    us = 345678912
    d = Duration.from_timedelta(datetime.timedelta(microseconds=us))
    assert d.to_nanoseconds() == 1000 * us

# fmt: off
STR_CASES = [
    ('ns',                   'string',                'fmt'                 ),
    ( dhmsn(2, 3, 4, 5, 6),  '2:03:04:05.000000006',  '2d03h04m05s000000006'),
    ( dhmsn(2, 3, 4, 5.78),  '2:03:04:05.780',        '2d03h04m05s780'      ),
    ( dhmsn(2, 3, 4, 5, 0),  '2:03:04:05',            '2d03h04m05s'         ),
    ( dns(d=2, h=3, m=4),    '2:03:04:00',            '2d03h04m00s'         ),
    ( dns(h=2, m=10, s=40.5),   '2:10:40.500',           '2h10m40s500'      ),
    ( dns(m=14, s=0.6789),        '14:00.678900',          '14m00s678900'   ),
    ( dns(m=7, s=20),              '7:20',                  '7m20s'         ),
    ( dns(s=12, ns=345678912),       '12.345678912',          '12s345678912'),
    ( dns(s=2, ns=345678912),         '2.345678912',           '2s345678912'),
    ( dns(s=1),                       '1',                     '1s'         ),
    ( dns(),                          '0',                     '0s'         ),
    (-dhmsn(2, 3, 4, 5, 6), '-2:03:04:05.000000006', '-2d03h04m05s000000006'),
    (-dns(s=2, ns=345678912),        '-2.345678912',          '-2s345678912'),
]
# fmt: on

@pytest.mark.parametrize(*it2p(STR_CASES, ('ns', 'string')))
def test_duration_str(ns, string):
    assert str(Duration(nanoseconds=ns)) == string

@pytest.mark.parametrize(*it2p(STR_CASES, ('ns', 'fmt')))
def test_duration_fmt(ns, fmt):
    d = Duration(nanoseconds=ns)
    assert d.fmt() == fmt

# fmt: off
PARSE_CASES = [
    ('string',                  'ns'),
    ('123 days 5′ 10.3″',       dns(d=123, m=5, s=10.3)),
    ('1:23:45:57.39',           dns(d=1, h=23, m=45, s=57.39)),
    ('99',                      dns(s=99)),
    ('99:59',                   dns(m=99, s=59)),
    ('99:59.99',                dns(m=99, s=59.99)),
    ('99:59:59.999',            dns(h=99, m=59, s=59.999)),
    ('99:23:59:59.999',         dns(d=99, h=23, m=59, s=59.999)),
    ('123 Hours 5:10.3',        dns(h=123, m=5, s=10.3)),
    ('123 hours 10.25',         dns(h=123, m=10.25)),
    ('123 hours 99s1024',       dns(h=123, s=99, ns=102_400_000)),
    ('1d 23 59 59',             dns(d=1, h=23, m=59, s=59)),
    ('1 23H 59 59',             dns(d=1, h=23, m=59, s=59)),
    ('1d 23 59 59s',            dns(d=1, h=23, m=59, s=59)),
    (' 1 day 14 µs ',           dns(d=1, ns=14000)),
]
# fmt: on

@pytest.mark.parametrize(*it2p(PARSE_CASES))
def test_duration_parse(string, ns):
    assert Duration.parse(string).to_nanoseconds() == ns

# fmt: off
BAD_PARSE_CASES = [
    ('string',                  'match'),
    ('',                        'not a number'),
    ('bad',                     'not a number'),
    ('1:23:45:57:39',           'too many'),
    ('1:23:45.2:57',            'decimal'),
    ('24:60',                   'seconds'),
    ('24:60:21.5',              'minutes'),
    ('01:25:59:59.9',           'hours'),
    ('12s34.56',                'ambiguous'),
    ('12ns34',                  'ambiguous'),
    ('12s 34 56',               'too many'),
    ('12 34d',                  'no units larger'),
    ('12 mikkrosekkundz',       'not a unit'),
    ('5 7us',                   'ambiguous'),
]
# fmt: on

@pytest.mark.parametrize(*it2p(BAD_PARSE_CASES))
def test_duration_parse_error(string, match):
    with pytest.raises(ValueError, match=match):
        _ = Duration.parse(string)
