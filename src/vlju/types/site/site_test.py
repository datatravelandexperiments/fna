# SPDX-License-Identifier: MIT
"""Test SiteBase and site_class()"""

from vlju.types.site import SiteBase, site_class
from vlju.types.uri import Authority

class SiteA(SiteBase):
    _scheme = 'https'
    _authority = Authority('example.com')

class SiteB(SiteA):
    normalize_template = '{x.upper()}'

def test_site_base_constructor():
    s = SiteA('value')
    assert s.lv() == 'https://example.com/value'

def test_site_base_normalize():
    s = SiteB('value')
    assert s.lv() == 'https://example.com/VALUE'

def test_site_class():
    SiteC = site_class(
        'SiteC', host='example.com', path='item/{x}')
    c0 = SiteC('000')
    c1 = SiteC('111')
    assert c0.lv() == 'https://example.com/item/000'
    assert c1.lv() == 'https://example.com/item/111'

    SiteD = site_class(
        name='SiteD',
        scheme='http',
        host='example.com',
        path='item',
        query='q={x}')
    d0 = SiteD('alpha beta')
    assert d0.lv() == 'http://example.com/item?q=alpha+beta'

    SiteE = site_class(
        name='SiteE',
        scheme='https',
        host='example.com',
        path="{x.split(',')[0]}",
        query="{x.split(',')[1]}",
        fragment="{x.split(',')[2]}",
        normalize="{x.replace('_', ',')}")
    e0 = SiteE('foo_bar_baz')
    assert e0.lv() == 'https://example.com/foo?bar#baz'
