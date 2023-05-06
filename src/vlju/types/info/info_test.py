# SPDX-License-Identifier: MIT
"""Test Info."""

import pytest

from vlju.types.info import Info, URI

INFO_CASES = [
    ('abc', '10.1234/5678'),
    ('def', 'stuff'),
]

@pytest.mark.parametrize("k,v", INFO_CASES)
def test_info_from_kv(k, v):
    """Test Info"""
    n = Info(v, authority=k)
    assert str(n) == f'{k}/{v}'

@pytest.mark.parametrize("k,v", INFO_CASES)
def test_info_to_uri(k, v):
    n = Info(v, authority=k)
    uri = URI(n)
    assert str(uri) == f'info:{k}/{v}'

@pytest.mark.parametrize("k,v", INFO_CASES)
def test_info_bad_cast(k, v):
    n = Info(v, authority=k)
    with pytest.raises(TypeError):
        _ = n.cast_params(int)
