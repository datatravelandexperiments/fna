# SPDX-License-Identifier: MIT
"""Info - an entity in the ‘info’ URI scheme."""

from vlju.types.uri import URI, auth

class Info(URI):
    """Represents an entity in the ‘info’ URI scheme.

    short:  uri
    long:   uri
    """

    def __init__(self, s: str, **kwargs):
        super().__init__(
            s,
            scheme='info',
            authority=auth(kwargs.get('authority')),
            sa=':',
            ap='/')

    def __str__(self) -> str:
        return f'{self.sauthority()}/{self._value}'

    def sauthority(self) -> str:
        a = self.authority()
        return str(a.host) if a else ''

    def cast_params(self, t) -> tuple[str, dict]:
        if t is URI:
            return (self._value, {
                'scheme': self._scheme,
                'authority': self._authority,
                'sa': ':',
            })
        raise self.cast_param_error(t)
