"""Telegram access: client setup, channel resolution, and message walking."""

from __future__ import annotations

import os
import sys

from . import config
from .naming import split_title_author


def _telethon():
    try:
        from telethon import TelegramClient
    except ImportError:
        sys.exit("Telethon is not installed. Run: pip install telethon")
    return TelegramClient


async def connect(api_id: str | None = None, api_hash: str | None = None):
    TelegramClient = _telethon()
    config.ensure_home()
    if api_id is None or api_hash is None:
        api_id, api_hash = config.credentials()
    client = TelegramClient(config.SESSION_PATH, int(api_id), api_hash)
    await client.start()
    return client


async def resolve(client, ref: str):
    """Resolve a channel by numeric id, @username, or exact dialog title."""
    if ref.lstrip("-").isdigit():
        try:
            return await client.get_entity(int(ref))
        except (ValueError, TypeError):
            pass

    try:
        return await client.get_entity(ref)
    except (ValueError, TypeError):
        pass

    async for dialog in client.iter_dialogs():
        if getattr(dialog, "name", None) == ref:
            return dialog.entity

    sys.exit(f"Could not resolve channel: {ref}")


async def iter_dialogs(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_channel or dialog.is_group:
            yield dialog


def as_record(message, channel_name: str, channel_id: int | None) -> dict | None:
    """Build a catalogue row from a message, or None if it holds no ebook."""
    if not (message.document and message.file and message.file.name):
        return None

    file_name = message.file.name
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in config.EBOOK_EXTENSIONS:
        return None

    title, author = split_title_author(file_name)
    return {
        "channel": channel_name,
        "channel_id": channel_id,
        "msg_id": message.id,
        "file_name": file_name,
        "title": title,
        "author": author,
        "ext": ext,
        "size": message.file.size or 0,
        "date": message.date.strftime("%Y-%m-%d") if message.date else "",
        "caption": (message.message or "")[:500],
    }
