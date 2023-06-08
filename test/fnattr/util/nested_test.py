# SPDX-License-Identifier: MIT
"""Test util.nested.n"""

import pytest

from fnattr.util import nested

D0 = {
    'v0': 0,
    'w0': 0,
    'd0': {
        'd1': {
            'v2': 2,
        },
        'l1': [1, 2, 3],
        's1': {10, 11, 12},
    },
}

D1 = {
    'w0': 2,
    'd0': {
        'd1': {
            'v3': 3,
        },
        'l1': [4, 5],
        's1': {13, 14},
        'v1': 100,
    },
}

def test_nested_nget_top():
    assert nested.ngetor(D0, ['w0']) == 0

def test_nested_nget_inner():
    assert nested.ngetor(D0, ['d0', 'd1', 'v2']) == 2

def test_nested_nget_top_missing():
    assert nested.ngetor(D0, ['zz'], 'DeFault') == 'DeFault'

def test_nested_ngetor_top_missing():
    assert nested.ngetor(D0, ['zz']) is None

def test_nested_nget_inner_missing():
    assert nested.nget(D0, ['d0', 'd1', 'zz'], 'DeFault') == 'DeFault'

def test_nested_nget_non_container():
    assert nested.ngetor(D0, ['v0', 'v1']) is None

def test_nested_dgetor():
    assert nested.dgetor(D0, 'd0.d1.v2') == 2

def test_nested_dget():
    assert nested.dget(D0, 'd0.d1.noway', 'DeFault') == 'DeFault'

def test_nested_nstore():
    d = {1: {}}
    nested.nset(d, [1, 2, 3], 123)
    assert d[1][2][3] == 123

def test_nested_nstore_replace():
    d = {1: {2: {3: 4}}}
    nested.nset(d, [1], 123)
    assert d == {1: 123}

def test_nested_nstore_empty():
    d = {}
    with pytest.raises(KeyError):
        nested.nset(d, [], 123)

def test_nested_nstore_ni():
    d = {}
    with pytest.raises(TypeError):
        nested.nset(d, 4, 123)

def test_nested_nupdate():
    d = D0.copy()
    nested.nupdate(d, D1)
    assert d['v0'] == 0
    assert d['w0'] == 2
    assert d['d0']['d1'] == {'v2': 2, 'v3': 3}
    assert d['d0']['l1'] == [1, 2, 3, 4, 5]
    assert d['d0']['s1'] == set(range(10, 15))
    assert d['d0']['v1'] == 100

def test_nested_nupdate_mismatch():
    d = D0.copy()
    with pytest.raises(TypeError):
        nested.nupdate(d, {'d0': {'d1': {'v2': 'test'}}})
