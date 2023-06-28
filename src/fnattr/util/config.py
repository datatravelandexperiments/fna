# SPDX-License-Identifier: MIT
"""Configuration-file related utilities."""

import argparse
import contextlib
import logging
import os
import tomllib

from collections.abc import Generator, Iterable, Mapping
from pathlib import Path
from typing import Any, Self

from fnattr.util import nested

class Dirs(list[Path]):
    """Maintain a list of directories."""

    def add_env_dir(self, evar: str, default: Path | None = None) -> Self:
        """
        Add an environment-variable-based or default directory.

        Based on XDG conventions. If the environment variable named `evar`
        exists and contains a directory path, add it; otherwise, if the
        `default` exists, add that.
        """
        if evar in os.environ:
            p = Path(os.environ[evar])
            if p.is_dir():
                self.append(p)
        elif default and default.is_dir():
            self.append(default)
        return self

    def add_env_dirs(self, env: str, default: list[Path]) -> Self:
        """
        Add a list of environment-variable-based or default directories.

        Based on XDG conventions. If the environment variable named `evar`
        exists, treat it as a `:`-separated path and add any existing absolute
        directory. Otherwise, add any existing directory in `default`.
        """
        if env in os.environ:
            for d in os.environ[env].split(':'):
                p = Path(d)
                if p.is_dir() and p.is_absolute():
                    self.append(p)
        else:
            for p in default:
                if p.is_dir():
                    self.append(p)
        return self

    def add_xdg_dirs(self,
                     name: str,
                     default_dir: str,
                     default_paths: list[Path],
                     home: Path | None = None) -> Self:
        """Obtain a list of XDG directories of the given kind."""
        if home is None:
            with contextlib.suppress(RuntimeError):
                home = Path.home()
        default_path = None if home is None else home / default_dir
        self.add_env_dir(f'XDG_{name}_HOME', default_path)
        self.add_env_dirs(f'XDG_{name}_DIRS', default_paths)
        return self

def xdg_config_dirs() -> Dirs:
    return Dirs().add_xdg_dirs('CONFIG', '.config', [Path('/etc/xdg')])

def find_file_in_dirs(file: Path | str,
                      dirs: Iterable[Path]) -> Generator[Path, None, None]:
    for i in dirs:
        d = i / file
        exists = d.exists()
        logging.debug('%s config: %s', 'found' if exists else 'tried', d)
        if exists:
            yield d

def read_toml_config(file: Path | str) -> dict | None:
    logging.debug('using config: %s', file)
    with Path(file).open('rb') as f:
        try:
            return tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            logging.error('%s: %s', file, str(e))
            return None

def read_configs(args: Iterable[Path | str]) -> dict:
    config: dict[str, Any] = {}
    for p in args:
        if c := read_toml_config(p):
            nested.nupdate(config, c)
    return config

def cmd_config_files(cmds: str | Iterable[str]) -> list[Path]:
    files = []
    dirs = xdg_config_dirs()
    names = ['vlju', cmds] if isinstance(cmds, str) else ['vlju', *cmds]
    for name in names:
        for file in find_file_in_dirs(Path(f'fnattr/{name}.toml'), dirs):
            files.append(file)
    return files

def merge_options(options: dict[str, Any] | None, args: argparse.Namespace,
                  **kwargs) -> dict[str, Any]:
    if options is None:
        options = {}
    for k, d in kwargs.items():
        option = d.get('option', k) if isinstance(d, Mapping) else k
        default = d.get('default') if isinstance(d, Mapping) else d
        if (a := getattr(args, k)) is not None:
            nested.dset(options, option, a)
        elif k not in options and default is not None:
            nested.dset(options, option, default)
    return options

def read_cmd_configs_and_merge_options(cmds: str | Iterable[str],
                                       config_files: Iterable[Path | str],
                                       args: argparse.Namespace,
                                       **kwargs) -> tuple[dict, dict]:
    config = read_configs(cmd_config_files(cmds) + list(config_files or []))
    options = merge_options(config.get('option'), args, **kwargs)
    return config, options
