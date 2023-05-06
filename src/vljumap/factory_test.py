# SPDX-License-Identifier: MIT
"""Test VljuFactory"""

import pytest

from util.pytestutil import it2p
from vlju import Vlju
from vlju.types.ean import EAN13
from vlju.types.ean.isbn import ISBN
from vlju.types.ean.ismn import ISMN
from vlju.types.ean.issn import ISSN
from vljumap.factory import FactoryError, MappedFactory

# yapf: disable
CASES = [
    ('key',     'cls',  'value'),
    ('ean13',   EAN13,  '4534530128942'),
    ('isbn',    ISBN,   '9780804429573'),
    ('ismn',    ISMN,   '9790692006282'),
    ('issn',    ISSN,   '9771351538009'),
]
# yapf: enable

@pytest.fixture(name="factory")
def fixture_factory():
    return MappedFactory({key: cls for key, cls, _ in CASES}, Vlju)

@pytest.mark.parametrize(*it2p(CASES))
def test_mapped_factory(factory, key, cls, value):
    k, v = factory(key, value)
    assert k == key
    assert str(v) == value
    assert type(v) == cls   # pylint: disable=unidiomatic-typecheck

def test_mapped_factory_unknown_class(factory):
    _, v = factory('other', 'thing')
    assert type(v) == Vlju  # pylint: disable=unidiomatic-typecheck

def test_mapped_factory_set(factory):
    factory.set('isbn', EAN13)
    _, v = factory('isbn', '9780804429573')
    assert type(v) == EAN13  # pylint: disable=unidiomatic-typecheck

def test_mapped_factory_catch(factory):
    with pytest.raises(FactoryError):
        _ = factory('isbn', 1)
