# SPDX-License-Identifier: MIT
"""Test io."""

import io
import sys

from fnattr.util.io import open_input, open_output, opener

def test_opener_none_is_default():
    f = opener(None, 'w', sys.stdout)
    assert f.file == sys.stdout
    assert not f.opened

def test_opener_dash_is_default():
    f = opener('-', 'w', sys.stdout)
    assert f.file == sys.stdout
    assert not f.opened

def test_opener_file_is_itself():
    f = opener(sys.stderr, 'w', sys.stdout)
    assert f.file == sys.stderr, False
    assert not f.opened

def test_open_output_none_is_stdout():
    with open_output(None) as f:
        assert f == sys.stdout

def test_open_output_dash_is_stdout():
    with open_output('-') as f:
        assert f == sys.stdout

def test_open_output_file_is_itself():
    with open_output(sys.stderr) as f:
        assert f == sys.stderr

def test_open_output_string_io_is_itself():
    s = io.StringIO()
    with open_output(s) as f:
        assert f == s
        f.write('test')
    assert s.getvalue() == 'test'

def test_open_output_filename_is_openend(mocker):
    filename = 'something'
    o = mocker.patch('pathlib.Path.open', mocker.mock_open())
    with open_output(filename) as f:
        fp = f
    o.assert_called_once_with('w', encoding='utf-8')
    fp.close.assert_called_once()

def test_open_input_none_is_stdin():
    with open_input(None) as f:
        assert f == sys.stdin

def test_open_input_dash_is_stdin():
    with open_input('-') as f:
        assert f == sys.stdin

def test_open_input_string_io_is_itself():
    s = io.StringIO('data')
    with open_input(s) as f:
        assert f == s
        t = f.read()
    assert s.getvalue() == t

def test_open_input_filename_is_openend(mocker):
    filename = 'something'
    o = mocker.patch('pathlib.Path.open', mocker.mock_open())
    with open_input(filename) as f:
        fp = f
    o.assert_called_once_with('r', encoding='utf-8')
    fp.close.assert_called_once()   # pylint: disable=no-member
