# Coded and conventional keys

## `a`

Author, Artist.

- Accepted values: any

This is handled specially by some encoders.

## `c`

Character.

- Accepted values: any

## `ch`

Chapter.

- Accepted values: any

## `cx`

Character-crossover.

- Accepted values: any

## `dan`

[Danbooru](https://danbooru.donmai.us/) item.

- Accepted values: number
- Representation: number
- Long form: `https://danbooru.donmai.us/posts/`_number_

This is not defined within `fna`,
but is present in the example configuration file.

## `date`

Date.

- Accepted values: any

This might get a class and parsing in the future.

## `doi`

Document Object Identifier.

- Accepted values: TBD
- Representation: _prefix_`,`_suffix_
- Long form: (`doi:`_prefix_`/`_suffixᵖ_) | _uri_
- Class: `DOI`

## `e`

Episode.

- Accepted values: any

## `ean`

International Article Number.

- Accepted values: EAN13 or SBN or ISBN or ISMN or ISSN or UPC-A
- Representation: 13-digits including corrected check digit.
- Long form: ‘urn:ean13:’_number_
- Class: `EAN13`

## `file`

Local file path.

- Accepted values: path
- Class: `File`

## `gel`

[Gelbooru](https://gelbooru.com/) item.

- Accepted values: number
- Representation: number
- Long form: `https://gelbooru.com/index.php?page=post&s=view&id=`_number_

This is not defined within `fna`,
but is present in the example configuration file.

## `info`

‘info’ uri.

- Accepted values: URI
- Representation: URI
- Class: `Info`

## `isbn`

International Standard Book Number.

- Accepted values: EAN-13 in the ISBN range, ISBN, or SBN
- Representation: ISBN
- Class: `ISBN`

## `ismn`

International Standard Music Number.

- Accepted values: EAN-13 in the ISMN range, or ISMN (`M` followed by 9 digits)
- Representation: EAN-13
- Long form: ISMN (`M` followed by 9 digits)
- Class: `ISMN`

## `issn`

International Standard Serial Number.

- Accepted values: EAN-13 in the ISSN range, or ISSN
- Representation: EAN-13
- Long form: ISSN
- Class: `ISSN`

## `j`

Enclosing work (journal, album, etc.).

- Accepted values: any

## `lang`

Language.

- Accepted values: any

Might get a class with ISO-639 interpretation in the future.

## `lccn`

Library of Congress Catalog Number.

- Accepted values: LCCN
- Class: `LCCN`

## `n`

Sequence number (track, issue, etc.).

Handled specially by some encoders.

## `p`

Page(s) in a paginated work.

## `pixiv`

[Pixiv](https://www.pixiv.net/) item.

- Accepted values: _id_ or _id_`_p`_item_
- Representation: _id_`_p`_item_
- Long form: `https://www.pixiv.net/en/artworks/`_id_[`#`_item_]

This is not defined within `fna`,
but is present in the example configuration file.

## `sub`

Subtitle language.

- Accepted values: any

Might get a class with ISO-639 interpretation in the future.

## `t`

Timestamp (within a work; for points in time use `date`).

- Accepted values: any

This might get a class and parsing in the future.

## `tcom`

Composer.

- Accepted values: any

Named for the ID3v2 tag.

## `text`

Lyricist.

- Accepted values: any

Named for the ID3v2 tag.

## `tweet`

[Twitter](https://twitter.com/) post.

- Accepted values: [_account_`,`]_post_
- Long form: URL

This is not defined within `fna`,
but is present in the example configuration file.

## `uri`

Universal Resource Identifier.

- Accepted values: URI
- Class: `URI`

## `url`

Universal Resource Locator.

- Accepted values: URL
- Class: `URL`

## `urn`

Universal Resource Name.

- Class: `URN`

## `v`

Volume (of a multi-volume work).

- Accepted values: any

## `yt`

YouTube video.

- Accepted values: _id_
- Long form: `https://www.youtube.com/watch?v=`_id_

This is not defined within `fna`,
but is present in the example configuration file.
