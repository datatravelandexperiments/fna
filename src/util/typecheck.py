# SPDX-License-Identifier: MIT

def istype(value, *args) -> bool:   # noqa: ANN001
    for i in args:
        if i is None:
            return value is None
        if isinstance(value, i):
            return True
    return False

def needtype(value, *args):
    if istype(value, *args):
        return value
    raise TypeError((value, args))
