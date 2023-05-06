# SPDX-License-Identifier: MIT
"""I/O utilities."""

import contextlib
import io
import os
import sys

from typing import cast, IO

# Paths and open files are accepted.
PathLike = io.IOBase | IO | os.PathLike | str

class IOState:
    def __init__(self, file: IO, opened: bool):
        self.file = file
        self.opened = opened

def opener(file: PathLike | None,
           mode: str,
           default: IO,
           encoding: str = 'utf-8',
           **kwargs) -> IOState:
    """Open a file.

    The file can be an IOBase, '-' for the default, or a path.

    Returns a tuple of the file and a flag indicating whether the file
    was opened by this function.
    """
    if file is None or file == '-':
        return IOState(default, False)
    if isinstance(file, (io.IOBase, IO)):
        return IOState(cast(IO, file), False)
    return IOState(open(file, mode, encoding=encoding, **kwargs), True)

def open_context(file: PathLike | None,
                 mode: str,
                 default: IO,
                 encoding: str = 'utf-8',
                 **kwargs) -> contextlib.AbstractContextManager:
    s = opener(file, mode, default, encoding, **kwargs)
    if s.opened:
        return contextlib.closing(s.file)
    return contextlib.nullcontext(s.file)

def open_output(file: PathLike | None,
                default=sys.stdout,
                encoding='utf-8',
                **kwargs) -> contextlib.AbstractContextManager:
    return open_context(file, 'w', default, encoding, **kwargs)

def open_input(file: PathLike | None,
               default=sys.stdin,
               encoding='utf-8',
               **kwargs) -> contextlib.AbstractContextManager:
    return open_context(file, 'r', default, encoding, **kwargs)
