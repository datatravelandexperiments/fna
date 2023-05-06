# SPDX-License-Identifier: MIT
"""Test Registry"""

import pytest

from util.registry import Registry

def test_registry_default():
    r: Registry[int] = Registry()
    r.set_default(99)
    assert r.get() == 99

def test_registry_no_default():
    r: Registry[int] = Registry()
    with pytest.raises(KeyError, match='no default value'):
        _ = r.get()

def test_registry_named_no_default():
    r: Registry[int] = Registry('reg')
    with pytest.raises(KeyError, match='reg: no default value'):
        _ = r.get()

def test_registry_dict():
    r: Registry[int] = Registry()
    r.update({'a': 1, 'b': 2})
    assert r.get('a') == 1
    assert r.get('b') == 2
    assert r.keys() == set(('a', 'b'))
    with pytest.raises(KeyError):
        _ = r.get('c')

def test_registry_direct():
    r: Registry[int] = Registry()
    assert r.get(9) == 9
