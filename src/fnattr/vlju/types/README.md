Class hierarchy:

* Vlju
  * URI
    * Info
      * DOI
      * LCCN
    * File
    * URL
        * SiteBase
            * Danbooru
            * Gelbooru
            * Pixiv
            * Twitter
            * YouTube
    * URN
      * EAN13
        * ISBN
        * ISMN
        * ISSN


| Key   | Class                | short         | long          | URL |
|-------|----------------------|---------------|---------------|-----|
|       | Vlju                 | value         | value         |     |
| uri   |   URI                | uri           | uri           |     |
| info  |     Info             | uri           | uri           |     |
| doi   |       DOI            | sdoi          | doi \| uri    |  Y  |
| lccn  |       LCCN           | value         | uri           |  Y  |
| file  |     File             | file          | uri           |  Y  |
| url   |     URL              | uri           | uri           |  Y  |
|       |         SiteBase     | value         | uri           |  Y  |
| dan   |             Danbooru | value         | uri           |  Y  |
| gel   |             Gelbooru | value         | uri           |  Y  |
| pixiv |             Pixiv    | value         | uri           |  Y  |
| tweet |             Twitter  | value         | uri           |  Y  |
| yt    |             YouTube  | value         | uri           |  Y  |
| url   |     URN              | uri           | uri           |     |
| ean   |       EAN13          | value         | uri           |     |
| isbn  |         ISBN         | value         | uri           |     |
| ismn  |         ISMN         | value         | uri           |     |
| issn  |         ISSN         | value         | uri           |     |


|       |   |                                                               |
|-------|---|---------------------------------------------------------------|
| value | → | `_value`                                                      |
| uri   | → | `scheme()` `_sa` `sauthority()` `_ap` `spath()` qf            |
| qf    | → | `squery()` `sfragment()` `sr()` `sq()`                        |
| sdoi  | → | `_prefix` ‘,’ `_suffix`                                       |
| doi   | → | ‘doi:’ `_prefix` ‘/’ `_suffix`ᵖ                               |
| file  | → | `str(_file)`                                                  |
