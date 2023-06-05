# SPDX-License-Identifier: MIT
"""Test configuration utilities."""

import argparse
import io

from pathlib import Path

from fnattr.util import config

def test_add_env_dir_environ(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda _: True)
    monkeypatch.setenv('EVaR', '/test/dir')
    d = config.Dirs().add_env_dir('EVaR')
    assert d == [Path('/test/dir')]

def test_add_env_dir_environ_false(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda _: False)
    monkeypatch.setenv('EVaR', '/test/dir')
    d = config.Dirs().add_env_dir('EVaR')
    assert d == []

def test_add_env_dir_default(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda _: True)
    p = Path('/this/works')
    d = config.Dirs().add_env_dir('EVaR', p)
    assert d == [p]

def test_add_env_dir_default_false(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda _: False)
    p = Path('/this/works')
    d = config.Dirs().add_env_dir('EVaR', p)
    assert d == []

def test_add_env_dirs_environ(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda x: str(x)[1].islower())
    monkeypatch.setenv('EVaR', '/a/b:/c/d:/E/F')
    d = config.Dirs().add_env_dirs('EVaR', [])
    assert d == [Path('/a/b'), Path('/c/d')]

def test_add_env_dirs_default(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda _: True)
    p = [Path('/x'), Path('/y')]
    d = config.Dirs().add_env_dirs('EVaR', p)
    assert d == p

def test_add_env_dirs_default_false(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda _: False)
    p = [Path('/x'), Path('/y')]
    d = config.Dirs().add_env_dirs('EVaR', p)
    assert d == []

def test_find_first(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda _: True)
    monkeypatch.setattr(Path, 'exists', lambda x: str(x)[1] == 'y')
    p = [Path('/x'), Path('/y')]
    d = config.Dirs().add_env_dirs('EVaR', p)
    assert d.find_first('fu') == Path('/y/fu')

def test_find_first_fail(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda _: True)
    monkeypatch.setattr(Path, 'exists', lambda _: False)
    p = [Path('/x'), Path('/y')]
    d = config.Dirs().add_env_dirs('EVaR', p)
    assert d.find_first('fu') is None

def test_xdg_dirs_environ(monkeypatch):
    p0 = '/home/homu'
    p1 = '/home/test'
    p2 = '/etc/test'
    p3 = '/usr/share/test'
    monkeypatch.setattr(Path, 'is_dir', lambda _: True)
    monkeypatch.setattr(Path, 'home', lambda: Path(p0))
    monkeypatch.setenv('XDG_TEST_HOME', p1)
    monkeypatch.setenv('XDG_TEST_DIRS', f'{p2}:{p3}')
    d = config.xdg_dirs('TEST', 'testing', [])
    assert d == [Path(p1), Path(p2), Path(p3)]

def test_xdg_dirs_no_home(monkeypatch):

    def raise_runtime_error():
        raise RuntimeError

    p1 = '/home/test'
    p2 = '/etc/test'
    p3 = '/usr/share/test'
    monkeypatch.setattr(Path, 'is_dir', lambda _: True)
    monkeypatch.setattr(Path, 'home', raise_runtime_error)
    monkeypatch.setenv('XDG_TEST_HOME', p1)
    monkeypatch.setenv('XDG_TEST_DIRS', f'{p2}:{p3}')
    d = config.xdg_dirs('TEST', 'testing', [])
    assert d == [Path(p1), Path(p2), Path(p3)]

def test_xdg_dirs_environ_home(monkeypatch):
    p0 = '/home/homu'
    p1 = '/home/test'
    p2 = '/etc/test'
    p3 = '/usr/share/test'
    monkeypatch.setattr(Path, 'is_dir', lambda _: True)
    monkeypatch.setenv('XDG_TEST_HOME', p1)
    monkeypatch.setenv('XDG_TEST_DIRS', f'{p2}:{p3}')
    d = config.xdg_dirs('TEST', 'testing', [], Path(p0))
    assert d == [Path(p1), Path(p2), Path(p3)]

def test_xdg_dirs_defaults(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda _: True)
    monkeypatch.setattr(Path, 'home', lambda: Path('/home/homu'))
    d = config.xdg_dirs('TEST', 'testing', [Path('/etc/testing')])
    assert d == [Path('/home/homu/testing'), Path('/etc/testing')]

def test_xdg_config(monkeypatch):
    monkeypatch.setattr(Path, 'is_dir', lambda _: True)
    monkeypatch.setattr(Path, 'exists', lambda _: True)
    monkeypatch.setenv('XDG_CONFIG_HOME', '/home/homu/.config')
    monkeypatch.setenv('XDG_CONFIG_DIRS', '')
    p = config.xdg_config('testing.toml')
    assert p == Path('/home/homu/.config/testing.toml')

def test_read_configs(monkeypatch):
    f = io.BytesIO(b'[options]\nencoder = "v0"\n')
    monkeypatch.setattr(Path, 'open', lambda *_: f)
    d = config.read_cmd_configs('test', [])
    assert d == {'options': {'encoder': 'v0'}}

def test_read_configs_args(monkeypatch):
    f = io.BytesIO(b'[option]\nencoder = "v0"\n')
    monkeypatch.setattr(Path, 'is_dir', lambda _: False)
    monkeypatch.setattr(Path, 'open', lambda *_: f)
    d = config.read_cmd_configs('test', ['meh'])
    assert d == {'option': {'encoder': 'v0'}}

def test_merge_options(monkeypatch):
    option = {'a': 1, 'b': 2}
    args = argparse.Namespace(a=None, b=22, c=None, config=None)
    d = config.merge_options(
        option, args, a={'default': 10}, b={'default': 20}, c={'default': 30})
    assert d == {'a': 1, 'b': 22, 'c': 30}

def test_merge_options_none(monkeypatch):
    args = argparse.Namespace(a=None, b=22, c=None, config=None)
    d = config.merge_options(None, args, a=10, b=20, c=30)
    assert d == {'a': 10, 'b': 22, 'c': 30}

def test_rccamo(monkeypatch):
    f = io.BytesIO(b'[option]\nencoder = "v0"\na = 1\n')
    monkeypatch.setattr(Path, 'open', lambda *_: f)
    args = argparse.Namespace(a=None, b=22, c=None, config=None)
    c, options = config.read_cmd_configs_and_merge_options(
        'test', [], args, a=10, b=20, c=30)
    assert options == {'encoder': 'v0', 'a': 1, 'b': 22, 'c': 30}
    assert c == {'option': options}

def test_read_configs_bad_toml(monkeypatch, caplog):
    f = io.BytesIO(b'wtf!')
    monkeypatch.setattr(Path, 'open', lambda *_: f)
    d = config.read_cmd_configs('test', [])
    assert d == {}
    assert 'vlju.toml:' in caplog.record_tuples[0][2]

def test_read_configs_args_bad_toml(monkeypatch, caplog):
    f = io.BytesIO(b'wtf!')
    monkeypatch.setattr(Path, 'is_dir', lambda _: False)
    monkeypatch.setattr(Path, 'open', lambda *_: f)
    d = config.read_cmd_configs('test', ['meh'])
    assert d == {}
    assert 'meh:' in caplog.record_tuples[0][2]
