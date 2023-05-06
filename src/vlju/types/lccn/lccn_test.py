# SPDX-License-Identifier: MIT
"""Test LCCN"""

import pytest

from vlju.types.lccn import LCCN, normalize
from vlju.types.uri import URI
from vlju.types.url import URL

# yapf: disable
CASES = [
    ('n78-890351',          'n78890351'),
    ('n78-89035',           'n78089035'),
    ('n  78890351 ',        'n78890351'),
    ('   85000002 ',        '85000002'),
    ('85-2 ',               '85000002'),
    ('2001-000002',         '2001000002'),
    ('75-425165//r75',      '75425165'),
    (' 79139101 /AC/r932',  '79139101'),
]
# yapf: enable

@pytest.mark.parametrize("s,t", CASES)
def test_normalize(s, t):
    assert normalize(s) == t

@pytest.mark.parametrize("s,t", CASES)
def test_lccn(s, t):
    m = LCCN(s)
    assert str(m) == t

@pytest.mark.parametrize("s,t", CASES)
def test_lccn_to_uri(s, t):
    m = LCCN(s)
    uri = URI(m)
    assert str(uri) == f'info:lccn/{t}'

@pytest.mark.parametrize("s,t", CASES)
def test_lccn_to_url(s, t):
    m = LCCN(s)
    url = URL(m)
    assert str(url) == f'https://lccn.loc.gov/{t}'
