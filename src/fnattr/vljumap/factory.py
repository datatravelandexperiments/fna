# SPDX-License-Identifier: MIT
"""Vlju factories."""

from collections.abc import Callable, Mapping
from typing import Self

from fnattr.util.error import Error
from fnattr.vlju import Vlju

VljuFactory = Callable[[str, str], tuple[str, Vlju]]

class FactoryError(Error):
    """Factory error."""

def default_factory(k: str, v: str) -> tuple[str, Vlju]:
    return (k, Vlju(v))

class MappedFactory:
    """VljuFactory that maps keys to Vlju types."""

    def __init__(self,
                 kmap: Mapping[str, type[Vlju]],
                 default: type[Vlju] = Vlju) -> None:
        self.kmap = dict(kmap)
        self.default = default

    def setitem(self, k: str, v: type[Vlju]) -> Self:
        self.kmap[k] = v
        return self

    def __call__(self, k: str, v: str) -> tuple[str, Vlju]:
        try:
            return (k, self.kmap.get(k, self.default)(v))
        except Exception as e:  # noqa: blind-except
            msg = f'{k} {v}'
            raise FactoryError(msg) from e

class LooseMappedFactory(MappedFactory):
    """VljuFactory that maps keys for Vlju types, and reverts to default."""

    def __call__(self, k: str, v: str) -> tuple[str, Vlju]:
        try:
            value = self.kmap.get(k, self.default)(v)
        except Exception:   # noqa: blind-except
            value = self.default(v)
        return (k, value)
