# SPDX-License-Identifier: MIT
"""Timestamp."""

from fnattr.util.duration import Duration
from fnattr.vlju import Vlju

class Timestamp(Vlju):
    """
    Represents a timestamp.

    short:  [[[[[[_d_`:`]_h_]_h_`:`]_m_]_m_`:`]_s_]_s_[`.`_f_...]
    long:   [[[[[[_d_`d`]_h_]_h_`h`]_m_]_m_`m`]_s_]_s_[`.`_f_...]
    """

    def __init__(self, s: object) -> None:
        if isinstance(s, str):
            self._duration = Duration.parse(s)
        elif isinstance(s, Duration):
            self._duration = s
        elif hasattr(s, 'cast_params'):
            v, d = s.cast_params(type(self))
            self._duration = Duration.parse(v) if v else Duration(**d)
        else:
            raise TypeError(s)
        super().__init__(str(self._duration))

    def lv(self) -> str:
        return self._duration.fmt()

    def duration(self) -> Duration:
        return self._duration
