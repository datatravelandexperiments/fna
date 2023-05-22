# Configuration

Configuration files are in [TOML](https://toml.io/) form.

## Default configuration files

Unless otherwise directed by a command line option,
`fna` tries to read `vlju/config.toml` or `fna/config.toml`
under XDG locations (e.g. `$XDG_CONFIG_HOME/` or `$HOME/.config/`).
The former — the `vlju` subdirectory — is shared by all tools
using the Vlju library; the latter applies only to the `fna` command.

## Sections

### `[option]`

An `[option]` section can contain key-value pairs corresponding
to tool command line options.

### `[site.`_key_`]`

A `site` section defines a mapping from a short ‘id’,
which is to be used as a file name attribute value, to a URL.

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

At least one of `path`, `query`, or `fragment` must be present
in order for the URL to be useful.

The `path`, `query`, `fragment`, and `normalize` strings
take the form of Python
[f-strings](https://docs.python.org/3/reference/lexical_analysis.html#f-strings),
with restrictions.
Only the following Python names are available:
`False`, `None`, `True`,
`abs`, `all`, `any`, `ascii`, `bin`, `bool`, `chr`, `hex`, `int`, `len`,
`max`, `min`, `oct`, `ord`, `reversed`, `slice`, `sorted`, `str`.

In the `path`, `query`, and `fragment` strings,
`x` contains the canonical representation of the attribute value.
In the `normalize` string, `x` is the value read.

The distribution file `config/config.toml` contains some examples.
