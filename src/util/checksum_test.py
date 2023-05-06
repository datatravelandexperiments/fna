# SPDX-License-Identifier: MIT
"""Test checksums"""

import pytest

import util.checksum

@pytest.mark.parametrize("s", [
    '9780070342071',
    '9780127450407',
    '9780201896831',
    '9780804429573',
    '9790692006282',
    '0123456789012',
    '4534530128942',
])
def test_alt13(s):
    assert util.checksum.alt13_checksum(s[: 12]) == int(s[12])
    assert util.checksum.alt13(s[: 12]) == s[12]

@pytest.mark.parametrize("s,x", [
    ('0378595', '5'),
    ('0317847', '1'),
    ('1050124', 'X'),
    ('2434561', 'X'),
    ('080442957', 'X'),
    ('080442957', 'X'),
    ('020189683', '4'),
    ('007034207', '5'),
    ('012745040', '8'),
])
def test_mod11(s, x):
    assert util.checksum.mod11(s) == x
