# SPDX-License-Identifier: MIT
"""Utilities for testing."""

from collections.abc import Iterable, Iterator, Mapping, Sequence

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
