# SPDX-License-Identifier: MIT
"""Wrapper including context manager for sqlite3."""

import os
import sqlite3

from collections.abc import Iterable
from types import TracebackType
from typing import Any, Self

Connection = sqlite3.Connection
Cursor = sqlite3.Cursor
PathLike = os.PathLike | str

SQLITE3_OPEN_QUERY_KEYS = {
    'cache',
    'immutable',
    'mode',
    'modeof',
    'nolock',
    'psow',
    'vgs',
}

class SQLite:
    """Wrapper including context manager for sqlite3."""

    # These are intended for subclasses to provide initialization for all
    # instances of the subclasses. The model is that a subclass defines a
    # database including a schema definition as its `on_create`.
    on_create: Iterable[str] | None = None
    on_connect: Iterable[str] | None = None
    foreign_keys: bool | None = True

    def __init__(self,
                 filename: PathLike = '',
                 mode: str = '',
                 **kwargs) -> None:
        if not mode:
            mode = 'ro' if filename else 'rw'
        self._filename: PathLike = filename
        self._kwargs = kwargs
        self._kwargs['mode'] = mode
        self._connection: Connection | None = None
        self._table_columns: dict[str, list[str] | None] = {}

    def __enter__(self) -> Self:
        return self.connect()

    def connect(self) -> Self:
        """Open and initialize the database connection."""
        if not self._connection:
            self._connection, created = self._open()
            if self.foreign_keys is not None:
                self._connection.execute(
                    f'PRAGMA foreign_keys = {int(self.foreign_keys)};')
            if self.on_connect:
                for i in self.on_connect:
                    self._connection.execute(i)
            if created and self.on_create:
                for i in self.on_create:
                    self._connection.execute(i)
        return self

    def _open(self) -> tuple[Connection, bool]:
        if not self._filename or self._kwargs['mode'] == 'memory':
            # Temporary files are always created.
            created = True
        elif self._kwargs['mode'] == 'rwc':
            # Try first with 'rw', to see whether it needs to be created.
            self._kwargs['mode'] = 'rw'
            try:
                con = sqlite3.connect(self._uri(), uri=True)
            except sqlite3.OperationalError:
                pass
            else:
                return con, False
            self._kwargs['mode'] = 'rwc'
            created = True
        else:
            created = False
        return sqlite3.connect(self._uri(), uri=True), created

    def _uri(self) -> str:
        q = '&'.join(f'{k}={self._kwargs[k]!s}' for k in self._kwargs.keys()
                     & SQLITE3_OPEN_QUERY_KEYS)
        return f'file:{self._filename!s}?{q}'

    def __exit__(self,
                 et: type[BaseException],
                 ev: BaseException,
                 traceback: TracebackType) -> None:
        self.close()

    def close(self) -> Self:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
        self.clear_table_column_cache()
        return self

    def connection(self) -> Connection:
        if not self._connection:
            raise sqlite3.OperationalError
        return self._connection

    def commit(self) -> Self:
        self.connection().commit()
        return self

    def execute(self, query: str, *args, **kwargs) -> Cursor:
        if args and kwargs:
            message = 'cannot use both positional and keyword arguments'
            raise ValueError(message)
        if args:
            return self.connection().execute(query, args)
        if kwargs:
            return self.connection().execute(query, kwargs)
        return self.connection().execute(query)

    def store(self,
              table: str,
              on_conflict: str | None = None,
              **kwargs) -> Self:
        """
        Insert into a table.

        `kwargs` consists of column-value pairs.

        This is intended as a shorthand to be used with hard-coded keys,
        for example:

            db.store(users', user=u, password=p)

        However, due to splatting, it is possible that this function could
        be (mis)used with untrusted arguments. Therefore, we take precautions
        against injection, since table and column names must be part of the
        query string:

        - Verify that the supplied table and column names are actually
          existing table and column names in the database.
        - Quote table and column names.
        - Use generated parameter names.
        """
        columns = kwargs.keys()
        self.check_table_columns(table, kwargs.keys())
        p = BoundParameters(kwargs)
        q = (
            f'INSERT INTO {quote_id(table)}'                # noqa: S608
            f' ({",".join(quote_id(c) for c in columns)})'
            f' VALUES ({",".join(f":{k}" for k in p.value)})')
        if on_conflict:
            q += ' ON CONFLICT ' + on_conflict
        self.connection().execute(q, p.value)
        return self

    def load(self, table: str, *args: str, **kwargs) -> Cursor:
        """
        Read from a table.

        `args` consists of column names to be returned.

        `kwargs` consists of column-value pairs that become `WHERE`
        conditions on the select.

        Although this is not intended to handle untrusted arguments,
        we take precautions against injection, since table and column
        names must be part of the query string:

        - Verify that the supplied table and column names are actually
          existing table and column names in the database.
        - Quote table and column names.
        - Use generated parameter names.
        """
        check_columns = set(kwargs.keys())
        if args:
            check_columns |= set(args)
            cols = ','.join(quote_id(c) for c in args)
        else:
            cols = '*'
        self.check_table_columns(table, check_columns)
        q = f'SELECT {cols} FROM {quote_id(table)}'     # noqa: S608
        if not kwargs:
            return self.connection().execute(q)
        p = BoundParameters(kwargs)
        q += ' WHERE ' + ' AND '.join(f'{p.column[k]} = :{k}' for k in p.value)
        return self.connection().execute(q, p.value)

    def check_table_columns(self, table: str, columns: Iterable[str]) -> None:
        """Check that the columns exist in the table."""
        if not self._table_columns:
            self._init_table_column_cache()
        if table not in self._table_columns:
            message = f'table {table!r} does not exist'
            raise sqlite3.ProgrammingError(message)
        if (table_columns := self._table_columns[table]) is None:
            table_columns = self._load_table_column_cache(table)
        for c in columns:
            if c not in table_columns:
                message = f'column {c!r} does not exist in {table!r}'
                raise sqlite3.ProgrammingError(message)

    def _init_table_column_cache(self) -> None:
        c = self.connection().execute(
            'SELECT name FROM sqlite_master WHERE type == "table"')
        c.row_factory = None
        while (row := c.fetchone()):
            table = row[0]
            self._table_columns[table] = None

    def _load_table_column_cache(self, table: str) -> list[str]:
        r = []
        c = self.connection().execute(f'PRAGMA TABLE_INFO({quote_id(table)})')
        c.row_factory = None
        while (row := c.fetchone()):
            column = row[1]
            r.append(column)
        self._table_columns[table] = r
        return r

    def clear_table_column_cache(self) -> None:
        self._table_columns = {}

def quote_id(s: str) -> str:
    return '"' + s.replace('"', '""') + '"'

class BoundParameters:
    """Sanitization of bound parameters."""

    column: dict[str, str]  # Map from parameter name to quoted column name.
    value: dict[str, Any]   # Map from parameter name to value.

    def __init__(self, column_value: dict[str, Any]) -> None:
        self.column = {}
        self.value = {}
        for i, k in enumerate(column_value):
            p = f'p{i}'
            self.column[p] = quote_id(k)
            self.value[p] = column_value[k]
