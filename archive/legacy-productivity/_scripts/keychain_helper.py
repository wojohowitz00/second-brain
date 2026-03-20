#!/usr/bin/env python3
"""
Keychain helper for reading credentials from macOS Keychain.

This script reads credentials stored by the Swift app's KeychainManager.
Uses the `security` CLI tool to access Keychain.
"""

import subprocess
import sys
import os


def get_keychain_value(key: str, service: str = "com.secondbrain.app") -> str:
    """
    Get a value from macOS Keychain.
    
    Args:
        key: The account/key name
        service: The service name (default: com.secondbrain.app)
    
    Returns:
        The stored value, or empty string if not found
    """
    try:
        # Use security CLI to read from Keychain
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s", service,
                "-a", key,
                "-w"  # Write password to stdout
            ],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return ""
    except Exception as e:
        # Fallback to environment variable if Keychain access fails
        env_key = key.upper().replace("-", "_")
        return os.environ.get(env_key, "")


def get_slack_credentials() -> dict:
    """Get Slack credentials from Keychain."""
    return {
        "SLACK_BOT_TOKEN": get_keychain_value("slackBotToken"),
        "SLACK_CHANNEL_ID": get_keychain_value("slackChannelID"),
        "SLACK_USER_ID": get_keychain_value("slackUserID")
    }


def get_llm_credentials() -> dict:
    """Get LLM credentials from Keychain."""
    api_key = get_keychain_value("llmAPIKey")
    
    # Also check for provider-specific keys
    anthropic_key = get_keychain_value("anthropicAPIKey") or os.environ.get("ANTHROPIC_API_KEY", "")
    openai_key = get_keychain_value("openaiAPIKey") or os.environ.get("OPENAI_API_KEY", "")
    
    return {
        "ANTHROPIC_API_KEY": anthropic_key or api_key,
        "OPENAI_API_KEY": openai_key or api_key,
        "LLM_API_KEY": api_key
    }


if __name__ == "__main__":
    # CLI usage: python keychain_helper.py <key>
    if len(sys.argv) < 2:
        print("Usage: python keychain_helper.py <key>")
        print("Example: python keychain_helper.py slackBotToken")
        sys.exit(1)
    
    key = sys.argv[1]
    value = get_keychain_value(key)
    
    if value:
        print(value)
    else:
        sys.exit(1)
