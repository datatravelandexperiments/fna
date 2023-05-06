# SPDX-License-Identifier: MIT
"""Test VljuMap"""

from vlju import Vlju
from vljumap import VljuMap

CASES_KEY_LIST = {
    'isbn': ['0-8044-2957-X', '0-201-89683-4', '0-07-034207-5'],
    'ismn': ['M69200-628-2'],
    'issn': ['1351-5381'],
    'ean13': ['453-453012894-2', '1-23456-78901-2']
}

CASES_KEY_VALUE = [(k, v) for k, vs in CASES_KEY_LIST.items() for v in vs]

VX = Vlju('X')

def vx_factory(k: str, _: str) -> tuple[str, Vlju]:
    return (k, VX)

def test_vljumap_add_pairs_default_factory():
    n = VljuMap().add_pairs(CASES_KEY_VALUE)
    for k, vl in n.lists():
        assert k in CASES_KEY_LIST
        for nv, ev in zip(vl, CASES_KEY_LIST[k]):
            assert nv == Vlju(ev)

def test_vljumap_add_pairs_custom_factory():
    n = VljuMap().add_pairs(CASES_KEY_VALUE, vx_factory)
    for k, vl in n.lists():
        assert k in CASES_KEY_LIST
        for nv in vl:
            assert nv == VX

def test_vljumap_get_pairs():
    n = VljuMap().add_pairs(CASES_KEY_VALUE)
    assert list(n.get_pairs('default')) == CASES_KEY_VALUE

def test_vljumap_get_lists():
    n = VljuMap().add_pairs(CASES_KEY_VALUE)
    nl = n.get_lists()
    assert set(kv[0] for kv in nl) == set(CASES_KEY_LIST.keys())
    for k, vl in n.get_lists():
        assert k in CASES_KEY_LIST
        for nv, ev in zip(vl, CASES_KEY_LIST[k]):
            assert nv == ev

def test_vljumap_to_strings():
    n = VljuMap().add_pairs(CASES_KEY_VALUE)
    for k, v in n.to_strings().pairs():
        assert k in CASES_KEY_LIST
        assert v in CASES_KEY_LIST[k]
