# SPDX-License-Identifier: MIT
"""Like format, but scary."""

from collections.abc import Mapping
from typing import Any

import util.error

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
    'max',
    'min',
    'oct',
    'ord',
    'reversed',
    'slice',
    'sorted',
    'str',
)

BUILTINS = {k: globals()['__builtins__'][k] for k in ALLOWED_BUILTINS}

def fearmat(template: str,
            values: Mapping[str, Any],
            builtins: Mapping[str, Any] | None = None) -> str:
    if '"""' in template:
        raise util.error.Error('‘"""’ in ‘template’')
    template = 'f"""' + template + '"""'
    if builtins is None:
        builtins = BUILTINS
    g = dict(values) | {'__builtins__': builtins}
    return str(eval(template, g))
