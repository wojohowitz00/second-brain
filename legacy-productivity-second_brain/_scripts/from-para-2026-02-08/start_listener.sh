#!/bin/bash
# Start the real-time Second Brain listener
# Run with: ./start_listener.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

# Load environment variables
if [ -f ".env" ]; then
    source .env
else
    echo "❌ Error: .env file not found"
    echo "   Copy .env.example to .env and fill in your Slack tokens"
    exit 1
fi

# Check if app token is set
if [ "$SLACK_APP_TOKEN" = "xapp-YOUR-APP-TOKEN-HERE" ] || [ -z "$SLACK_APP_TOKEN" ]; then
    echo "❌ Error: SLACK_APP_TOKEN not configured"
    echo ""
    echo "To get your App-Level Token:"
    echo "  1. Go to: https://api.slack.com/apps"
    echo "  2. Select your app"
    echo "  3. Go to: Basic Information > App-Level Tokens"
    echo "  4. Click 'Generate Token and Scopes'"
    echo "  5. Name: 'socket-mode', Scope: 'connections:write'"
    echo "  6. Copy the token (starts with xapp-)"
    echo "  7. Paste it in .env as SLACK_APP_TOKEN"
    echo ""
    exit 1
fi

echo "🚀 Starting Second Brain real-time listener..."
export PATH="/Users/richardyu/.local/bin:$PATH"
uv run python3 realtime_listener.py
