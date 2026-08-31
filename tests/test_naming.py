import pytest

from kutub.naming import human_size, split_title_author


@pytest.mark.parametrize(
    ("file_name", "expected"),
    [
        ("Thinking, Fast and Slow - Daniel Kahneman.pdf",
         ("Thinking, Fast and Slow", "Daniel Kahneman")),
        ("Amok - Stefan Zweig.epub", ("Amok", "Stefan Zweig")),
        ("The Shadow of the Wind – Carlos Ruiz Zafon.epub",
         ("The Shadow of the Wind", "Carlos Ruiz Zafon")),
        ("Title|Author.mobi", ("Title", "Author")),
    ],
)
def test_splits_on_common_separators(file_name, expected):
    assert split_title_author(file_name) == expected


def test_author_first_names_are_reversed():
    # TODO: detect "Author - Title" ordering; needs an author list to be reliable.
    title, author = split_title_author("Carl Sagan - The Demon Haunted World.epub")
    assert title == "Carl Sagan"
    assert author == "The Demon Haunted World"


def test_underscores_become_spaces():
    title, author = split_title_author("a_long_book_title.epub")
    assert title == "a long book title"
    assert author == ""


def test_no_separator_yields_empty_author():
    assert split_title_author("standalone.epub") == ("standalone", "")


def test_empty_filename():
    assert split_title_author("") == ("", "")


def test_arabic_filename_splits_on_hyphen():
    title, author = split_title_author("ظل الريح - كارلوس زافون.epub")
    assert title == "ظل الريح"
    assert author == "كارلوس زافون"


def test_collapses_repeated_whitespace():
    title, _ = split_title_author("spaced    out    title.epub")
    assert title == "spaced out title"


@pytest.mark.parametrize(
    ("size", "expected"),
    [(None, "0.0MB"), (0, "0.0MB"), (1048576, "1.0MB"), (2621440, "2.5MB")],
)
def test_human_size(size, expected):
    assert human_size(size) == expected
