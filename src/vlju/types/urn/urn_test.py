# SPDX-License-Identifier: MIT
"""Test URN"""

import copy

from vlju import Vlju
from vlju.types.uri import Authority, URI
from vlju.types.urn import URN

def test_urn():
    """Test vlju.urn.URN"""
    u1 = URN('v', 'k')
    assert repr(u1) == "URN('v',authority=Authority('k'))"
    assert str(u1) == 'urn:k:v'
    assert u1.lv() == 'urn:k:v'

    u3 = URN('v/?/a/#/l/(u)/e', 'kind', 'q', 'r')
    assert str(u3) == 'urn:kind:v/%3F/a/%23/l/(u)/e?+r?=q'
    assert u3.spath() == 'v/%3F/a/%23/l/(u)/e'
    assert u3.scheme() == 'urn'
    assert u3.authority() == Authority('kind')
    assert u3.sauthority() == 'kind'
    assert u3.query() is None
    assert u3.fragment() is None
    assert u3.sfragment() == ''

    u4 = copy.copy(u3)
    assert u4 is not u3
    assert u4 == u3
    assert str(u4) == 'urn:kind:v/%3F/a/%23/l/(u)/e?+r?=q'

    v = Vlju('v')
    assert v != u1
    assert u1 != v

def test_urn_to_uri():
    urn = URN('v/?/a/#/l/(u)/e', 'kind', 'q', 'r')
    uri = URI(urn)
    assert str(uri) == 'urn:kind:v/%3F/a/%23/l/(u)/e?+r?=q'
