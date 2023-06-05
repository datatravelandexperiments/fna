# SPDX-License-Identifier: MIT
"""Configuration-file related utilities."""

import argparse
import contextlib
import logging
import os
import tomllib

from collections.abc import Iterable, Mapping
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

    def find_first(self, p: Path | str) -> Path | None:
        """Return the first matching file in the directory list."""
        for i in self:
            d = i / p
            if d.exists():
                return d
        return None

def xdg_dirs(name: str,
             default_dir: str,
             default_paths: list[Path],
             home: Path | None = None) -> Dirs:
    """Obtain a list of XDG directories of the given kind."""
    if home is None:
        with contextlib.suppress(RuntimeError):
            home = Path.home()

    default_path = None if home is None else home / default_dir
    d = Dirs()
    d.add_env_dir(f'XDG_{name}_HOME', default_path)
    d.add_env_dirs(f'XDG_{name}_DIRS', default_paths)
    return d

def xdg_config_dirs() -> Dirs:
    return xdg_dirs('CONFIG', '.config', [Path('/etc/xdg')])

def xdg_config(filename: Path | str) -> Path | None:
    return xdg_config_dirs().find_first(filename)

def read_toml_config(file: Path | str) -> dict | None:
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

def read_xdg_configs(files: Iterable[Path]) -> dict:
    config: dict[str, Any] = {}
    for file in files:
        if (cf := xdg_config(file)) and (c := read_toml_config(cf)):
            nested.nupdate(config, c)
    return config

def read_cmd_configs(cmds: str | Iterable[str],
                     config_files: Iterable[Path | str]) -> dict:
    paths = []
    names = ['vlju', cmds] if isinstance(cmds, str) else ['vlju', *cmds]
    for i in names:
        paths.append(Path(f'{i}.toml'))
        paths.append(Path(f'fnattr/{i}.toml'))
    config = read_xdg_configs(paths)
    if config_files:
        nested.nupdate(config, read_configs(config_files))
    return config

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
    config = read_cmd_configs(cmds, config_files)
    options = merge_options(config.get('option'), args, **kwargs)
    return config, options
