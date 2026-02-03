#!/usr/bin/env python3
"""
macOS Menu Bar application for Second Brain.

Provides visual feedback and controls for the sync process:
- Status icon (idle/syncing/error)
- Manual sync trigger
- Recent activity view
- Quit functionality

Usage:
    python menu_bar_app.py  # Starts the menu bar app
"""

import json
import os
import shutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import quote

try:
    import rumps
    RUMPS_AVAILABLE = True
except ImportError:
    RUMPS_AVAILABLE = False
    rumps = None

from ollama_client import OllamaClient
from process_inbox import process_all


# Status icons
STATUS_ICONS = {
    "idle": "🧠",
    "syncing": "🔄", 
    "error": "⚠️",
}

VALID_STATUSES = list(STATUS_ICONS.keys())

# State directory for persistence
STATE_DIR = Path(__file__).parent / ".state"
RECENT_ACTIVITY_FILE = STATE_DIR / "recent_activity.json"
MAX_RECENT_ACTIVITY = 5


class MenuBarCore:
    """
    Core logic for menu bar app, separated from UI.
    
    This class handles state, recent activity, and health checks
    without depending on rumps, making it testable.
    """
    
    def __init__(self, state_dir: Optional[Path] = None):
        """Initialize core state."""
        self.status = "idle"
        self.error_message: Optional[str] = None
        self._state_dir = state_dir or STATE_DIR
        self._sync_lock = threading.Lock()
        self._recent_activity_file = self._state_dir / "recent_activity.json"
    
    def set_status(self, status: str, message: Optional[str] = None):
        """
        Update the status.
        
        Args:
            status: One of 'idle', 'syncing', 'error'
            message: Optional error message for error status
            
        Raises:
            ValueError: If status is not valid
        """
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")
        
        self.status = status
        self.error_message = message if status == "error" else None
    
    def get_status_icon(self) -> str:
        """Get the icon for current status."""
        return STATUS_ICONS.get(self.status, STATUS_ICONS["idle"])
    
    def get_recent_activity(self) -> List[Dict]:
        """
        Get recent activity items.
        
        Returns:
            List of recent activity dicts with title, domain, path, timestamp
        """
        self._state_dir.mkdir(parents=True, exist_ok=True)
        
        if not self._recent_activity_file.exists():
            return []
        
        try:
            with open(self._recent_activity_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def add_recent_activity(self, title: str, domain: str, path: str):
        """
        Add item to recent activity.
        
        Args:
            title: Note title
            domain: Classification domain
            path: Path to the note file
        """
        self._state_dir.mkdir(parents=True, exist_ok=True)
        
        activity = self.get_recent_activity()
        
        # Add new item at front
        new_item = {
            "title": title,
            "domain": domain,
            "path": path,
            "timestamp": datetime.now().isoformat()
        }
        activity.insert(0, new_item)
        
        # Cap at max
        activity = activity[:MAX_RECENT_ACTIVITY]
        
        # Save
        with open(self._recent_activity_file, 'w') as f:
            json.dump(activity, f, indent=2)
    
    def health_check(self) -> Dict:
        """
        Check system health.
        
        Returns:
            Dict with health status for each component
        """
        result = {
            "ollama": {"ready": False, "error": None},
            "vault": {"ready": False, "error": None},
            "youtube": {"ready": True, "error": None},
        }
        
        # Check Ollama
        try:
            client = OllamaClient()
            status = client.health_check()
            result["ollama"]["ready"] = status.ready
            result["ollama"]["error"] = status.error
        except Exception as e:
            result["ollama"]["error"] = str(e)
        
        # Check vault
        from vault_scanner import VAULT_ROOT
        vault_path = VAULT_ROOT
        if vault_path.exists() and vault_path.is_dir():
            result["vault"]["ready"] = True
        else:
            result["vault"]["error"] = f"Vault not found at {vault_path}"

        # Optional: YouTube dependency checks (only when enabled)
        if _youtube_checks_enabled():
            yt_errors = []
            if shutil.which("yt-dlp") is None:
                yt_errors.append("yt-dlp not found")
            if shutil.which("ffmpeg") is None:
                yt_errors.append("ffmpeg not found")
            transcript_mode = (os.environ.get("YOUTUBE_TRANSCRIPT_MODE") or "").strip().lower()
            if transcript_mode == "whisper" and shutil.which("whisper") is None:
                yt_errors.append("whisper not found (required for whisper mode)")
            if yt_errors:
                result["youtube"]["ready"] = False
                result["youtube"]["error"] = "; ".join(yt_errors)

        return result
    
    def do_sync(self) -> bool:
        """
        Perform sync operation.
        
        Returns:
            True if sync completed successfully, False otherwise
        """
        if not self._sync_lock.acquire(blocking=False):
            return False  # Already syncing
        
        try:
            self.set_status("syncing")
            process_all()
            self.set_status("idle")
            return True
        except Exception as e:
            self.set_status("error", str(e)[:50])
            return False
        finally:
            self._sync_lock.release()


def open_note(path: str):
    """
    Open a note in Obsidian.
    
    Args:
        path: Absolute path to the note file
    """
    from vault_scanner import VAULT_ROOT
    vault_path = VAULT_ROOT
    try:
        note_path = Path(path)
        if note_path.is_relative_to(vault_path):
            relative_path = note_path.relative_to(vault_path)
        else:
            relative_path = note_path.name
    except (ValueError, TypeError):
        relative_path = Path(path).name
    
    # Build Obsidian URL (vault name = folder name, e.g. Home)
    encoded_path = quote(str(relative_path).replace('.md', ''))
    vault_name = vault_path.name
    obsidian_url = f"obsidian://open?vault={quote(vault_name)}&file={encoded_path}"
    
    # Open URL
    subprocess.run(["open", obsidian_url], check=False)


def _youtube_checks_enabled() -> bool:
    value = (os.environ.get("YOUTUBE_INGEST_ENABLED") or os.environ.get("CHECK_YOUTUBE_DEPS") or "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _infer_domain_from_path(note_path: Path) -> Optional[str]:
    from vault_scanner import VAULT_ROOT
    try:
        rel = Path(note_path).relative_to(VAULT_ROOT)
    except ValueError:
        return None
    return rel.parts[0] if rel.parts else None


class MenuBarApp:
    """
    macOS menu bar application for Second Brain.
    
    Wraps MenuBarCore with rumps UI. Can be instantiated without
    rumps available (for testing).
    """
    
    def __init__(self, core: Optional[MenuBarCore] = None):
        """Initialize the menu bar app."""
        self._core = core or MenuBarCore()
        self._rumps_app = None
        
        if RUMPS_AVAILABLE:
            self._init_rumps()
    
    def _init_rumps(self):
        """Initialize rumps app (only when rumps available)."""
        self._rumps_app = rumps.App(
            name="Second Brain",
            title=self._core.get_status_icon(),
            quit_button=None
        )
        self._build_menu()
    
    def _build_menu(self):
        """Build the menu structure."""
        if not self._rumps_app:
            return
            
        status_item = rumps.MenuItem(f"Status: {self._core.status.title()}")
        sync_item = rumps.MenuItem("Sync Now", callback=self._sync_callback)
        youtube_item = rumps.MenuItem("Ingest YouTube URL...", callback=self._ingest_youtube_callback)
        recent_menu = self._build_recent_menu()
        quit_item = rumps.MenuItem("Quit Second Brain", callback=self._quit_callback)
        
        self._rumps_app.menu = [
            status_item,
            None,  # Separator
            sync_item,
            youtube_item,
            recent_menu,
            None,  # Separator
            quit_item,
        ]
    
    def _build_recent_menu(self):
        """Build the recent activity submenu."""
        recent_menu = rumps.MenuItem("Recent Activity")
        activity = self._core.get_recent_activity()
        
        if not activity:
            recent_menu.add(rumps.MenuItem("No recent activity"))
        else:
            for item in activity:
                title = item.get('title', 'Untitled')
                if len(title) > 40:
                    title = title[:40] + "..."
                menu_item = rumps.MenuItem(title)
                # Store path for callback
                menu_item._note_path = item.get('path')
                recent_menu.add(menu_item)
        
        return recent_menu
    
    def _sync_callback(self, sender):
        """Callback for sync menu item."""
        thread = threading.Thread(target=self._do_sync_threaded, daemon=True)
        thread.start()

    def _ingest_youtube_callback(self, sender):
        """Prompt for YouTube URL and ingest in background."""
        if not self._rumps_app:
            return

        url_window = rumps.Window(
            "Enter a YouTube URL to ingest.",
            "Ingest YouTube URL"
        )
        url_response = url_window.run()
        if not url_response.clicked:
            return
        url = (url_response.text or "").strip()
        if not url:
            rumps.alert("YouTube ingest", "URL is required.")
            return

        domain_window = rumps.Window(
            "Optional domain (leave blank to use default).",
            "Domain (optional)"
        )
        domain_response = domain_window.run()
        domain = (domain_response.text or "").strip() if domain_response.clicked else ""

        thread = threading.Thread(
            target=self._do_youtube_ingest_threaded,
            args=(url, domain or None),
            daemon=True,
        )
        thread.start()
    
    def _do_sync_threaded(self):
        """Run sync in background thread."""
        self._core.do_sync()
        if self._rumps_app:
            self._rumps_app.title = self._core.get_status_icon()

    def _do_youtube_ingest_threaded(self, url: str, domain: Optional[str]):
        """Run YouTube ingestion in background thread."""
        try:
            self._core.set_status("syncing")
            if self._rumps_app:
                self._rumps_app.title = self._core.get_status_icon()

            from youtube_ingest import ingest_youtube
            note_path = ingest_youtube(url, domain=domain)

            if note_path:
                title = Path(note_path).stem
                domain_name = _infer_domain_from_path(note_path) or (domain or "Unknown")
                self._core.add_recent_activity(title, domain_name, str(note_path))

                try:
                    from notifications import notify_note_filed
                    notify_note_filed(
                        title=title,
                        domain=domain_name,
                        para_type="3_Resources",
                        path=str(note_path),
                    )
                except Exception:
                    pass
            else:
                rumps.alert("YouTube ingest", "URL already processed.")

            self._core.set_status("idle")
        except Exception as e:
            self._core.set_status("error", str(e)[:50])
            rumps.alert("YouTube ingest failed", str(e)[:300])
        finally:
            if self._rumps_app:
                self._rumps_app.title = self._core.get_status_icon()
    
    def _quit_callback(self, sender):
        """Callback for quit menu item."""
        if RUMPS_AVAILABLE:
            rumps.quit_application()
    
    # Public API delegating to core
    @property
    def status(self) -> str:
        return self._core.status
    
    @property
    def error_message(self) -> Optional[str]:
        return self._core.error_message
    
    def set_status(self, status: str, message: Optional[str] = None):
        """Set app status."""
        self._core.set_status(status, message)
        if self._rumps_app:
            self._rumps_app.title = self._core.get_status_icon()
    
    def get_recent_activity(self) -> List[Dict]:
        """Get recent activity."""
        return self._core.get_recent_activity()
    
    def add_recent_activity(self, title: str, domain: str, path: str):
        """Add to recent activity."""
        self._core.add_recent_activity(title, domain, path)
    
    def health_check(self) -> Dict:
        """Check system health."""
        return self._core.health_check()
    
    def sync_now(self, sender=None):
        """Trigger sync."""
        if self._rumps_app:
            self._sync_callback(sender)
        else:
            self._core.do_sync()
    
    def open_note(self, path: str):
        """Open note in Obsidian."""
        open_note(path)
    
    def quit(self, sender=None):
        """Quit the app."""
        self._quit_callback(sender)
    
    def run(self):
        """Run the app."""
        if self._rumps_app:
            self._rumps_app.run()
        else:
            raise RuntimeError("rumps not available - cannot run UI")


def run_menu_bar_app():
    """Start the menu bar application."""
    app = MenuBarApp()
    app.run()


if __name__ == "__main__":
    run_menu_bar_app()
