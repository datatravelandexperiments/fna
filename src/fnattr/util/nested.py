# SPDX-License-Identifier: MIT
"""Nested dictionaries."""

from collections.abc import (
    Iterable,
    Mapping,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Sequence,
    Set,
)
from typing import Any, TypeVar

T = TypeVar('T')
D = TypeVar('D')
MM = TypeVar('MM', bound=MutableMapping)

def nget(d: Mapping[T, Any], keys: Iterable[T], default) -> Any:
    """Get from nested dictionaries."""
    t: Any = d
    try:
        for k in keys:
            if k not in t:
                return default
            t = t[k]
    except (KeyError, TypeError):
        return default
    return t

def ngetor(d: Mapping[T, Any],
           keys: Iterable[T],
           default: D | None = None) -> Any | D | None:
    return nget(d, keys, default)

def nset(d: MutableMapping, keys: Iterable, value: Any) -> None:
    """Store in nested dictionaries."""
    ki = iter(keys)
    try:
        key: Any = next(ki)
    except StopIteration:
        raise KeyError(keys)
    while True:
        try:
            next_key = next(ki)
        except StopIteration:
            break
        if key not in d:
            d[key] = {}
        d = d[key]
        key = next_key
    d[key] = value

def nupdate(d: MM, s: Mapping) -> MM:
    """Update nested dictionaries."""
    for k, v in s.items():
        if k not in d:
            d[k] = v
            continue
        if isinstance(d[k], MutableMapping) and isinstance(v, Mapping):
            nupdate(d[k], v)
            continue
        if isinstance(d[k], MutableSequence) and isinstance(v, Sequence):
            d[k] += v
            continue
        if isinstance(d[k], MutableSet) and isinstance(v, Set):
            d[k] |= v
            continue
        if type(d[k]) is type(v):
            d[k] = v
            continue
        raise TypeError(k, d[k], v)
    return d

def dget(d: Mapping, keys: str, default: Any) -> Any:
    return nget(d, keys.split('.'), default)

def dgetor(d: Mapping, keys: str, default: Any | None = None) -> Any | None:
    return nget(d, keys.split('.'), default)

def dset(d: MutableMapping, keys: str, value: Any) -> None:
    nset(d, keys.split('.'), value)
