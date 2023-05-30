# SPDX-License-Identifier: MIT
"""URL - Vlju representable as a URL."""

from fnattr.vlju.types.uri import URI

class URL(URI):
    """Represents a URL."""

    def cast_params(self, t: object) -> tuple[str, dict]:
        if t is URL:
            return (self._value,
                    {
                        'scheme': self._scheme,
                        'authority': self._authority,
                        'query': self._query,
                        'fragment': self._fragment,
                        'urnq': self._urnq,
                        'urnr': self._urnr,
                        'sa': self._sa,
                        'ap': self._ap,
                    })
        return super().cast_params(t)

    def url(self) -> str:
        return self.lv()
