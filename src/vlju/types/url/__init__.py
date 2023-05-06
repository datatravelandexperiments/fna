# SPDX-License-Identifier: MIT

from vlju.types.uri import URI

class URL(URI):

    def cast_params(self, t) -> tuple[str, dict]:
        if t is URL:
            return (self._value, {
                'scheme': self._scheme,
                'authority': self._authority,
                'query': self._query,
                'fragment': self._fragment,
                'urnq': self._urnq,
                'urnr': self._urnr,
                'sa': self._sa,
                'ap': self._ap
            })
        return super().cast_params(t)

    def url(self) -> str:
        return self.lv()
