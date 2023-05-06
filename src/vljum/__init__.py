# SPDX-License-Identifier: MIT

import copy
import re
import sys

from collections import defaultdict
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Any, Self, Type

import util.io

from util.registry import Registry
from vlju.types.all import Vlju, File, URI, URL
from vljumap import VljuFactory, VljuMap, enc

VljuArg = Vlju | str | None
EncoderArg = enc.Encoder | str | None
FactoryArg = VljuFactory | str | None
ModeArg = str | None

class VljuM(VljuMap):
    """VljuMap operations."""
    default_registry: MutableMapping[str, Registry] = defaultdict(Registry)

    def __init__(self, i=None):
        super().__init__()
        self.factory = copy.copy(self.default_registry['factory'])
        self.encoder = copy.copy(self.default_registry['encoder'])
        self.decoder = copy.copy(self.default_registry['decoder'])
        self.mode = copy.copy(self.default_registry['mode'])
        self.original_path: Path
        self.modified_path: Path
        self._set_path(Path())
        if i is not None:
            if isinstance(i, VljuMap):
                self.extend(i)
            elif isinstance(i, File):
                self.file(i.filename())
            elif isinstance(i, Path):
                self._set_path(i)
            elif isinstance(i, str):
                self.decode(i)
            elif hasattr(i, 'cast_params'):
                s, d = i.cast_params(type(self))
                if s:
                    self._set_path(s)
                for k, v in d.items():
                    self.add(k, v)
            else:
                raise TypeError(i)

    def cast_params(self, t) -> tuple[str | Path, dict]:
        if t is File:
            return (self.filename(), {})
        if t is URI or t is URL:
            return (str(self.filename()), {'scheme': 'file', 'sa': '://'})
        raise TypeError((self, t))

    # Map operations.

    def add(self,
            k: str,
            v: VljuArg = None,
            factory: FactoryArg = None) -> Self:
        super().add(k, self._vlju(k, v, factory))
        return self

    def decode(self,
               s: str,
               decoder: EncoderArg = None,
               factory: FactoryArg = None) -> Self:
        self.decoder.get(decoder).decode(self, s, self.factory.get(factory))
        return self

    def dir(self, s: str | Path) -> Self:
        return self.with_dir(s)

    def extract(self, *args: str) -> Self:
        return self.submap(args)

    def file(self,
             s: str | Path,
             decoder: EncoderArg = None,
             factory: FactoryArg = None) -> Self:
        self._set_path(s)
        self.decoder.get(decoder).decode(self, self.original_path.stem,
                                         self.factory.get(factory))
        return self

    def order(self, *args: str) -> Self:
        return self.sortkeys(args or None)

    def read(self,
             file: util.io.PathLike = '-',
             decoder: EncoderArg = None,
             factory: FactoryArg = None) -> Self:
        with util.io.open_input(file, sys.stdin) as f:
            self.decoder.get(decoder).decode(self, f.read(),
                                             self.factory.get(factory))
        return self

    def remove(self,
               k: str,
               v: VljuArg = None,
               factory: FactoryArg = None) -> Self:
        if v is None:
            del self[k]
            return self
        super().remove(k, self._vlju(k, v, factory))
        return self

    def rename(self, encoder: EncoderArg = None, mode: ModeArg = None) -> Self:
        self.modified_path = self.filename(encoder, self.mode.get(mode))
        if self.modified_path.exists():
            if self.modified_path.samefile(self.original_path):
                return self
            raise FileExistsError(self.modified_path)
        self.original_path.rename(self.modified_path)
        self.original_path = self.modified_path
        return self

    def set(self,
            k: str,
            v: VljuArg = None,
            factory: FactoryArg = None) -> Self:
        del self[k]
        return self.add(k, v, factory)

    def sort(self, *args: str, mode: ModeArg = None) -> Self:
        return self.sortvalues(args or None,
                               lambda v: v.get(self.mode.get(mode)))

    def suffix(self, suffix: str) -> Self:
        return self.with_suffix(suffix)

    def with_dir(self, s: str | Path) -> Self:
        self.modified_path = Path(s) / self.modified_path.name
        return self

    def with_suffix(self, suffix: str) -> Self:
        if not suffix.startswith('.'):
            suffix = '.' + suffix
        self.modified_path = self.modified_path.with_suffix(suffix)
        return self

    def write(self,
              file: util.io.PathLike = '-',
              encoder: EncoderArg = None,
              mode: ModeArg = None) -> Self:
        with util.io.open_output(file, sys.stdout) as f:
            f.write(self.encoder.get(encoder).encode(self, self.mode.get(mode)))
        return self

    def z(self, file=sys.stderr) -> Self:  # pragma: no coverage
        print(repr(self), file=file)
        return self

    # String reductions.

    def __str__(self) -> str:
        if self.modified_path == Path():
            return self.encode()
        return str(self.filename())

    def lv(self) -> str:
        return self.encode(mode='long')

    def encode(self, encoder: EncoderArg = None, mode: ModeArg = None) -> str:
        return self.encoder.get(encoder).encode(self, self.mode.get(mode))

    def collect(self,
                *args: str,
                encoder: EncoderArg = None,
                mode: ModeArg = None) -> str:
        return self.encoder.get(encoder).encode(
            self.submap(args), self.mode.get(mode))

    def q(self) -> str:
        return ''

    def uri(self, encoder: EncoderArg = 'value') -> str:
        return self._url(URI).encode(encoder)

    def url(self, encoder: EncoderArg = 'value') -> str:
        return self._url(URL).encode(encoder)

    # Filename reduction.

    def filename(self,
                 encoder: EncoderArg = None,
                 mode: ModeArg = None) -> Path:
        return self.modified_path.with_stem(
            self.encode(encoder, self.mode.get(mode)))

    # Vlju reduction.

    def first(self, k: str | Type[Vlju]) -> Vlju:
        if isinstance(k, str):
            if k in self:
                return self[k][0]
        else:
            for _, v in self.pairs():
                if isinstance(v, k):
                    return v
        return Vlju('')

    # Helpers.

    def _set_path(self, s: str | Path) -> Self:
        if isinstance(s, str):
            s = Path(s)
        self.original_path = s
        self.modified_path = s
        return self

    def _url(self, cls: Type[Vlju]) -> Self:
        # Try hard to get URIs/URLs from the current map.
        out = type(self)()
        strings: list[tuple[str, str]] = []
        for k, v in self.pairs():
            try:
                u = cls(v)
            except TypeError:
                u = None
            if u:
                out.add(k, u)
            else:
                strings.append((k, str(v)))
        if strings:
            scheme_slashes_re = re.compile(r'\w+://.+')
            for k, v in strings:
                if '/' in v and not scheme_slashes_re.fullmatch(v):
                    v = 'http://' + v
                u = cls(v)
                if u and hasattr(u, 'authority') and u.authority():
                    out.add(k, u)
        return out

    def _vlju(self, k: str, v: VljuArg, factory: FactoryArg = None) -> Vlju:
        if v is None:
            r = Vlju('')
        elif isinstance(v, str):
            _, r = self.factory.get(factory)(k, v)
        else:
            r = v
        return r

    def __repr__(self) -> str:
        return (f'{type(self).__name__}'
                f'({repr(dict(self.data))},path={self.modified_path})')

    @classmethod
    def configure_options(cls, options: Mapping[str, Any]):
        for r in cls.default_registry:
            if (v := options.get(r)) is not None:
                cls.default_registry[r].set_default(v)
