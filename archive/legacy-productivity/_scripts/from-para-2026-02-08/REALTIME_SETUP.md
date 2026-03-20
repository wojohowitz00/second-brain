---
category:
- '[[Coding with AI]]'
- '[[App Development]]'
tags: []
created: '2026-01-28'
updated: '2026-01-28'
---
# Real-Time Socket Mode Setup

This guide helps you set up **instant processing** where your Second Brain processes Slack messages the moment you post them.

## Architecture

```
You post to Slack → WebSocket connection → realtime_listener.py → Instant processing → Obsidian
```

No polling, no delays, no webhooks needed!

---

## Step 1: Enable Socket Mode in Slack

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click your **Second Brain** app
3. Go to **Socket Mode** (in the left sidebar)
4. Toggle **Enable Socket Mode** to ON
5. You'll see a prompt about Event Subscriptions - click **OK**

---

## Step 2: Create App-Level Token

1. In your Slack app, go to **Basic Information** (left sidebar)
2. Scroll down to **App-Level Tokens**
3. Click **Generate Token and Scopes**
4. Name: `socket-mode`
5. Add scope: `connections:write`
6. Click **Generate**
7. **Copy the token** (starts with `xapp-`)
8. Click **Done**

---

## Step 3: Enable Event Subscriptions

1. Go to **Event Subscriptions** (left sidebar)
2. Toggle **Enable Events** to ON
3. Under **Subscribe to bot events**, add:
   - `message.channels` (for public channels)
   - `message.groups` (for private channels)
   - `app_mention` (optional, for @mentions)
4. Click **Save Changes**

**Note:** You might see a "Request URL" field - **ignore it**! Socket Mode doesn't need a public URL.

---

## Step 4: Add Token to .env

Edit your `.env` file:

```bash
cd ~/SecondBrain/_scripts
nano .env  # or use your preferred editor
```

Replace the placeholder with your real token:

```bash
export SLACK_APP_TOKEN="xapp-1-A0123456789-7890123456789-abc123def456..."
```

Save and exit.

---

## Step 5: Test the Real-Time Listener

Run the listener in your terminal:

```bash
cd ~/SecondBrain/_scripts
./start_listener.sh
```

You should see:

```
🚀 Second Brain real-time listener starting...
📁 Vault: /Users/richardyu/SecondBrain
📢 Watching channel: C0A7FJU1SDD
✨ Ready! Post messages to your Slack channel.
```

Now go to your `#wry_sb` channel and post a test message:

```
project: Testing my real-time second brain - this should process instantly!
```

You should see output in the terminal showing the message was received and processed!

---

## Step 6: Run as Background Service (Optional)

To have the listener start automatically when you log in:

### Install as macOS LaunchAgent

```bash
# Copy the plist file to LaunchAgents
cp ~/SecondBrain/_scripts/com.secondbrain.listener.plist ~/Library/LaunchAgents/

# Load and start the service
launchctl load ~/Library/LaunchAgents/com.secondbrain.listener.plist
```

### Check if it's running

```bash
launchctl list | grep secondbrain
```

### View logs

```bash
# Output log
tail -f /tmp/secondbrain-listener.log

# Error log
tail -f /tmp/secondbrain-listener-error.log
```

### Stop the service

```bash
launchctl unload ~/Library/LaunchAgents/com.secondbrain.listener.plist
```

### Restart the service

```bash
launchctl unload ~/Library/LaunchAgents/com.secondbrain.listener.plist
launchctl load ~/Library/LaunchAgents/com.secondbrain.listener.plist
```

---

## Troubleshooting

### "SLACK_APP_TOKEN not set"

Make sure you:
1. Created the app-level token in Slack
2. Added it to `.env` with the correct variable name
3. Ran `source .env` or restarted your terminal

### "No new messages"

Check that:
1. Socket Mode is enabled in your Slack app
2. Event Subscriptions are enabled
3. Your bot is invited to the channel (`/invite @SecondBrain`)

### Messages not processing

1. Check the terminal output for errors
2. Verify the channel ID in `.env` matches your `#wry_sb` channel
3. Check logs: `tail -f /tmp/secondbrain-listener.log`

### Can't connect to Slack

- Check your internet connection
- Verify your SLACK_BOT_TOKEN is still valid
- Make sure Socket Mode is enabled in the Slack app settings

---

## Comparison: Polling vs Real-Time

| Feature | Old (Polling) | New (Socket Mode) |
|---------|--------------|-------------------|
| Speed | Every 2 minutes | Instant |
| Resource usage | Low (only runs briefly) | Constant (listener always running) |
| Setup | Simple cron job | Requires Socket Mode + token |
| Reliability | High | High (auto-reconnects) |

**Recommendation:** Use Socket Mode for the best experience! The constant connection uses minimal resources.

---

## Going Back to Polling (If Needed)

If you prefer the old polling method:

1. Stop the listener (Ctrl+C or unload LaunchAgent)
2. Set up cron jobs as described in the main README
3. Socket Mode can stay enabled - it won't interfere

---

## Next Steps

Once real-time processing is working:

1. Open your Obsidian vault: `~/SecondBrain`
2. Install the **Dataview** plugin
3. Open `dashboard.md` to see your captured notes
4. Try trigger commands: post `digest`, `review`, or `health` to your channel

Enjoy your real-time second brain! 🧠✨
