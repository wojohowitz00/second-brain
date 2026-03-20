#!/usr/bin/env python3
"""
Status handler for updating task status via Slack commands.

Handles status transitions triggered by Slack thread replies:
- !done → status: done
- !progress → status: in_progress
- !blocked → status: blocked
- !backlog → status: backlog
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional

from task_parser import is_status_command, parse_status_command

# Configure module logger
logger = logging.getLogger(__name__)

# State directory and files
STATE_DIR = Path(__file__).parent / ".state"
MESSAGE_MAPPING_FILE = STATE_DIR / "message_mapping.json"


def get_file_for_message(message_id: str) -> Optional[Path]:
    """
    Look up the file path associated with a Slack message.
    
    Args:
        message_id: Slack message timestamp/ID
        
    Returns:
        Path to the file, or None if not found
    """
    try:
        if not MESSAGE_MAPPING_FILE.exists():
            return None
            
        mapping = json.loads(MESSAGE_MAPPING_FILE.read_text())
        file_path = mapping.get(message_id)
        
        if file_path:
            return Path(file_path)
        return None
        
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error reading message mapping: {e}")
        return None


def update_status_in_file(file_path: Path, new_status: str) -> bool:
    """
    Update the status field in a markdown file's YAML frontmatter.
    
    Args:
        file_path: Path to the markdown file
        new_status: New status value
        
    Returns:
        True if update succeeded, False otherwise
    """
    try:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return False
            
        content = file_path.read_text()
        
        # Check for frontmatter
        if not content.startswith("---"):
            logger.warning(f"No frontmatter in file: {file_path}")
            return False
        
        # Split frontmatter and body
        parts = content.split("---", 2)
        if len(parts) < 3:
            logger.warning(f"Invalid frontmatter format in: {file_path}")
            return False
            
        frontmatter = parts[1]
        body = parts[2]
        
        # Update status field using regex
        status_pattern = re.compile(r"^status:\s*.+$", re.MULTILINE)
        if status_pattern.search(frontmatter):
            new_frontmatter = status_pattern.sub(f"status: {new_status}", frontmatter)
        else:
            # Add status field if not present
            new_frontmatter = frontmatter.rstrip() + f"\nstatus: {new_status}\n"
        
        # Write back
        new_content = f"---{new_frontmatter}---{body}"
        file_path.write_text(new_content)
        
        logger.info(f"Updated status to '{new_status}' in {file_path}")
        return True
        
    except IOError as e:
        logger.error(f"Error updating file {file_path}: {e}")
        return False


def process_status_command(message_id: str, command_text: str) -> Dict:
    """
    Process a status command from a Slack thread reply.
    
    Args:
        message_id: Original message timestamp/ID
        command_text: Command text (e.g., "!done")
        
    Returns:
        Dict with:
        - success: bool
        - new_status: str (if success)
        - error: str (if failure)
    """
    # Validate command
    if not is_status_command(command_text):
        return {
            "success": False,
            "error": f"Invalid status command: {command_text}"
        }
    
    # Parse the new status
    new_status = parse_status_command(command_text)
    if new_status is None:
        return {
            "success": False,
            "error": f"Unknown status command: {command_text}"
        }
    
    # Look up file
    file_path = get_file_for_message(message_id)
    if file_path is None:
        return {
            "success": False,
            "error": f"Message not found: {message_id}"
        }
    
    # Update file
    if update_status_in_file(file_path, new_status):
        return {
            "success": True,
            "new_status": new_status,
            "file": str(file_path)
        }
    else:
        return {
            "success": False,
            "error": f"Failed to update file: {file_path}"
        }
