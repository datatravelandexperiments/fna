# SPDX-License-Identifier: MIT
"""File - Local file path"""

import pathlib

from typing import Any

import util.escape
import util.repr

from vlju.types.uri import URI, Authority
from vlju.types.url import URL

class File(URI):
    """Represents a local file path."""
    _authority = Authority('')

    def __init__(self, s: Any = ''):
        # `File` does not use the URI `path` component. Instead, it stores
        # the path as a `pathlib.Path` in `self._file`.
        if hasattr(s, 'cast_params'):
            s, _ = s.cast_params(type(self))
        if isinstance(s, pathlib.Path):
            self._file = s
            absolute = s.is_absolute()
        elif isinstance(s, str):
            self._file = pathlib.Path(s)
            absolute = s.startswith('/')
        else:
            raise TypeError(s)
        super().__init__(
            '',
            scheme='file',
            authority=self._authority,
            sa=('://' if absolute else ':'),
            ap='')

    # path() is already in use for the URI path component.
    def filename(self) -> pathlib.Path:
        return self._file

    def file(self) -> pathlib.Path:
        return self._file

    def cast_params(self, t) -> tuple[str, dict]:
        if t is URI or t is URL:
            return (str(self._file), {
                'scheme': 'file',
                'sa': self._sa,
                'ap': self._ap
            })
        raise self.cast_param_error(t)

    # Vlju overrides:

    def __eq__(self, other):
        try:
            return self._file == other._file
        except AttributeError:
            return False

    def __str__(self) -> str:
        return str(self._file)

    def __repr__(self) -> str:
        return util.repr.mkrepr(self, ['_file'])  # pragma: no cover

    # URI overrides:

    def path(self) -> str:
        return str(self._file)

    def spath(self) -> str:
        return util.escape.path.encode(str(self._file))
