# SPDX-License-Identifier: MIT
"""Test URL"""

from vlju.types.uri import URI
from vlju.types.url import URL

def test_url_constructor():
    url = 'https://example.com/with/a/path?n=1#id'
    u = URL(url)
    assert str(u) == url
    assert u.lv() == url
    assert u.url() == url

def test_url_to_uri():
    url = 'https://example.com/with/a/path?n=1#id'
    u = URL(url)
    v = URI(u)
    assert u == v

def test_url_to_url():
    url = 'https://example.com/with/a/path?n=1#id'
    u = URL(url)
    v = URL(u)
    assert u == v
