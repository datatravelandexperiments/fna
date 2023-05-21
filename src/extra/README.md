# fnaffle.py

Moves files to directories based on matching attributes.

A map file consists of lines of the form
```
    ‹directory› ‹op› ‹v3attributes›
```
where ‹op› is one of ‘=’, ‘⊂’, ‘⊆’, ‘⊃’, ‘⊇’.
Files on the command line are tested against these in order;
if one matches, the file is moved into the target ‹directory›.

Only keys mentioned in ‹v3attributes› are tested.
The same operator applies to all keys, which is not ideal,
and the reason this program is currently relegated to `extra/`.

# tellico_sqlite3_rename

Outdated and not currently working.
Renames files by matching hashes against a database derived
from the [Tellico collection manager](https://tellico-project.org).
