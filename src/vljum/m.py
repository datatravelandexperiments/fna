# SPDX-License-Identifier: MIT

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from util.registry import Registry
from vlju.types.all import Vlju, VLJU_TYPES
from vlju.types.site import site_class
from vljum import VljuM
from vljumap import enc
from vljumap.factory import default_factory, MappedFactory

V = Vlju

class M(VljuM):
    """Configured VljuM"""
    raw_factory = default_factory
    typed_factory = MappedFactory(VLJU_TYPES)
    default_registry = {
        'factory':
            Registry().update({
                'raw': raw_factory,
                'typed': typed_factory
            }).set_default('typed'),
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
    def configure_sites(cls, site: Mapping[str, Mapping[str, Any]]):
        for k, s in site.items():
            cls.typed_factory.set(k, site_class(**s))

    @classmethod
    def exports(cls) -> dict[str, Any]:
        x = EXPORTS.copy()
        for k, v in cls.typed_factory.kmap.items():
            x[k] = v
            x[v.__name__] = v
        return x

    @classmethod
    def evaluate(cls, s: str, g: dict[str, Any] | None = None):
        if g is None:
            g = cls.exports()
        return eval(s, g)   # pylint:disable=eval-used

    @classmethod
    def execute(cls, s: str, g: dict[str, Any] | None = None) -> dict[str, Any]:
        if g is None:
            g = cls.exports()
        exec(s, g)   # pylint:disable=exec-used
        return g

def _make_free_function(cls, name: str):
    method = getattr(cls, name)

    def f(*args, **kwargs):
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
    for k in ('add', 'decode', 'file', 'read', 'set')
}
