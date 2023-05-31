# SPDX-License-Identifier: MIT
"""Pre-configured VljuM."""

from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from fnattr.util.registry import Registry
from fnattr.vlju.types.all import VLJU_TYPES, Vlju
from fnattr.vlju.types.site import site_class
from fnattr.vljum import VljuM
from fnattr.vljumap import enc
from fnattr.vljumap.factory import (
    LooseMappedFactory,
    MappedFactory,
    default_factory,
)

V = Vlju

class M(VljuM):
    """Configured subclass of VljuM."""

    raw_factory = default_factory
    strict_factory = MappedFactory(VLJU_TYPES)
    loose_factory = LooseMappedFactory(VLJU_TYPES)
    default_registry = {
        'factory':
            Registry().update({
                'raw': raw_factory,
                'typed': loose_factory,
                'loose': loose_factory,
                'strict': strict_factory,
            }).set_default('loose'),
        'encoder':
            Registry().update(enc.encoder).set_default('v3'),
        'decoder':
            Registry().update(enc.decoder).set_default('v3'),
        'mode':
            Registry().update({
                k: k
                for k in ('short', 'long', 'repr')
            }).set_default('short'),
    }

    @classmethod
    def configure_sites(cls, site: Mapping[str, Mapping[str, Any]]) -> None:
        for k, s in site.items():
            scls = site_class(**s)
            cls.strict_factory.setitem(k, scls)
            cls.loose_factory.setitem(k, scls)

    @classmethod
    def exports(cls) -> dict[str, Any]:
        x = EXPORTS.copy()
        for k, v in cls.strict_factory.kmap.items():
            x[k] = v
            x[v.__name__] = v
        return x

    @classmethod
    def evaluate(cls,
                 s: str,
                 g: dict[str, Any] | None = None) -> Any:   # noqa: any-type
        if g is None:
            g = cls.exports()
        return eval(s, g)                                   # noqa: eval

    @classmethod
    def execute(cls, s: str, g: dict[str, Any] | None = None) -> dict[str, Any]:
        if g is None:
            g = cls.exports()
        exec(s, g)  # noqa: exec-builtin
        return g

def _make_free_function(cls: type, name: str) -> Callable:
    method = getattr(cls, name)

    def f(*args, **kwargs) -> Any:  # noqa: ANN401
        return method(cls(), *args, **kwargs)

    return f

EXPORTS: dict[str, Any] = {
                                                            # Aliases
    'Path': Path,
    'V': Vlju,
} | {
                                                            # Module definitions
    k: globals()[k]
    for k in ('M', )
} | {
                                                            # M() methods
    k: _make_free_function(M, k)
    for k in ('add', 'decode', 'file', 'read', 'reset')
}