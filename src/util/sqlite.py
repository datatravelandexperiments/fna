# SPDX-License-Identifier: MIT
"""Wrapper including context manager for sqlite3"""

import os
import sqlite3

from collections.abc import Iterable
from types import TracebackType
from typing import Self

Connection = sqlite3.Connection
Cursor = sqlite3.Cursor
PathLike = os.PathLike | str

SQLITE3_OPEN_QUERY_KEYS = {
    'cache', 'immutable', 'mode', 'modeof', 'nolock', 'psow', 'vgs'
}

class SQLite:
    """Wrapper including context manager for sqlite3"""

    # These are intended for subclasses to provide initialization for all
    # instances of the subclasses. The model is that a subclass defines a
    # database including a schema definition as its `on_create`.
    on_open: Iterable[str] | None = None
    on_create: Iterable[str] | None = None

    def __init__(self, filename: PathLike = '', mode: str = '', **kwargs):
        if not mode:
            mode = 'ro' if filename else 'rw'
        self._filename: PathLike = filename
        self._kwargs = kwargs
        self._kwargs['mode'] = mode
        self._connection: Connection | None = None

    def __enter__(self) -> Self:
        return self.open()

    def open(self) -> Self:
        """Open and initialize the database connection."""
        if not self._connection:
            created = self._open()
            assert self._connection
            if self.on_open:
                for i in self.on_open:
                    self._connection.execute(i)
            if created and self.on_create:
                for i in self.on_create:
                    self._connection.execute(i)
        return self

    def _open(self) -> bool:
        if self._filename == '' or self._kwargs['mode'] == 'memory':
            # Temporary files are always created.
            create = True
        elif self._kwargs['mode'] == 'rwc':
            # Try first with 'rw', to see whether it needs to be created.
            self._kwargs['mode'] = 'rw'
            try:
                self._connection = sqlite3.connect(self._uri(), uri=True)
                return False
            except sqlite3.OperationalError:
                pass
            self._kwargs['mode'] = 'rwc'
            create = True
        else:
            create = False
        self._connection = sqlite3.connect(self._uri(), uri=True)
        return create

    def _uri(self) -> str:
        q = '&'.join(
            (f'{k}={str(self._kwargs[k])}' for k in self._kwargs.keys()
             & SQLITE3_OPEN_QUERY_KEYS))
        uri = f'file:{str(self._filename)}?{q}'
        return uri

    def __exit__(self, et: type[BaseException], ev: BaseException,
                 traceback: TracebackType) -> None:
        self.close()

    def close(self) -> Self:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        return self

    def connection(self) -> Connection:
        assert self._connection
        return self._connection

    def commit(self) -> Self:
        self.connection().commit()
        return self

    def execute(self, query: str, *args, **kwargs) -> Cursor:
        assert not (args and kwargs)
        if args:
            return self.connection().execute(query, args)
        if kwargs:
            return self.connection().execute(query, kwargs)
        return self.connection().execute(query)

    def store(self,
              table: str,
              on_conflict: str | None = None,
              **kwargs) -> Self:
        q = (f'INSERT INTO {table} ({",".join(kwargs.keys())})'
             f' VALUES ({",".join(f":{k}" for k in kwargs)})')
        if on_conflict:
            q += ' ON CONFLICT ' + on_conflict
        self.connection().execute(q, kwargs)
        return self

    def load(self,
             table: str,
             columns: Iterable[str] | None = None,
             **kwargs) -> Cursor:
        cols = ','.join((f'"{c}"' for c in columns)) if columns else '*'
        q = f'SELECT {cols} FROM {table}'
        if kwargs:
            q += ' WHERE ' + ' AND '.join((f'{k}=:{k}' for k in kwargs))
            return self.connection().execute(q, kwargs)
        return self.connection().execute(q)
