# SPDX-License-Identifier: MIT
"""Test URI"""

import copy

import pytest

from util.pytestutil import im2p, it2p
from vlju import Vlju
from vlju.types.uri import Authority, URI
from vlju.types.url import URL

# yapf: disable
AUTHORITY_CASES = [
    ('host',          'port',   'user', 'pw',       'auth'),
    ('example.com',   None,     None,    None,      'example.com'),
    ('localhost',     8088,     None,    None,      'localhost:8088'),
    ('192.168.0.23',  80,       'me',    None,      'me@192.168.0.23:80'),
    ('example.org',   None,     'user',  'pass',    'user:pass@example.org'),
    ('example.org',   8080,     'u',     'p',       'u:p@example.org:8080'),
]
# yapf: enable

@pytest.mark.parametrize(*it2p(AUTHORITY_CASES))
def test_authority_composition(host, port, user, pw, auth):
    assert str(Authority(host, port, user, pw)) == auth

@pytest.mark.parametrize(*it2p(AUTHORITY_CASES))
def test_authority_decomposition(host, port, user, pw, auth):
    a = Authority(auth)
    assert a.host == host
    assert a.port == port
    assert a.username == user
    assert a.password == pw

@pytest.mark.parametrize(*it2p(AUTHORITY_CASES))
def test_authority_eq(host, port, user, pw, auth):
    a = Authority(host, port, user, pw)
    b = Authority(auth)
    c = Authority(host, port, user, 'other')
    assert a == a  # pylint: disable=comparison-with-itself
    assert a == b
    assert b == a
    assert a != c
    assert c != a

@pytest.mark.parametrize(*it2p(AUTHORITY_CASES, ['auth']))
def test_authority_wrap(auth):
    a = Authority(auth)
    c = Authority(a)
    assert a == c

@pytest.mark.parametrize(*it2p(AUTHORITY_CASES, ['auth']))
def test_authority_copy(auth):
    a = Authority(auth)
    b = copy.copy(a)
    assert b is not a
    assert b == a

def test_authority_slashes():
    a = Authority('//user:pass@example.org:81')
    assert a.host == 'example.org'
    assert a.port == 81
    assert a.username == 'user'
    assert a.password == 'pass'

def test_authority_type_error():
    with pytest.raises(TypeError):
        _ = Authority(1)  # type: ignore

@pytest.mark.parametrize("cls", [URI, URL])
def test_uri_constructor_minimal(cls):
    """Test vlju.uri.URI"""
    u1 = cls('v')
    assert str(u1) == 'v'

@pytest.mark.parametrize("cls", [URI, URL])
def test_uri_constructor_authority(cls):
    a = Authority('localhost')
    u2 = cls('v', scheme='s', authority=a, query='q', fragment='f')
    assert str(u2) == 's://localhost/v?q#f'
    assert u2.path() == 'v'

@pytest.mark.parametrize("cls", [URI, URL])
def test_uri_constructor_full(cls):
    u3 = cls(
        'v/?/a/#/l/(u)/e',
        scheme='s',
        authority='example.com',
        query='q#q',
        fragment='f#f')
    assert str(u3) == 's://example.com/v/%3F/a/%23/l/(u)/e?q%23q#f%23f'
    assert u3.spath() == 'v/%3F/a/%23/l/(u)/e'
    assert u3.scheme() == 's'
    assert u3.authority() == Authority('example.com')
    assert u3.sauthority() == 'example.com'
    assert u3.query() == 'q#q'
    assert u3.squery() == '?q%23q'
    assert u3.fragment() == 'f#f'
    assert u3.sfragment() == '#f%23f'

URI_CASES = [
    {
        'inp': 'https://example.com/with/a/path?n=1#id',
        'uri': 'https://example.com/with/a/path?n=1#id',
        'scheme': 'https',
        'host': 'example.com',
        'path': '/with/a/path',
        'query': 'n=1',
        'fragment': 'id',
    },
    {
        'inp': '//example.com/with/b/path?n=1#id',
        'uri': '//example.com/with/b/path?n=1#id',
        'scheme': '',
        'host': 'example.com',
        'path': '/with/b/path',
        'query': 'n=1',
        'fragment': 'id',
    },
    {
        'inp': 'https:with/c/path',
        'uri': 'https:with/c/path',
        'scheme': 'https',
        'host': None,
        'path': 'with/c/path',
        'query': None,
        'fragment': None,
    },
]

@pytest.mark.parametrize("cls", [URI, URL])
@pytest.mark.parametrize(*im2p(URI_CASES))
def test_uri_constructor(cls, inp, uri, path, scheme, host, query, fragment):
    u = cls(inp)
    assert str(u) == uri
    assert u.path() == path
    assert u.scheme() == scheme
    assert u.authority() == (Authority(host) if host else host)
    assert u.query() == query
    assert u.fragment() == fragment

@pytest.mark.parametrize("cls", [URI, URL])
@pytest.mark.parametrize(*im2p(URI_CASES))
def test_uri_get(cls, inp, uri, path, scheme, host, query, fragment):
    u = cls(inp)
    assert u['default'] == uri
    assert u['alternate'] == uri
    assert u['path'] == path
    assert u['scheme'] == scheme
    assert u['authority'] == (Authority(host) if host else host)
    assert u['query'] == query
    assert u['fragment'] == fragment

@pytest.mark.parametrize("cls", [URI, URL])
@pytest.mark.parametrize(*im2p(URI_CASES, ['inp']))
def test_uri_eq(cls, inp):
    u1 = cls(inp)
    u2 = cls(inp)
    u3 = cls('other')
    v = Vlju('/with/a/path')
    assert u1 is not u2
    assert u1 == u2
    assert u1 != u3
    assert u1 != v

@pytest.mark.parametrize("cls", [URI, URL])
@pytest.mark.parametrize(*im2p(URI_CASES, ['inp']))
def test_uri_copy(cls, inp):
    u1 = cls(inp)
    u2 = copy.copy(u1)
    assert u1 is not u2
    assert u1 == u2

def test_uri_bad_cast():
    a = URI('file:///etc/passwd')
    with pytest.raises(TypeError):
        _ = a.cast_params(int)
