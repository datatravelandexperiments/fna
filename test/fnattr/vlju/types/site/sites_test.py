# SPDX-License-Identifier: MIT
"""Test some site Vljus."""

# ruff: noqa: F821

import pathlib

import pytest

from fnattr.util.config import read_toml_config
from fnattr.util.error import Error
from fnattr.util.pytestutil import im2p
from fnattr.vlju.types.site import site_class
from fnattr.vlju.types.url import URL

config = read_toml_config(pathlib.Path('config/vlju.toml'))
assert config
for _, v in config['site'].items():
    globals()[v['name']] = site_class(**v)

CASES = [
    {
        'cls': Danbooru,
        'inp': '2077531',
        'val': '2077531',
        'scheme': 'https',
        'host': 'danbooru.donmai.us',
        'path': 'posts/2077531',
        'url': 'https://danbooru.donmai.us/posts/2077531',
    },
    {
        'cls': Gelbooru,
        'inp': '123',
        'val': '123',
        'scheme': 'https',
        'host': 'gelbooru.com',
        'path': 'index.php?page=post&s=view&id=123',
        'url': 'https://gelbooru.com/index.php?page=post&s=view&id=123',
    },
    {
        'cls':
            Pixiv,
        'inp':
            '90647064',
        'val':
            '90647064_p0',
        'scheme':
            'https',
        'host':
            'www.pixiv.net',
        'path':
            'en/artworks/90647064',
        'url':
            'https://i.pximg.net/img-original/img/2021/06/19/01/14/55/90647064_p0.jpg',
    },
    {
        'cls': Pixiv,
        'inp': '52112383_p4',
        'val': '52112383_p4',
        'scheme': 'https',
        'host': 'www.pixiv.net',
        'path': 'en/artworks/52112383#5',
        'url': 'https://pixiv.net/en/artworks/52112383#5',
    },
    {
        'cls': Twitter,
        'inp': '1152566724341878786',
        'val': '1152566724341878786',
        'scheme': 'https',
        'host': 'twitter.com',
        'path': 'i/web/status/1152566724341878786',
        'url': 'https://twitter.com/i/web/status/1152566724341878786',
    },
    {
        'cls': Twitter,
        'inp': 'ClariS_Staff,245010623375749121',
        'val': 'ClariS_Staff,245010623375749121',
        'scheme': 'https',
        'host': 'twitter.com',
        'path': 'ClariS_Staff/status/245010623375749121',
        'url': 'https://twitter.com/ClariS_Staff/status/245010623375749121',
    },
    {
        'cls': YouTube,
        'inp': 'ROsmdDujDH8',
        'val': 'ROsmdDujDH8',
        'scheme': 'https',
        'host': 'www.youtube.com',
        'path': 'watch?v=ROsmdDujDH8',
        'url': 'https://www.youtube.com/watch?v=ROsmdDujDH8',
    },
]

@pytest.mark.parametrize(*im2p(CASES, ('cls', 'inp', 'scheme')))
def test_scheme(cls, inp, scheme):
    assert cls(inp).scheme() == scheme

@pytest.mark.parametrize(*im2p(CASES, ('cls', 'inp', 'host')))
def test_authority(cls, inp, host):
    assert str(cls(inp).authority()) == host

@pytest.mark.parametrize(*im2p(CASES, ('cls', 'inp', 'val')))
def test_value(cls, inp, val):
    assert str(cls(inp)) == val

@pytest.mark.parametrize(*im2p(CASES, ('cls', 'inp', 'scheme', 'host', 'path')))
def test_url(cls, inp, scheme, host, path):
    y = cls(inp)
    url = URL(y)
    x = f'{scheme}://{host}/{path}'
    assert str(url) == x

@pytest.mark.parametrize(*im2p(CASES, ('cls', 'url', 'val')))
def test_from_url(cls, url, val):
    u = cls.from_url(url)
    assert isinstance(u, cls)
    assert str(u) == val

@pytest.mark.parametrize(*im2p(CASES, ('cls', 'url', 'val')))
def test_init_from_url(cls, url, val):
    assert str(cls(url)) == val

@pytest.mark.parametrize(*im2p(CASES, ('cls', 'inp', 'scheme', 'host', 'path')))
def test_site_bad_cast(cls, inp, scheme, host, path):
    y = cls(inp)
    with pytest.raises(TypeError):
        _ = y.cast_params(int)

@pytest.mark.parametrize(*im2p(CASES, ('cls',)))
def test_from_url_fail(cls):
    with pytest.raises(Error, match='not recognized'):
        _ = cls.from_url('http://example.com/')
