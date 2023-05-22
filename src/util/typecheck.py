# SPDX-License-Identifier: MIT
"""Runtime type checking utilities."""

from typing import TypeVar

T = TypeVar('T')

def istype(value, *args) -> bool:   # noqa: ANN001
    for i in args:
        if i is None:
            return value is None
        if isinstance(value, i):
            return True
    return False

def needtype(value: T, *args) -> T:
    if istype(value, *args):
        return value
    raise TypeError((value, args))
