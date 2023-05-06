# SPDX-License-Identifier: MIT
"""Test type checks."""

import pytest

from util.typecheck import istype, needtype

def test_istype_null():
    assert not istype(1)
    assert not istype({})
    assert not istype(None)

def test_istype_one():
    assert istype(1, int)
    assert not istype('', int)
    assert not istype(None, int)

def test_istype_two():
    assert istype(1, str, int)
    assert istype('', str, int)
    assert not istype({}, str, int)
    assert not istype(None, str, int)

def test_istype_nonetype():
    assert istype(1, int, None)
    assert istype(None, int, None)
    assert not istype('', int, None)

def test_needtype_null():
    with pytest.raises(TypeError):
        _ = needtype(1)

def test_needtype_one():
    assert needtype(1, int) == 1
    with pytest.raises(TypeError):
        _ = needtype('', int)
    with pytest.raises(TypeError):
        _ = needtype(None, int)

def test_needtype_two():
    assert needtype(1, str, int) == 1
    assert needtype('a', str, int) == 'a'
    with pytest.raises(TypeError):
        _ = needtype({}, str, int)
    with pytest.raises(TypeError):
        _ = needtype(None, str, int)

def test_needtype_nonetype():
    assert needtype(1, int, None) == 1
    assert needtype(None, int, None) is None
    with pytest.raises(TypeError):
        _ = needtype('', int, None)
