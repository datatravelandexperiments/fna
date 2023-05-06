# SPDX-License-Identifier: MIT
"""Known Vlju subtypes."""

from typing import Type

from vlju import Vlju
from vlju.types.doi import DOI
from vlju.types.ean import EAN13
from vlju.types.ean.isbn import ISBN
from vlju.types.ean.ismn import ISMN
from vlju.types.ean.issn import ISSN
from vlju.types.file import File
from vlju.types.info import Info
from vlju.types.lccn import LCCN
from vlju.types.uri import URI
from vlju.types.url import URL
from vlju.types.urn import URN

# yapf: disable
VLJU_TYPES: dict[str, Type[Vlju]] = {
    'doi':      DOI,
    'ean':      EAN13,
    'file':     File,
    'info':     Info,
    'isbn':     ISBN,
    'ismn':     ISMN,
    'issn':     ISSN,
    'lccn':     LCCN,
    'uri':      URI,
    'url':      URL,
    'urn':      URN,
}
# yapf: enable
