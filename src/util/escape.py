# SPDX-License-Identifier: MIT
"""Escape encodings"""

import shlex
import urllib.parse

from collections.abc import Callable
from typing import NamedTuple

UNSAFE_ON_WINDOWS = '"*/:<>?\\|'
UNSAFE_ON_UNIX = '/'
UNSAFE_ON_MACOS = ':'

def mktrans_urlish(encode_chars: str):
    return str.maketrans({
        c: ''.join((f'%{i:02X}' for i in c.encode('utf8')))
        for c in encode_chars + '%'
    })

def mkencode_urlish(encode_chars: str = '') -> Callable[[str], str]:
    tr = mktrans_urlish(encode_chars)

    def encode(s: str) -> str:
        return s.translate(tr)

    return encode

def mkencode_urllib(quote: Callable[[str, str], str],
                    safe: str = '') -> Callable[[str], str]:

    def encode(s: str) -> str:
        return quote(s, safe)

    return encode

class Escape(NamedTuple):
    """Escaping scheme with encode and decode operations."""
    encode: Callable[[str], str]
    decode: Callable[[str], str]

# Global registry of named Escapes.
escape: dict[str, Escape] = {}

def _register_escape(name: str, e: Escape) -> Escape:
    escape[name] = e
    return e

auth = _register_escape(
    'auth',
    Escape(
        mkencode_urllib(urllib.parse.quote, "!$&'()*+,;="),
        urllib.parse.unquote))

path = _register_escape(
    'path',
    Escape(
        mkencode_urllib(urllib.parse.quote, "!$&'()*+,;=:@/"),
        urllib.parse.unquote))

query = _register_escape(
    'query',
    Escape(
        mkencode_urllib(urllib.parse.quote_plus, ":@?/&="),
        urllib.parse.unquote_plus))

fragment = _register_escape('fragment', query)

unixfile = _register_escape(
    'unixfile', Escape(mkencode_urlish(UNSAFE_ON_UNIX), urllib.parse.unquote))

macfile = _register_escape(
    'macfile', Escape(mkencode_urlish(UNSAFE_ON_MACOS), urllib.parse.unquote))

umfile = _register_escape(
    'umfile',
    Escape(
        mkencode_urlish(UNSAFE_ON_UNIX + UNSAFE_ON_MACOS),
        urllib.parse.unquote))

winfile = _register_escape(
    'winfile', Escape(mkencode_urlish(UNSAFE_ON_WINDOWS), urllib.parse.unquote))

sh = _register_escape('sh',
                      Escape(shlex.quote, lambda s: ' '.join(shlex.split(s))))
