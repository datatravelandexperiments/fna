# SPDX-License-Identifier: MIT
"""Test encoding and decoding VljuMap"""

import pytest

from vlju import Vlju
from vljumap import VljuMap, enc
from vlju.types.doi import DOI

class TstEncVlju(Vlju):  # pylint: disable=W0223

    @staticmethod
    def factory(key: str, value: str) -> tuple[str, Vlju]:
        return (key, TstEncVlju(value))

CASES = {
    'A': {
        'MAP':
            VljuMap().add_pairs([
                ('n', '1'),
                ('edition', '2'),
                ('date', '2007'),
                ('isbn', '0123456789'),
            ], TstEncVlju.factory),
        'v3': ('1. [edition=2; date=2007; isbn=0123456789]'),
        'v2': ('1. {edition=2;date=2007;isbn=0123456789}'),
        'v1': ('[n=1,edition=2,date=2007,isbn=0123456789]'),
        'v0': ('0123456789'),
        'win': ('1. [edition=2; date=2007; isbn=0123456789]'),
        'sfc': ('0123456789 2nd edition 2007'),
        'json': ('{"n": ["1"], "edition": ["2"], "date": ["2007"], '
                 '"isbn": ["0123456789"]}'),
        'sh': ('n=(1)\n'
               'edition=(2)\n'
               'date=(2007)\n'
               'isbn=(0123456789)'),
        'keyvalue': ('n: 1\n'
                     'edition: 2\n'
                     'date: 2007\n'
                     'isbn: 0123456789'),
        'value': ('1\n'
                  '2\n'
                  '2007\n'
                  '0123456789'),
        'csv': ('"n","1"\n'
                '"edition","2"\n'
                '"date","2007"\n'
                '"isbn","0123456789"\n')
    },
    'B': {
        'MAP': VljuMap().add_pairs([('a', 'Author, A')], TstEncVlju.factory),
        'v3': ('[a=Author, A]'),
        'v2': ('{a=Author, A}'),
        'v1': ('Author, A:'),
        'v0': ('Author, A:'),
        'win': ('[a=Author, A]'),
        'sfc': ('by Author, A'),
        'json': ('{"a": ["Author, A"]}'),
        'sh': ("a=('Author, A')"),
        'keyvalue': ('a: Author, A'),
        'value': ('Author, A'),
        'csv': ('"a","Author, A"\n'),
    },
    'C': {
        'MAP':
            VljuMap().add_pairs([('title', 'About Things')],
                                TstEncVlju.factory),
        'v3': ('About Things'),
        'v2': ('About Things'),
        'v1': ('About Things'),
        'v0': ('About Things'),
        'win': ('About Things'),
        'sfc': ('About Things'),
        'json': ('{"title": ["About Things"]}'),
        'sh': ("title=('About Things')"),
        'keyvalue': ('title: About Things'),
        'value': ('About Things'),
        'csv': ('"title","About Things"\n'),
    },
    'D': {
        'MAP':
            VljuMap().add_pairs([
                ('a', 'Paul Penman'),
                ('a', 'Writer, W'),
                ('title', 'What?'),
                ('title', 'Strange - a subtitle?'),
                ('edition', '2'),
                ('date', '2007'),
                ('isbn', '9780123456786'),
                ('lccn', '89-456'),
                ('special', ''),
                ('n', '3'),
                ('n', '5'),
                ('t', '12:34:56'),
            ], TstEncVlju.factory),
        'v3': ('3.5. What? - Strange %2D a subtitle? '
               '[a=Paul Penman; a=Writer, W; edition=2; date=2007;'
               ' isbn=9780123456786; lccn=89-456; special; t=12:34:56]'),
        'v2': ('3.5. What? - Strange %2D a subtitle? '
               '{a=Paul Penman;a=Writer, W;edition=2;'
               'date=2007;isbn=9780123456786;'
               'lccn=89-456;special;t=12:34:56}'),
        'v1': ('Paul Penman; Writer, W: What?: Strange - a subtitle? '
               '[edition=2,date=2007,isbn=9780123456786,lccn=89-456,special,'
               'n=3,n=5,t=12:34:56]'),
        'v0': ('Paul Penman; Writer, W: What?: '
               'Strange - a subtitle? 9780123456786'),
        'win': ('3.5. What%3F - Strange %2D a subtitle%3F '
                '[a=Paul Penman; a=Writer, W; edition=2; date=2007;'
                ' isbn=9780123456786; lccn=89-456; special; t=12%3A34%3A56]'),
        'sfc': ('What? - Strange - a subtitle? by Paul Penman, Writer, W '
                '9780123456786 2nd edition 2007'),
        'json': ('{"a": ["Paul Penman", "Writer, W"], '
                 '"title": ["What?", "Strange - a subtitle?"], '
                 '"edition": ["2"], '
                 '"date": ["2007"], "isbn": ["9780123456786"], '
                 '"lccn": ["89-456"], "special": [""], "n": ["3", "5"], '
                 '"t": ["12:34:56"]}'),
        'json2': ('{"a": ["Paul Penman", "Writer, W"],'
                  '"title": ["What?", "Strange - a subtitle?"], "edition": 2,'
                  '"date": 2007, "isbn": 9780123456786, "lccn": "89-456",'
                  '"special": "","n": ["3", "5"], "t": ["12:34:56"]}'),
        'sh': ("a=('Paul Penman' 'Writer, W')\n"
               "title=('What?' 'Strange - a subtitle?')\n"
               "edition=(2)\n"
               "date=(2007)\n"
               "isbn=(9780123456786)\n"
               "lccn=(89-456)\n"
               "special=('')\n"
               "n=(3 5)\n"
               "t=(12:34:56)"),
        'keyvalue': ('a: Paul Penman\n'
                     'a: Writer, W\n'
                     'title: What?\n'
                     'title: Strange - a subtitle?\n'
                     'edition: 2\n'
                     'date: 2007\n'
                     'isbn: 9780123456786\n'
                     'lccn: 89-456\n'
                     'special: \n'
                     'n: 3\n'
                     'n: 5\n'
                     't: 12:34:56'),
        'value': ('Paul Penman\n'
                  'Writer, W\n'
                  'What?\n'
                  'Strange - a subtitle?\n'
                  '2\n'
                  '2007\n'
                  '9780123456786\n'
                  '89-456\n'
                  'special\n'
                  '3\n'
                  '5\n'
                  '12:34:56'),
        'csv': ('"a","Paul Penman"\n'
                '"a","Writer, W"\n'
                '"title","What?"\n'
                '"title","Strange - a subtitle?"\n'
                '"edition","2"\n'
                '"date","2007"\n'
                '"isbn","9780123456786"\n'
                '"lccn","89-456"\n'
                '"special",""\n'
                '"n","3"\n'
                '"n","5"\n'
                '"t","12:34:56"\n')
    },
    'E': {
        'MAP':
            VljuMap().add_pairs([
                ('a', 'Paul Penman'),
                ('a', 'Writer, W'),
                ('title', 'Mr. Book'),
                ('lccn', '89-456'),
            ], TstEncVlju.factory),
        'v3': ('Mr. Book [a=Paul Penman; a=Writer, W; lccn=89-456]'),
        'v2': ('Mr. Book {a=Paul Penman;a=Writer, W;lccn=89-456}'),
        'v1': ('Paul Penman; Writer, W: Mr. Book [lccn=89-456]'),
        'v0': ('Paul Penman; Writer, W: Mr. Book lccn=89-456'),
    }
}

CASES_MVE_ENCODE = [(CASES[c]['MAP'], v, CASES[c][v])
                    for c in CASES.keys()
                    for v in set(CASES[c].keys()) - set(('MAP', ))]

@pytest.mark.parametrize("m,v,e", CASES_MVE_ENCODE)
def test_encode(m, v, e):
    if v in enc.encoder:
        assert enc.encoder[v].encode(m) == e

CASES_MVE_DECODE = filter(lambda t: t[1] not in ('sfc', 'sh', 'v0', 'value'),
                          CASES_MVE_ENCODE)

@pytest.mark.parametrize("m,v,e", CASES_MVE_DECODE)
def test_decode(m, v, e):
    if v in enc.encoder:
        assert enc.encoder[v].decode(VljuMap(), e, TstEncVlju.factory) == m

def test_v3_encode_doi():
    m = VljuMap().add('doi', DOI('10.12345/67890'))
    assert enc.v3.encode(m) == '[doi=10.12345,67890]'

def test_v3_decode_title_only():
    v = enc.v3.decode(VljuMap(), 'Title', TstEncVlju.factory)['title'][0]
    assert str(v) == 'Title'

def test_v3_decode_missing_close():
    with pytest.warns(UserWarning, match='Expected'):
        assert enc.v3.decode(VljuMap(), CASES['A']['v3'][:-1],
                             TstEncVlju.factory) == CASES['A']['MAP']

def test_v3_decode_empty_key():
    assert enc.v3.decode(VljuMap(), '[=1]', TstEncVlju.factory) == VljuMap()

def test_v0_decode():
    assert enc.v0.decode(VljuMap(), CASES['A']['v0'],
                         TstEncVlju.factory) == CASES['A']['MAP'].submap(
                             ['isbn'])
    assert enc.v0.decode(VljuMap(), CASES['B']['v0'],
                         TstEncVlju.factory) == CASES['B']['MAP']
    assert enc.v0.decode(VljuMap(), CASES['C']['v0'],
                         TstEncVlju.factory) == CASES['C']['MAP']
    assert enc.v0.decode(VljuMap(), CASES['D']['v0'],
                         TstEncVlju.factory) == CASES['D']['MAP'].submap(
                             ['a', 'title', 'isbn'])
    assert enc.v0.decode(VljuMap(), CASES['E']['v0'],
                         TstEncVlju.factory) == CASES['E']['MAP']

def test_sfc_decode():
    assert enc.sfc.decode(VljuMap(), CASES['A']['sfc'],
                          TstEncVlju.factory) == CASES['A']['MAP'].submap(
                              ['edition', 'date', 'isbn'])
    assert enc.sfc.decode(VljuMap(), CASES['B']['sfc'],
                          TstEncVlju.factory) == CASES['B']['MAP']
    assert enc.sfc.decode(VljuMap(), CASES['C']['sfc'],
                          TstEncVlju.factory) == CASES['C']['MAP']
    assert enc.sfc.decode(VljuMap(), CASES['D']['sfc'],
                          TstEncVlju.factory) == CASES['D']['MAP'].submap(
                              ['title', 'a', 'isbn', 'edition', 'date'])

def test_json_encode():
    assert enc.json.encode(CASES['A']['MAP']) == CASES['A']['json']
    assert enc.json.encode(CASES['B']['MAP']) == CASES['B']['json']
    assert enc.json.encode(CASES['C']['MAP']) == CASES['C']['json']
    assert enc.json.encode(CASES['D']['MAP']) == CASES['D']['json']

def test_json_decode():
    assert enc.json.decode(VljuMap(), CASES['D']['json2'],
                           TstEncVlju.factory) == CASES['D']['MAP']

def test_keyvalue_decode():
    assert enc.keyvalue.decode(VljuMap(), CASES['D']['keyvalue'] + '\n',
                               TstEncVlju.factory) == CASES['D']['MAP']

def test_sh_encode():
    assert enc.sh.encode(CASES['D']['MAP']) == CASES['D']['sh']

def test_can_encode():
    assert enc.v3.can_encode()
    assert enc.sh.can_encode()

def test_can_decode():
    assert enc.v3.can_decode()
    assert enc.sh.can_decode() is False
