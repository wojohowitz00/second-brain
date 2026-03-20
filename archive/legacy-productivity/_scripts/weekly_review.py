#!/usr/bin/env python3
"""Generate weekly review from Obsidian vault, send to Slack DM."""

from pathlib import Path
from datetime import datetime, timedelta
import yaml
import os

# Use shared Slack client with retry logic
from slack_client import send_dm

# LLM provider system
from llm_provider import get_provider

# Keychain helper for credentials
try:
    from keychain_helper import get_llm_credentials
except ImportError:
    def get_llm_credentials():
        return {
            "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
            "LLM_API_KEY": os.environ.get("LLM_API_KEY", "")
        }

VAULT_PATH = Path.home() / "SecondBrain"


def gather_week_data():
    """Collect all items from past 7 days."""
    week_ago = datetime.now() - timedelta(days=7)
    
    # Read inbox logs from past week
    inbox_logs = []
    log_dir = VAULT_PATH / "_inbox_log"
    if log_dir.exists():
        for log_file in log_dir.glob("*.md"):
            try:
                date_str = log_file.stem
                log_date = datetime.strptime(date_str, "%Y-%m-%d")
                if log_date >= week_ago:
                    inbox_logs.append(log_file.read_text())
            except (ValueError, Exception) as e:
                print(f"Error reading log {log_file}: {e}")
    
    # Gather all active projects
    projects = []
    projects_dir = VAULT_PATH / "projects"
    if projects_dir.exists():
        for f in projects_dir.glob("*.md"):
            try:
                content = f.read_text()
                if "---" in content:
                    parts = content.split("---")
                    if len(parts) >= 2:
                        fm = yaml.safe_load(parts[1])
                        if fm:
                            projects.append(fm)
            except Exception as e:
                print(f"Error reading {f}: {e}")
    
    # Count items by type from logs
    stats = {"people": 0, "projects": 0, "ideas": 0, "admin": 0, "review": 0}
    for log_text in inbox_logs:
        for line in log_text.split("\n"):
            if "|" in line and "Destination" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    dest = parts[3].lower()
                    if "review" in dest:
                        stats["review"] += 1
                    elif dest in stats:
                        stats[dest] += 1
    
    return inbox_logs, projects, stats


REVIEW_PROMPT = """
Generate a weekly review under 250 words.

Items captured this week:
{stats}

Active projects:
{projects}

Structure:
1. **What you captured** (breakdown by type)
2. **Progress made** (projects moved forward)
3. **What's stuck** (projects with no recent activity)
4. **One insight** (pattern or theme from the week)

Keep it reflective and actionable.
"""


def _get_llm_provider():
    """Get configured LLM provider from environment or defaults."""
    provider_type = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    llm_creds = get_llm_credentials()
    
    try:
        if provider_type == "anthropic":
            api_key = llm_creds.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                return None
            return get_provider("anthropic", api_key=api_key, model=os.environ.get("LLM_MODEL", "claude-3-5-sonnet-20241022"))
        
        elif provider_type == "openai":
            api_key = llm_creds.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return None
            return get_provider("openai", api_key=api_key, model=os.environ.get("LLM_MODEL", "gpt-4"))
        
        elif provider_type == "ollama":
            base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
            model = os.environ.get("LLM_MODEL", "llama2")
            return get_provider("ollama", base_url=base_url, model=model)
        
        elif provider_type == "lmstudio":
            base_url = os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
            model = os.environ.get("LLM_MODEL", "local-model")
            return get_provider("lmstudio", base_url=base_url, model=model)
        
        else:
            # Default to Anthropic
            api_key = llm_creds.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
            if api_key:
                return get_provider("anthropic", api_key=api_key)
            return None
    
    except Exception as e:
        print(f"Error initializing LLM provider: {e}")
        return None


def generate_review(inbox_logs, projects, stats):
    """
    Generate review text using LLM provider.
    Falls back to simple formatting if no provider available.
    """
    provider = _get_llm_provider()
    
    if provider:
        try:
            context = {
                "projects": projects,
                "stats": stats
            }
            return provider.generate_review(context)
        except Exception as e:
            print(f"Error generating review with LLM: {e}")
            # Fall through to fallback
    
    # Fallback formatting
    lines = [
        f"*Weekly Review - Week of {datetime.now().strftime('%B %d, %Y')}*\n"
    ]
    
    # What you captured
    total = sum(stats.values())
    lines.append(f"*Captured {total} items this week:*")
    for dest, count in stats.items():
        if count > 0:
            lines.append(f"• {dest.title()}: {count}")
    
    # Progress
    active = [p for p in projects if p.get("status") == "active"]
    lines.append(f"\n*Active projects: {len(active)}*")
    for proj in active[:5]:
        name = proj.get("name", "Unnamed")
        next_action = proj.get("next_action", "")
        if next_action:
            lines.append(f"• {name}: {next_action}")
    
    # Stuck items
    stalled = [p for p in projects if p.get("status") == "active" and not p.get("next_action")]
    if stalled:
        lines.append(f"\n*Projects needing attention: {len(stalled)}*")
        for proj in stalled[:3]:
            lines.append(f"• {proj.get('name', 'Unnamed')}")
    
    return "\n".join(lines)


def main():
    """Main review generation."""
    inbox_logs, projects, stats = gather_week_data()
    
    review_text = generate_review(inbox_logs, projects, stats)
    
    # In actual use, Claude Code would call Claude API with REVIEW_PROMPT
    
    send_dm(review_text)
    print("Weekly review sent to Slack DM")


if __name__ == "__main__":
    main()
