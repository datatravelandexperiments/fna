# SPDX-License-Identifier: MIT
"""Test vljum.m."""

import pprint

from copy import deepcopy
from io import StringIO
from pathlib import Path

import pytest

from fnattr.util.error import Error
from fnattr.util.registry import Registry
from fnattr.vlju.testutil import CastParams
from fnattr.vlju.types.all import ISBN, URL, File
from fnattr.vljum.m import M, V

class TstVlju(V):
    """Vlju subclass for testing."""

def tst_vlju_factory(k: str, v: str) -> tuple[str, TstVlju]:
    return (k, TstVlju(v))

def test_configure_options():

    class N(M):
        default_registry = deepcopy(M.default_registry)

    N.configure_options({'decoder': 'v2', 'encoder': 'v1'})
    m = N().decode('{key=value; isbn=1234567890}')
    assert m.encode() == '[key=value,isbn=9781234567897]'

def test_configure_sites():

    class N(M):
        strict_factory = deepcopy(M.strict_factory)
        default_registry = deepcopy(M.default_registry)
        default_registry['factory'] = Registry().set_default(strict_factory)

    N.configure_sites({
        'test': {
            'name': 'SiteTest',
            'scheme': 'http',
            'host': 'example.com',
            'path': 'a/{x}/b',
            'url': [[r'https?://example.com/a/(\d+)/b']],
        },
    })
    pprint.pp(M.strict_factory.kmap)
    m = N().decode('[test=123]').z()
    assert m.url() == 'http://example.com/a/123/b'

    k, v = m.from_site_url('http://example.com/a/276/b')
    assert k == 'test'
    assert type(v).__name__ == 'SiteTest'
    assert str(v) == '276'

    k, v = m.from_site_url('http://www.example.com/q/276/p')
    assert k is None
    assert v is None

def test_m_construct_vljumap():
    m = M().add('key', 'value').add('key', 'two')
    mm = M(m)
    assert mm.encode() == '[key=value; key=two]'

def test_m_construct_file():
    m = M(File('/blah/Title [isbn=1234567890].pdf'))
    assert m.encode('keyvalue') == 'title: Title\nisbn: 9781234567897'

def test_m_construct_path():
    p = Path('/blah/Title [isbn=1234567890].pdf')
    m = M(p)
    assert m.encode() == ''
    assert m.original() == p

def test_m_construct_str():
    m = M('Title [isbn=1234567890]')
    assert m.encode('keyvalue') == 'title: Title\nisbn: 9781234567897'

def test_m_construct_cast_params():
    m = M(CastParams(None, {'a': V('42')}))
    assert str(m) == '[a=42]'

def test_m_construct_cast_params_with_path():
    p = Path('/blah/Title [isbn=1234567890].pdf')
    m = M(CastParams(str(p), {'a': V('42')}))
    assert str(m.filename()) == '/blah/[a=42].pdf'

def test_m_construct_other():
    with pytest.raises(TypeError):
        _ = M(1)

def test_m_add_string():
    m = M().add('key', 'value').add('key', 'two')
    assert m.encode() == '[key=value; key=two]'

def test_m_add_vlju():
    m = M().add('key', TstVlju('value'))
    assert m.encode() == '[key=value]'
    assert isinstance(m['key'][0], TstVlju)

def test_m_add_none():
    m = M().add('key')
    assert m.encode() == '[key]'
    assert str(m['key'][0]) == ''

def test_m_add_explicit_factory():
    m = M().add('isbn', '1234567897', tst_vlju_factory)
    assert m.encode() == '[isbn=1234567897]'
    assert isinstance(m['isbn'][0], TstVlju)

def test_m_add_implicit_factory():
    m = M().add('isbn', '1234567897')
    assert m.encode() == '[isbn=9781234567897]'

def test_m_decode():
    m = M().decode('[key=value; isbn=1234567890]')
    assert m.keys() == {'key', 'isbn'}
    assert str(m['key'][0]) == 'value'
    assert str(m['isbn'][0]) == '9781234567897'

def test_m_dir():
    m = M().file('/blah/f.pdf').with_dir('/etc')
    assert m.filename() == Path('/etc/f.pdf')

def test_m_extract():
    m = M().decode('[key=value; x=1; isbn=1234567890]').extract('key', 'isbn')
    assert m.keys() == {'key', 'isbn'}
    assert str(m['key'][0]) == 'value'
    assert str(m['isbn'][0]) == '9781234567897'

def test_m_file():
    p = '/blah/Title [isbn=1234567890].pdf'
    m = M().file(p)
    assert m.original() == Path(p)
    assert str(m) == '/blah/Title [isbn=9781234567897].pdf'

def test_m_filename():
    p = '/blah/[isbn=1234567890].pdf'
    m = M().file(p).add('title', 'Title')
    assert m.original() == Path(p)
    assert m.filename() == Path('/blah/Title [isbn=9781234567897].pdf')

def test_m_filename_empty():
    m = M()
    with pytest.raises(Error):
        _ = m.filename()

def test_m_first_key():
    m = M().decode('[y=1; y=2; x=a]')
    v = m.first('y')
    assert str(v) == '1'

def test_m_first_type():
    m = M().decode('[isbn=1234567890; isbn=9876543210; x=a]')
    v = m.first(ISBN)
    assert str(v) == '9781234567897'

def test_m_first_missing_key():
    m = M().decode('[y=1; y=2; x=a]')
    v = m.first('z')
    assert v == V('')

def test_m_first_missing_type():
    m = M().decode('[y=1; y=2; x=a]')
    v = m.first(ISBN)
    assert v == V('')

def test_m_collect():
    m = M().decode('[key=value; x=1; isbn=1234567890]')
    assert m.collect('key', 'isbn') == '[key=value; isbn=9781234567897]'

def test_m_lv():
    m = M().add('isbn', '1234567890')
    assert m.lv() == '[isbn=urn:isbn:9781234567897]'
    m.encoder.set_default('keyvalue')
    assert m.lv() == 'isbn: urn:isbn:9781234567897'

def test_m_order():
    m = M().decode('[z=1; y=2; x=a]').order('y', 'x')
    assert str(m) == '[y=2; x=a; z=1]'

def test_m_order_all():
    m = M().decode('[z=1; y=2; x=a]').order()
    assert str(m) == '[x=a; y=2; z=1]'

def test_m_q():
    m = M().add('key', 'one')
    assert m.q() == ''

def test_m_read():
    f = StringIO('[key=value; isbn=1234567890]')
    m = M().read(f)
    assert str(m) == '[key=value; isbn=9781234567897]'

def test_m_rename(monkeypatch):
    p = Path('/blah/[isbn=1234567890].jpeg')
    q = Path('/home/sfc/Title [isbn=9781234567897].jpg')
    m = M().file(p)
    assert m.original() == p

    def mk_mock_rename():
        d = {}

        def mock(self, target):
            d['src'] = self
            d['dst'] = target
            return target

        return (mock, d)

    mock_rename, result = mk_mock_rename()
    monkeypatch.setattr(Path, 'rename', mock_rename)

    m.with_dir('/home/sfc').with_suffix('jpg').add('title', 'Title').rename()
    assert m.original() == q
    assert result['src'] == p
    assert result['dst'] == q

def test_m_rename_no_original():
    m = M()
    with pytest.raises(Error, match='no file'):
        m.rename()

def test_m_rename_exists(monkeypatch):
    m = M().file('/etc/passwd')
    monkeypatch.setattr(Path, 'exists', lambda _: True)
    monkeypatch.setattr(Path, 'samefile', lambda _1, _2: False)
    with pytest.raises(FileExistsError):
        m.rename()

def test_m_rename_samefile(monkeypatch):
    m = M().file('/etc/passwd')
    monkeypatch.setattr(Path, 'exists', lambda _: True)
    monkeypatch.setattr(Path, 'samefile', lambda _1, _2: True)
    m.rename()

def test_m_remove_one():
    m = M().decode('[x=1; x=2; x=3; z=a]').remove('x', '2')
    assert str(m) == '[x=1; x=3; z=a]'

def test_m_remove_all():
    m = M().decode('[x=1; x=2; x=3; z=a]').remove('x')
    assert str(m) == '[z=a]'

def test_m_set():
    m = M().add('key', 'one').add('key', 'two')
    assert m.encode() == '[key=one; key=two]'
    m.reset('key', 'value')
    assert m.encode() == '[key=value]'

def test_m_sort_all():
    m = M().decode('[x=3; x=2; x=1; z=b; z=a]').sort()
    assert str(m) == '[x=1; x=2; x=3; z=a; z=b]'

def test_m_sort_one():
    m = M().decode('[x=3; x=2; x=1; z=b; z=a]').sort('x')
    assert str(m) == '[x=1; x=2; x=3; z=b; z=a]'

def test_m_str():
    m = M().add('isbn', '1234567890')
    assert str(m) == '[isbn=9781234567897]'
    m.encoder.set_default('keyvalue')
    assert str(m) == 'isbn: 9781234567897'

def test_m_suffix():
    m = M().file('/blah/f.pdf').with_suffix('jpg')
    assert m.original() == Path('/blah/f.pdf')
    assert m.filename() == Path('/blah/f.jpg')

def test_m_suffix_dot():
    m = M().file('/blah/f.pdf').with_suffix('.jpg')
    assert m.original() == Path('/blah/f.pdf')
    assert m.filename() == Path('/blah/f.jpg')

def test_m_uri():
    m = M().decode('[a=1; doi=10.1234,56-78; v=foo/bar]')
    assert m.uri() == ('info:doi/10.1234/56-78\n'
                       'http://foo/bar')

def test_m_url():
    m = M().decode('[doi=10.1234,56-78]')
    assert m.url() == 'https://doi.org/10.1234/56-78'

def test_m_write():
    f = StringIO()
    M().add('key', 'one').write(f)
    assert f.getvalue() == '[key=one]'

def test_m_to_file():
    p = '/blah/[isbn=1234567890].pdf'
    m = M().file(p).add('title', 'Title')
    assert m.original() == Path(p)
    f = File(m)
    assert str(f) == '/blah/Title [isbn=9781234567897].pdf'

def test_m_to_url():
    p = '/blah/[isbn=1234567890].pdf'
    m = M().file(p).add('title', 'Title')
    assert m.original() == Path(p)
    f = URL(m)
    assert str(f) == 'file:///blah/Title%20%5Bisbn=9781234567897%5D.pdf'

def test_m_to_other():
    with pytest.raises(TypeError):
        _ = M().cast_params(int)

def test_evaluate():
    r = M.evaluate("str(add('isbn', '1234567890'))")
    assert r == '[isbn=9781234567897]'

def test_evaluate_g():
    r = M.evaluate("str(add('isbn', '1234567890'))", {'add': lambda _1, _2: 1})
    assert r == '1'

def test_execute():
    g = M.execute("xxx = str(add('isbn', '1234567890'))")
    assert g['xxx'] == '[isbn=9781234567897]'

def test_execute_g():
    g = {'add': lambda _1, _2: 2}
    M.execute("xxx = add('isbn', '1234567890')", g)
    assert g['xxx'] == 2
