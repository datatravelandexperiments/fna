# fna

`fna` — Manage key/value attributes in file names.

## Usage

`fna` \[[_options_](#options)\]  \[_subcommand_(#subcommands) ...\]

For a list of [_subcommands_](#subcommands), run `fna help`.
For information on a specific subcommand, run `fna help` _subcommand_

### Options

#### `--config` _file_, `-c` _file_

Read the given [configuration _file_](configuration.md),
instead of the looking for
[default configuration files](configuration.md#default-files).

#### `--decoder` _decoder_, `-d` _decoder_

Specify the default [string decoder](#encodings).

#### `--encoder` _encoder_, `-e` _encoder_

Specify the default [string encoder](#encodings).

#### `--dsl`, `-D`

Positional arguments are [subcommands](#subcommands).
This is the default.

#### `--evaluate`, `-E`

Positional arguments are Python expressions to evaluate.
Not further documented and may not be stable.

#### `--execute`, `-x`

Positional arguments are Python statements to execute.
Not further documented and may not be stable.

#### `--file`, `-f`

Positional arguments are Python program files.
Not further documented and may not be stable.

### Subcommands

- [`add`](#add) - Add an attribute.
- [`decode`](#decode) - Decode a string.
- [`decoder`](#decoder) - Set the current active decoder.
- [`delete`](#delete) - Delete all attributes for one or more ‹key›s.
- [`dir`](#dir) - Set the directory associated with a file name.
- [`encode`](#encode) - Encode and prints the current attributes.
- [`encoder`](#encoder) - Set the current active encoder.
- [`extract`](#extract) - Extract attributes for one or more keys.
- [`factory`](#factory) - Set the current active factory.
- [`file`](#file) - Decode a file name.
- [`filename`](#filename) - Encode and print the current attributes as a file name.
- [`help`](#help) - Show information about a subcommand, or list subcommands.
- [`mode`](#mode) - Set the current active mode.
- [`order`](#order) - Arranges keys.
- [`remove`](#remove) - Remove a specific attribute.
- [`rename`](#rename) - Rename a file.
- [`set`](#set) - Set an attribute.
- [`sort`](#sort) - Sorts values for a given key or all keys.
- [`suffix`](#suffix) - Set the suffix associated with a file name.
- [`uri`](#uri) - Print attribute URI(s).
- [`url`](#url) - Print attribute URL(s).

#### add

`add` _key_ _value_

Add an attribute.
Constructs the _value_ using the current active [factory](#factories).

#### decode

`decode` _string_

Decode a _string_,
using the current active [decoder](#encodings).

#### decoder

`decoder` _decoder_

Set the current active [_decoder_](#encodings).

#### delete

`delete` _key_[`,`_key_]*

Delete all attributes for one or more _key_s.

It is not an error for keys not to be present.
The complement of `delete` is `extract`.

#### compare

`compare`

Print the original file name from a `file` command
and current encoded file name, if they differ.
Encodes using the current active encoder.
This can be used as a ‘dry run’ for `rename`.

#### dir

`dir` _directory_

Set the directory associated with a file name.

#### encode

`encode`

Encode and prints the current attributes,
using the current active [encoder](#encodings).

#### encoder

`encoder` _encoder_

Set the current active [_encoder_](#encodings).

#### extract

`extract` _key_[`,`_key_]*

Extract attributes for one or more _key_s.

It is not an error for keys not to be present.
The complement of `extract` is `delete`.

#### factory

`factory` _factory_

Set the current active [factory](#factory).

#### file

`file` _filename_

Decode a file name,
using the current active [decoder](#encodings).

In addition to establishing an attribute dictionary, like [`decode`](#decode),
the `file` command retains the associated directory and suffix (extension).

#### filename

`encode`

Encode and print the current attributes as a file name,
using the current active [encoder](#encodings),
and the currently associated directory and suffix (extension).

#### help

`help` [_subcommand_]*

Show information about a subcommand, or list subcommands.

#### mode

`mode` _mode_

Set the current active [_mode_](#modes).

#### order

`order` (`--all` | _key_[`,`_key_]*)

Arranges keys.
With `--all`, arranges the attribute keys in alphabetical order.
With given _key_s, arranges the attribute set so that those keys appear
in the specified order. Other keys will follow in their original order.

#### remove

`remove` _key_ _value_

Remove a specific attribute.
Constructs the _value_ using the current active [factory](#factories).

#### rename

`rename`

If attributes, [directory](#dir), or [suffix](#suffix) have changed
since the [`file`](#file) name decoding,
rename the original file according to the current state.

#### set

`set` _key_ _value_

Set an attribute.

Replaces any existing attributes for the same _key_.
Constructs the _value_ using the current active [factory](#factories).

#### sort

`sort` (`--all` | _key_[`,`_key_]*)

Sorts values for a given key or all keys.

#### suffix

`suffix` _ext_

Set the suffix (filename extension) associated with a file name.
This will be separated from the base file name with a period `.`,
whether or not the given _ext_ starts with one.

#### uri

`uri`

Print attribute URI(s).

If multiple attributes have URIs, they will be printed on separate lines.

#### url

`url`

Print attribute URL(s).

If multiple attributes have URLs, they will be printed on separate lines.

## Encodings

An _encoding_ determines the text representation of a set of attributes.

Typical use of `fna` will not change from the default encoding, [`v3`](#v3).

### `csv`

Comma-separated values.
Attributes are presented as a CSV table of two columns, the first being
the key and the second the associated value.

### `json`

JavaScript Object Notation. Attributes are encoded in JSON,
as an object where each key contains a list of values.

### `keyvalue`

Attributes are presented as a key, followed by `: `, follow by a value.
Each attribute (including multiple attributes for the same key)
appears on its own line.

### `sfc`

Encoder format `sfc` consists of a title and optional subtitles,
optional authors, and optional specific attributes: ISBN, year, and edition.

Title and optional subtitles are separated by ` - ` (including the spaces).

Authors are preceded by ` by ` and separated by commas.

An ISBN may follow. A four-digit year may follow. An edition, consisting
of a number, a number suffix, and the word `edition`, may follow.

```
    sfc       → sfctitle [‘ by ’ sfcauthor] [«‘ ’» (isbn | date | sfced)]*
    sfctitle  → [title [‘ - ’ title]*]
    sfcauthor → author [‘, ’ author]*
    sfced     → edition (‘st’ | ‘nd’ | ‘rd’ | ‘th’) ‘ edition’
    a «j» b   → (a | b | ajb)
```

### `sh`

Attributes are encoded as shell arrays (ksh, bash).
Decoding is not implemented.

### `v0`

The most obsolete format.

Encoder format v0 is strictly limited in the attributes it can represent.
This is supported only to convert old file names.

```
    v0        → v1author «‘ ’» v1title «‘ ’» (isbn | ‘lccn=’ lccn)
    a «j» b   → (a | b | ajb)
```

### `v1`

An obsolete format.

Encoder format v1 begins with optional authors, followed by optional
title and subtitle, followed by optional attributes.

Authors are separated by `; ` and followed by a `:`.

Titles and subtitles are separated by `: `.

Attributes are surrounded by `[` … `]` and separated by `,`.

This is supported only to covert old file names; it should not be used
due to the ambiguity between authors and titles with subtitles.

```
    v1        → v1author ‘:’ «‘ ’» v1title «‘ ’» v1attrs
    v1author  → [author [‘; ’ author]*]
    v1title   → [title [‘: ’ title]*]
    v1attrs   → [‘[’ v1kv [‘,’ v1kv]* ‘]’]
    v1kv      → k ‘=’ v
    a «j» b   → (a | b | ajb)
```

### `v2`

An obsolete format.

Encoder format v2 is similar to [v3](#v3),
except that attributes are surrounded by `{` … `}` rather than `[` … `]`,
and separated by semicolons with no space.

This is supported only to covert old file names.

```
    v2        → v2seq «‘ ’» v2title «‘ ’» v2attrs
    v2title   → [title [‘ - ’ title]*]
    v2attrs   → [‘{’ v2kv [‘;’ v2kv]* ‘}’]
    v2kv      → k ‘=’ v
    v2seq     → [digit (alnum | ‘.’)* ‘.’]
    a «j» b   → (a | b | ajb)
```

### `v3`

This is the default encoding format.

Encoder format v3 consists, in order, of optional sequence numbers,
optional title and subtitles, and optional attributes.

Sequence numbers begin with a digit and end with a period.
Multiple sequence numbers are allowed, but they must be adjacent.

Title and optional subtitles are separated by ` - ` (including the spaces).

Attributes are surrounded by `[` … `]` and separated by `;`.
(A space follows each semicolon when encoding,
but is not required when decoding.)
Each attribute consists of a key, optionally followed by `=` and a value.

Characters with special meaning to the encoding, or not allowed in file
names, are represented using URL-style % encoding.

```
    v3        → v3seq «‘ ’» v3title «‘ ’» v3attrs
    v3title   → [title [‘ - ’ title]*]
    v3attrs   → [‘[’ v3kv [‘; ’ v3kv]* ‘]’]
    v3kv      → k ‘=’ v
    v3seq     → [digit (alnum | ‘.’)* ‘.’]
    a «j» b   → (a | b | ajb)
```

### `value`

Attributes are presented as raw strings, one per line.
Since keys are not represented, decoding is not possible.

### `win`

This is the same as [v3](#v3) encoding format,
except that additional characters are URL-escaped
to comply with Windows file name limitations.

## Factories

A ‘factory’ defines how a text attribute value is interpreted.
There are three factories:

- `raw`:
  The value text is retained as-is.
- `typed` or `loose`:
  The value text is potentially interpreted according to the associated key.
  [In some cases](keys.md), this provides additional semantic features
  like normalization or URL representation, but this can come with
  restrictions on the accepted text. If the supplied value is not suitable
  for the associated type, it is retained as-is, untyped.
  This is the default.
- `strict`:
  Typed, but it is an error if the supplied value is not suitable.

## Modes

TBD
