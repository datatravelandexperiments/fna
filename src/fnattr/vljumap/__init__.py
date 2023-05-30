# SPDX-License-Identifier: MIT
"""VljuMap."""

from collections.abc import Generator, Iterable
from typing import Self

from fnattr.util.multimap import MultiMap
from fnattr.vlju import Vlju
from fnattr.vljumap.factory import VljuFactory, default_factory

class VljuMap(MultiMap[str, Vlju]):
    """MultiMap of Vlju."""

    def get_pairs(
        self,
        mode: str | None = None,
    ) -> Generator[tuple[str, str | None], None, None]:
        for k, v in self.pairs():
            yield (k, v.get(mode))

    def get_lists(
        self,
        mode: str | None = None,
    ) -> Generator[tuple[str, list[str | None]], None, None]:
        for k, vlist in self.lists():
            yield (k, [v.get(mode) for v in vlist])

    def to_strings(self, mode: str | None = None) -> MultiMap[str, str]:
        m: MultiMap[str, str] = MultiMap()
        for k, v in self.get_pairs(mode):
            m.add(k, str(v))
        return m

    def add_pairs(self,
                  i: Iterable[tuple[str, str]],
                  factory: VljuFactory | None = None) -> Self:
        if factory is None:
            factory = default_factory
        for k, v in i:
            self.add(*factory(k, v))
        return self
