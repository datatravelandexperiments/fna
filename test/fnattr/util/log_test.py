# SPDX-License-Identifier: MIT
"""Test logging utilities."""

import dataclasses
import logging
import pytest

from fnattr.util import log, pytestutil

def test_choices():
    choices = frozenset(('critical', 'error', 'warning', 'info', 'debug'))
    s = frozenset(log.CHOICES) & choices
    assert s == choices

# fmt: off
LEVEL_CASES = [
    {'name': 'critical',    'level': logging.CRITICAL},
    {'name': 'error',       'level': logging.ERROR},
    {'name': 'warning',     'level': logging.WARNING},
    {'name': 'info',        'level': logging.INFO},
    {'name': 'debug',       'level': logging.DEBUG},
]
# fmt: on

@pytest.mark.parametrize(*pytestutil.im2p(LEVEL_CASES))
def test_level_name(level, name):
    assert log.level_name(level) == name

@dataclasses.dataclass
class Args:
    log_level: str | int
    dryrun: bool

@pytest.mark.parametrize(*pytestutil.im2p(LEVEL_CASES))
def test_config_str(level, name, monkeypatch):
    cmd = 'testccommand'
    fake_basic_config, report = pytestutil.make_fixed()
    monkeypatch.setattr(logging, 'basicConfig', fake_basic_config)
    args = Args(name, dryrun=False)
    r = log.config(cmd, args)
    assert r == level
    assert report[0].kwargs['level'] == level
    assert report[0].kwargs['format'].startswith(f'{cmd}: ')

@pytest.mark.parametrize(*pytestutil.im2p(LEVEL_CASES, ['level']))
def test_config_int(level, monkeypatch):
    cmd = 'testccommand'
    fake_basic_config, report = pytestutil.make_fixed()
    monkeypatch.setattr(logging, 'basicConfig', fake_basic_config)
    args = Args(level, dryrun=False)
    r = log.config(cmd, args)
    assert r == level
    assert report[0].kwargs['level'] == level
    assert report[0].kwargs['format'].startswith(f'{cmd}: ')

@pytest.mark.parametrize(*pytestutil.im2p(LEVEL_CASES))
def test_config_dryrun(level, name, monkeypatch):
    expect_level = min(level, logging.INFO)
    cmd = 'testccommand'
    fake_basic_config, report = pytestutil.make_fixed()
    monkeypatch.setattr(logging, 'basicConfig', fake_basic_config)
    args = Args(name, dryrun=True)
    r = log.config(cmd, args)
    assert r == expect_level
    assert report[0].kwargs['level'] == expect_level
