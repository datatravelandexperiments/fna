# SPDX-License-Identifier: MIT
"""Test fearmat."""

import pytest

from util.error import Error
from util.fearmat import fearmat

def test_fearmat():
    template = '{a}a{b}{b}e{b}'
    assert fearmat(template, {'a': 'p', 'b': 's'}) == 'passes'
    assert fearmat(template, {'a': 'w', 'b': 'd'}) == 'wadded'

def test_fearmat_triple():
    with pytest.raises(Error):
        _ = fearmat('{a}a"""{b}"""a{a}', {'a': 'p', 'b': 's'})

def test_fearmat_disallowed():
    with pytest.raises(NameError):
        _ = fearmat('{open(x)}', {'x': '/etc/passwd'})

def test_fearmat_builtins():
    s = fearmat('{open(x)}', {'x': '/etc/passwd'},
                {'open': lambda s: s.upper()})
    assert s == '/ETC/PASSWD'
