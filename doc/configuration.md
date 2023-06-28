# Configuration

Configuration files are in [TOML](https://toml.io/) form.

## Files

`fna` first tries to read fixed configuration files,
and then any files named by `--config` command line options, in order.
Later files override earlier ones.

For fixed configuration files, `fna` follows
[XDG conventions](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html).
The highest priority location is `$XDG_CONFIG_HOME`,
or if that is not set, `$HOME/.config`.
Next are the directories given by `$XDG_CONFIG_DIRS`,
or if that is not set, `/etc/xdg`.
(If configuration files are present in multiple such locations,
they are read in the opposite order, so that the first listed has priority.)

`fna` first reads any `fnattr/vlju.toml` in those locations,
and then any `fnattr/fna.toml`.
(For clarity, _all_ of the former will be read before _any_ of the latter.)
The former — `vlju.toml` — is shared by all tools
using the Vlju library; the latter applies only to the `fna` command.

## Sections

### `[option]`

An `[option]` section can contain key-value pairs corresponding
to tool command line options.

### `[site.`_key_`]`

A `site` section defines a mapping from a short ‘id’,
which is to be used as a file name attribute value, to a URL.
Optionally, it can also define rules to extract an id from a URL.

The _key_ is the attribute key associated with the site type.

It contains a number of required and optional fields,
all of which have string values.

- `name`: required. A unique name, used for the Python class.
- `scheme`: optional. The URL scheme, typically `https` or `http`.
  If absent, the scheme is `https`.
- `host`: required. The host name of the site, e.g. `example.com`.
- `path`: optional. Path component of a site URL, if any.
- `query`: optional. Query component of a site URL, if any.
- `fragment`: optional. Fragment component of a site URL, if any.
- `normalize`: optional. Converts an attribute value to canonical form.
- `url`: optional. Converts a URL to an attribute value.

The distribution file `config/config.toml` contains some examples.

#### To URL

At least one of `path`, `query`, or `fragment` must be present
in order for the URL to be useful.

The `path`, `query`, `fragment`, and `normalize` strings
take the form of Python
[f-strings](https://docs.python.org/3/reference/lexical_analysis.html#f-strings).
In the `path`, `query`, and `fragment` strings,
`id` contains the canonical representation of the attribute value.
In the `normalize` string, `id` is the value read.

Only the following Python names are available:
`False`, `None`, `True`,
`abs`, `add`, `all`, `any`, `ascii`, `bin`, `bool`, `chr`, `hex`, `int`, `len`,
`map`, `max`, `min`, `oct`, `ord`, `reversed`, `slice`, `sorted`, `str`, `sub`.
(Python does not provide perfect isolation, so it's possible in principle
for a malicious configuration string to do harm, but it's not more dangerous
than running an untrusted program in the first place.)

#### From URL

The optional `url` field provides regular expressions
[using Python
syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax)
Its value must be a list.
Each element of the list is another list containing one or two elements:
the first is a regular expression pattern tried against a URL,
and the second is a substitution result used if case of a match.
If there is no second element, the substitution result is `'\1'`,
that is, the contents of the first match group.
Patterns are tried in order; the first to match defines the attribute value.
