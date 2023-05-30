# SPDX-License-Identifier: MIT
"""Like format, but scary."""

import operator

from collections.abc import Mapping
from typing import Any

from fnattr.util.error import Error

ALLOWED_BUILTINS = (
    'False',
    'None',
    'True',
    'abs',
    'all',
    'any',
    'ascii',
    'bin',
    'bool',
    'chr',
    'hex',
    'int',
    'len',
    'map',
    'max',
    'min',
    'oct',
    'ord',
    'reversed',
    'slice',
    'sorted',
    'str',
)
ALLOWED_OPERATORS = (
    'add',
    'sub',
)

BUILTINS = {
    k: globals()['__builtins__'][k]
    for k in ALLOWED_BUILTINS
} | {
    k: getattr(operator, k)
    for k in ALLOWED_OPERATORS
}

def fearmat(template: str,
            values: Mapping[str, Any],
            builtins: Mapping[str, Any] | None = None) -> str:
    if '"""' in template:
        msg = '‘"""’ in ‘template’'
        raise Error(msg)
    template = 'f"""' + template + '"""'
    if builtins is None:
        builtins = BUILTINS
    g = dict(values) | {'__builtins__': builtins}
    return str(eval(template, g))   # noqa: PGH001, eval-used
