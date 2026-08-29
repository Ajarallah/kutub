"""Command line interface."""

from __future__ import annotations

import argparse
import asyncio
import sys

from . import __version__, catalogue, config, kindle, telegram
from .naming import human_size

COMMIT_EVERY = 250


def _show(rows: list[tuple]) -> None:
    if not rows:
        print("No results.")
        return
    for book_id, title, author, ext, size, _channel in rows:
        line = f"[{book_id}] {title}"
        if author:
            line += f" — {author}"
        print(f"{line}  ({ext.lstrip('.')}, {human_size(size)})")
    print(f"\n{len(rows)} result(s). Download with: kutub get <id> [--kindle]")


async def login(args) -> None:
    cfg = config.load()
    api_id = args.api_id or cfg.get("api_id") or input("api_id: ").strip()
    api_hash = args.api_hash or cfg.get("api_hash") or input("api_hash: ").strip()
    config.save({**cfg, "api_id": api_id, "api_hash": api_hash})

    client = await telegram.connect(api_id, api_hash)
    me = await client.get_me()
    handle = f" (@{me.username})" if me.username else ""
    print(f"Signed in as {me.first_name}{handle}")
    await client.disconnect()


async def channels(args) -> None:
    client = await telegram.connect()
    print(f"{'ID':<16} {'TYPE':<8} NAME")
    async for dialog in telegram.iter_dialogs(client):
        kind = "channel" if dialog.is_channel else "group"
        print(f"{dialog.id:<16} {kind:<8} {dialog.name}")
    await client.disconnect()


async def index(args) -> None:
    client = await telegram.connect()
    entity = await telegram.resolve(client, args.channel)
    name = getattr(entity, "title", args.channel)
    entity_id = getattr(entity, "id", None)

    con = catalogue.connect()
    print(f"Indexing: {name}")

    added = skipped = 0
    async for message in client.iter_messages(entity, limit=args.limit):
        record = telegram.as_record(message, name, entity_id)
        if record is None:
            continue
        if catalogue.insert(con, record):
            added += 1
            if added % COMMIT_EVERY == 0:
                con.commit()
                print(f"  … {added}")
        else:
            skipped += 1

    con.commit()
    catalogue.reindex(con)
    print(f"Added {added} book(s) | skipped {skipped} already indexed")
    await client.disconnect()


def search(args) -> None:
    _show(catalogue.search(catalogue.connect(), args.query, args.n))


def listing(args) -> None:
    _show(catalogue.recent(catalogue.connect(), args.n, args.channel))


def stats(args) -> None:
    total, by_channel, by_format = catalogue.totals(catalogue.connect())
    print(f"Total books: {total}")
    if not total:
        return
    print("\nBy channel:")
    for channel, count in by_channel:
        print(f"  {count:>6}  {channel}")
    print("\nBy format:")
    for ext, count in by_format:
        print(f"  {count:>6}  {ext}")


async def get(args) -> None:
    row = catalogue.get(catalogue.connect(), args.id)
    if row is None:
        sys.exit(f"No book with id {args.id}")
    channel, channel_id, msg_id, file_name, title, author, ext = row

    client = await telegram.connect()
    entity = await telegram.resolve(client, str(channel_id) if channel_id else channel)
    message = await client.get_messages(entity, ids=msg_id)
    if message is None:
        await client.disconnect()
        sys.exit("That message is no longer available in the channel")

    destination = config.download_dir(args.out) / file_name
    print(f"Downloading: {title}")
    await client.download_media(message, file=str(destination))
    print(f"Saved to: {destination}")
    await client.disconnect()

    if args.kindle:
        kindle.send(destination, title, author, ext, args.device)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kutub",
        description="Index and search ebooks shared in Telegram channels.",
    )
    parser.add_argument("-V", "--version", action="version", version=f"kutub {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("login", help="authenticate with Telegram (one time)")
    p.add_argument("--api-id", help="api_id from my.telegram.org/apps")
    p.add_argument("--api-hash", help="api_hash from my.telegram.org/apps")
    p.set_defaults(handler=login)

    p = sub.add_parser("channels", help="list channels and groups you belong to")
    p.set_defaults(handler=channels)

    p = sub.add_parser("index", help="catalogue every ebook in a channel")
    p.add_argument("channel", help="channel id, @username, or exact title")
    p.add_argument("--limit", type=int, help="stop after N messages")
    p.set_defaults(handler=index)

    p = sub.add_parser("search", help="full-text search the catalogue")
    p.add_argument("query")
    p.add_argument("-n", type=int, default=25, help="max results (default 25)")
    p.set_defaults(handler=search)

    p = sub.add_parser("list", help="list recently indexed books")
    p.add_argument("--channel", help="filter by channel name")
    p.add_argument("-n", type=int, default=30, help="max results (default 30)")
    p.set_defaults(handler=listing)

    p = sub.add_parser("stats", help="totals by channel and format")
    p.set_defaults(handler=stats)

    p = sub.add_parser("get", help="download a book by id")
    p.add_argument("id", type=int)
    p.add_argument("--kindle", action="store_true", help="also send via Send-to-Kindle")
    p.add_argument("--device", help="Kindle serial (overrides KINDLE_SERIAL)")
    p.add_argument("--out", help="download directory")
    p.set_defaults(handler=get)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        if asyncio.iscoroutinefunction(args.handler):
            asyncio.run(args.handler(args))
        else:
            args.handler(args)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
