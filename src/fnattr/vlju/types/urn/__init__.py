# SPDX-License-Identifier: MIT
"""URN - Vlju representable as a URN."""

from fnattr.util.repr import mkrepr
from fnattr.vlju.types.uri import URI, Authority

class URN(URI):
    """
    Represents a URN.

    short:  uri
    long:   uri
    """

    def __init__(self,
                 s: str,
                 authority: Authority | str | None = None,
                 q: str | None = None,
                 r: str | None = None) -> None:
        super().__init__(
            s,
            scheme='urn',
            authority=authority,
            urnq=q,
            urnr=r,
            sa=':',
            ap=':')

    # URI overrides:

    def sauthority(self) -> str:
        a = self.authority()
        return str(a.host) if a else ''

    # Vlju overrides:

    def __eq__(self, other: object) -> bool:
        if isinstance(other, URN):
            return (self._value == other._value                 # noqa: SLF001
                    and self._scheme == other._scheme           # noqa: SLF001
                    and self._authority == other._authority     # noqa: SLF001
                    and self._urnq == other._urnq               # noqa: SLF001
                    and self._urnr == other._urnr)              # noqa: SLF001
        return False

    def __repr__(self) -> str:
        return mkrepr(self, ['_value'], ['_authority', '_urnq', '_urnr'])
