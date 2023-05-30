# SPDX-License-Identifier: MIT
"""Helper for testing construction using cast_params()."""

from typing import Any

class CastParams:
    """Helper for testing construction using cast_params()."""

    def __init__(self, s: str | None, d: dict[str, Any]) -> None:
        self.s = s
        self.d = d

    def cast_params(self, _) -> tuple[str | None, dict[str, Any]]:
        return (self.s, self.d)
