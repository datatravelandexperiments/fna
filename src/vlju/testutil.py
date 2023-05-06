# SPDX-License-Identifier: MIT

class CastParams:

    def __init__(self, s, d):
        self.s = s
        self.d = d

    def cast_params(self, _):
        return (self.s, self.d)
