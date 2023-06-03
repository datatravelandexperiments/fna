# fna

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Implementation](#implementation)

## Introduction

### The problem

Many types of files have associated metadata, e.g. title and creators, but
there is no universal way to record this. Some file formats contain metadata
fields, but not all do. Some file systems provide for metadata tagging,
but most don't. Both are externally invisible, which makes them easy to
accidentally lose. There are external tagging tools, but the association
between a file and its external records is likewise easy to lose.

### This solution

Some metadata is placed in the file name itself, where it won't be
_accidentally_ separated from the file. In many cases, this metadata includes
some kind of unique identifier (e.g. ISBN for books, DOI for papers) that
can be used to find additional information.

This tool, `fna` (for ‘File Name Attributes’) helps automate managing
key-value pairs in file names.

For certain keys, the values can have associated semantics beyond their text.
For example, ISBNs can be normalized to ISBN-13 and have their checksums
corrected.

## Installation

The easiest (?) way to install `fna` is from
[PyPi](https://pypi.org/project/fnattr/) using `pip`.
Depending on your system, one of the following may work:

- `pip install fnattr`
- `pip install --user fnattr`
- `pipx install fnattr`
- `python -m pip install fnattr`

## Usage

By default, `fna` follows a subcommand familiar from tools like `git`, except
that it's typical to chain multiple subcommands in a single invocation.

Run `fna help` to get a list of subcommands, and `fna help ‹subcommand›`
for information on a particular subcommand.

See [doc/fna.md](doc/fna.md) for more information.

(More complicated operations are possible using Python expressions rather
than the subcommands, but this is not yet stable or documented.)

### Examples

This example uses two subcommands, `file`, which takes a file name as
argument, and `add`, which takes key and value as arguments:

```
$ fna file '/tmp/My Book.pdf' add isbn 1234567890
/tmp/My Book [isbn=9781234567897].pdf
```

If no subcommand causes output or side effects, `fna` prints the resulting
file name or string.

Rename a file (three subcommands):

```
$ fna file '/tmp/My Book.pdf' add isbn 1234567890 rename
```

```
$ fna file '/tmp/My Book.pdf' add isbn 1234567890 json encode
{"title": ["My Book"], "isbn": ["9781234567897"]}
```

## Configuration

Unless otherwise directed by a command line option,
`fna` tries to read `fnattr/vlju.toml` or `fnattr/fna.toml`
from XDG locations (e.g. `$HOME/.config/`).
The former is shared by all tools using the Vlju
library, while the latter applies only to the `fna` command.

This file can define keys and classes associated with web sites,
mapping between a compact ID to a URL.
The distribution file `config/vlju.toml` contains some examples.

See [doc/configuration.md](doc/configuration.md) for more information.

## Implementation

The current public home for `fna` is
[https://codeberg.org/datatravelandexperiments/fna](https://codeberg.org/datatravelandexperiments/fna)

`fna` is written in Python primarily because (in the original version) the
standard library `shlex` module provided input file tokenization ‘for free’
(sometimes free is expensive). It was originally written in Python 2 circa
2010, and substantially revised in 2023.

`fna` aims for 100% unit test coverage (outside of `extra/`)
and full type annotation (outside of unit tests).

### src/util

Code that does not depend on `vlju`, and could be useful in unrelated projects.

### src/vlju

`vlju.Vlju` (pronounced ‘value’) is the base data type for attribute
values. Every `Vlju` has a string representation. Many subclasses have
additional internal structure; e.g. the `ISBN` subclass handles 10- and
13-digit ISBNs including their checksums.

`src/vlju` can depend on `src/util`.

### src/vljumap

`vljumap.VljuMap` is a key-value store (multimap) associating string keys
with (one or more) `Vlju` values.

`vljumap.enc` contains code to convert `VljuMap` to and from string
representations.

`src/vljumap` can depend on `src/vlju` and `src/util`.

### src/vljum

Code implementing the subcommands.

`src/vljum` can depend on `src/vljumap`, `src/vlju` and `src/util`.

### src/fna

The command line tool `fna`.

### TODO

- Better error handling. Too much still just raises exceptions.
- Document operation with `-[EFx]`.
