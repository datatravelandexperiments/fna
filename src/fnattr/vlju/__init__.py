# SPDX-License-Identifier: MIT
"""Vlju - top-level of the Vlju hierarchy."""

from fnattr.util.repr import mkrepr

class Vlju:
    """
    Vlju - Top level of the Vlju hierarchy.

    A Vlju is at minimum representable as a string.
    Subclasses may have additional structure.

    Subclasses constructors must take a single positional argument
    and accept at least a string. The canonical (short) representation
    produced by `__str__()` _must_ be accepted; the long representation
    produced by `lv()` _should_ be accepted.

    short:  value
    long:   value
    where:
        value → `_value`
    """

    def __init__(self, s: str) -> None:
        if not isinstance(s, str):
            raise TypeError(s)
        self._value = s

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vlju):
            return self._value == other._value  # noqa: SLF001
        return False

    def __repr__(self) -> str:
        return mkrepr(self, ['_value'])

    def __str__(self) -> str:
        """Return the canonical (short) value."""
        return self._value

    def lv(self) -> str:
        """Return the long value."""
        return self._value

    def get(self,
            key: str | None = None,
            default: str | None = None) -> str | None:
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key: str | None) -> str:
        match key:
            case None | 'default' | 'short' | 'str':
                return str(self)
            case 'long' | 'alternate':
                return self.lv()
            case 'repr':
                return repr(self)
        raise KeyError(key)

    def cast_param_error(self, t: object) -> TypeError:
        return TypeError((self, t))
