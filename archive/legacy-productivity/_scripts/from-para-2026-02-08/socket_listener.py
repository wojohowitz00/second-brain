#!/usr/bin/env python3
"""
Slack Socket Mode bridge that forwards new channel messages to the
existing Second Brain processing pipeline.
"""

import logging
import os
from typing import Any, Dict

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from process_inbox import process_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _require_env(var: str) -> str:
    value = os.environ.get(var)
    if not value:
        raise RuntimeError(f"Environment variable {var} is required for Socket Mode")
    return value


# Load required env vars up front so failures are obvious
SLACK_BOT_TOKEN = _require_env("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = _require_env("SLACK_APP_TOKEN")
SLACK_CHANNEL_ID = _require_env("SLACK_CHANNEL_ID")

# Reuse the bot token that the rest of the scripts already use
app = App(token=SLACK_BOT_TOKEN)


@app.event("message")
def handle_message_events(body: Dict[str, Any], ack, logger):
    """
    Handle new messages from Slack in real time.
    """
    # Always ack immediately so Slack considers the event delivered
    ack()

    event = body.get("event", {})
    channel = event.get("channel")
    subtype = event.get("subtype")

    # Only process plain user messages in the configured channel
    if channel != SLACK_CHANNEL_ID:
        return
    if subtype:  # ignore bot edits/deletes/etc.
        return

    text = (event.get("text") or "").strip()
    ts = event.get("ts")

    if not text or not ts:
        return

    try:
        success = process_message({"text": text, "ts": ts})
        if not success:
            logger.error("Processing failed for message ts=%s", ts)
    except Exception as e:  # noqa: BLE001
        logger.exception("Unexpected error handling message ts=%s: %s", ts, e)


def main():
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    main()
