# SPDX-License-Identifier: MIT

from util.docsplit import docsplit

A = 'One part.'
B = 'Another part.'
C = 'Third part, different from the first.'
DK = 'Synopsis'
DV = 'This is the synopsis.'
EK = 'Bugs'
EV = 'There are none.'

def test_docsplit():
    a, b = docsplit(f'{A}\n\n{B}\n\n{DK}:  {DV}\n\n{C}\n\n{EK}:{EV}\n\n\n')
    assert a == [A, B, C]
    assert b == {DK.lower(): DV, EK.lower(): EV}

def test_docsplit_list_only():
    a, b = docsplit(f'{A}\n\n{B}\n\n\n\n{C}\n')
    assert a == [A, B, C]
    assert not b

def test_docsplit_dict_only():
    a, b = docsplit(f'\n\n\n{DK}:  {DV}\n\n{EK}:{EV}')
    assert not a
    assert b == {DK.lower(): DV, EK.lower(): EV}
