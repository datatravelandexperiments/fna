# SPDX-License-Identifier: MIT
"""Test Timestamp."""

import pytest

from util.duration import Duration
from vlju.types.timestamp import Timestamp

def test_timestamp_init_string():
    t = Timestamp('12h34m56.0')
    assert str(t) == '12:34:56'

def test_timestamp_init_duration():
    t = Timestamp(Duration(hours=12, minutes=34, seconds=56))
    assert str(t) == '12:34:56'

def test_timestamp_init_cast_params_string():

    class T:

        def cast_params(self, _: object) -> tuple[str, dict]:
            return '12h34m56.0', {}

    t = Timestamp(T())
    assert str(t) == '12:34:56'

def test_timestamp_init_cast_params_dict():

    class T:

        def cast_params(self, _: object) -> tuple[str, dict]:
            return '', {'hours': 12, 'minutes': 34, 'seconds': 56}

    t = Timestamp(T())
    assert str(t) == '12:34:56'

def test_timestamp_init_type_error():
    with pytest.raises(TypeError):
        _ = Timestamp(int)

def test_timestamp_lv():
    t = Timestamp(Duration(hours=12, minutes=34, seconds=56))
    assert t.lv() == '12h34m56s'

def test_timestamp_duration():
    d = Duration(hours=12, minutes=34, seconds=56)
    e = Duration(hours=12, minutes=34, seconds=56)
    t = Timestamp(d)
    assert t.duration() == e
