# SPDX-License-Identifier: MIT
"""Helper to format a repr resembling a constructor."""

from collections.abc import Iterable, Mapping
from typing import Any

# pylint: disable=dangerous-default-value
# pylint does not understand that Iterator and Mapping are immutable.
def mkrepr(
    obj,
    pos: Iterable[str],
    kws: Iterable[str] = [],
    defaults: Mapping[str, Any] = {}
):
    """Helper to format a repr resembling a constructor.

    pos - positional argument names
    kws - keyword argument names
    defaults - argument default values
    """
    r = []
    kw = False
    for attr in pos:
        v = getattr(obj, attr)
        if v is None or v == defaults.get(attr):
            # Omitted, so subsequent parameters need a keyword.
            kw = True
        elif kw:
            r.append(f'{attr.lstrip("_")}={repr(v)}')
        else:
            r.append(repr(v))
    for attr in kws:
        v = getattr(obj, attr)
        if v is not None and v != defaults.get(attr):
            r.append(f'{attr.lstrip("_")}={repr(v)}')
    return f'{type(obj).__name__}({",".join(r)})'
