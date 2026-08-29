"""SQLite catalogue with an FTS5 search index."""

from __future__ import annotations

import sqlite3

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    channel     TEXT    NOT NULL,
    channel_id  INTEGER,
    msg_id      INTEGER NOT NULL,
    file_name   TEXT    NOT NULL,
    title       TEXT,
    author      TEXT,
    ext         TEXT,
    size        INTEGER,
    date        TEXT,
    caption     TEXT,
    UNIQUE (channel, msg_id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS books_fts
    USING fts5(title, author, file_name, caption,
               content='books', content_rowid='id');
"""

COLUMNS = "id, title, author, ext, size, channel"


def connect() -> sqlite3.Connection:
    config.ensure_home()
    con = sqlite3.connect(config.DB_PATH)
    con.executescript(SCHEMA)
    con.commit()
    return con


def insert(con: sqlite3.Connection, record: dict) -> bool:
    """Return True if the row was new, False if this message was already indexed."""
    try:
        con.execute(
            "INSERT INTO books (channel, channel_id, msg_id, file_name, title,"
            " author, ext, size, date, caption)"
            " VALUES (:channel, :channel_id, :msg_id, :file_name, :title,"
            " :author, :ext, :size, :date, :caption)",
            record,
        )
        return True
    except sqlite3.IntegrityError:
        return False


def reindex(con: sqlite3.Connection) -> None:
    con.execute("INSERT INTO books_fts(books_fts) VALUES('rebuild')")
    con.commit()


def search(con: sqlite3.Connection, query: str, limit: int) -> list[tuple]:
    cleaned = query.replace('"', " ").strip()
    if not cleaned:
        return []
    rows = con.execute(
        f"SELECT b.{COLUMNS.replace(', ', ', b.')}"
        " FROM books_fts f JOIN books b ON b.id = f.rowid"
        " WHERE books_fts MATCH ? LIMIT ?",
        (f'"{cleaned}"*', limit),
    ).fetchall()
    if rows:
        return rows
    # FTS5 misses partial words inside compound filenames; LIKE catches those.
    like = f"%{cleaned}%"
    return con.execute(
        f"SELECT {COLUMNS} FROM books"
        " WHERE title LIKE ? OR author LIKE ? OR file_name LIKE ? LIMIT ?",
        (like, like, like, limit),
    ).fetchall()


def recent(con: sqlite3.Connection, limit: int, channel: str | None = None) -> list[tuple]:
    if channel:
        return con.execute(
            f"SELECT {COLUMNS} FROM books WHERE channel LIKE ?"
            " ORDER BY id DESC LIMIT ?",
            (f"%{channel}%", limit),
        ).fetchall()
    return con.execute(
        f"SELECT {COLUMNS} FROM books ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()


def get(con: sqlite3.Connection, book_id: int) -> tuple | None:
    return con.execute(
        "SELECT channel, channel_id, msg_id, file_name, title, author, ext"
        " FROM books WHERE id = ?",
        (book_id,),
    ).fetchone()


def totals(con: sqlite3.Connection) -> tuple[int, list, list]:
    total = con.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    by_channel = con.execute(
        "SELECT channel, COUNT(*) FROM books GROUP BY channel ORDER BY 2 DESC"
    ).fetchall()
    by_format = con.execute(
        "SELECT ext, COUNT(*) FROM books GROUP BY ext ORDER BY 2 DESC"
    ).fetchall()
    return total, by_channel, by_format
