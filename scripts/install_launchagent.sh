#!/bin/bash
# Install Second Brain LaunchAgent for login startup
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST_NAME="com.secondbrain.app.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "=== Installing Second Brain LaunchAgent ==="

# Check if app is installed
if [ ! -d "/Applications/Second Brain.app" ]; then
    echo "Error: Second Brain.app not found in /Applications"
    echo "Please install the app first using the .pkg installer"
    exit 1
fi

# Create LaunchAgents directory if needed
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy plist
echo "Copying LaunchAgent plist..."
cp "$PROJECT_DIR/resources/$PLIST_NAME" "$LAUNCH_AGENTS_DIR/"

# Unload if already loaded (ignore errors)
launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_NAME" 2>/dev/null || true

# Load the agent
echo "Loading LaunchAgent..."
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_NAME"

echo ""
echo "✓ LaunchAgent installed"
echo ""
echo "Second Brain will now start automatically on login."
echo ""
echo "To disable: ./scripts/uninstall.sh --launchagent-only"
echo "To check status: launchctl list | grep secondbrain"
