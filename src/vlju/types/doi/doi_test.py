# SPDX-Licnse-Identifier: MIT
"""Test DOI"""

import copy

import pytest

from vlju.types.doi import DOI, Prefix
from vlju.types.uri import Authority, URI
from vlju.types.url import URL

def test_doi_prefix():
    """Test vlju.doi.Prefix"""
    p = Prefix('10.1234')
    q = Prefix([10, 11, 23])
    r = Prefix(p)
    s = Prefix('11.12')

    assert str(p) == '10.1234'
    assert str(q) == '10.11.23'
    assert p is not r
    assert p == r
    assert p.prefix == p
    assert p[0] == 10
    assert p[1] == 1234
    assert p.is_doi()
    assert not s.is_doi()
    assert q == [10, 11, 23]

@pytest.mark.parametrize("prefix,suffix", [('10.1234', 'Lorem'),
                                           (Prefix('10.4567'), 'ipsum'),
                                           ([11, 12, 13], 'dolor/sit/a(me)t')])
def test_doi_init_parts(prefix, suffix):
    """Test directly constructed DOI."""
    d = DOI(prefix=prefix, suffix=suffix)
    p = Prefix(prefix)
    q = str(p)
    s = suffix.lower()
    if d.prefix()[0] == 10:
        a = 'doi'
        # host = 'doi.org'
        doi = 'doi:'
    else:
        a = 'hdl'
        # host = 'hdl.handle.net'
        doi = 'info:hdl/'
    assert d.authority() == Authority(a)
    assert d.sauthority() == a
    assert str(d) == f'{q},{s}'
    assert d.lv() == f'{doi}{q}/{s}'
    assert str(d.prefix()) == f'{q}'
    assert d.suffix() == f'{s}'
    assert d.hdl() == f'info:hdl/{q}/{s}'
    assert d.doi() == f'{doi}{q}/{s}'
    assert repr(d) == f'DOI(prefix={repr(p)},suffix={repr(s)})'

@pytest.mark.parametrize("s,x", [
    ('10.1234/56.78', 'info:doi/10.1234/56.78'),
    ('10.1234,56.78', 'info:doi/10.1234/56.78'),
    ('11.12.13/dolor/sit/a(me)t', 'info:hdl/11.12.13/dolor/sit/a(me)t'),
    ('doi:10.12.34/56.78', 'info:doi/10.12.34/56.78'),
    ('info:doi/10.12.34/56.78', 'info:doi/10.12.34/56.78'),
    ('http://dx.doi.org/10.1234/56-78/9', 'info:doi/10.1234/56-78/9'),
    ('https://dx.doi.org/10.1234/56-78/9', 'info:doi/10.1234/56-78/9'),
    ('http://doi.org/10.1234/56-78/9', 'info:doi/10.1234/56-78/9'),
    ('https://doi.org/10.1234/56-78/9', 'info:doi/10.1234/56-78/9'),
    ('http://hdl.handle.net/10.1234/56-78/9', 'info:doi/10.1234/56-78/9'),
    ('https://hdl.handle.net/10.1234/56-78/9', 'info:doi/10.1234/56-78/9'),
    ('https://doi.org/10.1016/0003-6870(84)90060-7',
     'info:doi/10.1016/0003-6870(84)90060-7'),
    ('https://doi.org/10.1016/0003-6870%2884%2990060-7',
     'info:doi/10.1016/0003-6870(84)90060-7'),
    ('info:hdl/11.12.34/56.78', 'info:hdl/11.12.34/56.78'),
    ('http://hdl.handle.net/11.1234/56-78/9', 'info:hdl/11.1234/56-78/9'),
    ('https://hdl.handle.net/11.1234/56-78/9', 'info:hdl/11.1234/56-78/9'),
])
def test_doi_init(s, x):
    """Test complicated DOI parsing."""
    assert str(URI(DOI(s))) == x

def test_doi_init_empty():
    with pytest.raises(ValueError):
        _ = DOI('')

def test_doi_copy():
    a = DOI('10.1234/lorem')
    b = copy.copy(a)
    assert a is not b
    assert a == b

def test_doi_eq():
    a = DOI('10.1234/lorem')
    b = DOI('10.1234/lorem')
    c = URL(b)
    assert a is not b
    assert a == b
    assert a != c

def test_doi_eq_prefix():
    a = DOI('10.1234/lorem')
    b = DOI('10.1235/lorem')
    assert a != b

def test_doi_eq_suffix():
    a = DOI('10.1234/lorem')
    b = DOI('10.1234/ipsum')
    assert a != b

def test_doi_to_uri():
    a = DOI('10.1234/56.78')
    uri = URI(a)
    assert str(uri) == 'info:doi/10.1234/56.78'

def test_doi_to_url():
    a = DOI('10.1234/56.78')
    url = URL(a)
    assert str(url) == 'https://doi.org/10.1234/56.78'

def test_doi_bad_cast():
    a = DOI('10.1234/56.78')
    with pytest.raises(TypeError):
        _ = a.cast_params(int)
