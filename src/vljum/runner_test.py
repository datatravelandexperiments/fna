# SPDX-License-Identifier: MIT

from collections.abc import Iterable, Sequence
from pathlib import Path

import pytest

import util.error
import vljumap
import vljumap.enc
import vljumap.factory
import vlju.types.all
import vljum.m
import vljum.runner

def mk(pairs: Iterable[tuple[str, str]] | None = None,
       args: Sequence[str] | None = None) -> vljum.runner.Runner:
    """Create an initial machine."""
    m = vljum.m.M()
    if pairs:
        m.add_pairs(pairs, m.factory.get())
    state = vljum.runner.Runner(m)
    if args:
        state.run(args)
    return state

F1SFC = 'What? by Paul Penman 0123456789 2nd edition 2007'
F1V3 = 'What? [a=Paul Penman; isbn=9780123456786; edition=2; date=2007]'
D1SFC = f'/home/sfc/books/{F1SFC}.pdf'
D1V3 = f'/home/sfc/books/{F1V3}.pdf'

MK_IN = [('x', '2'), ('z', 'Z'), ('x', '1'), ('z', 'Y'), ('y', 'Why')]
MK_V3 = '[x=2; x=1; z=Z; z=Y; y=Why]'
MK_V2 = '{x=2;x=1;z=Z;z=Y;y=Why}'

def test_runner_init():
    r = mk(MK_IN)
    assert r.m.encode() == MK_V3

def test_runner_command_add():
    r = mk(MK_IN)
    r.runs('add y 7 set y 8 add y 9 set x 7')
    assert r.m.encode() == '[z=Z; z=Y; y=8; y=9; x=7]'

def test_runner_command_decode():
    r = mk()
    r.run(['decode', MK_V3])
    assert r.m == vljum.m.M().add_pairs(MK_IN)

def test_runner_command_decoder():
    r = mk()
    r.run(['decoder', 'v2', 'decode', 'Mr. Book {a=Paul Penman;lccn=89-456}'])
    assert r.m.encode() == 'Mr. Book [a=Paul Penman; lccn=89000456]'

def test_runner_decoder_name():
    r = mk()
    r.run(['v2', 'decode', MK_V2])
    assert r.m.encode('v3') == MK_V3

def test_runner_command_delete():
    r = mk(MK_IN)
    r.runs('delete a,z')
    assert r.m.encode() == '[x=2; x=1; y=Why]'

def test_runner_command_dir():
    r = mk(args=['file', 'whatever.jpg'])
    r.runs('dir /tmp')
    assert r.m.filename() == Path('/tmp/whatever.jpg')

def test_runner_command_encode(capsys):
    r = mk(MK_IN)
    r.runs('encode')
    assert capsys.readouterr().out == MK_V3 + '\n'
    assert not r.report

def test_runner_command_encoder(capsys):
    r = mk(MK_IN)
    r.runs('encoder v2 encode')
    assert capsys.readouterr().out == MK_V2 + '\n'
    assert not r.report

def test_runner_command_encoder_name(capsys):
    r = mk(MK_IN)
    r.runs('v2 encode')
    assert capsys.readouterr().out == MK_V2 + '\n'
    assert not r.report

def test_runner_command_encoder_name_partial():
    r = mk()
    r.runs('value')
    assert r.m.encoder.get() == vljumap.enc.value
    assert r.m.decoder.get() == vljumap.enc.v3

def test_runner_command_encoder_unknown():
    r = mk()
    with pytest.raises(util.error.Error):
        r.runs('encoder lalala')

def test_runner_command_extract():
    r = mk(MK_IN)
    r.runs('extract w,x')
    assert r.m.encode() == '[x=2; x=1]'

def test_runner_command_factory():
    r = mk()
    r.runs('factory raw add isbn 7')
    assert r.m.encode() == '[isbn=7]'
    assert type(r.m.first('isbn')) is vlju.Vlju

def test_runner_command_factory_name():
    r = mk()
    r.runs('raw add isbn 7')
    assert r.m.encode() == '[isbn=7]'
    assert type(r.m.first('isbn')) is vlju.Vlju

def test_runner_command_file():
    r = mk()
    r.run(['sfc', 'file', D1SFC, 'order', 'a,isbn,edition'])
    assert r.m.encode('v3') == F1V3
    assert r.m.filename('v3') == Path(D1V3)

def test_runner_command_filename(capsys):
    r = mk(args=['sfc', 'file', D1SFC, 'order', 'a,isbn,edition', 'quiet'])
    r.runs('v3 filename')
    assert capsys.readouterr().out == D1V3 + '\n'
    assert not r.report

def test_runner_command_mode(capsys):
    r = mk(args=['decode', 'Title [a=Author; isbn=9780123456786]', 'quiet'])
    r.runs('mode long encode')
    captured = capsys.readouterr()
    assert captured.out == 'Title [a=Author; isbn=urn:isbn:9780123456786]\n'

def test_runner_command_mode_name(capsys):
    r = mk(args=['decode', 'Title [a=Author; isbn=9780123456786]', 'quiet'])
    r.runs('long encode')
    captured = capsys.readouterr()
    assert captured.out == 'Title [a=Author; isbn=urn:isbn:9780123456786]\n'

def test_runner_command_order():
    r = mk(MK_IN)
    r.runs('order y,z')
    assert r.m.encode() == '[y=Why; z=Z; z=Y; x=2; x=1]'

def test_runner_command_remove():
    r = mk(MK_IN)
    r.runs('remove y Why')
    assert r.m.encode() == '[x=2; x=1; z=Z; z=Y]'

def mk_mock_rename():
    d = {}

    def mock(self, target):
        d['src'] = self
        d['dst'] = target
        return target

    return (mock, d)

def test_runner_command_rename(monkeypatch):
    r = mk(args=['decoder', 'sfc', 'file', D1SFC, 'order', 'a,isbn,edition'])
    mock_rename, result = mk_mock_rename()
    monkeypatch.setattr(Path, 'rename', mock_rename)
    r.runs('rename')
    assert result['src'] == Path(D1SFC)
    assert result['dst'] == Path(D1V3)

def test_runner_command_rename_exists(monkeypatch):
    r = mk(args=['file', D1V3, 'quiet'])
    monkeypatch.setattr(Path, 'exists', lambda p: True)
    monkeypatch.setattr(Path, 'samefile', lambda p, q: False)
    with pytest.raises(FileExistsError):
        r.runs('rename')

def test_runner_command_rename_samefile(monkeypatch):
    r = mk(args=['file', D1V3, 'quiet'])
    monkeypatch.setattr(Path, 'exists', lambda p: True)
    monkeypatch.setattr(Path, 'samefile', lambda p, q: True)
    r.runs('rename')

def test_runner_command_set():
    r = mk(MK_IN)
    r.runs('set x 7')
    assert r.m.encode() == '[z=Z; z=Y; y=Why; x=7]'

def test_runner_command_sort_all():
    r = mk(MK_IN)
    r.runs('sort --all')
    assert r.m.encode() == '[x=1; x=2; z=Y; z=Z; y=Why]'

def test_runner_command_sort_keys():
    r = mk(MK_IN)
    r.runs('sort w,x,y')
    assert r.m.encode() == '[x=1; x=2; z=Z; z=Y; y=Why]'

def test_runner_command_suffix():
    r = mk(args=['file', 'whatever.jpg'])
    r.runs('suffix png')
    assert r.m.filename() == Path('whatever.png')

def test_runner_command_suffix_dot():
    r = mk(args=['file', 'whatever.jpg'])
    r.runs('suffix .png')
    assert r.m.filename() == Path('whatever.png')

def test_runner_missing_arguments():
    r = mk()
    with pytest.raises(util.error.Error):
        r.run(['add'])

def test_runner_run_unknown_command():
    r = mk()
    with pytest.raises(util.error.Error):
        r.run(['probably not a command name'])

def test_runner_run_empty():
    r = mk()
    r.run([])

def test_runner_token_empty():
    r = mk()
    assert r.token() is None

def test_runner_need_token_empty():
    r = mk()
    with pytest.raises(util.error.Error):
        _ = r.need()

def test_runner_uri(capsys):
    r = mk(args=['decode', F1V3, 'quiet'])
    r.runs('uri')
    assert capsys.readouterr().out == 'urn:isbn:9780123456786\n'

def test_runner_url(capsys):
    r = mk(args=['decode', 'T [doi=10.1234/5678-90; a=George]', 'quiet'])
    r.runs('url')
    assert capsys.readouterr().out == 'https://doi.org/10.1234/5678-90\n'

def test_runner_url_all(capsys):
    r = mk(args=['decode', 'T [doi=10.1234/5678-90; lccn=89456]', 'quiet'])
    r.runs('url')
    assert capsys.readouterr().out == ('https://doi.org/10.1234/5678-90\n'
                                       'https://lccn.loc.gov/89456\n')

def test_runner_url_string(capsys):
    r = mk([('asdf', 'what/a/thing')])
    r.runs('url')
    assert capsys.readouterr().out == 'http://what/a/thing\n'

def test_runner_url_none(capsys):
    r = mk(args=['decode', F1V3, 'quiet'])
    r.runs('url')
    assert capsys.readouterr().out == ''

def test_runner_help(capsys):
    r = mk()
    r.runs('help')
    captured = capsys.readouterr()
    assert 'COMMANDS' in captured.out

def test_runner_help_one(capsys):
    r = mk()
    r.runs('help help')
    captured = capsys.readouterr()
    assert 'Show information' in captured.out

def test_runner_help_unknown_command(capsys):
    r = mk()
    r.runs('help asdfjkl')
    captured = capsys.readouterr()
    assert 'COMMANDS' in captured.out
