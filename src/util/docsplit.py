# SPDX-License-Identifier: MIT
"""Split a docstring."""

import textwrap

def docsplit(s: str) -> tuple[list[str], dict[str, str]]:
    """Split off keyword sections.

    Puts paragraphs that begin with a word followed by `:` into the dictionary
    result, and others into the list result.
    """
    r = []
    d = {}
    for t in s.split('\n\n'):
        t = textwrap.dedent(t).strip()
        if ((n := t.find(':')) > 0) and t[: n].isalpha():
            k, v = t.split(':', 1)
            d[k.lower()] = v.strip()
            continue
        t = t.strip()
        if t:
            r.append(t)
    return (r, d)
