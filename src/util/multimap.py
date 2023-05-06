# SPDX-License-Identifier: MIT
"""MultiMap"""

import collections
import collections.abc
import functools

from collections.abc import Callable, Iterable
from typing import Any, Generic, Self, TypeVar

K = TypeVar('K')
V = TypeVar('V')

T = TypeVar('T')
W = TypeVar('W')

class MultiMap(Generic[K, V]):
    """Multi-valued dictionary."""

    def __init__(self):
        self.data = collections.defaultdict(list[V])

    def __eq__(self, other):
        # pylint:disable=unidiomatic-typecheck
        return (type(self) == type(other)) and (self.data == other.data)

    def __getitem__(self, k: K) -> list[V]:
        return self.data[k]

    def __delitem__(self, k: K):
        if k in self.data:
            del self.data[k]

    def __contains__(self, k) -> bool:
        return (k in self.data) and (self.data[k] != [])

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f'MultiMap({repr(dict(self.data))})'

    def __iter__(self):
        return iter(self.data)

    def copy(self) -> Self:
        r = type(self)()
        r.data = self.data.copy()
        return r

    def get(self, k: K, default: list[V] | None = None) -> list[V]:
        if k in self.data:
            return self.data[k]
        if default is None:
            return []
        return default

    def keys(self):
        return self.data.keys()

    def pairs(self):
        """Yields (k, v), potentially repeating k."""
        for k, vlist in self.data.items():
            for v in vlist:
                yield (k, v)

    def lists(self) -> collections.abc.ItemsView[K, list[V]]:
        """Yields (k, vlist)"""
        return self.data.items()

    def add(self, k: K, v: V) -> Self:
        if v not in self.data[k]:
            self.data[k].append(v)
        return self

    def remove(self, k: K, v: V) -> Self:
        self.data[k].remove(v)
        return self

    def pop(self, key: K, default=None):
        if self.data[key]:
            return self.data[key].pop()
        return default

    def top(self, k: K):
        if self.data[k]:
            return self.data[k][-1]
        return None

    def extend(self, other) -> Self:
        for k, v in other.pairs():
            self.add(k, v)
        return self

    def sortkeys(self, keys: Iterable[K] | None = None):
        """Put the map keys in alphabetical order, or specified order."""
        if keys is None:
            keys = sorted(self.data.keys())
        old = self.data
        self.data = collections.defaultdict(list[V])
        for k in keys:
            if k in old:
                self.data[k] = old[k]
                del old[k]
        self.data.update(old)
        return self

    def sortvalues(self, keys: Iterable[K] | None = None, key=None):
        if keys is None:
            keys = self.data.keys()
        for k in keys:
            self.data[k].sort(key=key)  # type:ignore
        return self

    def _reduce(
        self,
        iterator: Iterable[tuple[K, W]],
        combine: Callable[[T, Any], T],
        f: Callable[[K, W], T],
        initializer: T | None = None,
        predicate: Callable[[tuple[K, W]], bool] | None = None,
        empty: T | None = None,
    ) -> T | None:
        """Helper for `reduce_pairs()` and `reduce_lists()`."""
        i = [f(k, v) for k, v in filter(predicate, iterator)]
        if initializer is None:
            if not i:
                return empty
            return functools.reduce(combine, i)
        return functools.reduce(combine, i, initializer)

    def reduce_pairs(
        self,
        combine: Callable[[T, T], T],
        f: Callable[[K, V], T],
        initializer: T | None = None,
        predicate: Callable[[tuple[K, V]], bool] | None = None,
        empty: T | None = None,
    ) -> T | None:
        return self._reduce(self.pairs(), combine, f, initializer, predicate,
                            empty)

    def reduce_lists(
        self,
        combine: Callable[[T, T], T],
        f: Callable[[K, list[V]], T],
        initializer: T | None = None,
        predicate: Callable[[tuple[K, list[V]]], bool] | None = None,
        empty: T | None = None,
    ) -> T | None:
        return self._reduce(self.lists(), combine, f, initializer, predicate,
                            empty)

    def submap(self, keys: Iterable[K] | None = None):
        if not keys:
            return self
        r = type(self)()
        for k in keys or []:
            if k in self.data:
                r.data[k] = self.data[k]
        return r
