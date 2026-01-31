#!/usr/bin/env python3
"""
macOS notification system for Second Brain.

Sends native macOS notifications when notes are filed,
providing passive feedback without checking the menu bar.

Uses osascript for notifications (no external dependencies).
"""

import json
import subprocess
from pathlib import Path
from typing import Optional


# Default config directory
DEFAULT_CONFIG_DIR = Path(__file__).parent / ".state"
CONFIG_FILE = "notifications_config.json"


def _build_notification_script(title: str, subtitle: str) -> str:
    """
    Build AppleScript for displaying notification.
    
    Args:
        title: Notification subtitle (note title)
        subtitle: Notification body (filed location)
        
    Returns:
        AppleScript string
    """
    # Escape quotes for AppleScript
    title_escaped = title.replace('"', '\\"')
    subtitle_escaped = subtitle.replace('"', '\\"')
    
    return f'''display notification "{subtitle_escaped}" with title "Second Brain" subtitle "{title_escaped}"'''


def notify_note_filed(
    title: str,
    domain: str,
    para_type: str,
    path: str,
    config_dir: Optional[Path] = None
):
    """
    Send macOS notification when a note is filed.
    
    Args:
        title: Note title (will be truncated to 50 chars)
        domain: Classification domain (e.g., "Personal", "CCBH")
        para_type: PARA type (e.g., "1_Projects", "2_Areas")
        path: Path to the created note file
        config_dir: Optional config directory for settings
    """
    config_dir = config_dir or DEFAULT_CONFIG_DIR
    
    # Check if notifications are enabled
    if not notifications_enabled(config_dir=config_dir):
        return
    
    # Truncate long titles
    if len(title) > 50:
        title = title[:47] + "..."
    
    # Build notification content
    subtitle = f"Filed to {domain}/{para_type}"
    script = _build_notification_script(title, subtitle)
    
    # Send notification via osascript
    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=False,
            capture_output=True
        )
    except Exception:
        # Silently fail - notifications are non-critical
        pass


def notifications_enabled(config_dir: Optional[Path] = None) -> bool:
    """
    Check if notifications are enabled.
    
    Args:
        config_dir: Optional config directory
        
    Returns:
        True if notifications are enabled (default), False otherwise
    """
    config_dir = config_dir or DEFAULT_CONFIG_DIR
    config_file = config_dir / CONFIG_FILE
    
    if not config_file.exists():
        return True  # Enabled by default
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get("notifications_enabled", True)
    except (json.JSONDecodeError, IOError):
        return True


def set_notifications_enabled(enabled: bool, config_dir: Optional[Path] = None):
    """
    Enable or disable notifications.
    
    Args:
        enabled: True to enable, False to disable
        config_dir: Optional config directory
    """
    config_dir = config_dir or DEFAULT_CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / CONFIG_FILE
    
    # Load existing config or create new
    config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    config["notifications_enabled"] = enabled
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


# Convenience function for integration
def notify_classification_complete(
    title: str,
    domain: str,
    para_type: str,
    subject: str,
    category: str,
    path: str,
    config_dir: Optional[Path] = None
):
    """
    Notify when classification and filing is complete.
    
    Extended version with full classification details.
    
    Args:
        title: Note title
        domain: Classification domain
        para_type: PARA type
        subject: Subject folder
        category: Message category
        path: Path to created file
        config_dir: Optional config directory
    """
    notify_note_filed(
        title=title,
        domain=domain,
        para_type=para_type,
        path=path,
        config_dir=config_dir
    )
