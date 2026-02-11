#!/usr/bin/env python3
"""
Real-time Socket Mode listener for Second Brain.
Processes messages instantly when posted to Slack.
Run as: uv run python3 realtime_listener.py
"""

import os
import sys
from pathlib import Path
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Import processing logic from existing script
sys.path.insert(0, str(Path(__file__).parent))
from process_inbox import process_message, VAULT_PATH
from state import is_message_processed, mark_message_processed

# Load environment variables
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")

if not SLACK_BOT_TOKEN:
    print("❌ Error: SLACK_BOT_TOKEN not set in environment")
    sys.exit(1)

if not SLACK_APP_TOKEN:
    print("❌ Error: SLACK_APP_TOKEN not set in environment")
    print("   Get it from: https://api.slack.com/apps > Your App > Basic Information > App-Level Tokens")
    sys.exit(1)

if not SLACK_CHANNEL_ID:
    print("❌ Error: SLACK_CHANNEL_ID not set in environment")
    sys.exit(1)

# Initialize Slack app
app = App(token=SLACK_BOT_TOKEN)

print("🚀 Second Brain real-time listener starting...")
print(f"📁 Vault: {VAULT_PATH}")
print(f"📢 Watching channel: {SLACK_CHANNEL_ID}")
print("✨ Ready! Post messages to your Slack channel.\n")


@app.event("message")
def handle_message_events(event, say, logger):
    """Handle incoming messages from Slack."""

    # Extract message details
    channel = event.get("channel")
    user = event.get("user")
    text = event.get("text", "")
    ts = event.get("ts")
    subtype = event.get("subtype")

    # Filter: Only process messages from our target channel
    if channel != SLACK_CHANNEL_ID:
        return

    # Skip bot messages, edits, and system messages
    if subtype in ["bot_message", "message_changed", "message_deleted"]:
        return

    # Skip messages we've already processed
    if is_message_processed(ts):
        logger.debug(f"Already processed message {ts}")
        return

    # Log the message
    print(f"\n📨 New message from user {user}")
    print(f"   Content: {text[:60]}{'...' if len(text) > 60 else ''}")

    try:
        # Process the message using existing logic
        # process_message expects a dict with 'text' and 'ts' keys
        msg = {
            "text": text,
            "ts": ts,
            "user": user
        }
        process_message(msg)

        # Mark as processed
        mark_message_processed(ts)

        print(f"✅ Processed successfully\n")

    except Exception as e:
        logger.error(f"Error processing message {ts}: {e}")
        print(f"❌ Error: {e}\n")


@app.event("app_mention")
def handle_mentions(event, say):
    """Handle when the bot is mentioned."""
    user = event.get("user")
    say(f"👋 Hi <@{user}>! Just post your thoughts here and I'll organize them in your second brain.")


# Start the Socket Mode handler
if __name__ == "__main__":
    try:
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
