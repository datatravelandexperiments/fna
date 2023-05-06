# SPDX-License-Identifier: MIT
"""Execute commands."""

import textwrap

from collections.abc import Callable, Iterable

from util.docsplit import docsplit
from util.error import Error
from util.registry import Registry
from vljum.m import M

class Runner:
    commands: dict[str, Callable] = {}

    def __init__(self, m: M | None = None):
        self.tokens: Iterable[str] | None = None
        self.m = M() if m is None else m
        self.report = False
        self.help: dict | None = None
        self.commands = {}
        for i in dir(type(self)):
            if i.startswith('command_'):
                m = getattr(type(self), i)
                if callable(m):  # pragma: no branch
                    self.commands[i[8 :]] = m
        self.commands |= {
            # Factories
            k: type(self).set_factory
            for k in self.m.factory.keys()
        } | {
            # Encoders/decoders.
            k: type(self).set_coder
            for k in self.m.encoder.keys()
        } | {
            # Modes.
            k: type(self).set_mode
            for k in self.m.mode.keys()
        }

    def token(self) -> str | None:
        if self.tokens:
            try:
                return next(self.tokens)
            except StopIteration:
                pass
        return None

    def need(self, message: str = 'expected token') -> str:
        t = self.token()
        if t is None:
            raise Error(message)
        return t

    def command_add(self, cmd: str):
        """Add an attribute.

        Constructs the value using the current active factory.

        Synopsis: add ‹key› ‹value›
        """
        key = self.need(f'{cmd}: expected key')
        val = self.need(f'{cmd}: expected value')
        self.m.add(key, val)
        self.report = True

    def command_decode(self, cmd: str):
        """Decode a string.

        Decodes using the current active decoder.

        Synopsis: decode ‹string›
        """
        self.m.decode(self.need(f'{cmd}: expected string'))
        self.report = True

    def command_decoder(self, cmd: str):
        """Set the current active decoder.

        Synopsis: decoder ‹decoder›
        """
        self.set_registry(self.m.decoder, cmd)

    def command_delete(self, cmd: str):
        """Delete all attributes for one or more ‹key›s.

        It is not an error for keys not to be present.
        The complement of `delete` is `extract`.

        Synopsis: delete ‹key›[,‹key›]*
        """
        for key in self.need(f'{cmd}: expected keys').split(','):
            self.m.remove(key)
        self.report = True

    def command_dir(self, cmd: str):
        self.m.dir(self.need(f'{cmd}: expected directory'))
        self.report = True

    def command_encode(self, cmd: str):
        """Encode and prints the current attributes.

        Encodes using the current active encoder.

        Synopsis: encode
        """
        print(self.m.encode())
        self.report = False

    def command_encoder(self, cmd: str):
        """Set the current active encoder.

        Synopsis: encoder ‹encoder›
        """
        self.set_registry(self.m.encoder, cmd)

    def command_extract(self, cmd: str):
        """Extract attributes for one or more keys.

        It is not an error for keys not to be present.
        The complement of `extract` is `delete`.

        Synopsis: extract ‹key›[,‹key›]*
        """
        self.m = self.m.submap(self.need(f'{cmd}: expected keys').split(','))
        self.report = True

    def command_factory(self, cmd: str):
        """Set the current active factory.

        Synopsis: factory ‹factory›
        """
        self.set_registry(self.m.factory, cmd)

    def command_file(self, cmd: str):
        """Decode a file name.

        Decodes using the current active decoder.

        Synopsis: file ‹filename›
        """
        self.m.file(self.need(f'{cmd}: expected filename'))
        self.report = True

    def command_filename(self, cmd: str):
        """Encode and print the current attributes as a file name.

        Encodes using the current active encoder.

        Synopsis: encode
        """
        print(self.m.filename())
        self.report = False

    def command_help(self, cmd: str):
        """Show information about a subcommand, or list subcommands.

        Synopsis: help [‹subcommand›]*
        """
        if self.help is None:  # pragma: no branch
            self.help = {}
            for k, c in self.commands.items():
                if c.__doc__:
                    self.help[k] = docsplit(c.__doc__)
        helped = 0
        while (name := self.token()) is not None:
            helped += 1
            if name not in self.help:
                print(f'No help available for {name}\n')
                helped = 0
                break
            desc, info = self.help[name]
            print(f'NAME\n  {name} - {desc[0]}\n')
            synopsis = info.get('synopsis')
            if synopsis:  # pragma: no branch
                print(f'SYNOPSIS\n  {synopsis}\n')
            description = '\n\n'.join(desc)
            if description:  # pragma: no branch
                print(f'DESCRIPTION\n{textwrap.indent(description, "  ")}\n')
        if helped == 0:
            print('COMMANDS')
            for name in sorted(self.help.keys()):
                print(f'  {name:8} - {self.help[name][0][0]}')

    def command_mode(self, cmd: str):
        """Set the current active mode.

        Synopsis: mode ‹mode›
        """
        self.set_registry(self.m.mode, cmd)

    def command_order(self, cmd: str):
        """Arranges keys.

        With `--all`, arranges the attribute keys in alphabetical order.

        With given ‹key›s, arranges the attribute set so that those keys appear
        in the specified order. Other keys will follow in their original order.

        Synopsis: order (--all | ‹key›[,‹key›]*)
        """
        t = self.need(f'{cmd}: expected keys')
        self.m = self.m.sortkeys(None if t == '--all' else t.split(','))
        self.report = True

    def command_quiet(self, cmd: str):
        self.report = False

    def command_remove(self, cmd: str):
        """Remove a specific attribute.

        Constructs the value using the current active factory.

        Synopsis: remove ‹key› ‹value›
        """
        key = self.need(f'{cmd}: expected key')
        val = self.need(f'{cmd}: expected value')
        self.m.remove(key, val)
        self.report = True

    def command_rename(self, cmd: str):
        self.m.rename()
        self.report = False

    def command_set(self, cmd: str):
        """Set an attribute.

        Replaces any existing attributes for the same ‹key›.
        Constructs the value using the current active factory.

        Synopsis: set ‹key› ‹value›
        """
        key = self.need(f'{cmd}: expected key')
        val = self.need(f'{cmd}: expected value')
        self.m.set(key, val)
        self.report = True

    def command_sort(self, cmd: str):
        """Sorts values for a given key or all keys.

        Synopsis: sort (--all | ‹key›[,‹key›]*)
        """
        t = self.need(f'{cmd}: expected keys or ‘--all’')
        if t == '--all':
            self.m.sort()
        else:
            self.m.sort(*t.split(','))
        self.report = True

    def command_suffix(self, cmd: str):
        self.m.suffix(self.need(f'{cmd}: expected suffix'))
        self.report = True

    def command_uri(self, cmd: str):
        """Print attribute URI(s).

        If multiple attributes have URIs, they will be printed on separate
        lines.

        Synopsis: uri
        """
        print(self.m.uri())
        self.report = False

    def command_url(self, cmd: str):
        """Print attribute URL(s).

        If multiple attributes have URLs, they will be printed on separate
        lines.

        Synopsis: url
        """
        u = self.m.url()
        if u:
            print(u)
        self.report = False

    def set_coder(self, cmd: str):
        if cmd in self.m.decoder.keys():
            self.m.decoder.set_default(cmd)
        if cmd in self.m.encoder.keys():  # pragma: no branch
            self.m.encoder.set_default(cmd)

    def set_factory(self, cmd: str):
        self.m.factory.set_default(cmd)

    def set_mode(self, cmd: str):
        self.m.mode.set_default(cmd)

    def set_registry(self, r: Registry, cmd: str):
        keys = r.keys()
        choices = ', '.join(f'‘{k}’' for k in keys)
        message = f'{cmd}: expected one of: {choices}'
        t = self.need(message)
        if t not in keys:
            raise Error(message)
        r.set_default(t)

    def run(self, args: Iterable[str]):
        self.tokens = iter(args)
        self.report = False
        while (cmd := self.token()) is not None:
            c = self.commands.get(cmd)
            if not c:
                raise Error(f'{cmd}: Unknown command')
            c(self, cmd)
        if self.report:
            print(self.m)

    def runs(self, s: str):
        return self.run(s.split())
