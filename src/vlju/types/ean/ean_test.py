# SPDX-License-Identifier: MIT
"""Test EAN13"""

import pytest

from vlju.types.ean import EAN13, is_valid_ean13, key13, to13
from vlju.types.ean.isbn import ISBN
from vlju.types.ean.ismn import ISMN
from vlju.types.ean.issn import ISSN
from vlju.types.uri import URI

# yapf: disable
CASES = [
    # SBN
    ('8044-2957-X',         'isbn',     ISBN,   '9780804429573'),
    ('201-89683-4',         'isbn',     ISBN,   '9780201896831'),
    ('07-034207-5',         'isbn',     ISBN,   '9780070342071'),
    ('12-745040-8',         'isbn',     ISBN,   '9780127450407'),
    # ISBN
    ('0-8044-2957-X',       'isbn',     ISBN,   '9780804429573'),
    ('0-201-89683-4',       'isbn',     ISBN,   '9780201896831'),
    ('0-07-034207-5',       'isbn',     ISBN,   '9780070342071'),
    ('0-12-745040-8',       'isbn',     ISBN,   '9780127450407'),
    ('978-0-12-745040-7',   'isbn',     ISBN,   '9780127450407'),
    ('979-1692006289',      'isbn',     ISBN,   '9791692006289'),
    # ISMN
    ('M69200-628-2',        'ismn',     ISMN,   '9790692006282'),
    # ISSN
    ('1351-5381',           'issn',     ISSN,   '9771351538009'),
    # UPC-A
    ('1-23456-78901-2',     'ean13',    EAN13,  '0123456789012'),
    # EAN-13
    ('453-453012894-2',     'ean13',    EAN13,  '4534530128942'),
]
# yapf: enable

@pytest.mark.parametrize("i,out", ((i, out) for i, key, cls, out in CASES))
def test_is_valid_ean13(i, out):
    assert is_valid_ean13(i) is False
    assert is_valid_ean13(out) is True

@pytest.mark.parametrize("i,out", ((i, out) for i, key, cls, out in CASES))
def test_to13(i, out):
    """Verify conversion to 13 digits."""
    assert to13(i) == out

@pytest.mark.parametrize("key,out", ((key, out) for i, key, cls, out in CASES))
def test_key13(key, out):
    """Verify conversion to 13 digits."""
    assert key13(out) == key

@pytest.mark.parametrize("i,out", ((i, out) for i, key, cls, out in CASES))
def test_ean13(i, out):
    e = EAN13(i)
    assert str(e) == out
    assert int(e) == int(out)

def test_ean13_value_error():
    with pytest.raises(ValueError):
        _ = EAN13('1')

@pytest.mark.parametrize("i,out", ((i, out) for i, key, cls, out in CASES))
def test_ean13_to_uri(i, out):
    e = EAN13(i)
    uri = URI(e)
    assert str(uri) == f'urn:ean13:{out}'
