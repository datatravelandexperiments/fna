# Extras

This directory contains unpolished experimental code.

These are all concerned with renaming and moving files,
and in the long run some unified tool might come out of
these explorations.

## fnaffle.py

Moves files to directories based on matching attributes.

A map file consists of lines of the form
```
    ‹directory› ‹op› ‹v3attributes›
```
where ‹op› is one of ‘=’, ‘⊂’, ‘⊆’, ‘⊃’, ‘⊇’.
Files on the command line are tested against these in order;
if one matches, the file is moved into the target ‹directory›.

Only keys mentioned in ‹v3attributes› are tested.
The same operator applies to all keys, which is not ideal.

## tellico_sqlite3_rename.py

Renames and moves files by matching hashes against a database derived
from the [Tellico collection manager](https://tellico-project.org).

1. Export from Tellico as CSV.
2. Import into SQLite: `.import -csv EXPORTED.csv tellico`.

## danname.py

Rename an image file according to metadata looked up online.
