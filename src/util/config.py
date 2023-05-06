# SPDX-License-Identifier: MIT
"""Configuration-file related utilities."""

import os
import tomllib

from collections.abc import Iterable
from pathlib import Path
from typing import Any, Self

class Dirs(list[Path]):
    """Maintain a list of directories."""

    def add_env_dir(self, evar: str, default: Path | None = None) -> Self:
        """Add an environment-variable-based or default directory.

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
        """Add a list of environment-variable-based or default directories.

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
        try:
            home = Path.home()
        except RuntimeError:
            pass
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
    with open(file, 'rb') as f:
        try:
            return tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            print(f'{file}: {e}')
            return None

def read_configs(args: Iterable[Path | str]) -> dict:
    config: dict[str, Any] = {}
    for p in args:
        if c := read_toml_config(p):
            nested_update(config, c)
    return config

def read_xdg_configs(files: Iterable[Path]) -> dict:
    config: dict[str, Any] = {}
    for file in files:
        if (cf := xdg_config(file)) and (c := read_toml_config(cf)):
            nested_update(config, c)
    return config

def read_cmd_configs(cmd: str, args: Iterable[Path | str]) -> dict:
    if args:
        return read_configs(args)
    return read_xdg_configs([
        Path('vlju/config.toml'),
        Path(f'{cmd}/config.toml'),
    ])

def nested_update(dst: dict, src: dict):
    for k, v in src.items():
        if k in dst and isinstance(dst[k], dict) and isinstance(v, dict):
            nested_update(dst[k], v)
        else:
            dst[k] = v
    return dst
