# fna

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

## Usage

By default, `fna` follows a subcommand familiar from tools like `git`, except
that it's typical to chain multiple subcommands in a single invocation.

Run `fna help` to get a list of subcommands, and `fna help ‹subcommand›`
for information on a particular subcommand.

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

`fna` tries to read `fna/config.toml` from XDG locations
(e.g. `$HOME/.config/`).
This file can define keys and classes associated with web sites,
mapping from a compact ID to a URL. (The other direction does not yet exist.)
The distribution file `config/config.toml` contains some examples.

## Implementation

`fna` is written in Python primarily because (in the original version) the
standard library `shlex` module provided input file tokenization ‘for free’
(sometimes free is expensive). It was originally written in Python 2 circa
2010, and substantially revised in 2023.

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

## TODO

- Better documentation.
- Logging options.
- Better error handling. Too much still just raises exceptions.

<!-- vim:set textwidth=79: -->
