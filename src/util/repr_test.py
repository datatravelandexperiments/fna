# SPDX-License-Identifier: MIT
"""Test repr utilities"""

import pytest

from util.repr import mkrepr
from util.pytestutil import it2p

@pytest.fixture(name='test_mkrepr_object')
def mkrepr_object():

    class T(dict):
        __getattr__ = dict.__getitem__

    t = T()
    # In order to make the cases fit on a line, we test with single-letter
    # attribute names and take advantage of the fact that iterating over a
    # string yields single-character strings.
    for c in "abcdef":
        t[c] = c.upper()
    return t

# yapf: disable
CASES_MKREPR = [
    ('pos',     'kws',  'defaults',             'expect'),
    # ---        ---     --------                ------
    ("a",       "",     {},                     "T('A')"),
    ("ab",      "",     {},                     "T('A','B')"),
    ("a",       "c",    {},                     "T('A',c='C')"),
    ("",        "c",    {},                     "T(c='C')"),
    ("ab",      "cd",   {},                     "T('A','B',c='C',d='D')"),
    ("ab",      "cd",   {'a': 'A'},             "T(b='B',c='C',d='D')"),
    ("ab",      "cd",   {'c': 'C'},             "T('A','B',d='D')"),
    ("ab",      "cd",   {'a': 'A', 'c': 'C'},   "T(b='B',d='D')"),
]
# yapf: enable

@pytest.mark.parametrize(*it2p(CASES_MKREPR))
def test_mkrepr(test_mkrepr_object, pos, kws, defaults, expect):
    assert mkrepr(test_mkrepr_object, pos, kws, defaults) == expect
