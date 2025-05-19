# Coded, configured, and conventional keys

## `a`

Author, Artist. (_coded_)

- Accepted values: any

This is handled specially by some encoders.

## `c`

Character. (_convention_)

- Accepted values: any

## `ch`

Chapter. (_convention_)

- Accepted values: any

## `cx`

Character-crossover. (_convention_)

- Accepted values: any

## `dan`

[Danbooru](https://danbooru.donmai.us/) item. (_configured_)

- Accepted values: numeric _id_, or long form URL.
- Representation: _id_
- Long form: `https://danbooru.donmai.us/posts/`_id_

This is not defined within `fna`,
but is present in the example configuration file.

## `date`

Date. (_convention_; may become _coded_)

- Accepted values: any

This might get a class and parsing in the future.

## `doi`

Document Object Identifier. (_coded_)

- Accepted values: [_intro_]_prefix_(`/`|`,`)_suffix_
  where _intro_ is one of:
  - empty
  - `doi:`(`/`)*
  - [`info:`]\(`doi`|`hdl`)`/`
  - `https://`[`dx.`]`doi.org/`
  - `https://hdl.handle.net/`
- Representation: _prefix_`,`_suffix_
- Long form: (`doi:`_prefix_`/`_suffixᵖ_) | _uri_
- Class: `DOI`

## `e`

Episode. (_convention_)

- Accepted values: any

## `ean`

International Article Number (_coded_).

- Accepted values: EAN13 or SBN or ISBN or ISMN or ISSN or UPC-A
- Representation: 13-digits including corrected check digit.
- Long form: ‘urn:ean13:’_number_
- Class: `EAN13`

## `file`

Local file path. (_coded_)

- Accepted values: path
- Class: `File`

## `gel`

[Gelbooru](https://gelbooru.com/) item. (_configured_)

- Accepted values: numeric _id_, or long form URL.
- Representation: _id_
- Long form: `https://gelbooru.com/index.php?page=post&s=view&id=`_id_

This is not defined within `fna`,
but is present in the example configuration file.

## `info`

‘info’ uri. (_coded_)

- Accepted values: URI
- Representation: URI
- Class: `Info`

## `isbn`

International Standard Book Number. (_coded_)

- Accepted values: EAN-13 in the ISBN range, ISBN, or SBN
- Representation: ISBN
- Class: `ISBN`

## `ismn`

International Standard Music Number. (_coded_)

- Accepted values: EAN-13 in the ISMN range, or ISMN (`M` followed by 9 digits)
- Representation: EAN-13
- Long form: ISMN (`M` followed by 9 digits)
- Class: `ISMN`

## `issn`

International Standard Serial Number. (_coded_)

- Accepted values: EAN-13 in the ISSN range, or ISSN
- Representation: EAN-13
- Long form: ISSN
- Class: `ISSN`

## `j`

Enclosing work (journal, album, series, etc.). (_convention_)

- Accepted values: any

## `lang`

Language. (_convention_; may become _coded_)

- Accepted values: any

Might get a class with ISO-639 interpretation in the future.

## `lccn`

Library of Congress Catalog Number. (_coded_)

- Accepted values: LCCN
- Class: `LCCN`

## `n`

Sequence number (track, issue, etc.). (_coded_)

Handled specially by some encoders.

## `p`

Page(s) in a paginated work (_convention_).

## `pixiv`

[Pixiv](https://www.pixiv.net/) item. (_configured_)

- Accepted values: _id_[`,`_item_] or _id_`_p`_item_ or long form URL
- Representation: _id_[`,`_item_]
- Long form: `https://www.pixiv.net/en/artworks/`_id_[`#`_item_]

This is not defined within `fna`,
but is present in the example configuration file.

## `r`

Aspect ratio (_convention_).

## `sub`

Subtitle language. (_convention_; may become _coded_)

- Accepted values: any

Might get a class with ISO-639 interpretation in the future.

## `t`

Timestamp (within a work; for points in time use `date`). (_coded_)

- Accepted values: Handles many unambiguous representations.
  For example:
    - `1:23:45:57.39`
    - `123days 5′10.3″`
    - `99`
    - `99:59`
    - `99:59.99`
    - `99:59:59.999`
    - `99:23:59:59.999`
    - `123 Hours 5:10.3`
    - `123 hours 10.25`
    - `123 hours 99s1024`
    - `1d 23 59 59`
    - `1 23H 59 59`
    - `1d 23 59 59s`
    - `1 day 14 µs`
- Representation: _days_`:`_hh_`:`_mm_`:`_ss_`.`_fraction_,
  but the `.`_fraction_ and leading fields or digits are omitted if zero.
- Class: `Timestamp`

## `tcom`

Composer. (_convention_)

- Accepted values: any

Named for the ID3v2 tag.

## `text`

Lyricist. (_convention_)

- Accepted values: any

Named for the ID3v2 tag.

## `tl`

Translation (to) Language. (_convention_; may become _coded_)

- Accepted values: any

Might get a class with ISO-639 interpretation in the future.

## `tr`

Translator. (_convention_)

- Accepted values: any

## `tweet`

[Twitter](https://twitter.com/) post. (_configured_)

- Accepted values: [_account_`,`]_post_ or long form URL
- Representation: [_account_`,`]_post_
- Long form: URL

This is not defined within `fna`,
but is present in the example configuration file.

## `uri`

Universal Resource Identifier. (_coded_)

- Accepted values: URI
- Class: `URI`

## `url`

Universal Resource Locator. (_coded_)

- Accepted values: URL
- Class: `URL`

## `urn`

Universal Resource Name. (_coded_)

- Class: `URN`

## `v`

Volume (of a multi-volume work). (_convention_)

- Accepted values: any

## `yt`

YouTube video. (_configured_)

- Accepted values: _id_ or long form URL or `youtu.be/`_id_ URL
- Representation: _id_
- Long form: `https://www.youtube.com/watch?v=`_id_

This is not defined within `fna`,
but is present in the example configuration file.
