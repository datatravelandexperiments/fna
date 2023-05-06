# SPDX-License-Identifier: MIT
"""Test some site Vljus"""

import pathlib

import pytest

from util.config import read_toml_config
from util.pytestutil import im2p
from vlju.types.site import site_class
from vlju.types.url import URL

config = read_toml_config(pathlib.Path('config/config.toml'))
assert config
for k, v in config['site'].items():
    globals()[v['name']] = site_class(**v)

CASES = [
    {
        'cls': Danbooru,
        'inp': '2077531',
        'val': '2077531',
        'scheme': 'https',
        'host': 'danbooru.donmai.us',
        'path': 'posts/2077531',
    },
    {
        'cls': Gelbooru,
        'inp': '1',
        'val': '1',
        'scheme': 'https',
        'host': 'gelbooru.com',
        'path': 'index.php?page=post&s=view&id=1',
    },
    {
        'cls': Pixiv,
        'inp': '90647064',
        'val': '90647064_p0',
        'scheme': 'https',
        'host': 'www.pixiv.net',
        'path': 'en/artworks/90647064',
    },
    {
        'cls': Pixiv,
        'inp': '51307116_p14',
        'val': '51307116_p14',
        'scheme': 'https',
        'host': 'www.pixiv.net',
        'path': 'en/artworks/51307116#15',
    },
    {
        'cls': Twitter,
        'inp': '1152566724341878786',
        'val': '1152566724341878786',
        'scheme': 'https',
        'host': 'twitter.com',
        'path': 'i/web/status/1152566724341878786',
    },
    {
        'cls': Twitter,
        'inp': 'ClariS_Staff,245010623375749121',
        'val': 'ClariS_Staff,245010623375749121',
        'scheme': 'https',
        'host': 'twitter.com',
        'path': 'ClariS_Staff/status/245010623375749121',
    },
    {
        'cls': YouTube,
        'inp': 'ROsmdDujDH8',
        'val': 'ROsmdDujDH8',
        'scheme': 'https',
        'host': 'www.youtube.com',
        'path': 'watch?v=ROsmdDujDH8',
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

@pytest.mark.parametrize(*im2p(CASES, ('cls', 'inp', 'scheme', 'host', 'path')))
def test_site_bad_cast(cls, inp, scheme, host, path):
    y = cls(inp)
    with pytest.raises(TypeError):
        _ = y.cast_params(int)
