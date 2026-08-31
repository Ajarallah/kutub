
import pytest

from kutub import catalogue


def record(msg_id: int, title: str, author: str = "", channel: str = "Books") -> dict:
    return {
        "channel": channel,
        "channel_id": 1,
        "msg_id": msg_id,
        "file_name": f"{title} - {author}.epub",
        "title": title,
        "author": author,
        "ext": ".epub",
        "size": 1048576,
        "date": "2026-01-01",
        "caption": "",
    }


@pytest.fixture()
def con(monkeypatch, tmp_path):
    monkeypatch.setattr(catalogue.config, "DB_PATH", tmp_path / "books.db")
    monkeypatch.setattr(catalogue.config, "HOME", tmp_path)
    connection = catalogue.connect()
    yield connection
    connection.close()


def test_schema_is_created(con):
    tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master")}
    assert {"books", "books_fts"} <= tables


def test_insert_returns_true_for_new_rows(con):
    assert catalogue.insert(con, record(1, "Dune", "Herbert")) is True


def test_duplicate_message_is_rejected(con):
    catalogue.insert(con, record(1, "Dune", "Herbert"))
    assert catalogue.insert(con, record(1, "Dune", "Herbert")) is False


def test_same_id_in_another_channel_is_allowed(con):
    catalogue.insert(con, record(1, "Dune", "Herbert", channel="A"))
    assert catalogue.insert(con, record(1, "Dune", "Herbert", channel="B")) is True


def test_search_finds_by_title(con):
    catalogue.insert(con, record(1, "Dune", "Frank Herbert"))
    catalogue.reindex(con)
    assert len(catalogue.search(con, "Dune", 10)) == 1


def test_search_finds_by_author(con):
    catalogue.insert(con, record(1, "Dune", "Frank Herbert"))
    catalogue.reindex(con)
    assert catalogue.search(con, "Herbert", 10)


def test_search_respects_limit(con):
    for i in range(5):
        catalogue.insert(con, record(i, f"Book {i}", "Author"))
    catalogue.reindex(con)
    assert len(catalogue.search(con, "Book", 2)) == 2


def test_empty_query_returns_nothing(con):
    catalogue.insert(con, record(1, "Dune"))
    catalogue.reindex(con)
    assert catalogue.search(con, "   ", 10) == []


def test_quotes_in_query_do_not_break_fts(con):
    catalogue.insert(con, record(1, "Dune"))
    catalogue.reindex(con)
    assert catalogue.search(con, 'Du"ne', 10) is not None


def test_recent_orders_newest_first(con):
    catalogue.insert(con, record(1, "First"))
    catalogue.insert(con, record(2, "Second"))
    assert catalogue.recent(con, 10)[0][1] == "Second"


def test_recent_filters_by_channel(con):
    catalogue.insert(con, record(1, "A", channel="Alpha"))
    catalogue.insert(con, record(2, "B", channel="Beta"))
    rows = catalogue.recent(con, 10, channel="Alpha")
    assert len(rows) == 1 and rows[0][1] == "A"


def test_get_returns_none_for_missing_id(con):
    assert catalogue.get(con, 999) is None


def test_get_returns_message_coordinates(con):
    catalogue.insert(con, record(42, "Dune", "Herbert"))
    row = catalogue.get(con, 1)
    assert row[2] == 42


def test_totals_group_by_channel_and_format(con):
    catalogue.insert(con, record(1, "A", channel="Alpha"))
    catalogue.insert(con, record(2, "B", channel="Alpha"))
    catalogue.insert(con, record(3, "C", channel="Beta"))
    total, by_channel, by_format = catalogue.totals(con)
    assert total == 3
    assert by_channel[0] == ("Alpha", 2)
    assert by_format == [(".epub", 3)]


def test_totals_on_empty_catalogue(con):
    assert catalogue.totals(con)[0] == 0
