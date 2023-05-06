# SPDX-License-Identifier: MIT
"""Test ISBN"""

import pytest

from vlju.types.ean.isbn import ISBN
from vlju.types.uri import URI

CASES = [
    ('080442957X', '9780804429573', '0-8044-2957-X', '978-0-8044-2957-3'),
    ('0201896834', '9780201896831', '0-201-89683-4', '978-0-201-89683-1'),
    ('0070342075', '9780070342071', '0-07-034207-5', '978-0-07-034207-1'),
    ('0127450408', '9780127450407', '0-12-745040-8', '978-0-12-745040-7'),
]

NOT_ISBN_CASES = ['4545784063439', 'Not an ISBN']

@pytest.mark.parametrize("s10,s13,split10,split13", CASES)
def test_isbn_constructor(s10, s13, split10, split13):
    ISBN.split_all = False
    i10 = ISBN(s10)
    i13 = ISBN(s13)
    j10 = ISBN(split10)
    j13 = ISBN(split13)
    assert i10 == i13
    assert j10 == i13
    assert j13 == i13
    assert str(i10) == s13
    assert str(i13) == s13
    assert str(j10) == s13
    assert str(j13) == s13

@pytest.mark.parametrize("i", NOT_ISBN_CASES)
def test_isbn_constructor_not_isbn(i):
    with pytest.raises(ValueError):
        _ = ISBN(i)

@pytest.mark.parametrize("s10", (c[0] for c in CASES))
def test_isbn_isbn10(s10):
    ISBN.split_all = False
    i10 = ISBN(s10)
    assert i10.isbn10() == s10

def test_isbn_isbn10_not_isbn10():
    # Not representable as ISBN-10:
    assert ISBN('9791692006289').isbn10() is None

@pytest.mark.parametrize("s10,s13", ((c[0], c[1]) for c in CASES))
def test_isbn_isbn13(s10, s13):
    ISBN.split_all = False
    i10 = ISBN(s10)
    assert i10.isbn13() == s13

@pytest.mark.parametrize("s10,s13", ((c[0], c[1]) for c in CASES))
def test_isbn_to_uri(s10, s13):
    ISBN.split_all = False
    i10 = ISBN(s10)
    uri = URI(i10)
    assert str(uri) == f'urn:isbn:{s13}'

@pytest.mark.parametrize("s10,split10,split13",
                         ((c[0], c[2], c[3]) for c in CASES))
def test_isbn_split(s10, split10, split13):
    ISBN.split_all = True
    i10 = ISBN(s10)
    assert i10.split10() == split10
    assert i10.split13() == split13
    assert i10.split() == tuple(split13.split('-'))

    # Not representable as ISBN-10:
    assert ISBN('9791692006289').split10() is None

def test_isbn_split_unknown():
    ISBN.split_all = False
    i = ISBN(CASES[0][0])
    # Cheat for testing; set the value to an unsplittable EAN.
    i._value = NOT_ISBN_CASES[0]    # pylint:disable=protected-access
    with pytest.warns(UserWarning, match='not found'):
        assert i.split13() == NOT_ISBN_CASES[0]
