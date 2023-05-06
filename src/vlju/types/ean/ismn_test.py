# SPDX-License-Identifier: MIT
"""Test ISMN"""

import pytest

from vlju.types.ean.ismn import ISMN
from vlju.types.uri import URI

# yapf: disable
CASES = [
    ('M692006282', '9790692006282'),
    ('M345246805', '9790345246805'),
]
# yapf: enable

NOT_ISMN_CASES = ['9780127450407', 'Not an ISMN']

@pytest.mark.parametrize("ismn,ean", CASES)
def test_ismn_constructor(ismn, ean):
    i = ISMN(ismn)
    j = ISMN(ean)
    assert isinstance(i, ISMN)
    assert isinstance(j, ISMN)
    assert str(i) == ean
    assert str(j) == ean
    assert i == j

@pytest.mark.parametrize("i", NOT_ISMN_CASES)
def test_ismn_constructor_not_ismn(i):
    with pytest.raises(ValueError):
        _ = ISMN(i)

@pytest.mark.parametrize("ismn,ean", CASES)
def test_ismn_lv(ismn, ean):
    i = ISMN(ismn)
    j = ISMN(ean)
    assert i.lv() == ismn
    assert j.lv() == ismn

@pytest.mark.parametrize("ismn,ean", CASES)
def test_ismn_uri(ismn, ean):
    i = ISMN(ismn)
    j = ISMN(ean)
    assert str(URI(i)) == f'urn:ismn:{ismn}'
    assert str(URI(j)) == f'urn:ismn:{ismn}'
