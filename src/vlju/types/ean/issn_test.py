# SPDX-License-Identifier: MIT
"""Test ISSN"""

import pytest

from vlju.types.ean.issn import ISSN
from vlju.types.uri import URI

# yapf: disable
CASES = [
    ('13515381', '9771351538009', '1351-5381', '977-1351-538-00-9'),
    ('10962905', '9771096290002', '1096-2905', '977-1096-290-00-2'),
]
# yapf: enable

NOT_ISSN_CASES = ['9780127450407', 'Not an ISSN']

@pytest.mark.parametrize("s8,s13,split8,split13", CASES)
def test_issn_constructor(s8, s13, split8, split13):
    i8 = ISSN(s8)
    i13 = ISSN(s13)
    j8 = ISSN(split8)
    j13 = ISSN(split13)
    assert i8 == i13
    assert j8 == i13
    assert j13 == i13
    assert str(i8) == s13
    assert str(i13) == s13
    assert str(j8) == s13
    assert str(j13) == s13

@pytest.mark.parametrize("i", NOT_ISSN_CASES)
def test_issn_constructor_not_issn(i):
    for i in NOT_ISSN_CASES:
        with pytest.raises(ValueError):
            _ = ISSN(i)

@pytest.mark.parametrize("s8,s13", ((c[0], c[1]) for c in CASES))
def test_issn_issn13(s8, s13):
    i = ISSN(s8)
    assert i.issn13() == s13

@pytest.mark.parametrize("s8,s13", ((c[0], c[1]) for c in CASES))
def test_issn_issn8(s8, s13):
    i = ISSN(s13)
    assert i.issn8() == s8

def test_issn_issn8_not_issn():
    # Cheat for testing; set the value to an EAN that is not an ISSN.
    i = ISSN(CASES[0][0])
    i._value = NOT_ISSN_CASES[0]    # pylint:disable=protected-access
    assert i.issn8() is None

@pytest.mark.parametrize("s8,split13", ((c[0], c[3]) for c in CASES))
def test_issn_split13(s8, split13):
    for s8, _, _, split13 in CASES:
        i = ISSN(s8)
        assert i.split13() == split13

@pytest.mark.parametrize("s13,split8", ((c[1], c[2]) for c in CASES))
def test_issn_split8(s13, split8):
    i = ISSN(s13)
    assert i.split8() == split8

def test_issn_split8_not_issn():
    # Cheat for testing; set the value to an EAN that is not an ISSN.
    i = ISSN(CASES[0][0])
    i._value = NOT_ISSN_CASES[0]    # pylint:disable=protected-access
    assert i.split8() is None

@pytest.mark.parametrize("s8,split8", ((c[0], c[2]) for c in CASES))
def test_issn_to_uri(s8, split8):
    i8 = ISSN(s8)
    uri = URI(i8)
    assert str(uri) == f'urn:issn:{split8}'
