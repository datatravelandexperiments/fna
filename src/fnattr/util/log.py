# SPDX-License-Identifier: MIT
"""Logging utilities."""

import logging

CHOICES = [c.lower() for c in logging.getLevelNamesMapping() if c != 'NOTSET']

def level_name(level: int) -> str:
    return logging.getLevelName(level).lower()

def config_level(cmd: str,
                 s: str | int,
                 *,
                 dryrun: bool = False,
                 dryrun_level: int = logging.INFO) -> int:
    log_level = getattr(logging, s.upper()) if isinstance(s, str) else s
    if dryrun and log_level > dryrun_level:
        log_level = dryrun_level
    logging.basicConfig(
        level=log_level, format=f'{cmd}: %(levelname)s: %(message)s')
    return log_level

def config(cmd: str, args: object) -> int:
    return config_level(
        cmd,
        getattr(args, 'log_level', logging.WARNING),
        dryrun=getattr(args, 'dryrun', False))
