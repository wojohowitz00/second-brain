#!/usr/bin/env python3
"""
Health check script for Second Brain system.

Verifies:
- Last successful run is recent
- No excessive failures
- State files are accessible

Run via cron hourly or manually to monitor system health.
"""

import os
import shutil
import sys
from datetime import datetime

from state import (
    is_system_healthy,
    get_last_run_status,
    get_failed_count_today,
)
from slack_client import send_dm, SlackAPIError


def check_health(max_age_minutes: int = 60, alert: bool = True) -> tuple[bool, list[str]]:
    """
    Run all health checks.

    Args:
        max_age_minutes: Maximum age of last successful run
        alert: Whether to send Slack alert on failure

    Returns:
        Tuple of (is_healthy, list of issue descriptions)
    """
    issues = []

    # Check last run
    healthy, message = is_system_healthy(max_age_minutes)
    if not healthy:
        issues.append(f"Run health: {message}")

    # Check failure count
    failed_today = get_failed_count_today()
    if failed_today > 0:
        issues.append(f"Failures today: {failed_today} messages")

    # Check if we can read status
    status = get_last_run_status()
    if not status:
        issues.append("Cannot read run status (state may be corrupted)")

    # Optional: YouTube dependencies (only when enabled)
    if _youtube_checks_enabled():
        issues.extend(check_youtube_dependencies())

    # Report
    is_healthy = len(issues) == 0

    if not is_healthy:
        print("UNHEALTHY - Issues found:")
        for issue in issues:
            print(f"  - {issue}")

        if alert:
            try:
                send_dm(
                    f"⚠️ *Second Brain Health Check Failed*\n\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"Issues:\n" + "\n".join(f"• {i}" for i in issues)
                )
                print("Alert sent to Slack DM")
            except SlackAPIError as e:
                print(f"Failed to send alert: {e}")
            except Exception as e:
                print(f"Unexpected error sending alert: {e}")
    else:
        print("HEALTHY - All checks passed")
        if status:
            last_success = status.get("last_success", "unknown")
            print(f"  Last success: {last_success}")

    return is_healthy, issues


def main():
    """Run health check from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Check Second Brain health")
    parser.add_argument(
        "--max-age",
        type=int,
        default=60,
        help="Maximum minutes since last successful run (default: 60)"
    )
    parser.add_argument(
        "--no-alert",
        action="store_true",
        help="Don't send Slack alert on failure"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output on failure"
    )

    args = parser.parse_args()

    is_healthy, issues = check_health(
        max_age_minutes=args.max_age,
        alert=not args.no_alert
    )

    if args.quiet and is_healthy:
        pass  # Silent success
    elif not is_healthy:
        sys.exit(1)


def _youtube_checks_enabled() -> bool:
    value = (os.environ.get("YOUTUBE_INGEST_ENABLED") or os.environ.get("CHECK_YOUTUBE_DEPS") or "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def check_youtube_dependencies() -> list[str]:
    issues = []
    if shutil.which("yt-dlp") is None:
        issues.append("YouTube: yt-dlp not found")
    if shutil.which("ffmpeg") is None:
        issues.append("YouTube: ffmpeg not found")
    mode = (os.environ.get("YOUTUBE_TRANSCRIPT_MODE") or "").strip().lower()
    if mode == "whisper" and shutil.which("whisper") is None:
        issues.append("YouTube: whisper not found (required for whisper mode)")
    return issues


if __name__ == "__main__":
    main()
