#!/usr/bin/env python3
"""Generate morning digest from Obsidian vault, send to Slack DM."""

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


def gather_active_items():
    """Collect active projects and people with follow-ups."""
    projects = []
    people = []
    
    projects_dir = VAULT_PATH / "projects"
    if projects_dir.exists():
        for f in projects_dir.glob("*.md"):
            try:
                content = f.read_text()
                if "---" in content:
                    parts = content.split("---")
                    if len(parts) >= 2:
                        fm = yaml.safe_load(parts[1])
                        if fm and fm.get("status") == "active":
                            projects.append(fm)
            except Exception as e:
                print(f"Error reading {f}: {e}")
    
    people_dir = VAULT_PATH / "people"
    if people_dir.exists():
        for f in people_dir.glob("*.md"):
            try:
                content = f.read_text()
                if "---" in content:
                    parts = content.split("---")
                    if len(parts) >= 2:
                        fm = yaml.safe_load(parts[1])
                        if fm and fm.get("follow_ups"):
                            people.append(fm)
            except Exception as e:
                print(f"Error reading {f}: {e}")
    
    return projects, people


def find_stalled_items(projects):
    """Find oldest or most stalled project."""
    stalled = None
    oldest_date = None
    
    for proj in projects:
        created = proj.get("created", "")
        if created:
            try:
                created_date = datetime.strptime(created, "%Y-%m-%d")
                if oldest_date is None or created_date < oldest_date:
                    oldest_date = created_date
                    stalled = proj
            except ValueError:
                continue
    
    return stalled


DIGEST_PROMPT = """
Generate a daily digest under 150 words.

Active projects:
{projects}

People with follow-ups:
{people}

Stalled item (if any):
{stalled}

Structure:
1. **Top 3 actions for today** (concrete next actions from projects)
2. **One thing you might be avoiding** (oldest or most stalled item)
3. **People follow-ups** (if any are time-sensitive)

Keep it scannable on a phone screen.
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


def generate_digest(projects, people, stalled):
    """
    Generate digest text using LLM provider.
    Falls back to simple formatting if no provider available.
    """
    provider = _get_llm_provider()
    
    if provider:
        try:
            context = {
                "projects": projects,
                "people": people,
                "stalled": stalled
            }
            return provider.generate_digest(context)
        except Exception as e:
            print(f"Error generating digest with LLM: {e}")
            # Fall through to fallback
    
    # Fallback formatting
    lines = ["*Daily Digest - " + datetime.now().strftime("%B %d, %Y") + "*\n"]
    
    # Top 3 actions
    lines.append("*Top 3 Actions:*")
    for i, proj in enumerate(projects[:3], 1):
        next_action = proj.get("next_action", "No action defined")
        name = proj.get("name", "Unnamed project")
        lines.append(f"{i}. {next_action} ({name})")
    
    # Stalled item
    if stalled:
        lines.append(f"\n*You might be avoiding:* {stalled.get('name', 'Unknown')}")
        if stalled.get("next_action"):
            lines.append(f"  Next: {stalled['next_action']}")
    
    # People follow-ups
    if people:
        lines.append("\n*People to follow up with:*")
        for person in people[:3]:
            name = person.get("name", "Unknown")
            follow_ups = person.get("follow_ups", [])
            if follow_ups:
                lines.append(f"• {name}: {follow_ups[0]}")
    
    return "\n".join(lines)


def main():
    """Main digest generation."""
    projects, people = gather_active_items()
    stalled = find_stalled_items(projects)
    
    digest_text = generate_digest(projects, people, stalled)
    
    # In actual use, Claude Code would call Claude API with DIGEST_PROMPT
    # and use the generated text here
    
    send_dm(digest_text)
    print("Digest sent to Slack DM")


if __name__ == "__main__":
    main()
