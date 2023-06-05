# SPDX-License-Identifier: MIT
"""VljuMap operations."""

import copy
import filecmp
import logging
import re
import sys

from collections import defaultdict
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Any, Self, TextIO

from fnattr.util.error import Error
from fnattr.util.io import PathLike, open_input, open_output
from fnattr.util.registry import Registry
from fnattr.vlju.types.all import URI, URL, File, Vlju
from fnattr.vljumap import VljuFactory, VljuMap, enc

VljuArg = Vlju | str | None
EncoderArg = enc.Encoder | str | None
FactoryArg = VljuFactory | str | None
ModeArg = str | None

class VljuM(VljuMap):
    """VljuMap operations."""

    default_registry: MutableMapping[str, Registry] = defaultdict(Registry)

    def __init__(self, i: VljuMap | File | Path | str | object = None) -> None:
        super().__init__()
        self.factory = copy.copy(self.default_registry['factory'])
        self.encoder = copy.copy(self.default_registry['encoder'])
        self.decoder = copy.copy(self.default_registry['decoder'])
        self.mode = copy.copy(self.default_registry['mode'])
        self._original_path: Path
        self._current_dir: Path
        self._current_suffix: str
        self.set_path(Path())
        if i is not None:
            if isinstance(i, VljuMap):
                self.extend(i)
            elif isinstance(i, File):
                self.file(i.filename())
            elif isinstance(i, Path):
                self.set_path(i)
            elif isinstance(i, str):
                self.decode(i)
            elif hasattr(i, 'cast_params'):
                s, d = i.cast_params(type(self))
                if s:
                    self.set_path(s)
                for k, v in d.items():
                    self.add(k, v)
            else:
                raise TypeError(i)

    def cast_params(self, t: object) -> tuple[str | Path, dict]:
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

    def extract(self, *args: str) -> Self:
        return self.submap(args)

    def file(self,
             s: str | Path,
             decoder: EncoderArg = None,
             factory: FactoryArg = None) -> Self:
        self.set_path(s)
        r = self.decoder.get(decoder).decode_file(self, self._original_path,
                                                  self.factory.get(factory))
        self._current_dir = r.directory
        self._current_suffix = r.suffix
        return self

    def order(self, *args: str) -> Self:
        return self.sortkeys(args or None)

    def read(self,
             file: PathLike = '-',
             decoder: EncoderArg = None,
             factory: FactoryArg = None) -> Self:
        with open_input(file, sys.stdin) as f:
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

    def rename(self,
               encoder: EncoderArg = None,
               mode: ModeArg = None,
               *,
               mkdir: bool = True,
               dedup: bool = False,
               dryrun: bool = False) -> Self:
        if self._original_path == Path():
            message = 'no file to rename'
            raise Error(message)
        modified_path = self.filename(encoder, self.mode.get(mode))
        logging.info('rename: %s', self._original_path)
        logging.info('    to: %s', modified_path)
        if dryrun:
            return self
        if modified_path.exists():
            if modified_path.samefile(self._original_path):
                logging.info('same file')
                return self
            if dedup and filecmp.cmp(
                    self._original_path, modified_path, shallow=False):
                logging.info('removing duplicate')
                self._original_path.unlink()
                return self
            raise FileExistsError(modified_path)
        if mkdir and not modified_path.parent.exists():
            modified_path.parent.mkdir(parents=True)
        self._original_path.rename(modified_path)
        self.set_path(modified_path)
        return self

    def reset(self,
              k: str,
              v: VljuArg = None,
              factory: FactoryArg = None) -> Self:
        del self[k]
        return self.add(k, v, factory)

    def sort(self, *args: str, mode: ModeArg = None) -> Self:
        return self.sortvalues(args or None,
                               lambda v: v.get(self.mode.get(mode)))

    def with_dir(self, s: str | Path) -> Self:
        self._current_dir = Path(s)
        return self

    def with_suffix(self, suffix: str) -> Self:
        if not suffix.startswith('.'):
            suffix = '.' + suffix
        self._current_suffix = suffix
        return self

    def write(self,
              file: PathLike = '-',
              encoder: EncoderArg = None,
              mode: ModeArg = None) -> Self:
        with open_output(file, sys.stdout) as f:
            f.write(self.encoder.get(encoder).encode(self, self.mode.get(mode)))
        return self

    def z(self, file: TextIO = sys.stderr) -> Self:  # pragma: no coverage
        print(repr(self), file=file)
        return self

    # String reductions.

    def __str__(self) -> str:
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

    def original(self) -> Path:
        return self._original_path

    def filename(self,
                 encoder: EncoderArg = None,
                 mode: ModeArg = None) -> Path:
        e = self.encode(encoder, self.mode.get(mode))
        if not e:
            message = 'no file name'
            raise Error(message)
        e += self._current_suffix
        return self._current_dir / e

    # Vlju reduction.

    def first(self, k: str | type[Vlju]) -> Vlju:
        if isinstance(k, str):
            if k in self:
                return self[k][0]
        else:
            for _, v in self.pairs():
                if isinstance(v, k):
                    return v
        return Vlju('')

    # Helpers.

    def set_path(self, s: str | Path) -> Self:
        if isinstance(s, str):
            s = Path(s)
        self._original_path = s
        self._current_dir = s.parent
        self._current_suffix = s.suffix
        return self

    def _url(self, cls: type) -> Self:
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
            for k, s in strings:
                if '/' not in s or scheme_slashes_re.fullmatch(s):
                    t = s
                else:
                    t = 'http://' + s
                u = cls(t)
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
        return f'{type(self).__name__}({dict(self.data)!r})'

    @classmethod
    def configure_options(cls, options: Mapping[str, Any]) -> None:
        for r in cls.default_registry:
            if (v := options.get(r)) is not None:
                cls.default_registry[r].set_default(v)
