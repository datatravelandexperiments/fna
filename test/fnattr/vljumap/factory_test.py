# SPDX-License-Identifier: MIT
"""Test VljuFactory."""

import pytest

from fnattr.util.pytestutil import it2p
from fnattr.vlju import Vlju
from fnattr.vlju.types.ean import EAN13
from fnattr.vlju.types.ean.isbn import ISBN
from fnattr.vlju.types.ean.ismn import ISMN
from fnattr.vlju.types.ean.issn import ISSN
from fnattr.vljumap.factory import (
    FactoryError,
    LooseMappedFactory,
    MappedFactory,
)

# fmt: off
CASES = [
    ('key',     'cls',  'value'),
    ('ean13',   EAN13,  '4534530128942'),
    ('isbn',    ISBN,   '9780804429573'),
    ('ismn',    ISMN,   '9790692006282'),
    ('issn',    ISSN,   '9771351538009'),
]
# fmt: on

@pytest.fixture(name='factory')
def fixture_mapped_factory():
    return MappedFactory({key: cls for key, cls, _ in CASES}, Vlju)

@pytest.fixture(name='loose_factory')
def fixture_loose_factory():
    return LooseMappedFactory({key: cls for key, cls, _ in CASES}, Vlju)

@pytest.mark.parametrize(*it2p(CASES))
def test_mapped_factory(factory, key, cls, value):
    k, v = factory(key, value)
    assert k == key
    assert str(v) == value
    assert type(v) == cls   # pylint: disable=unidiomatic-typecheck

def test_mapped_factory_unknown_class(factory):
    _, v = factory('other', 'thing')
    assert type(v) == Vlju  # pylint: disable=unidiomatic-typecheck

def test_mapped_factory_setitem(factory):
    factory.setitem('isbn', EAN13)
    _, v = factory('isbn', '9780804429573')
    assert type(v) == EAN13  # pylint: disable=unidiomatic-typecheck

def test_mapped_factory_catch(factory):
    with pytest.raises(FactoryError):
        _ = factory('isbn', '123')

def test_loose_mapped_factory(loose_factory):
    _, v = loose_factory('isbn', '123')
    assert type(v) == Vlju  # pylint: disable=unidiomatic-typecheck
    assert str(v) == '123'
