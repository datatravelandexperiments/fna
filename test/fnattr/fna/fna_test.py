# SPDX-License-Identifier: MIT
"""Test fna command."""

import logging
from pathlib import Path

import pytest

import fnattr.fna

from fnattr.util import pytestutil

MK_V2 = '{x=2;x=1;z=Z;z=Y;y=Why}'
MK_V3 = '[x=2; x=1; z=Z; z=Y; y=Why]'
F1SFC = 'What? by Paul Penman 0123456789 2nd edition 2007'
F1V3 = 'What? [a=Paul Penman; isbn=9780123456786; edition=2; date=2007]'
D1SFC = f'/home/sfc/books/{F1SFC}.pdf'
D1V3 = f'/home/sfc/books/{F1V3}.pdf'

def fna(argv: list[str], cap) -> tuple[int, str]:
    status = fnattr.fna.main(['fna', '--no-default-config', *argv])
    out, err = cap.readouterr()
    assert err == ''
    return status, out

def test_fna_none(capsys, caplog):
    r, out = fna([], capsys)
    assert r == 0
    assert out == ''
    assert caplog.text == ''

def test_fna_add(capsys, caplog):
    r, out = fna(
        ['add', 'y', '7', 'set', 'y', '8', 'add', 'y', '9', 'set', 'x', '7'],
        capsys)
    assert r == 0
    assert out == '[y=8; y=9; x=7]\n'
    assert caplog.text == ''

def test_fna_compare_different(capsys, caplog):
    r, out = fna([
        '--decode=sfc',
        'file',
        D1SFC,
        'order',
        'a,isbn,edition',
        'quiet',
        'compare',
    ], capsys)
    assert r == 0
    assert out == f'{D1SFC}\n{D1V3}\n'
    assert caplog.text == ''

def test_fna_compare_same(capsys, caplog):
    r, out = fna(['file', D1V3, 'quiet', 'compare'], capsys)
    assert r == 0
    assert out == ''
    assert caplog.text == ''

def test_fna_decode(capsys, caplog):
    r, out = fna(['decode', MK_V3], capsys)
    assert r == 0
    assert out == MK_V3 + '\n'
    assert caplog.text == ''

def test_fna_decoder(capsys, caplog):
    r, out = fna(
        ['decoder', 'v2', 'decode', 'Mr. Book {a=Paul Penman;lccn=89-456}'],
        capsys)
    assert r == 0
    assert out == 'Mr. Book [a=Paul Penman; lccn=89000456]\n'
    assert caplog.text == ''

def test_fna_decoder_name(capsys, caplog):
    r, out = fna(['v2', 'decode', MK_V2, 'v3'], capsys)
    assert r == 0
    assert out == MK_V3 + '\n'
    assert caplog.text == ''

def test_fna_delete(capsys, caplog):
    r, out = fna(['decode', MK_V3, 'delete', 'a,z'], capsys)
    assert r == 0
    assert out == '[x=2; x=1; y=Why]\n'
    assert caplog.text == ''

def test_fna_dir(capsys, caplog):
    r, out = fna(['file', 'whatever.jpg', 'dir', '/blah'], capsys)
    assert r == 0
    assert out == '/blah/whatever.jpg\n'
    assert caplog.text == ''

def test_fna_encode(capsys, caplog):
    r, out = fna(['decode', MK_V3, 'encode'], capsys)
    assert r == 0
    assert out == MK_V3 + '\n'
    assert caplog.text == ''

def test_fna_encoder(capsys, caplog):
    r, out = fna(['decode', MK_V3, 'encoder', 'v2', 'encode'], capsys)
    assert r == 0
    assert out == MK_V2 + '\n'
    assert caplog.text == ''

def test_fna_encoder_name(capsys, caplog):
    r, out = fna(['decode', MK_V3, 'v2', 'encode'], capsys)
    assert r == 0
    assert out == MK_V2 + '\n'
    assert caplog.text == ''

def test_fna_encoder_unknown(capsys, caplog):
    r, out = fna(['encoder', 'lalala'], capsys)
    assert r != 0
    assert out == ''
    assert 'encoder: expected one' in caplog.text

def test_fna_extract(capsys, caplog):
    r, out = fna(['decode', MK_V3, 'extract', 'w,x'], capsys)
    assert r == 0
    assert out == '[x=2; x=1]\n'
    assert caplog.text == ''

def test_fna_factory(capsys, caplog):
    r, out = fna(['factory', 'raw', 'add', 'isbn', '7'], capsys)
    assert r == 0
    assert out == '[isbn=7]\n'
    assert caplog.text == ''

def test_fna_factory_name(capsys, caplog):
    r, out = fna(['raw', 'add', 'isbn', '7'], capsys)
    assert r == 0
    assert out == '[isbn=7]\n'
    assert caplog.text == ''

def test_fna_file(capsys, caplog):
    r, out = fna(['sfc', 'file', D1SFC, 'order', 'a,isbn,edition', 'v3'],
                 capsys)
    assert r == 0
    assert out == D1V3 + '\n'
    assert caplog.text == ''

def test_fna_filename(capsys, caplog):
    r, out = fna([
        'sfc',
        'file',
        D1SFC,
        'order',
        'a,isbn,edition',
        'quiet',
        'v3',
        'filename',
    ], capsys)
    assert r == 0
    assert out == D1V3 + '\n'
    assert caplog.text == ''

def test_fna_mode(capsys, caplog):
    r, out = fna([
        'decode',
        'Title [a=Author; isbn=9780123456786]',
        'mode',
        'long',
        'encode',
    ], capsys)
    assert r == 0
    assert out == 'Title [a=Author; isbn=urn:isbn:9780123456786]\n'
    assert caplog.text == ''

def test_fna_mode_name(capsys, caplog):
    r, out = fna(
        ['decode', 'Title [a=Author; isbn=9780123456786]', 'long', 'encode'],
        capsys)
    assert r == 0
    assert out == 'Title [a=Author; isbn=urn:isbn:9780123456786]\n'
    assert caplog.text == ''

def test_fna_order(capsys, caplog):
    r, out = fna(['decode', MK_V3, 'order', 'y,z'], capsys)
    assert r == 0
    assert out == '[y=Why; z=Z; z=Y; x=2; x=1]\n'
    assert caplog.text == ''

def test_fna_remove(capsys, caplog):
    r, out = fna(['decode', MK_V3, 'remove', 'y', 'Why'], capsys)
    assert r == 0
    assert out == '[x=2; x=1; z=Z; z=Y]\n'
    assert caplog.text == ''

def test_fna_rename(capsys, caplog, monkeypatch):
    mock_rename, result = pytestutil.make_fixed()
    monkeypatch.setattr(Path, 'rename', mock_rename)
    monkeypatch.setattr(Path, 'mkdir', lambda _, **_kw: True)
    r, out = fna(
        ['decoder', 'sfc', 'file', D1SFC, 'order', 'a,isbn,edition', 'rename'],
        capsys)
    assert r == 0
    assert out == ''
    assert result[0].args[0] == Path(D1SFC)
    assert result[0].args[1] == Path(D1V3)
    assert caplog.text == ''

def test_fna_rename_exists(capsys, caplog, monkeypatch):
    monkeypatch.setattr(Path, 'exists', lambda _: True)
    monkeypatch.setattr(Path, 'samefile', lambda *_: False)
    r, out = fna(['file', D1V3, 'quiet', 'rename'], capsys)
    assert r != 0
    assert out == ''
    assert 'FileExistsError' in caplog.text

def test_fna_rename_samefile(capsys, caplog, monkeypatch):
    monkeypatch.setattr(Path, 'exists', lambda _: True)
    monkeypatch.setattr(Path, 'samefile', lambda *_: True)
    r, out = fna(['file', D1V3, 'quiet', 'rename'], capsys)
    assert r == 0
    assert out == ''
    assert caplog.text == ''

def test_fna_set(capsys, caplog):
    r, out = fna(['decode', MK_V3, 'set', 'x', '7'], capsys)
    assert r == 0
    assert out == '[z=Z; z=Y; y=Why; x=7]\n'
    assert caplog.text == ''

def test_fna_sort_all(capsys, caplog):
    r, out = fna(['decode', MK_V3, 'sort', '--all'], capsys)
    assert r == 0
    assert out == '[x=1; x=2; z=Y; z=Z; y=Why]\n'
    assert caplog.text == ''

def test_fna_sort_keys(capsys, caplog):
    r, out = fna(['decode', MK_V3, 'sort', 'w,x,y'], capsys)
    assert r == 0
    assert out == '[x=1; x=2; z=Z; z=Y; y=Why]\n'
    assert caplog.text == ''

def test_fna_suffix(capsys, caplog):
    r, out = fna(['file', 'whatever.jpg', 'suffix', 'png'], capsys)
    assert r == 0
    assert out == 'whatever.png\n'
    assert caplog.text == ''

def test_fna_suffix_dot(capsys, caplog):
    r, out = fna(['file', 'whatever.jpg', 'suffix', '.png'], capsys)
    assert r == 0
    assert out == 'whatever.png\n'
    assert caplog.text == ''

def test_fna_missing_arguments(capsys, caplog):
    r, out = fna(['add'], capsys)
    assert r != 0
    assert out == ''
    assert 'add: expected key' in caplog.text

def test_fna_run_unknown_command(capsys, caplog):
    r, out = fna(['probably not a command name'], capsys)
    assert r != 0
    assert out == ''
    assert 'probably not' in caplog.text

def test_fna_run_empty(capsys, caplog):
    r, out = fna([], capsys)
    assert r == 0
    assert out == ''
    assert caplog.text == ''

def test_fna_uri(capsys, caplog):
    r, out = fna(['decode', F1V3, 'quiet', 'uri'], capsys)
    assert r == 0
    assert out == 'urn:isbn:9780123456786\n'
    assert caplog.text == ''

def test_fna_url(capsys, caplog):
    r, out = fna(
        ['decode', 'T [doi=10.1234/5678-90; a=George]', 'quiet', 'url'], capsys)
    assert r == 0
    assert out == 'https://doi.org/10.1234/5678-90\n'
    assert caplog.text == ''

def test_fna_url_all(capsys, caplog):
    r, out = fna(
        ['decode', 'T [doi=10.1234/5678-90; lccn=89456]', 'quiet', 'url'],
        capsys)
    assert r == 0
    assert out == ('https://doi.org/10.1234/5678-90\n'
                   'https://lccn.loc.gov/89456\n')
    assert caplog.text == ''

def test_fna_url_string(capsys, caplog):
    r, out = fna(['add', 'asdf', 'what/a/thing', 'url'], capsys)
    assert r == 0
    assert out == 'http://what/a/thing\n'
    assert caplog.text == ''

def test_fna_url_none(capsys, caplog):
    r, out = fna(['decode', F1V3, 'quiet', 'url'], capsys)
    assert r == 0
    assert out == ''
    assert caplog.text == ''

def test_fna_help(capsys, caplog):
    r, out = fna(['help'], capsys)
    assert r == 0
    assert 'COMMANDS' in out
    assert caplog.text == ''

def test_fna_help_one(capsys, caplog):
    r, out = fna(['help', 'help'], capsys)
    assert r == 0
    assert 'Show information' in out
    assert caplog.text == ''

def test_fna_help_unknown_command(capsys, caplog):
    r, out = fna(['help', 'asdfjkl'], capsys)
    assert r == 0
    assert 'COMMANDS' in out
    assert caplog.text == ''

def test_fna_mode_evaluate(capsys, caplog):
    r, out = fna(['--evaluate', 'add("isbn", "1234567890")'], capsys)
    assert r == 0
    assert out == '[isbn=9781234567897]\n'
    assert caplog.text == ''

def test_fna_mode_evaluate_none(capsys, caplog):
    r, out = fna(['--evaluate', 'None'], capsys)
    assert r == 0
    assert out == ''
    assert caplog.text == ''

def test_fna_mode_execute(capsys, caplog):
    r, out = fna(['--execute', 'if True: print("what")'], capsys)
    assert r == 0
    assert out == 'what\n'
    assert caplog.text == ''

def test_fna_mode_file(capsys, caplog, monkeypatch):
    infile = pytestutil.stringio('if True: print("what")')
    monkeypatch.setattr(Path, 'open', pytestutil.fake_fixed(infile))
    r, out = fna(['--file', 'testfile'], capsys)
    assert r == 0
    assert out == 'what\n'
    assert caplog.text == ''

def test_fna_no_reraise(capsys, caplog):
    r, out = fna(['--log-level=info', '--execute', 'raise RuntimeError'],
                 capsys)
    assert r != 0
    assert out == ''
    assert 'RuntimeError' in caplog.text

def test_fna_reraise(capsys, caplog):
    with pytest.raises(RuntimeError):
        _ = fna(['--log-level=debug', '--execute', 'raise RuntimeError'],
                capsys)
