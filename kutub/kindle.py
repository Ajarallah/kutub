"""Send-to-Kindle delivery through the stkclient CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from . import config


def resolve_serial(override: str | None = None) -> str | None:
    return (
        override
        or os.environ.get("KINDLE_SERIAL")
        or config.load().get("kindle_serial")
    )


def send(path: Path, title: str, author: str, ext: str, device: str | None) -> bool:
    serial = resolve_serial(device)
    if not serial:
        print(
            "No Kindle device configured.\n"
            "  export KINDLE_SERIAL=<serial>\n"
            "Find yours with: python3 -m stkclient devices",
            file=sys.stderr,
        )
        return False

    command = [
        sys.executable, "-m", "stkclient", "send", str(path), serial,
        "--title", title,
        "--format", ext.lstrip("."),
    ]
    if author:
        command += ["--author", author]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("Sent to Kindle.")
        return True

    print(f"Kindle delivery failed:\n{result.stderr.strip()[:500]}", file=sys.stderr)
    return False
