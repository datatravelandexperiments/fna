# SPDX-License-Identifier: MIT
"""VljuFactory"""

from collections.abc import Callable, Mapping
from typing import Self, Type

from util.error import Error
from vlju import Vlju

VljuFactory = Callable[[str, str], tuple[str, Vlju]]

class FactoryError(Error):
    pass

def default_factory(k: str, v: str) -> tuple[str, Vlju]:
    return (k, Vlju(v))

class MappedFactory:

    def __init__(self,
                 kmap: Mapping[str, Type[Vlju]],
                 default: Type[Vlju] = Vlju):
        self.kmap = dict(kmap)
        self.default = default

    def set(self, k: str, v: Type[Vlju]) -> Self:
        self.kmap[k] = v
        return self

    def __call__(self, k: str, v: str) -> tuple[str, Vlju]:
        try:
            return (k, self.kmap.get(k, self.default)(v))
        except Exception as e:
            raise FactoryError(f'{k} {v}') from e
