# SPDX-License-Identifier: MIT
"""Checksums"""

def alt13_checksum(s: str) -> int:
    """Calculate an EAN checksum."""
    r = -10
    multiplier = 1
    for c in s:
        r += multiplier * int(c)
        multiplier = 4 - multiplier
    return (10 - r % 10) % 10

def alt13_checksum_to_check_digit(n: int) -> str:
    return str(n)

def alt13(s: str) -> str:
    return alt13_checksum_to_check_digit(alt13_checksum(s))

def mod11_checksum(s: str) -> int:
    """Calculate an ISBN-10 checksum."""
    r = 0
    for n in range(1, 1 + len(s)):
        r += (n + 1) * int(s[-n])
    r = 11 - r % 11
    return r

def mod11_checksum_to_check_digit(n: int) -> str:
    return '0123456789X'[n]

def mod11(s: str) -> str:
    return mod11_checksum_to_check_digit(mod11_checksum(s))
