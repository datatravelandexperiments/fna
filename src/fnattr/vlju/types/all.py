# SPDX-License-Identifier: MIT
"""Known Vlju subtypes."""

from fnattr.vlju import Vlju
from fnattr.vlju.types.doi import DOI
from fnattr.vlju.types.ean import EAN13
from fnattr.vlju.types.ean.isbn import ISBN
from fnattr.vlju.types.ean.ismn import ISMN
from fnattr.vlju.types.ean.issn import ISSN
from fnattr.vlju.types.file import File
from fnattr.vlju.types.info import Info
from fnattr.vlju.types.lccn import LCCN
from fnattr.vlju.types.timestamp import Timestamp
from fnattr.vlju.types.uri import URI
from fnattr.vlju.types.url import URL
from fnattr.vlju.types.urn import URN

# yapf: disable
VLJU_TYPES: dict[str, type[Vlju]] = {
    'doi':      DOI,
    'ean':      EAN13,
    'file':     File,
    'info':     Info,
    'isbn':     ISBN,
    'ismn':     ISMN,
    'issn':     ISSN,
    'lccn':     LCCN,
    't':        Timestamp,
    'uri':      URI,
    'url':      URL,
    'urn':      URN,
}
# yapf: enable
