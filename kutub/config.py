"""Paths, config file access, and Telegram credential lookup."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HOME = Path(os.environ.get("KUTUB_HOME") or Path.home() / ".kutub")
DB_PATH = HOME / "books.db"
SESSION_PATH = str(HOME / "session")
CONFIG_PATH = HOME / "config.json"

EBOOK_EXTENSIONS = frozenset(
    {".epub", ".pdf", ".mobi", ".azw3", ".txt", ".docx", ".fb2", ".djvu"}
)


def ensure_home() -> Path:
    HOME.mkdir(parents=True, exist_ok=True)
    return HOME


def load() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError:
        print(f"warning: {CONFIG_PATH} is not valid JSON, ignoring", file=sys.stderr)
        return {}


def save(data: dict) -> None:
    ensure_home()
    CONFIG_PATH.write_text(json.dumps(data, indent=2))
    CONFIG_PATH.chmod(0o600)


def credentials() -> tuple[str, str]:
    cfg = load()
    api_id = os.environ.get("TG_API_ID") or cfg.get("api_id")
    api_hash = os.environ.get("TG_API_HASH") or cfg.get("api_hash")
    if not api_id or not api_hash:
        sys.exit(
            "No Telegram API credentials found.\n"
            "Get them at https://my.telegram.org/apps, then run: kutub login"
        )
    return str(api_id), str(api_hash)


def download_dir(override: str | None = None) -> Path:
    target = Path(
        override or os.environ.get("KUTUB_DOWNLOAD_DIR") or Path.home() / "Downloads"
    )
    target.mkdir(parents=True, exist_ok=True)
    return target
