# SPDX-License-Identifier: MIT
"""Path test."""

import copy

import pytest

import pathlib

from vlju import Vlju
from vlju.testutil import CastParams
from vlju.types.file import File
from vlju.types.uri import URI
from vlju.types.url import URL

def test_file_constructor_str():
    p = File('/etc/passwd')
    assert str(p) == '/etc/passwd'
    assert p.path() == '/etc/passwd'
    assert p.spath() == '/etc/passwd'

def test_file_constructor_path():
    p = File(pathlib.Path('/etc/passwd'))
    assert str(p) == '/etc/passwd'
    assert p.path() == '/etc/passwd'
    assert p.spath() == '/etc/passwd'

def test_file_constructor_cast():
    p = File(CastParams('/etc/passwd', {}))
    assert str(p) == '/etc/passwd'
    assert p.path() == '/etc/passwd'
    assert p.spath() == '/etc/passwd'

def test_file_constructor_other():
    with pytest.raises(TypeError):
        _ = File(1)

def test_file_eq():
    p = File('/etc/passwd')
    q = File('/etc/passwd')
    assert q == p
    assert str(p) == str(q)
    assert p.path() == q.path()

    r = File('/etc/shadow')
    assert r != p

    v = Vlju('/etc/passwd')
    assert v != p
    assert p != v

def test_file_copy():
    p = File('/etc/passwd')
    r = copy.copy(p)
    assert r is not p
    assert r == p

def test_file_file():
    p = File('/etc/passwd')
    assert p.file() == pathlib.Path('/etc/passwd')
    assert p.filename() is p.file()

def test_file_to_uri():
    f = File('/etc/passwd')
    uri = URI(f)
    assert str(uri) == 'file:///etc/passwd'

def test_file_to_url():
    f = File('/etc/passwd')
    url = URL(f)
    assert str(url) == 'file:///etc/passwd'

def test_file_bad_cast():
    a = File('/etc/passwd')
    with pytest.raises(TypeError):
        _ = a.cast_params(int)
