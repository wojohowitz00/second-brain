#!/bin/bash
# Uninstall Second Brain
set -e

PLIST_NAME="com.secondbrain.app.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
APP_PATH="/Applications/Second Brain.app"

echo "=== Uninstalling Second Brain ==="

# Parse arguments
LAUNCHAGENT_ONLY=false
if [ "$1" = "--launchagent-only" ]; then
    LAUNCHAGENT_ONLY=true
fi

# Unload and remove LaunchAgent
if [ -f "$LAUNCH_AGENTS_DIR/$PLIST_NAME" ]; then
    echo "Removing LaunchAgent..."
    launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_NAME" 2>/dev/null || true
    rm -f "$LAUNCH_AGENTS_DIR/$PLIST_NAME"
    echo "✓ LaunchAgent removed"
else
    echo "- LaunchAgent not found (already removed)"
fi

# Remove app if not launchagent-only
if [ "$LAUNCHAGENT_ONLY" = false ]; then
    if [ -d "$APP_PATH" ]; then
        echo "Removing application..."
        rm -rf "$APP_PATH"
        echo "✓ Application removed from /Applications"
    else
        echo "- Application not found in /Applications"
    fi
    
    # Remove log files
    echo "Removing log files..."
    rm -f /tmp/secondbrain.out.log /tmp/secondbrain.err.log 2>/dev/null || true
    echo "✓ Log files removed"
fi

echo ""
if [ "$LAUNCHAGENT_ONLY" = true ]; then
    echo "LaunchAgent uninstalled."
    echo "Second Brain will no longer start on login."
    echo "The application remains in /Applications."
else
    echo "Second Brain has been completely uninstalled."
fi
