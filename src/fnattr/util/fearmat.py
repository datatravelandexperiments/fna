# SPDX-License-Identifier: MIT
"""Like format, but scary."""

import builtins
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
    k: getattr(builtins, k)
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
    return str(evaluate(template, values, builtins))

def evaluate(s: str,
             values: Mapping[str, Any],
             builtins: Mapping[str, Any]) -> Any:
    g = dict(values) | {'__builtins__': builtins}
    return eval(s, g)   # noqa: PGH001, eval-used
