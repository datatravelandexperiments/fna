# SPDX-License-Identifier: MIT
"""Test Vlju"""

import copy

import pytest

from vlju import Vlju

def test_vlju_constructor():
    v = Vlju('one')
    assert str(v) == 'one'

def test_vlju_constructor_non_string():
    with pytest.raises(TypeError):
        v = Vlju(1)

def test_vlju_copy():
    v = Vlju('one')
    w = copy.copy(v)
    assert w is not v
    assert str(w) == str(v)

def test_vlju_eq():
    v = Vlju('one')
    w = Vlju('one')
    assert w is not v
    assert w == v

def test_vlju_repr():
    v = Vlju('one')
    assert repr(v) == "Vlju('one')"

def test_vlju_v():
    v = Vlju('one')
    assert str(v) == 'one'

def test_vlju_lv():
    v = Vlju('one')
    assert v.lv() == 'one'

def test_vlju_get():
    v = Vlju('one')
    assert v['default'] == 'one'
    assert v['long'] == 'one'
    assert v['str'] == 'one'
    assert v['repr'] == "Vlju('one')"
    with pytest.raises(KeyError):
        _ = v['unknown']

    assert v.get() == 'one'
    assert v.get('default') == 'one'
    assert v.get('long') == 'one'
    assert v.get('str') == 'one'
    assert v.get('repr') == "Vlju('one')"
    assert v.get('unknown') is None
    assert v.get('unknown', 'DEFAULT') == 'DEFAULT'

    class T(Vlju):
        """Test subclass returning known strings."""

        def lv(self) -> str:
            return 'LV'

        def __str__(self) -> str:
            return 'STR'

        def __repr__(self) -> str:
            return 'REPR'

    t = T('dummy')
    assert t.get(default='D') == 'STR'
    assert t.get('default', default='D') == 'STR'
    assert t.get('long', default='D') == 'LV'
    assert t.get('str', default='D') == 'STR'
    assert t.get('repr', default='D') == 'REPR'
    assert t.get('none', default='D') == 'D'
