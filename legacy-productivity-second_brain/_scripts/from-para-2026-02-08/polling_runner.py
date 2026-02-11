#!/usr/bin/env python3
"""
Cron-friendly runner for polling Slack messages without Socket Mode.

Adds a simple file lock so overlapping cron invocations do not collide.
"""

from pathlib import Path
import fcntl
import sys

from process_inbox import process_all

LOCK_FILE = Path(__file__).parent / ".state" / "polling.lock"


def main() -> int:
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOCK_FILE, "w") as lock_handle:
        try:
            fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            # Another run is still in progress; exit silently for cron friendliness
            return 0

        try:
            process_all()
        finally:
            fcntl.flock(lock_handle, fcntl.LOCK_UN)

    return 0


if __name__ == "__main__":
    sys.exit(main())
