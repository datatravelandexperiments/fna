# SPDX-License-Identifier: MIT
"""Utilities for testing."""

import io

from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

def im2p(cases: Iterable[Mapping],
         keys: Sequence[str] | None = None) -> tuple[str, list]:
    """Convert Mappings to pytest Parameters."""
    if keys is None:
        keys = list(next(iter(cases)).keys())
    return _2p(iter(cases), keys, keys)

def it2p(cases: Iterable[tuple],
         keys: Sequence[str] | None = None) -> tuple[str, list]:
    """Convert tuples to pytest Parameters. First entry is field names."""
    it = iter(cases)
    names = next(it)
    if keys is None:
        keys = names
    return _2p(it, keys, [names.index(k) for k in keys])

def _2p(it: Iterator, keys: Sequence[str],
        indices: Sequence) -> tuple[str, list]:
    if len(indices) == 1:
        # For this case, pytest requires bare items, not single-element tuples.
        index = indices[0]
        r = [i[index] for i in it]
    else:
        r = [tuple(i[index] for index in indices) for i in it]
    return (','.join(keys), r)

def stringio(initial_value: str = '') -> io.StringIO:
    s = io.StringIO(initial_value)
    s.close = lambda: None
    return s

@dataclass
class Arguments:
    """Record of fake function arguments."""

    args: tuple
    kwargs: dict[str, Any]

Fakery = tuple[Callable, list[Arguments]]

def make_str0mapped(d: Mapping, default: Any | None = None) -> Fakery:
    record: list[Arguments] = []

    def fake(*args, **kwargs) -> Any | None:
        record.append(Arguments(args, kwargs))
        return d.get(str(args[0]), default) if args else default

    return fake, record

def fake_str0mapped(d: Mapping, default: Any | None = None) -> Callable:
    return make_str0mapped(d, default)[0]

def make_fixed(default: Any | None = None) -> tuple[Callable, list]:
    return make_str0mapped({}, default)

def fake_fixed(default: Any | None = None) -> Callable:
    return make_fixed(default)[0]
