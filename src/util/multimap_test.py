# SPDX-License-Identifier: MIT
"""Test MultiMap"""

from typing import TypeVar

from util.multimap import MultiMap

CASES_KEY_LIST = {
    'isbn': ['0-8044-2957-X', '0-201-89683-4', '0-07-034207-5'],
    'ismn': ['M69200-628-2'],
    'issn': ['1351-5381'],
    'ean13': ['453-453012894-2', '1-23456-78901-2']
}

CASES_KEY_VALUE = [(k, v) for k, vs in CASES_KEY_LIST.items() for v in vs]

def mk(kld: dict[str, list[str]]) -> MultiMap:
    d: MultiMap = MultiMap()
    for k, vs in kld.items():
        for v in vs:
            d.add(k, v)
    return d

T = TypeVar('T')

def combine(r: list[T], i: T):
    return r + [i]

def kv(k: str, v: str) -> str:
    return f'{k}:{v}'

def test_multimap_empty():
    d: MultiMap[str, int] = MultiMap()
    assert len(d) == 0

def test_multimap_eq():
    d = mk(CASES_KEY_LIST)
    e = mk(CASES_KEY_LIST)
    assert d is not e
    assert d == e

def test_multimap_getitem():
    d = mk(CASES_KEY_LIST)
    assert d['issn'] == ['1351-5381']
    assert d['none'] == []

def test_multimap_get():
    d = mk(CASES_KEY_LIST)
    assert d.get('issn') == ['1351-5381']
    assert d.get('none', ['oh']) == ['oh']
    assert d.get('none') == []

def test_multimap_delitem():
    d = mk(CASES_KEY_LIST)
    del d['issn']
    assert d['issn'] == []
    del d['none']
    assert d['none'] == []

def test_multimap_contains():
    d = mk(CASES_KEY_LIST)
    assert 'isbn' in d
    assert 'none' not in d
    assert 'issn' in d
    _ = d.pop('issn')
    assert 'issn' not in d

def test_multimap_len():
    d = mk(CASES_KEY_LIST)
    assert len(d) == 4
    del d['issn']
    assert len(d) == 3

    e: MultiMap[str, int] = MultiMap()
    assert len(e) == 0

def test_multimap_repr():
    d = mk(CASES_KEY_LIST)
    assert repr(d) == f'MultiMap({repr(CASES_KEY_LIST)})'
    e: MultiMap[str, int] = MultiMap()
    assert repr(e) == 'MultiMap({})'

def test_multimap_iter():
    d = mk(CASES_KEY_LIST)
    assert list(iter(d)) == list(CASES_KEY_LIST.keys())

def test_multimap_copy():
    d = mk(CASES_KEY_LIST)
    e = d.copy()
    assert e == d
    assert e is not d
    del d['issn']
    assert e != d

def test_multimap_keys():
    d = mk(CASES_KEY_LIST)
    assert list(d.keys()) == list(CASES_KEY_LIST.keys())

def test_multimap_pairs():
    d = mk(CASES_KEY_LIST)
    for a, b in zip(d.pairs(), CASES_KEY_VALUE):
        assert a == b

def test_multimap_lists():
    d = mk(CASES_KEY_LIST)
    for a, b in zip(d.lists(), CASES_KEY_LIST.items()):
        assert a == b

def test_multimap_add():
    d = mk(CASES_KEY_LIST)
    assert len(d) == 4
    for k in d.keys():  # pylint:disable=consider-using-dict-items
        assert d[k] == CASES_KEY_LIST[k]

def test_multimap_add_duplicate():
    d: MultiMap[str, str] = MultiMap()
    for k, vs in CASES_KEY_LIST.items():
        for v in vs:
            d.add(k, v)
            d.add(k, v)
    assert len(d) == 4
    for k, vl in d.lists():
        assert vl == CASES_KEY_LIST[k]

def test_multimap_remove():
    d = mk(CASES_KEY_LIST)
    d.remove('ean13', '1-23456-78901-2')
    assert d['ean13'] == ['453-453012894-2']

def test_multimap_pop():
    d = mk(CASES_KEY_LIST)
    assert d.pop('none') is None
    assert d.pop('isbn') == CASES_KEY_LIST['isbn'][-1]
    assert d['isbn'] == CASES_KEY_LIST['isbn'][:-1]
    assert d.pop('issn') == CASES_KEY_LIST['issn'][-1]
    assert d['issn'] == []
    assert d.pop('issn') is None

def test_multimap_top():
    d = mk(CASES_KEY_LIST)
    assert d.top('none') is None
    assert d.top('isbn') == CASES_KEY_LIST['isbn'][-1]
    assert d['isbn'] == CASES_KEY_LIST['isbn']

def test_multimap_extend():
    d = mk(CASES_KEY_LIST)
    del d['isbn']
    h: MultiMap[str, str] = MultiMap()
    h.extend(d)
    assert h == d

    e = mk(CASES_KEY_LIST)
    h.extend(e)
    assert h == e

def test_multimap_sortkeys():
    d = mk(CASES_KEY_LIST)
    d.sortkeys(['ismn', 'ean13', 'nonexistent'])
    assert list(d.keys()) == ['ismn', 'ean13', 'isbn', 'issn']
    d.sortkeys()
    assert list(d.keys()) == ['ean13', 'isbn', 'ismn', 'issn']

def test_multimap_sortvalues():
    d = mk(CASES_KEY_LIST)
    d.sortvalues(['isbn'])
    assert d['isbn'] == ['0-07-034207-5', '0-201-89683-4', '0-8044-2957-X']

    e = mk(CASES_KEY_LIST)
    del e['issn']
    del e['ismn']
    e.sortvalues()
    assert e['isbn'] == ['0-07-034207-5', '0-201-89683-4', '0-8044-2957-X']
    assert e['ean13'] == ['1-23456-78901-2', '453-453012894-2']

def test_multimap_reduce_pairs():
    d = mk(CASES_KEY_LIST)
    sr = d.reduce_pairs(combine, kv, [])
    sx = [kv(k, v) for k, v in CASES_KEY_VALUE]
    assert sr == sx

    tx = ";".join(sx)
    tr = d.reduce_pairs(lambda r, i: f'{r};{i}', kv)
    assert tr == tx

    e = MultiMap()
    ts = e.reduce_pairs(  # pragma: no branch
        lambda r, i: f'{r};{i}', lambda k, v: f'{k}:{v}')
    assert ts is None

def test_multimap_reduce_lists():
    d = mk(CASES_KEY_LIST)
    mx = [f'{k}:{",".join(v)}' for k, v in CASES_KEY_LIST.items()]
    mr = d.reduce_lists(combine,
                        lambda k, v: f'{k}:{",".join(str(i) for i in v)}', [])
    assert mr == mx

def test_multimap_submap():
    d = mk(CASES_KEY_LIST)
    e = d.submap()
    assert d is e

    h = d.submap(['issn', 'ismn', 'none'])
    assert list(h.keys()) == ['issn', 'ismn']
    assert h['issn'] == d['issn']
    assert h['ismn'] == d['ismn']
