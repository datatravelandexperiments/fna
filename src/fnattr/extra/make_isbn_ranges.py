# SPDX-License-Identifier: MIT
"""Generate isbn_ranges.py."""

# ruff: noqa: S101

import argparse
import array
import datetime
import logging
import pathlib
import pprint
import sys
import xml.etree.ElementTree as ElT

from collections.abc import MutableSequence
from pathlib import Path
from typing import TextIO

from fnattr.vlju.types.ean.isbn import RangeAgencies, Ranges

class RangesFromXml(Ranges):
    """Load ranges from an XML file."""

    def __init__(self, xmlfile: Path) -> None:
        """Load ISBN ranges from a file."""
        root = ElT.parse(xmlfile).getroot()
        assert root.tag == 'ISBNRangeMessage'

        starts: list[int] = []
        lengths: list[int] = []
        self.agencies: RangeAgencies = {}
        for rg in root.iter('RegistrationGroups'):
            for g in rg.iter('Group'):
                self._load_group(g, starts, lengths, self.agencies)
        super().__init__(array.array('Q', starts), array.array('I', lengths))

    def _load_group(self,
                    g: ElT.Element,
                    starts: MutableSequence[int],
                    lengths: MutableSequence[int],
                    agencies: RangeAgencies) -> None:
        s_prefix = g.findtext('Prefix')
        assert s_prefix is not None
        s_compact_prefix = s_prefix.replace('-', '')
        ts_prefix: tuple[str, ...] = tuple(s_prefix.split('-'))
        agency = g.findtext('Agency')
        if agency:
            agencies[ts_prefix] = agency
        ti_prefix_length: tuple[int, ...] = tuple(map(len, ts_prefix))
        remaining = 12 - sum(ti_prefix_length)
        logging.debug('prefix %s %s + %d',
                      s_prefix,
                      ti_prefix_length,
                      remaining)

        for r in g.iter('Rule'):
            s_range = r.findtext('Range')
            assert s_range is not None
            s_length = r.findtext('Length')
            assert s_length is not None
            length = int(s_length)

            s_first, s_last = s_range.split('-')
            pad = '0' * (remaining - len(s_first))
            s_first = (s_first + pad)[: remaining]
            s_last = (s_last + pad)[: remaining]

            if length:
                ti_lengths = (*ti_prefix_length, length, remaining - length, 1)
            else:
                ti_lengths = (*ti_prefix_length, remaining, 1)
            assert sum(ti_lengths) == 13
            s_lengths = ''.join(map(str, ti_lengths))
            # Assert that each segment length is at most 9.
            assert len(s_lengths) == len(ti_lengths)
            i_lengths = int(s_lengths[1 :])

            s_compact_first = s_compact_prefix + s_first + '0'
            s_compact_last = s_compact_prefix + s_last + '9'

            i_first = int(s_compact_first)
            i_last = int(s_compact_last)

            logging.debug('B %d to %d : %s to %s : %s %d',
                          i_first,
                          i_last,
                          '-'.join(self._isplit(s_compact_first, i_lengths)),
                          '-'.join(self._isplit(s_compact_last, i_lengths)),
                          ti_lengths,
                          i_lengths)

            starts.append(i_first)
            lengths.append(i_lengths)

    def write(self, f: TextIO) -> None:
        f.write('\nAGENCY = ')
        pprint.pprint(self.agencies, stream=f)
        f.write(f'\nSTART = {self._start!r}\n')
        f.write(f'\nSPLIT = {self._split!r}\n')

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv
    cmd = pathlib.Path(argv[0]).stem
    parser = argparse.ArgumentParser(
        prog=cmd, description='Generate ISBN ranges')
    parser.add_argument(
        '--input',
        '-i',
        metavar='FILE',
        default='third_party/data/RangeMessage.xml',
        help='Input file.')
    parser.add_argument(
        '--output',
        '-o',
        metavar='FILE',
        default='src/vlju/types/ean/isbn_ranges.py',
        help='Output file.')
    args = parser.parse_args(argv[1 :])

    ranges = RangesFromXml(args.input)
    with pathlib.Path(args.output).open('w', encoding='utf-8') as f:
        f.write('"""Generated ISBN range data."""\n\n')
        f.write('# DO NOT EDIT!\n')
        f.write(f'# Generated from {args.input}\n')
        f.write(
            f'# at {datetime.datetime.now(tz=datetime.UTC).isoformat()}\n\n')
        f.write('from array import array\n')
        ranges.write(f)

    return 0

if __name__ == '__main__':
    sys.exit(main())
