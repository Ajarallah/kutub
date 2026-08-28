"""Turn shared filenames into title and author fields."""

from __future__ import annotations

import re

# Order matters: the Arabic " ل " prefix is checked last so that a hyphen
# elsewhere in the name wins, which matches how most channels name files.
SEPARATORS = (" - ", " – ", " — ", "|", " ل ")

EXTENSION_RE = re.compile(r"\.[A-Za-z0-9]{2,5}$")
WHITESPACE_RE = re.compile(r"\s+")


def split_title_author(file_name: str) -> tuple[str, str]:
    """Split "Title - Author.epub" into ("Title", "Author").

    Assumes the title comes first, which is what the overwhelming majority of
    shared files use. Returns an empty author when no separator is found.
    """
    stem = EXTENSION_RE.sub("", file_name).replace("_", " ").strip()
    author = ""

    for separator in SEPARATORS:
        if separator not in stem:
            continue
        left, _, right = stem.partition(separator)
        stem, author = left.strip(), right.strip()
        break

    return WHITESPACE_RE.sub(" ", stem), WHITESPACE_RE.sub(" ", author)


def human_size(num_bytes: int | None) -> str:
    return f"{(num_bytes or 0) / 1048576:.1f}MB"
