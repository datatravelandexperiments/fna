# SPDX-License-Identifier: MIT
"""Test string escaping"""

import pytest

import util.escape as e

from util.pytestutil import it2p

# yapf: disable
CASES = [
    ('name',     'esc',      'raw',          'escaped'),
    ('auth',     e.auth,     " !\"#$%&'",    "%20!%22%23$%25&'"),
    ('auth',     e.auth,     "()*+,-./0",    "()*+,-.%2F0"),
    ('auth',     e.auth,     ":;<=>?@A[\\]", "%3A;%3C=%3E%3F%40A%5B%5C%5D"),
    ('auth',     e.auth,     "^_`a{|}~",     "%5E_%60a%7B%7C%7D~"),
    ('path',     e.path,     " !\"#$%&'",    "%20!%22%23$%25&'"),
    ('path',     e.path,     "()*+,-./0",    "()*+,-./0"),
    ('path',     e.path,     ":;<=>?@A[\\]", ":;%3C=%3E%3F@A%5B%5C%5D"),
    ('path',     e.path,     "^_`a{|}~",     "%5E_%60a%7B%7C%7D~"),
    ('query',    e.query,    " !\"#$%&'",    "+%21%22%23%24%25&%27"),
    ('query',    e.query,    "()*+,-./0",    "%28%29%2A%2B%2C-./0"),
    ('query',    e.query,    ":;<=>?@A[\\]", ":%3B%3C=%3E?@A%5B%5C%5D"),
    ('query',    e.query,    "^_`a{|}~",     "%5E_%60a%7B%7C%7D~"),
    ('fragment', e.fragment, " !\"#$%&'",    "+%21%22%23%24%25&%27"),
    ('fragment', e.fragment, "()*+,-./0",    "%28%29%2A%2B%2C-./0"),
    ('fragment', e.fragment, ":;<=>?@A[\\]", ":%3B%3C=%3E?@A%5B%5C%5D"),
    ('fragment', e.fragment, "^_`a{|}~",     "%5E_%60a%7B%7C%7D~"),
    ('unixfile', e.unixfile, " !\"#$%&'",    " !\"#$%25&'"),
    ('unixfile', e.unixfile, "()*+,-./0",    "()*+,-.%2F0"),
    ('unixfile', e.unixfile, ":;<=>?@A[\\]", ":;<=>?@A[\\]"),
    ('unixfile', e.unixfile, "^_`a{|}~",     "^_`a{|}~"),
    ('macfile',  e.macfile,  " !\"#$%&'",    " !\"#$%25&'"),
    ('macfile',  e.macfile,  "()*+,-./0",    "()*+,-./0"),
    ('macfile',  e.macfile,  ":;<=>?@A[\\]", "%3A;<=>?@A[\\]"),
    ('macfile',  e.macfile,  "^_`a{|}~",     "^_`a{|}~"),
    ('umfile',   e.umfile,   " !\"#$%&'",    " !\"#$%25&'"),
    ('umfile',   e.umfile,   "()*+,-./0",    "()*+,-.%2F0"),
    ('umfile',   e.umfile,   ":;<=>?@A[\\]", "%3A;<=>?@A[\\]"),
    ('umfile',   e.umfile,   "^_`a{|}~",     "^_`a{|}~"),
    ('winfile',  e.winfile,  " !\"#$%&'",    " !%22#$%25&'"),
    ('winfile',  e.winfile,  "()*+,-./0",    "()%2A+,-.%2F0"),
    ('winfile',  e.winfile,  ":;<=>?@A[\\]", "%3A;%3C=%3E%3F@A[%5C]"),
    ('winfile',  e.winfile,  "^_`a{|}~",     "^_`a{%7C}~"),
    ('sh',       e.sh,       "'",            "''\"'\"''"),
    ('sh',       e.sh,       '"',            "'\"'"),
    ('sh',       e.sh,       '\\',           "'\\'"),
    ('sh',       e.sh,       " !#$&()*",     "' !#$&()*'"),
    ('sh',       e.sh,       ";<>?[]^`{|}~", "';<>?[]^`{|}~'"),
    ('sh',       e.sh,       "%+,-./0",      "%+,-./0"),
    ('sh',       e.sh,       ":=@A_a",       ":=@A_a"),
]
# yapf: enable

@pytest.mark.parametrize(*it2p(CASES))
def test_escapes(name, esc, raw, escaped):
    assert e.escape[name] == esc
    assert esc.encode(raw) == escaped
    assert esc.decode(escaped) == raw
