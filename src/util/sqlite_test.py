# SPDX-License-Identifier: MIT

import sqlite3

import pytest

from util.sqlite import SQLite

class ValueDatabase(SQLite):
    on_open = ['PRAGMA application_id = 0x12345679;']
    on_create = ['CREATE TABLE test (value INTEGER);']

class KeyValueDatabase(SQLite):
    on_create = ['CREATE TABLE test (key INTEGER, value INTEGER);']

def test_database():
    db = SQLite()
    db.open()
    db.execute('CREATE TABLE test (value INTEGER);')
    db.execute('INSERT INTO test VALUES (23);')
    cur = db.execute('SELECT * FROM test;')
    assert cur.fetchone() == (23, )
    assert cur.fetchone() is None
    db.close()

def test_database_read_only():
    with SQLite(mode='ro') as db:
        with pytest.raises(sqlite3.OperationalError):
            db.execute('CREATE TABLE test (value INTEGER);')

def test_database_with_on_open():
    with ValueDatabase() as db:
        cur = db.execute('PRAGMA application_id;')
        assert cur.fetchone() == (0x12345679, )

def test_database_with_on_create():
    with ValueDatabase() as db:
        cur = db.execute('SELECT COUNT(*) FROM test;')
        assert cur.fetchone() == (0, )

def test_database_idempotent_open():
    db = ValueDatabase()
    db.open()
    db.open()
    db.store('test', value=42)
    db.open()
    cur = db.execute('SELECT * FROM test;')
    assert cur.fetchone() == (42, )
    assert cur.fetchone() is None
    db.close()

def test_database_idempotent_close():
    db = ValueDatabase()
    db.close()
    db.open()
    db.store('test', value=42)
    cur = db.execute('SELECT * FROM test;')
    assert cur.fetchone() == (42, )
    assert cur.fetchone() is None
    db.close()
    db.close()

def test_database_file_create(tmp_path):
    filename = tmp_path / 'test.db'
    with ValueDatabase(filename, mode='rwc') as db:
        cur = db.execute('SELECT COUNT(*) FROM test;')
        assert cur.fetchone() == (0, )

def test_database_file_persists(tmp_path):
    filename = tmp_path / 'test.db'
    with KeyValueDatabase(filename, mode='rwc') as db:
        db.store('test', on_conflict='do nothing', key=1, value=23)
        db.commit()
    with KeyValueDatabase(filename, mode='rwc') as db:
        cur = db.load('test')
        assert cur.fetchone() == (1, 23)
        assert cur.fetchone() is None

def test_database_file_nonexistent(tmp_path):
    filename = tmp_path / 'test.db'
    db = ValueDatabase(filename)
    with pytest.raises(sqlite3.OperationalError):
        db.open()

def test_database_store():
    with ValueDatabase() as db:
        db.store('test', value=42)
        cur = db.execute('SELECT * FROM test;')
        assert cur.fetchone() == (42, )
        assert cur.fetchone() is None

def test_database_load():
    with KeyValueDatabase() as db:
        db.store('test', key=1, value=42).store('test', key=2, value=23)

        cur = db.load('test')
        t = cur.fetchone()
        assert t == (1, 42) or t == (2, 23)
        t = cur.fetchone()
        assert t == (1, 42) or t == (2, 23)
        assert cur.fetchone() is None

        cur = db.load('test', ['value'], key=1)
        assert cur.fetchone() == (42,)
        assert cur.fetchone() is None

def test_database_execute_unnamed_parameters():
    with KeyValueDatabase() as db:
        db.execute('INSERT INTO test VALUES (1, ?), (2, ?);', 23, 42)
        cur = db.execute('SELECT * FROM test WHERE key=?;', 2)
        assert cur.fetchone() == (2, 42)
        assert cur.fetchone() is None

def test_database_execute_named_parameters():
    with KeyValueDatabase() as db:
        db.execute('INSERT INTO test VALUES (1, :a), (2, :b);', b=42, a=23)
        cur = db.execute('SELECT * FROM test WHERE key=?;', 2)
        assert cur.fetchone() == (2, 42)
        assert cur.fetchone() is None

def test_database_commit():
    with ValueDatabase() as db:
        db.execute('BEGIN;')
        db.store('test', value=42)
        db.commit()
        cur = db.execute('SELECT * FROM test;')
        assert cur.fetchone() == (42, )
        assert cur.fetchone() is None
