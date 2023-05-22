# SPDX-License-Identifier: MIT
"""I/O utilities."""

import contextlib
import io
import os
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import IO, cast

# Paths and open files are accepted.
PathLike = io.IOBase | IO | os.PathLike | str

@dataclass
class IOState:
    """Hold IO and whether we opened it."""

    file: IO
    opened: bool

def opener(file: PathLike | None,
           mode: str,
           default: IO,
           encoding: str = 'utf-8',
           **kwargs) -> IOState:
    """
    Open a file.

    The file can be an IOBase, '-' for the default, or a path.

    Returns a tuple of the file and a flag indicating whether the file
    was opened by this function.
    """
    if file is None or file == '-':
        return IOState(default, opened=False)
    if isinstance(file, io.IOBase | IO):
        return IOState(cast(IO, file), opened=False)
    return IOState(
        Path(file).open(mode, encoding=encoding, **kwargs), opened=True)

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
                default: IO = sys.stdout,
                encoding: str = 'utf-8',
                **kwargs) -> contextlib.AbstractContextManager:
    return open_context(file, 'w', default, encoding, **kwargs)

def open_input(file: PathLike | None,
               default: IO = sys.stdin,
               encoding: str = 'utf-8',
               **kwargs) -> contextlib.AbstractContextManager:
    return open_context(file, 'r', default, encoding, **kwargs)
