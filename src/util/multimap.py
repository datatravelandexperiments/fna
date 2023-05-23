# SPDX-License-Identifier: MIT
"""MultiMap."""

from collections import defaultdict
from collections.abc import (
    Callable,
    Generator,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
)
from typing import Generic, Self, TypeVar

K = TypeVar('K')
V = TypeVar('V')

T = TypeVar('T')
W = TypeVar('W')

class MultiMap(Generic[K, V]):
    """Multi-valued dictionary."""

    def __init__(self) -> None:
        self.data: defaultdict[K, list[V]] = defaultdict(list[V])

    def __eq__(self, other: object) -> bool:
        # pylint:disable=unidiomatic-typecheck
        if isinstance(other, MultiMap):
            return (type(self) == type(other)) and (self.data == other.data)
        return False

    def __getitem__(self, k: K) -> list[V]:
        return self.data[k]

    def __delitem__(self, k: K) -> None:
        if k in self.data:
            del self.data[k]

    def __contains__(self, k: K) -> bool:
        return (k in self.data) and (self.data[k] != [])

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f'MultiMap({dict(self.data)!r})'

    def __iter__(self) -> Iterator[K]:
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

    def keys(self) -> KeysView[K]:
        return self.data.keys()

    def pairs(self) -> Generator[tuple[K, V], None, None]:
        """Yield (k, v), potentially repeating k."""
        for k, vlist in self.data.items():
            for v in vlist:
                yield (k, v)

    def lists(self) -> ItemsView[K, list[V]]:
        """Yield (k, vlist)."""
        return self.data.items()

    def add(self, k: K, v: V) -> Self:
        if v not in self.data[k]:
            self.data[k].append(v)
        return self

    def remove(self, k: K, v: V) -> Self:
        self.data[k].remove(v)
        return self

    def pop(self, key: K, default: T | None = None) -> V | T | None:
        if self.data[key]:
            return self.data[key].pop()
        return default

    def top(self, k: K) -> V | None:
        if self.data[k]:
            return self.data[k][-1]
        return None

    def extend(self, other: 'MultiMap') -> Self:
        for k, v in other.pairs():
            self.add(k, v)
        return self

    def sortkeys(self, keys: Iterable[K] | None = None) -> Self:
        """Put the map keys in alphabetical order, or specified order."""
        if keys is None:
            keys = sorted(self.data.keys())
        old = self.data
        self.data = defaultdict(list[V])
        for k in keys:
            if k in old:
                self.data[k] = old[k]
                del old[k]
        self.data.update(old)
        return self

    def sortvalues(self,
                   keys: Iterable[K] | None = None,
                   key: Callable | None = None) -> Self:
        if keys is None:
            keys = self.data.keys()
        for k in keys:
            self.data[k].sort(key=key)  # type: ignore[reportGeneralTypeIssues]
        return self

    def submap(self, keys: Iterable[K] | None = None) -> Self:
        if not keys:
            return self
        r = type(self)()
        for k in keys or []:
            if k in self.data:
                r.data[k] = self.data[k]
        return r
