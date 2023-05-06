# SPDX-License-Identifier: MIT
"""URN - Vlju representable as a URN"""

import util.escape
import util.repr

from vlju.types.uri import Authority, URI

class URN(URI):
    """Represents a URN.

    short:  uri
    long:   uri
    """

    def __init__(self,
                 s: str,
                 authority: Authority | str | None = None,
                 q: str | None = None,
                 r: str | None = None):
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

    def __eq__(self, other):
        try:
            return (self._value == other._value
                    and self._scheme == other._scheme
                    and self._authority == other._authority
                    and self._urnq == other._urnq and self._urnr == other._urnr)
        except AttributeError:
            return False

    def __repr__(self) -> str:
        return util.repr.mkrepr(self, ['_value'],
                                ['_authority', '_urnq', '_urnr'])
